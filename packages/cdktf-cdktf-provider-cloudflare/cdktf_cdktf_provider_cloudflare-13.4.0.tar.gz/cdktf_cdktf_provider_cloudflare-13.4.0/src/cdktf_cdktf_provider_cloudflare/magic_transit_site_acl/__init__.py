r'''
# `cloudflare_magic_transit_site_acl`

Refer to the Terraform Registry for docs: [`cloudflare_magic_transit_site_acl`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl).
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


class MagicTransitSiteAcl(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.magicTransitSiteAcl.MagicTransitSiteAcl",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl cloudflare_magic_transit_site_acl}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        lan1: typing.Union["MagicTransitSiteAclLan1", typing.Dict[builtins.str, typing.Any]],
        lan2: typing.Union["MagicTransitSiteAclLan2", typing.Dict[builtins.str, typing.Any]],
        name: builtins.str,
        site_id: builtins.str,
        description: typing.Optional[builtins.str] = None,
        forward_locally: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        protocols: typing.Optional[typing.Sequence[builtins.str]] = None,
        unidirectional: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl cloudflare_magic_transit_site_acl} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#account_id MagicTransitSiteAcl#account_id}
        :param lan1: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#lan_1 MagicTransitSiteAcl#lan_1}.
        :param lan2: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#lan_2 MagicTransitSiteAcl#lan_2}.
        :param name: The name of the ACL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#name MagicTransitSiteAcl#name}
        :param site_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#site_id MagicTransitSiteAcl#site_id}
        :param description: Description for the ACL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#description MagicTransitSiteAcl#description}
        :param forward_locally: The desired forwarding action for this ACL policy. If set to "false", the policy will forward traffic to Cloudflare. If set to "true", the policy will forward traffic locally on the Magic Connector. If not included in request, will default to false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#forward_locally MagicTransitSiteAcl#forward_locally}
        :param protocols: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#protocols MagicTransitSiteAcl#protocols}.
        :param unidirectional: The desired traffic direction for this ACL policy. If set to "false", the policy will allow bidirectional traffic. If set to "true", the policy will only allow traffic in one direction. If not included in request, will default to false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#unidirectional MagicTransitSiteAcl#unidirectional}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d84d277e913722ff35466a2037d3d78f433a3ba3b0ed0d2861a816aba5ead91f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = MagicTransitSiteAclConfig(
            account_id=account_id,
            lan1=lan1,
            lan2=lan2,
            name=name,
            site_id=site_id,
            description=description,
            forward_locally=forward_locally,
            protocols=protocols,
            unidirectional=unidirectional,
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
        '''Generates CDKTF code for importing a MagicTransitSiteAcl resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the MagicTransitSiteAcl to import.
        :param import_from_id: The id of the existing MagicTransitSiteAcl that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the MagicTransitSiteAcl to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4644f3b5d39954f6c86004bc99d4f3a2f8eee53c59c25bebfc92190f2ad65507)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putLan1")
    def put_lan1(
        self,
        *,
        lan_id: builtins.str,
        lan_name: typing.Optional[builtins.str] = None,
        port_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
        ports: typing.Optional[typing.Sequence[jsii.Number]] = None,
        subnets: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param lan_id: The identifier for the LAN you want to create an ACL policy with. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#lan_id MagicTransitSiteAcl#lan_id}
        :param lan_name: The name of the LAN based on the provided lan_id. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#lan_name MagicTransitSiteAcl#lan_name}
        :param port_ranges: Array of port ranges on the provided LAN that will be included in the ACL. If no ports or port rangess are provided, communication on any port on this LAN is allowed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#port_ranges MagicTransitSiteAcl#port_ranges}
        :param ports: Array of ports on the provided LAN that will be included in the ACL. If no ports or port ranges are provided, communication on any port on this LAN is allowed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#ports MagicTransitSiteAcl#ports}
        :param subnets: Array of subnet IPs within the LAN that will be included in the ACL. If no subnets are provided, communication on any subnets on this LAN are allowed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#subnets MagicTransitSiteAcl#subnets}
        '''
        value = MagicTransitSiteAclLan1(
            lan_id=lan_id,
            lan_name=lan_name,
            port_ranges=port_ranges,
            ports=ports,
            subnets=subnets,
        )

        return typing.cast(None, jsii.invoke(self, "putLan1", [value]))

    @jsii.member(jsii_name="putLan2")
    def put_lan2(
        self,
        *,
        lan_id: builtins.str,
        lan_name: typing.Optional[builtins.str] = None,
        port_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
        ports: typing.Optional[typing.Sequence[jsii.Number]] = None,
        subnets: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param lan_id: The identifier for the LAN you want to create an ACL policy with. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#lan_id MagicTransitSiteAcl#lan_id}
        :param lan_name: The name of the LAN based on the provided lan_id. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#lan_name MagicTransitSiteAcl#lan_name}
        :param port_ranges: Array of port ranges on the provided LAN that will be included in the ACL. If no ports or port rangess are provided, communication on any port on this LAN is allowed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#port_ranges MagicTransitSiteAcl#port_ranges}
        :param ports: Array of ports on the provided LAN that will be included in the ACL. If no ports or port ranges are provided, communication on any port on this LAN is allowed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#ports MagicTransitSiteAcl#ports}
        :param subnets: Array of subnet IPs within the LAN that will be included in the ACL. If no subnets are provided, communication on any subnets on this LAN are allowed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#subnets MagicTransitSiteAcl#subnets}
        '''
        value = MagicTransitSiteAclLan2(
            lan_id=lan_id,
            lan_name=lan_name,
            port_ranges=port_ranges,
            ports=ports,
            subnets=subnets,
        )

        return typing.cast(None, jsii.invoke(self, "putLan2", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetForwardLocally")
    def reset_forward_locally(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForwardLocally", []))

    @jsii.member(jsii_name="resetProtocols")
    def reset_protocols(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProtocols", []))

    @jsii.member(jsii_name="resetUnidirectional")
    def reset_unidirectional(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnidirectional", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="lan1")
    def lan1(self) -> "MagicTransitSiteAclLan1OutputReference":
        return typing.cast("MagicTransitSiteAclLan1OutputReference", jsii.get(self, "lan1"))

    @builtins.property
    @jsii.member(jsii_name="lan2")
    def lan2(self) -> "MagicTransitSiteAclLan2OutputReference":
        return typing.cast("MagicTransitSiteAclLan2OutputReference", jsii.get(self, "lan2"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="forwardLocallyInput")
    def forward_locally_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "forwardLocallyInput"))

    @builtins.property
    @jsii.member(jsii_name="lan1Input")
    def lan1_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "MagicTransitSiteAclLan1"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "MagicTransitSiteAclLan1"]], jsii.get(self, "lan1Input"))

    @builtins.property
    @jsii.member(jsii_name="lan2Input")
    def lan2_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "MagicTransitSiteAclLan2"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "MagicTransitSiteAclLan2"]], jsii.get(self, "lan2Input"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="protocolsInput")
    def protocols_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "protocolsInput"))

    @builtins.property
    @jsii.member(jsii_name="siteIdInput")
    def site_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "siteIdInput"))

    @builtins.property
    @jsii.member(jsii_name="unidirectionalInput")
    def unidirectional_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "unidirectionalInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1108d6658e96a7cdfdb89953f2c788c2e82cf250cd5a206c828d50e2169ac5c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a83c421912a482c94621675e07e2575fb7afa9077a9dfcf4da778b6fda240f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="forwardLocally")
    def forward_locally(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "forwardLocally"))

    @forward_locally.setter
    def forward_locally(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a334ff4e00e67df13bd6ee7ea52cb25af0abc32378f0d1809c718fc9dab8dea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forwardLocally", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6405c9fb9503f5b0d0dec6e350028ed78f18579c73c455cdf04c9964ec503429)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="protocols")
    def protocols(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "protocols"))

    @protocols.setter
    def protocols(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3ea25da1c237a59762a3deb01ce8ca3b180d5d58e1ecdb34481c83274e03623)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "protocols", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="siteId")
    def site_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "siteId"))

    @site_id.setter
    def site_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2ce1b21ee2eeadcc369467aded062d10c2cee30fbef250c7899746e35b65532)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "siteId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="unidirectional")
    def unidirectional(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "unidirectional"))

    @unidirectional.setter
    def unidirectional(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efefe06e766025a5a5378a089783fd7366f7ab005307d266171c74d7bc46e8b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unidirectional", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.magicTransitSiteAcl.MagicTransitSiteAclConfig",
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
        "lan1": "lan1",
        "lan2": "lan2",
        "name": "name",
        "site_id": "siteId",
        "description": "description",
        "forward_locally": "forwardLocally",
        "protocols": "protocols",
        "unidirectional": "unidirectional",
    },
)
class MagicTransitSiteAclConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        lan1: typing.Union["MagicTransitSiteAclLan1", typing.Dict[builtins.str, typing.Any]],
        lan2: typing.Union["MagicTransitSiteAclLan2", typing.Dict[builtins.str, typing.Any]],
        name: builtins.str,
        site_id: builtins.str,
        description: typing.Optional[builtins.str] = None,
        forward_locally: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        protocols: typing.Optional[typing.Sequence[builtins.str]] = None,
        unidirectional: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#account_id MagicTransitSiteAcl#account_id}
        :param lan1: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#lan_1 MagicTransitSiteAcl#lan_1}.
        :param lan2: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#lan_2 MagicTransitSiteAcl#lan_2}.
        :param name: The name of the ACL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#name MagicTransitSiteAcl#name}
        :param site_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#site_id MagicTransitSiteAcl#site_id}
        :param description: Description for the ACL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#description MagicTransitSiteAcl#description}
        :param forward_locally: The desired forwarding action for this ACL policy. If set to "false", the policy will forward traffic to Cloudflare. If set to "true", the policy will forward traffic locally on the Magic Connector. If not included in request, will default to false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#forward_locally MagicTransitSiteAcl#forward_locally}
        :param protocols: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#protocols MagicTransitSiteAcl#protocols}.
        :param unidirectional: The desired traffic direction for this ACL policy. If set to "false", the policy will allow bidirectional traffic. If set to "true", the policy will only allow traffic in one direction. If not included in request, will default to false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#unidirectional MagicTransitSiteAcl#unidirectional}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(lan1, dict):
            lan1 = MagicTransitSiteAclLan1(**lan1)
        if isinstance(lan2, dict):
            lan2 = MagicTransitSiteAclLan2(**lan2)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__999d0272748716b72e5d98668961d7c81cff77545d8b6e511233283739231834)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument lan1", value=lan1, expected_type=type_hints["lan1"])
            check_type(argname="argument lan2", value=lan2, expected_type=type_hints["lan2"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument site_id", value=site_id, expected_type=type_hints["site_id"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument forward_locally", value=forward_locally, expected_type=type_hints["forward_locally"])
            check_type(argname="argument protocols", value=protocols, expected_type=type_hints["protocols"])
            check_type(argname="argument unidirectional", value=unidirectional, expected_type=type_hints["unidirectional"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
            "lan1": lan1,
            "lan2": lan2,
            "name": name,
            "site_id": site_id,
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
        if description is not None:
            self._values["description"] = description
        if forward_locally is not None:
            self._values["forward_locally"] = forward_locally
        if protocols is not None:
            self._values["protocols"] = protocols
        if unidirectional is not None:
            self._values["unidirectional"] = unidirectional

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#account_id MagicTransitSiteAcl#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lan1(self) -> "MagicTransitSiteAclLan1":
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#lan_1 MagicTransitSiteAcl#lan_1}.'''
        result = self._values.get("lan1")
        assert result is not None, "Required property 'lan1' is missing"
        return typing.cast("MagicTransitSiteAclLan1", result)

    @builtins.property
    def lan2(self) -> "MagicTransitSiteAclLan2":
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#lan_2 MagicTransitSiteAcl#lan_2}.'''
        result = self._values.get("lan2")
        assert result is not None, "Required property 'lan2' is missing"
        return typing.cast("MagicTransitSiteAclLan2", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the ACL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#name MagicTransitSiteAcl#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def site_id(self) -> builtins.str:
        '''Identifier.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#site_id MagicTransitSiteAcl#site_id}
        '''
        result = self._values.get("site_id")
        assert result is not None, "Required property 'site_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description for the ACL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#description MagicTransitSiteAcl#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def forward_locally(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''The desired forwarding action for this ACL policy.

        If set to "false", the policy will forward traffic to Cloudflare. If set to "true", the policy will forward traffic locally on the Magic Connector. If not included in request, will default to false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#forward_locally MagicTransitSiteAcl#forward_locally}
        '''
        result = self._values.get("forward_locally")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def protocols(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#protocols MagicTransitSiteAcl#protocols}.'''
        result = self._values.get("protocols")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def unidirectional(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''The desired traffic direction for this ACL policy.

        If set to "false", the policy will allow bidirectional traffic. If set to "true", the policy will only allow traffic in one direction. If not included in request, will default to false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#unidirectional MagicTransitSiteAcl#unidirectional}
        '''
        result = self._values.get("unidirectional")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MagicTransitSiteAclConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.magicTransitSiteAcl.MagicTransitSiteAclLan1",
    jsii_struct_bases=[],
    name_mapping={
        "lan_id": "lanId",
        "lan_name": "lanName",
        "port_ranges": "portRanges",
        "ports": "ports",
        "subnets": "subnets",
    },
)
class MagicTransitSiteAclLan1:
    def __init__(
        self,
        *,
        lan_id: builtins.str,
        lan_name: typing.Optional[builtins.str] = None,
        port_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
        ports: typing.Optional[typing.Sequence[jsii.Number]] = None,
        subnets: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param lan_id: The identifier for the LAN you want to create an ACL policy with. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#lan_id MagicTransitSiteAcl#lan_id}
        :param lan_name: The name of the LAN based on the provided lan_id. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#lan_name MagicTransitSiteAcl#lan_name}
        :param port_ranges: Array of port ranges on the provided LAN that will be included in the ACL. If no ports or port rangess are provided, communication on any port on this LAN is allowed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#port_ranges MagicTransitSiteAcl#port_ranges}
        :param ports: Array of ports on the provided LAN that will be included in the ACL. If no ports or port ranges are provided, communication on any port on this LAN is allowed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#ports MagicTransitSiteAcl#ports}
        :param subnets: Array of subnet IPs within the LAN that will be included in the ACL. If no subnets are provided, communication on any subnets on this LAN are allowed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#subnets MagicTransitSiteAcl#subnets}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34d6cc1acab8ad1a9e708482c2120864868b7eacfaa9b33145e8470cfcae3066)
            check_type(argname="argument lan_id", value=lan_id, expected_type=type_hints["lan_id"])
            check_type(argname="argument lan_name", value=lan_name, expected_type=type_hints["lan_name"])
            check_type(argname="argument port_ranges", value=port_ranges, expected_type=type_hints["port_ranges"])
            check_type(argname="argument ports", value=ports, expected_type=type_hints["ports"])
            check_type(argname="argument subnets", value=subnets, expected_type=type_hints["subnets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "lan_id": lan_id,
        }
        if lan_name is not None:
            self._values["lan_name"] = lan_name
        if port_ranges is not None:
            self._values["port_ranges"] = port_ranges
        if ports is not None:
            self._values["ports"] = ports
        if subnets is not None:
            self._values["subnets"] = subnets

    @builtins.property
    def lan_id(self) -> builtins.str:
        '''The identifier for the LAN you want to create an ACL policy with.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#lan_id MagicTransitSiteAcl#lan_id}
        '''
        result = self._values.get("lan_id")
        assert result is not None, "Required property 'lan_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lan_name(self) -> typing.Optional[builtins.str]:
        '''The name of the LAN based on the provided lan_id.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#lan_name MagicTransitSiteAcl#lan_name}
        '''
        result = self._values.get("lan_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port_ranges(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Array of port ranges on the provided LAN that will be included in the ACL.

        If no ports or port rangess are provided, communication on any port on this LAN is allowed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#port_ranges MagicTransitSiteAcl#port_ranges}
        '''
        result = self._values.get("port_ranges")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ports(self) -> typing.Optional[typing.List[jsii.Number]]:
        '''Array of ports on the provided LAN that will be included in the ACL.

        If no ports or port ranges are provided, communication on any port on this LAN is allowed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#ports MagicTransitSiteAcl#ports}
        '''
        result = self._values.get("ports")
        return typing.cast(typing.Optional[typing.List[jsii.Number]], result)

    @builtins.property
    def subnets(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Array of subnet IPs within the LAN that will be included in the ACL.

        If no subnets are provided, communication on any subnets on this LAN are allowed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#subnets MagicTransitSiteAcl#subnets}
        '''
        result = self._values.get("subnets")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MagicTransitSiteAclLan1(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MagicTransitSiteAclLan1OutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.magicTransitSiteAcl.MagicTransitSiteAclLan1OutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__abf8794bf9059dafe7a6978960a857cc3510a5f6938c9c85a71352c4e39d9669)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetLanName")
    def reset_lan_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLanName", []))

    @jsii.member(jsii_name="resetPortRanges")
    def reset_port_ranges(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPortRanges", []))

    @jsii.member(jsii_name="resetPorts")
    def reset_ports(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPorts", []))

    @jsii.member(jsii_name="resetSubnets")
    def reset_subnets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubnets", []))

    @builtins.property
    @jsii.member(jsii_name="lanIdInput")
    def lan_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lanIdInput"))

    @builtins.property
    @jsii.member(jsii_name="lanNameInput")
    def lan_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lanNameInput"))

    @builtins.property
    @jsii.member(jsii_name="portRangesInput")
    def port_ranges_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "portRangesInput"))

    @builtins.property
    @jsii.member(jsii_name="portsInput")
    def ports_input(self) -> typing.Optional[typing.List[jsii.Number]]:
        return typing.cast(typing.Optional[typing.List[jsii.Number]], jsii.get(self, "portsInput"))

    @builtins.property
    @jsii.member(jsii_name="subnetsInput")
    def subnets_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "subnetsInput"))

    @builtins.property
    @jsii.member(jsii_name="lanId")
    def lan_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lanId"))

    @lan_id.setter
    def lan_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29a7983d049b61e0d0f8991079ccd16cebf0607a265c896f2b3d853c2f70cc03)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lanId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lanName")
    def lan_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lanName"))

    @lan_name.setter
    def lan_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__018f7b93db45d1224f8156ed6433ee0f6f958e744a45530037ecbbdde7b8f598)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lanName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="portRanges")
    def port_ranges(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "portRanges"))

    @port_ranges.setter
    def port_ranges(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77e7a92ed1af9e07633aa65ec1f1dc52f90de7388aa8d1cf1ecd6d0d6347f187)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "portRanges", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ports")
    def ports(self) -> typing.List[jsii.Number]:
        return typing.cast(typing.List[jsii.Number], jsii.get(self, "ports"))

    @ports.setter
    def ports(self, value: typing.List[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e526cb306c8dc149f4651b450f768740d2472b825fb039a868fb7f6a88847ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ports", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subnets")
    def subnets(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subnets"))

    @subnets.setter
    def subnets(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__019f7f1cfd7bc6655beab5d2ecec3eeb90b1c022e44bf48ea26c8a14929e3e75)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subnets", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteAclLan1]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteAclLan1]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteAclLan1]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5c8b39ba05ce32671287c4513b0b477d2a3b055d71d7c80d633c192e841c840)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.magicTransitSiteAcl.MagicTransitSiteAclLan2",
    jsii_struct_bases=[],
    name_mapping={
        "lan_id": "lanId",
        "lan_name": "lanName",
        "port_ranges": "portRanges",
        "ports": "ports",
        "subnets": "subnets",
    },
)
class MagicTransitSiteAclLan2:
    def __init__(
        self,
        *,
        lan_id: builtins.str,
        lan_name: typing.Optional[builtins.str] = None,
        port_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
        ports: typing.Optional[typing.Sequence[jsii.Number]] = None,
        subnets: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param lan_id: The identifier for the LAN you want to create an ACL policy with. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#lan_id MagicTransitSiteAcl#lan_id}
        :param lan_name: The name of the LAN based on the provided lan_id. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#lan_name MagicTransitSiteAcl#lan_name}
        :param port_ranges: Array of port ranges on the provided LAN that will be included in the ACL. If no ports or port rangess are provided, communication on any port on this LAN is allowed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#port_ranges MagicTransitSiteAcl#port_ranges}
        :param ports: Array of ports on the provided LAN that will be included in the ACL. If no ports or port ranges are provided, communication on any port on this LAN is allowed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#ports MagicTransitSiteAcl#ports}
        :param subnets: Array of subnet IPs within the LAN that will be included in the ACL. If no subnets are provided, communication on any subnets on this LAN are allowed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#subnets MagicTransitSiteAcl#subnets}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__903c99fcfcaa2f9066c5d8cee2e27ce46bde8eb3b46f14fc51689e520569416c)
            check_type(argname="argument lan_id", value=lan_id, expected_type=type_hints["lan_id"])
            check_type(argname="argument lan_name", value=lan_name, expected_type=type_hints["lan_name"])
            check_type(argname="argument port_ranges", value=port_ranges, expected_type=type_hints["port_ranges"])
            check_type(argname="argument ports", value=ports, expected_type=type_hints["ports"])
            check_type(argname="argument subnets", value=subnets, expected_type=type_hints["subnets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "lan_id": lan_id,
        }
        if lan_name is not None:
            self._values["lan_name"] = lan_name
        if port_ranges is not None:
            self._values["port_ranges"] = port_ranges
        if ports is not None:
            self._values["ports"] = ports
        if subnets is not None:
            self._values["subnets"] = subnets

    @builtins.property
    def lan_id(self) -> builtins.str:
        '''The identifier for the LAN you want to create an ACL policy with.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#lan_id MagicTransitSiteAcl#lan_id}
        '''
        result = self._values.get("lan_id")
        assert result is not None, "Required property 'lan_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lan_name(self) -> typing.Optional[builtins.str]:
        '''The name of the LAN based on the provided lan_id.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#lan_name MagicTransitSiteAcl#lan_name}
        '''
        result = self._values.get("lan_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port_ranges(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Array of port ranges on the provided LAN that will be included in the ACL.

        If no ports or port rangess are provided, communication on any port on this LAN is allowed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#port_ranges MagicTransitSiteAcl#port_ranges}
        '''
        result = self._values.get("port_ranges")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ports(self) -> typing.Optional[typing.List[jsii.Number]]:
        '''Array of ports on the provided LAN that will be included in the ACL.

        If no ports or port ranges are provided, communication on any port on this LAN is allowed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#ports MagicTransitSiteAcl#ports}
        '''
        result = self._values.get("ports")
        return typing.cast(typing.Optional[typing.List[jsii.Number]], result)

    @builtins.property
    def subnets(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Array of subnet IPs within the LAN that will be included in the ACL.

        If no subnets are provided, communication on any subnets on this LAN are allowed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/magic_transit_site_acl#subnets MagicTransitSiteAcl#subnets}
        '''
        result = self._values.get("subnets")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MagicTransitSiteAclLan2(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MagicTransitSiteAclLan2OutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.magicTransitSiteAcl.MagicTransitSiteAclLan2OutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__34a20bbefe0fddf2e5d2755d85705fa92f8abf5027bd94e8eae9d1890e72fa52)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetLanName")
    def reset_lan_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLanName", []))

    @jsii.member(jsii_name="resetPortRanges")
    def reset_port_ranges(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPortRanges", []))

    @jsii.member(jsii_name="resetPorts")
    def reset_ports(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPorts", []))

    @jsii.member(jsii_name="resetSubnets")
    def reset_subnets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubnets", []))

    @builtins.property
    @jsii.member(jsii_name="lanIdInput")
    def lan_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lanIdInput"))

    @builtins.property
    @jsii.member(jsii_name="lanNameInput")
    def lan_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lanNameInput"))

    @builtins.property
    @jsii.member(jsii_name="portRangesInput")
    def port_ranges_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "portRangesInput"))

    @builtins.property
    @jsii.member(jsii_name="portsInput")
    def ports_input(self) -> typing.Optional[typing.List[jsii.Number]]:
        return typing.cast(typing.Optional[typing.List[jsii.Number]], jsii.get(self, "portsInput"))

    @builtins.property
    @jsii.member(jsii_name="subnetsInput")
    def subnets_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "subnetsInput"))

    @builtins.property
    @jsii.member(jsii_name="lanId")
    def lan_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lanId"))

    @lan_id.setter
    def lan_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6066e27bffb3abf8b51bb9fa5efef443b4e351e3d3acc345db9ed96fc62de6b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lanId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lanName")
    def lan_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lanName"))

    @lan_name.setter
    def lan_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__135e93d9802cb83bdad7c9af4760ad5ba87de7bd9697de1b068b2ac3f1283faa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lanName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="portRanges")
    def port_ranges(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "portRanges"))

    @port_ranges.setter
    def port_ranges(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d9e1c19f0117d468b7e0276cd853990b8a70696d2a8f6436133491637cc245c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "portRanges", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ports")
    def ports(self) -> typing.List[jsii.Number]:
        return typing.cast(typing.List[jsii.Number], jsii.get(self, "ports"))

    @ports.setter
    def ports(self, value: typing.List[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29d27a7d037f35a60b52016dfd82c00291dfa1051a79fc5af3a82ec427746f07)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ports", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subnets")
    def subnets(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subnets"))

    @subnets.setter
    def subnets(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67daa3ffc12924da9038990f3f6a558e8f2dd585743bb82c121ed4b6b96ff815)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subnets", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteAclLan2]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteAclLan2]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteAclLan2]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75509234dc019af5738ef83e29a311588f35d65a97580914029e4635de011281)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "MagicTransitSiteAcl",
    "MagicTransitSiteAclConfig",
    "MagicTransitSiteAclLan1",
    "MagicTransitSiteAclLan1OutputReference",
    "MagicTransitSiteAclLan2",
    "MagicTransitSiteAclLan2OutputReference",
]

publication.publish()

def _typecheckingstub__d84d277e913722ff35466a2037d3d78f433a3ba3b0ed0d2861a816aba5ead91f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    lan1: typing.Union[MagicTransitSiteAclLan1, typing.Dict[builtins.str, typing.Any]],
    lan2: typing.Union[MagicTransitSiteAclLan2, typing.Dict[builtins.str, typing.Any]],
    name: builtins.str,
    site_id: builtins.str,
    description: typing.Optional[builtins.str] = None,
    forward_locally: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    protocols: typing.Optional[typing.Sequence[builtins.str]] = None,
    unidirectional: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__4644f3b5d39954f6c86004bc99d4f3a2f8eee53c59c25bebfc92190f2ad65507(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1108d6658e96a7cdfdb89953f2c788c2e82cf250cd5a206c828d50e2169ac5c2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a83c421912a482c94621675e07e2575fb7afa9077a9dfcf4da778b6fda240f6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a334ff4e00e67df13bd6ee7ea52cb25af0abc32378f0d1809c718fc9dab8dea(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6405c9fb9503f5b0d0dec6e350028ed78f18579c73c455cdf04c9964ec503429(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3ea25da1c237a59762a3deb01ce8ca3b180d5d58e1ecdb34481c83274e03623(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2ce1b21ee2eeadcc369467aded062d10c2cee30fbef250c7899746e35b65532(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efefe06e766025a5a5378a089783fd7366f7ab005307d266171c74d7bc46e8b7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__999d0272748716b72e5d98668961d7c81cff77545d8b6e511233283739231834(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    lan1: typing.Union[MagicTransitSiteAclLan1, typing.Dict[builtins.str, typing.Any]],
    lan2: typing.Union[MagicTransitSiteAclLan2, typing.Dict[builtins.str, typing.Any]],
    name: builtins.str,
    site_id: builtins.str,
    description: typing.Optional[builtins.str] = None,
    forward_locally: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    protocols: typing.Optional[typing.Sequence[builtins.str]] = None,
    unidirectional: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34d6cc1acab8ad1a9e708482c2120864868b7eacfaa9b33145e8470cfcae3066(
    *,
    lan_id: builtins.str,
    lan_name: typing.Optional[builtins.str] = None,
    port_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
    ports: typing.Optional[typing.Sequence[jsii.Number]] = None,
    subnets: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abf8794bf9059dafe7a6978960a857cc3510a5f6938c9c85a71352c4e39d9669(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29a7983d049b61e0d0f8991079ccd16cebf0607a265c896f2b3d853c2f70cc03(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__018f7b93db45d1224f8156ed6433ee0f6f958e744a45530037ecbbdde7b8f598(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77e7a92ed1af9e07633aa65ec1f1dc52f90de7388aa8d1cf1ecd6d0d6347f187(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e526cb306c8dc149f4651b450f768740d2472b825fb039a868fb7f6a88847ff(
    value: typing.List[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__019f7f1cfd7bc6655beab5d2ecec3eeb90b1c022e44bf48ea26c8a14929e3e75(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5c8b39ba05ce32671287c4513b0b477d2a3b055d71d7c80d633c192e841c840(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteAclLan1]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__903c99fcfcaa2f9066c5d8cee2e27ce46bde8eb3b46f14fc51689e520569416c(
    *,
    lan_id: builtins.str,
    lan_name: typing.Optional[builtins.str] = None,
    port_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
    ports: typing.Optional[typing.Sequence[jsii.Number]] = None,
    subnets: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34a20bbefe0fddf2e5d2755d85705fa92f8abf5027bd94e8eae9d1890e72fa52(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6066e27bffb3abf8b51bb9fa5efef443b4e351e3d3acc345db9ed96fc62de6b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__135e93d9802cb83bdad7c9af4760ad5ba87de7bd9697de1b068b2ac3f1283faa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d9e1c19f0117d468b7e0276cd853990b8a70696d2a8f6436133491637cc245c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29d27a7d037f35a60b52016dfd82c00291dfa1051a79fc5af3a82ec427746f07(
    value: typing.List[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67daa3ffc12924da9038990f3f6a558e8f2dd585743bb82c121ed4b6b96ff815(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75509234dc019af5738ef83e29a311588f35d65a97580914029e4635de011281(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MagicTransitSiteAclLan2]],
) -> None:
    """Type checking stubs"""
    pass
