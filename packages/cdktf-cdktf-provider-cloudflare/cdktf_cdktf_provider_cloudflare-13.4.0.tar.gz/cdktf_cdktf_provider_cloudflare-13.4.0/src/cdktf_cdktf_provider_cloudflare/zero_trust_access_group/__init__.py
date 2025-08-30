r'''
# `cloudflare_zero_trust_access_group`

Refer to the Terraform Registry for docs: [`cloudflare_zero_trust_access_group`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group).
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


class ZeroTrustAccessGroup(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroup",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group cloudflare_zero_trust_access_group}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        include: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustAccessGroupInclude", typing.Dict[builtins.str, typing.Any]]]],
        name: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
        exclude: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustAccessGroupExclude", typing.Dict[builtins.str, typing.Any]]]]] = None,
        is_default: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        require: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustAccessGroupRequire", typing.Dict[builtins.str, typing.Any]]]]] = None,
        zone_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group cloudflare_zero_trust_access_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param include: Rules evaluated with an OR logical operator. A user needs to meet only one of the Include rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#include ZeroTrustAccessGroup#include}
        :param name: The name of the Access group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#name ZeroTrustAccessGroup#name}
        :param account_id: The Account ID to use for this endpoint. Mutually exclusive with the Zone ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#account_id ZeroTrustAccessGroup#account_id}
        :param exclude: Rules evaluated with a NOT logical operator. To match a policy, a user cannot meet any of the Exclude rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#exclude ZeroTrustAccessGroup#exclude}
        :param is_default: Whether this is the default group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#is_default ZeroTrustAccessGroup#is_default}
        :param require: Rules evaluated with an AND logical operator. To match a policy, a user must meet all of the Require rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#require ZeroTrustAccessGroup#require}
        :param zone_id: The Zone ID to use for this endpoint. Mutually exclusive with the Account ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#zone_id ZeroTrustAccessGroup#zone_id}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23b8565a975674909f1ebeeedba58fe2284efca31d92de03bb26e485aed38248)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = ZeroTrustAccessGroupConfig(
            include=include,
            name=name,
            account_id=account_id,
            exclude=exclude,
            is_default=is_default,
            require=require,
            zone_id=zone_id,
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
        '''Generates CDKTF code for importing a ZeroTrustAccessGroup resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ZeroTrustAccessGroup to import.
        :param import_from_id: The id of the existing ZeroTrustAccessGroup that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ZeroTrustAccessGroup to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4d01177b10c75fce53a506600ccbffd4b52eee31889acab160899dd38bf86ec)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putExclude")
    def put_exclude(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustAccessGroupExclude", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c70d0a9b35ff4cb45f933520027bca1ea4b9848c771ee8281912a577183440d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putExclude", [value]))

    @jsii.member(jsii_name="putInclude")
    def put_include(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustAccessGroupInclude", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0319cb7c9c38b726f1a9534fcb6772539470bf867a4ee6a9b136bc1fd5e10dad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putInclude", [value]))

    @jsii.member(jsii_name="putRequire")
    def put_require(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustAccessGroupRequire", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7daedfd2ebb78dd4e0b2e900469d546570d7b583e431877505ade16cea987bc7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRequire", [value]))

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="resetExclude")
    def reset_exclude(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExclude", []))

    @jsii.member(jsii_name="resetIsDefault")
    def reset_is_default(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsDefault", []))

    @jsii.member(jsii_name="resetRequire")
    def reset_require(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequire", []))

    @jsii.member(jsii_name="resetZoneId")
    def reset_zone_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetZoneId", []))

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
    @jsii.member(jsii_name="exclude")
    def exclude(self) -> "ZeroTrustAccessGroupExcludeList":
        return typing.cast("ZeroTrustAccessGroupExcludeList", jsii.get(self, "exclude"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="include")
    def include(self) -> "ZeroTrustAccessGroupIncludeList":
        return typing.cast("ZeroTrustAccessGroupIncludeList", jsii.get(self, "include"))

    @builtins.property
    @jsii.member(jsii_name="require")
    def require(self) -> "ZeroTrustAccessGroupRequireList":
        return typing.cast("ZeroTrustAccessGroupRequireList", jsii.get(self, "require"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="excludeInput")
    def exclude_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessGroupExclude"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessGroupExclude"]]], jsii.get(self, "excludeInput"))

    @builtins.property
    @jsii.member(jsii_name="includeInput")
    def include_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessGroupInclude"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessGroupInclude"]]], jsii.get(self, "includeInput"))

    @builtins.property
    @jsii.member(jsii_name="isDefaultInput")
    def is_default_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isDefaultInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="requireInput")
    def require_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessGroupRequire"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessGroupRequire"]]], jsii.get(self, "requireInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneIdInput")
    def zone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__913e3ba7c5a4e602e693172256207d474beaa5a445dc60fdc1d5bfdf7c53f088)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isDefault")
    def is_default(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isDefault"))

    @is_default.setter
    def is_default(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b6759beba719c0e4ef03e39964f38b4307e3c6fa1a0df5a5431059e60195d73)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isDefault", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2ba14b8b09b8022bc34a4d18d1fe27a0c37fdfe75f1a088d0095acad31084d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2815e3f53d5045dcacb219cb791a53f83ea3a08be166953061bbbfbdcecb73f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "include": "include",
        "name": "name",
        "account_id": "accountId",
        "exclude": "exclude",
        "is_default": "isDefault",
        "require": "require",
        "zone_id": "zoneId",
    },
)
class ZeroTrustAccessGroupConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        include: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustAccessGroupInclude", typing.Dict[builtins.str, typing.Any]]]],
        name: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
        exclude: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustAccessGroupExclude", typing.Dict[builtins.str, typing.Any]]]]] = None,
        is_default: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        require: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustAccessGroupRequire", typing.Dict[builtins.str, typing.Any]]]]] = None,
        zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param include: Rules evaluated with an OR logical operator. A user needs to meet only one of the Include rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#include ZeroTrustAccessGroup#include}
        :param name: The name of the Access group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#name ZeroTrustAccessGroup#name}
        :param account_id: The Account ID to use for this endpoint. Mutually exclusive with the Zone ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#account_id ZeroTrustAccessGroup#account_id}
        :param exclude: Rules evaluated with a NOT logical operator. To match a policy, a user cannot meet any of the Exclude rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#exclude ZeroTrustAccessGroup#exclude}
        :param is_default: Whether this is the default group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#is_default ZeroTrustAccessGroup#is_default}
        :param require: Rules evaluated with an AND logical operator. To match a policy, a user must meet all of the Require rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#require ZeroTrustAccessGroup#require}
        :param zone_id: The Zone ID to use for this endpoint. Mutually exclusive with the Account ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#zone_id ZeroTrustAccessGroup#zone_id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ceb08f483d09781f38c84657e26fa8b9c737c1ab7375a4373ef7e726ccdb6fcd)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument include", value=include, expected_type=type_hints["include"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument exclude", value=exclude, expected_type=type_hints["exclude"])
            check_type(argname="argument is_default", value=is_default, expected_type=type_hints["is_default"])
            check_type(argname="argument require", value=require, expected_type=type_hints["require"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "include": include,
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
        if account_id is not None:
            self._values["account_id"] = account_id
        if exclude is not None:
            self._values["exclude"] = exclude
        if is_default is not None:
            self._values["is_default"] = is_default
        if require is not None:
            self._values["require"] = require
        if zone_id is not None:
            self._values["zone_id"] = zone_id

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
    def include(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessGroupInclude"]]:
        '''Rules evaluated with an OR logical operator. A user needs to meet only one of the Include rules.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#include ZeroTrustAccessGroup#include}
        '''
        result = self._values.get("include")
        assert result is not None, "Required property 'include' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessGroupInclude"]], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the Access group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#name ZeroTrustAccessGroup#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[builtins.str]:
        '''The Account ID to use for this endpoint. Mutually exclusive with the Zone ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#account_id ZeroTrustAccessGroup#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def exclude(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessGroupExclude"]]]:
        '''Rules evaluated with a NOT logical operator.

        To match a policy, a user cannot meet any of the Exclude rules.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#exclude ZeroTrustAccessGroup#exclude}
        '''
        result = self._values.get("exclude")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessGroupExclude"]]], result)

    @builtins.property
    def is_default(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether this is the default group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#is_default ZeroTrustAccessGroup#is_default}
        '''
        result = self._values.get("is_default")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def require(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessGroupRequire"]]]:
        '''Rules evaluated with an AND logical operator.

        To match a policy, a user must meet all of the Require rules.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#require ZeroTrustAccessGroup#require}
        '''
        result = self._values.get("require")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessGroupRequire"]]], result)

    @builtins.property
    def zone_id(self) -> typing.Optional[builtins.str]:
        '''The Zone ID to use for this endpoint. Mutually exclusive with the Account ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#zone_id ZeroTrustAccessGroup#zone_id}
        '''
        result = self._values.get("zone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExclude",
    jsii_struct_bases=[],
    name_mapping={
        "any_valid_service_token": "anyValidServiceToken",
        "auth_context": "authContext",
        "auth_method": "authMethod",
        "azure_ad": "azureAd",
        "certificate": "certificate",
        "common_name": "commonName",
        "device_posture": "devicePosture",
        "email": "email",
        "email_domain": "emailDomain",
        "email_list": "emailList",
        "everyone": "everyone",
        "external_evaluation": "externalEvaluation",
        "geo": "geo",
        "github_organization": "githubOrganization",
        "group": "group",
        "gsuite": "gsuite",
        "ip": "ip",
        "ip_list": "ipList",
        "linked_app_token": "linkedAppToken",
        "login_method": "loginMethod",
        "oidc": "oidc",
        "okta": "okta",
        "saml": "saml",
        "service_token": "serviceToken",
    },
)
class ZeroTrustAccessGroupExclude:
    def __init__(
        self,
        *,
        any_valid_service_token: typing.Optional[typing.Union["ZeroTrustAccessGroupExcludeAnyValidServiceToken", typing.Dict[builtins.str, typing.Any]]] = None,
        auth_context: typing.Optional[typing.Union["ZeroTrustAccessGroupExcludeAuthContext", typing.Dict[builtins.str, typing.Any]]] = None,
        auth_method: typing.Optional[typing.Union["ZeroTrustAccessGroupExcludeAuthMethod", typing.Dict[builtins.str, typing.Any]]] = None,
        azure_ad: typing.Optional[typing.Union["ZeroTrustAccessGroupExcludeAzureAd", typing.Dict[builtins.str, typing.Any]]] = None,
        certificate: typing.Optional[typing.Union["ZeroTrustAccessGroupExcludeCertificate", typing.Dict[builtins.str, typing.Any]]] = None,
        common_name: typing.Optional[typing.Union["ZeroTrustAccessGroupExcludeCommonName", typing.Dict[builtins.str, typing.Any]]] = None,
        device_posture: typing.Optional[typing.Union["ZeroTrustAccessGroupExcludeDevicePosture", typing.Dict[builtins.str, typing.Any]]] = None,
        email: typing.Optional[typing.Union["ZeroTrustAccessGroupExcludeEmail", typing.Dict[builtins.str, typing.Any]]] = None,
        email_domain: typing.Optional[typing.Union["ZeroTrustAccessGroupExcludeEmailDomain", typing.Dict[builtins.str, typing.Any]]] = None,
        email_list: typing.Optional[typing.Union["ZeroTrustAccessGroupExcludeEmailListStruct", typing.Dict[builtins.str, typing.Any]]] = None,
        everyone: typing.Optional[typing.Union["ZeroTrustAccessGroupExcludeEveryone", typing.Dict[builtins.str, typing.Any]]] = None,
        external_evaluation: typing.Optional[typing.Union["ZeroTrustAccessGroupExcludeExternalEvaluation", typing.Dict[builtins.str, typing.Any]]] = None,
        geo: typing.Optional[typing.Union["ZeroTrustAccessGroupExcludeGeo", typing.Dict[builtins.str, typing.Any]]] = None,
        github_organization: typing.Optional[typing.Union["ZeroTrustAccessGroupExcludeGithubOrganization", typing.Dict[builtins.str, typing.Any]]] = None,
        group: typing.Optional[typing.Union["ZeroTrustAccessGroupExcludeGroup", typing.Dict[builtins.str, typing.Any]]] = None,
        gsuite: typing.Optional[typing.Union["ZeroTrustAccessGroupExcludeGsuite", typing.Dict[builtins.str, typing.Any]]] = None,
        ip: typing.Optional[typing.Union["ZeroTrustAccessGroupExcludeIp", typing.Dict[builtins.str, typing.Any]]] = None,
        ip_list: typing.Optional[typing.Union["ZeroTrustAccessGroupExcludeIpListStruct", typing.Dict[builtins.str, typing.Any]]] = None,
        linked_app_token: typing.Optional[typing.Union["ZeroTrustAccessGroupExcludeLinkedAppToken", typing.Dict[builtins.str, typing.Any]]] = None,
        login_method: typing.Optional[typing.Union["ZeroTrustAccessGroupExcludeLoginMethod", typing.Dict[builtins.str, typing.Any]]] = None,
        oidc: typing.Optional[typing.Union["ZeroTrustAccessGroupExcludeOidc", typing.Dict[builtins.str, typing.Any]]] = None,
        okta: typing.Optional[typing.Union["ZeroTrustAccessGroupExcludeOkta", typing.Dict[builtins.str, typing.Any]]] = None,
        saml: typing.Optional[typing.Union["ZeroTrustAccessGroupExcludeSaml", typing.Dict[builtins.str, typing.Any]]] = None,
        service_token: typing.Optional[typing.Union["ZeroTrustAccessGroupExcludeServiceToken", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param any_valid_service_token: An empty object which matches on all service tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#any_valid_service_token ZeroTrustAccessGroup#any_valid_service_token}
        :param auth_context: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#auth_context ZeroTrustAccessGroup#auth_context}.
        :param auth_method: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#auth_method ZeroTrustAccessGroup#auth_method}.
        :param azure_ad: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#azure_ad ZeroTrustAccessGroup#azure_ad}.
        :param certificate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#certificate ZeroTrustAccessGroup#certificate}.
        :param common_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#common_name ZeroTrustAccessGroup#common_name}.
        :param device_posture: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#device_posture ZeroTrustAccessGroup#device_posture}.
        :param email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email ZeroTrustAccessGroup#email}.
        :param email_domain: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email_domain ZeroTrustAccessGroup#email_domain}.
        :param email_list: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email_list ZeroTrustAccessGroup#email_list}.
        :param everyone: An empty object which matches on all users. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#everyone ZeroTrustAccessGroup#everyone}
        :param external_evaluation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#external_evaluation ZeroTrustAccessGroup#external_evaluation}.
        :param geo: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#geo ZeroTrustAccessGroup#geo}.
        :param github_organization: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#github_organization ZeroTrustAccessGroup#github_organization}.
        :param group: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#group ZeroTrustAccessGroup#group}.
        :param gsuite: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#gsuite ZeroTrustAccessGroup#gsuite}.
        :param ip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ip ZeroTrustAccessGroup#ip}.
        :param ip_list: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ip_list ZeroTrustAccessGroup#ip_list}.
        :param linked_app_token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#linked_app_token ZeroTrustAccessGroup#linked_app_token}.
        :param login_method: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#login_method ZeroTrustAccessGroup#login_method}.
        :param oidc: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#oidc ZeroTrustAccessGroup#oidc}.
        :param okta: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#okta ZeroTrustAccessGroup#okta}.
        :param saml: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#saml ZeroTrustAccessGroup#saml}.
        :param service_token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#service_token ZeroTrustAccessGroup#service_token}.
        '''
        if isinstance(any_valid_service_token, dict):
            any_valid_service_token = ZeroTrustAccessGroupExcludeAnyValidServiceToken(**any_valid_service_token)
        if isinstance(auth_context, dict):
            auth_context = ZeroTrustAccessGroupExcludeAuthContext(**auth_context)
        if isinstance(auth_method, dict):
            auth_method = ZeroTrustAccessGroupExcludeAuthMethod(**auth_method)
        if isinstance(azure_ad, dict):
            azure_ad = ZeroTrustAccessGroupExcludeAzureAd(**azure_ad)
        if isinstance(certificate, dict):
            certificate = ZeroTrustAccessGroupExcludeCertificate(**certificate)
        if isinstance(common_name, dict):
            common_name = ZeroTrustAccessGroupExcludeCommonName(**common_name)
        if isinstance(device_posture, dict):
            device_posture = ZeroTrustAccessGroupExcludeDevicePosture(**device_posture)
        if isinstance(email, dict):
            email = ZeroTrustAccessGroupExcludeEmail(**email)
        if isinstance(email_domain, dict):
            email_domain = ZeroTrustAccessGroupExcludeEmailDomain(**email_domain)
        if isinstance(email_list, dict):
            email_list = ZeroTrustAccessGroupExcludeEmailListStruct(**email_list)
        if isinstance(everyone, dict):
            everyone = ZeroTrustAccessGroupExcludeEveryone(**everyone)
        if isinstance(external_evaluation, dict):
            external_evaluation = ZeroTrustAccessGroupExcludeExternalEvaluation(**external_evaluation)
        if isinstance(geo, dict):
            geo = ZeroTrustAccessGroupExcludeGeo(**geo)
        if isinstance(github_organization, dict):
            github_organization = ZeroTrustAccessGroupExcludeGithubOrganization(**github_organization)
        if isinstance(group, dict):
            group = ZeroTrustAccessGroupExcludeGroup(**group)
        if isinstance(gsuite, dict):
            gsuite = ZeroTrustAccessGroupExcludeGsuite(**gsuite)
        if isinstance(ip, dict):
            ip = ZeroTrustAccessGroupExcludeIp(**ip)
        if isinstance(ip_list, dict):
            ip_list = ZeroTrustAccessGroupExcludeIpListStruct(**ip_list)
        if isinstance(linked_app_token, dict):
            linked_app_token = ZeroTrustAccessGroupExcludeLinkedAppToken(**linked_app_token)
        if isinstance(login_method, dict):
            login_method = ZeroTrustAccessGroupExcludeLoginMethod(**login_method)
        if isinstance(oidc, dict):
            oidc = ZeroTrustAccessGroupExcludeOidc(**oidc)
        if isinstance(okta, dict):
            okta = ZeroTrustAccessGroupExcludeOkta(**okta)
        if isinstance(saml, dict):
            saml = ZeroTrustAccessGroupExcludeSaml(**saml)
        if isinstance(service_token, dict):
            service_token = ZeroTrustAccessGroupExcludeServiceToken(**service_token)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__032a7b58f7e87dcd85c1e29db2bd7d9c98c3061cadf55e8a8b5a9dae1359b75e)
            check_type(argname="argument any_valid_service_token", value=any_valid_service_token, expected_type=type_hints["any_valid_service_token"])
            check_type(argname="argument auth_context", value=auth_context, expected_type=type_hints["auth_context"])
            check_type(argname="argument auth_method", value=auth_method, expected_type=type_hints["auth_method"])
            check_type(argname="argument azure_ad", value=azure_ad, expected_type=type_hints["azure_ad"])
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument common_name", value=common_name, expected_type=type_hints["common_name"])
            check_type(argname="argument device_posture", value=device_posture, expected_type=type_hints["device_posture"])
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
            check_type(argname="argument email_domain", value=email_domain, expected_type=type_hints["email_domain"])
            check_type(argname="argument email_list", value=email_list, expected_type=type_hints["email_list"])
            check_type(argname="argument everyone", value=everyone, expected_type=type_hints["everyone"])
            check_type(argname="argument external_evaluation", value=external_evaluation, expected_type=type_hints["external_evaluation"])
            check_type(argname="argument geo", value=geo, expected_type=type_hints["geo"])
            check_type(argname="argument github_organization", value=github_organization, expected_type=type_hints["github_organization"])
            check_type(argname="argument group", value=group, expected_type=type_hints["group"])
            check_type(argname="argument gsuite", value=gsuite, expected_type=type_hints["gsuite"])
            check_type(argname="argument ip", value=ip, expected_type=type_hints["ip"])
            check_type(argname="argument ip_list", value=ip_list, expected_type=type_hints["ip_list"])
            check_type(argname="argument linked_app_token", value=linked_app_token, expected_type=type_hints["linked_app_token"])
            check_type(argname="argument login_method", value=login_method, expected_type=type_hints["login_method"])
            check_type(argname="argument oidc", value=oidc, expected_type=type_hints["oidc"])
            check_type(argname="argument okta", value=okta, expected_type=type_hints["okta"])
            check_type(argname="argument saml", value=saml, expected_type=type_hints["saml"])
            check_type(argname="argument service_token", value=service_token, expected_type=type_hints["service_token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if any_valid_service_token is not None:
            self._values["any_valid_service_token"] = any_valid_service_token
        if auth_context is not None:
            self._values["auth_context"] = auth_context
        if auth_method is not None:
            self._values["auth_method"] = auth_method
        if azure_ad is not None:
            self._values["azure_ad"] = azure_ad
        if certificate is not None:
            self._values["certificate"] = certificate
        if common_name is not None:
            self._values["common_name"] = common_name
        if device_posture is not None:
            self._values["device_posture"] = device_posture
        if email is not None:
            self._values["email"] = email
        if email_domain is not None:
            self._values["email_domain"] = email_domain
        if email_list is not None:
            self._values["email_list"] = email_list
        if everyone is not None:
            self._values["everyone"] = everyone
        if external_evaluation is not None:
            self._values["external_evaluation"] = external_evaluation
        if geo is not None:
            self._values["geo"] = geo
        if github_organization is not None:
            self._values["github_organization"] = github_organization
        if group is not None:
            self._values["group"] = group
        if gsuite is not None:
            self._values["gsuite"] = gsuite
        if ip is not None:
            self._values["ip"] = ip
        if ip_list is not None:
            self._values["ip_list"] = ip_list
        if linked_app_token is not None:
            self._values["linked_app_token"] = linked_app_token
        if login_method is not None:
            self._values["login_method"] = login_method
        if oidc is not None:
            self._values["oidc"] = oidc
        if okta is not None:
            self._values["okta"] = okta
        if saml is not None:
            self._values["saml"] = saml
        if service_token is not None:
            self._values["service_token"] = service_token

    @builtins.property
    def any_valid_service_token(
        self,
    ) -> typing.Optional["ZeroTrustAccessGroupExcludeAnyValidServiceToken"]:
        '''An empty object which matches on all service tokens.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#any_valid_service_token ZeroTrustAccessGroup#any_valid_service_token}
        '''
        result = self._values.get("any_valid_service_token")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupExcludeAnyValidServiceToken"], result)

    @builtins.property
    def auth_context(self) -> typing.Optional["ZeroTrustAccessGroupExcludeAuthContext"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#auth_context ZeroTrustAccessGroup#auth_context}.'''
        result = self._values.get("auth_context")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupExcludeAuthContext"], result)

    @builtins.property
    def auth_method(self) -> typing.Optional["ZeroTrustAccessGroupExcludeAuthMethod"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#auth_method ZeroTrustAccessGroup#auth_method}.'''
        result = self._values.get("auth_method")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupExcludeAuthMethod"], result)

    @builtins.property
    def azure_ad(self) -> typing.Optional["ZeroTrustAccessGroupExcludeAzureAd"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#azure_ad ZeroTrustAccessGroup#azure_ad}.'''
        result = self._values.get("azure_ad")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupExcludeAzureAd"], result)

    @builtins.property
    def certificate(self) -> typing.Optional["ZeroTrustAccessGroupExcludeCertificate"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#certificate ZeroTrustAccessGroup#certificate}.'''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupExcludeCertificate"], result)

    @builtins.property
    def common_name(self) -> typing.Optional["ZeroTrustAccessGroupExcludeCommonName"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#common_name ZeroTrustAccessGroup#common_name}.'''
        result = self._values.get("common_name")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupExcludeCommonName"], result)

    @builtins.property
    def device_posture(
        self,
    ) -> typing.Optional["ZeroTrustAccessGroupExcludeDevicePosture"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#device_posture ZeroTrustAccessGroup#device_posture}.'''
        result = self._values.get("device_posture")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupExcludeDevicePosture"], result)

    @builtins.property
    def email(self) -> typing.Optional["ZeroTrustAccessGroupExcludeEmail"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email ZeroTrustAccessGroup#email}.'''
        result = self._values.get("email")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupExcludeEmail"], result)

    @builtins.property
    def email_domain(self) -> typing.Optional["ZeroTrustAccessGroupExcludeEmailDomain"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email_domain ZeroTrustAccessGroup#email_domain}.'''
        result = self._values.get("email_domain")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupExcludeEmailDomain"], result)

    @builtins.property
    def email_list(
        self,
    ) -> typing.Optional["ZeroTrustAccessGroupExcludeEmailListStruct"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email_list ZeroTrustAccessGroup#email_list}.'''
        result = self._values.get("email_list")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupExcludeEmailListStruct"], result)

    @builtins.property
    def everyone(self) -> typing.Optional["ZeroTrustAccessGroupExcludeEveryone"]:
        '''An empty object which matches on all users.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#everyone ZeroTrustAccessGroup#everyone}
        '''
        result = self._values.get("everyone")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupExcludeEveryone"], result)

    @builtins.property
    def external_evaluation(
        self,
    ) -> typing.Optional["ZeroTrustAccessGroupExcludeExternalEvaluation"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#external_evaluation ZeroTrustAccessGroup#external_evaluation}.'''
        result = self._values.get("external_evaluation")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupExcludeExternalEvaluation"], result)

    @builtins.property
    def geo(self) -> typing.Optional["ZeroTrustAccessGroupExcludeGeo"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#geo ZeroTrustAccessGroup#geo}.'''
        result = self._values.get("geo")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupExcludeGeo"], result)

    @builtins.property
    def github_organization(
        self,
    ) -> typing.Optional["ZeroTrustAccessGroupExcludeGithubOrganization"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#github_organization ZeroTrustAccessGroup#github_organization}.'''
        result = self._values.get("github_organization")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupExcludeGithubOrganization"], result)

    @builtins.property
    def group(self) -> typing.Optional["ZeroTrustAccessGroupExcludeGroup"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#group ZeroTrustAccessGroup#group}.'''
        result = self._values.get("group")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupExcludeGroup"], result)

    @builtins.property
    def gsuite(self) -> typing.Optional["ZeroTrustAccessGroupExcludeGsuite"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#gsuite ZeroTrustAccessGroup#gsuite}.'''
        result = self._values.get("gsuite")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupExcludeGsuite"], result)

    @builtins.property
    def ip(self) -> typing.Optional["ZeroTrustAccessGroupExcludeIp"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ip ZeroTrustAccessGroup#ip}.'''
        result = self._values.get("ip")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupExcludeIp"], result)

    @builtins.property
    def ip_list(self) -> typing.Optional["ZeroTrustAccessGroupExcludeIpListStruct"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ip_list ZeroTrustAccessGroup#ip_list}.'''
        result = self._values.get("ip_list")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupExcludeIpListStruct"], result)

    @builtins.property
    def linked_app_token(
        self,
    ) -> typing.Optional["ZeroTrustAccessGroupExcludeLinkedAppToken"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#linked_app_token ZeroTrustAccessGroup#linked_app_token}.'''
        result = self._values.get("linked_app_token")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupExcludeLinkedAppToken"], result)

    @builtins.property
    def login_method(self) -> typing.Optional["ZeroTrustAccessGroupExcludeLoginMethod"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#login_method ZeroTrustAccessGroup#login_method}.'''
        result = self._values.get("login_method")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupExcludeLoginMethod"], result)

    @builtins.property
    def oidc(self) -> typing.Optional["ZeroTrustAccessGroupExcludeOidc"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#oidc ZeroTrustAccessGroup#oidc}.'''
        result = self._values.get("oidc")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupExcludeOidc"], result)

    @builtins.property
    def okta(self) -> typing.Optional["ZeroTrustAccessGroupExcludeOkta"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#okta ZeroTrustAccessGroup#okta}.'''
        result = self._values.get("okta")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupExcludeOkta"], result)

    @builtins.property
    def saml(self) -> typing.Optional["ZeroTrustAccessGroupExcludeSaml"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#saml ZeroTrustAccessGroup#saml}.'''
        result = self._values.get("saml")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupExcludeSaml"], result)

    @builtins.property
    def service_token(
        self,
    ) -> typing.Optional["ZeroTrustAccessGroupExcludeServiceToken"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#service_token ZeroTrustAccessGroup#service_token}.'''
        result = self._values.get("service_token")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupExcludeServiceToken"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupExclude(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeAnyValidServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class ZeroTrustAccessGroupExcludeAnyValidServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupExcludeAnyValidServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupExcludeAnyValidServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeAnyValidServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__94507dfda0f4ea3199e55b6428ebe1f9134b35b8e5db63367dfa8f8713ae6bbd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeAnyValidServiceToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeAnyValidServiceToken]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeAnyValidServiceToken]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22b5307473370c0fbc7e4bff0bca6e703b64c05daf636d5c08fb5c82c901f6cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeAuthContext",
    jsii_struct_bases=[],
    name_mapping={
        "ac_id": "acId",
        "id": "id",
        "identity_provider_id": "identityProviderId",
    },
)
class ZeroTrustAccessGroupExcludeAuthContext:
    def __init__(
        self,
        *,
        ac_id: builtins.str,
        id: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param ac_id: The ACID of an Authentication context. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ac_id ZeroTrustAccessGroup#ac_id}
        :param id: The ID of an Authentication context. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider_id: The ID of your Azure identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b692cbf7c9373b74e90abe89cdf54fae7d7570d85f2c806a667fe0327c61d441)
            check_type(argname="argument ac_id", value=ac_id, expected_type=type_hints["ac_id"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "ac_id": ac_id,
            "id": id,
            "identity_provider_id": identity_provider_id,
        }

    @builtins.property
    def ac_id(self) -> builtins.str:
        '''The ACID of an Authentication context.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ac_id ZeroTrustAccessGroup#ac_id}
        '''
        result = self._values.get("ac_id")
        assert result is not None, "Required property 'ac_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of an Authentication context.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your Azure identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupExcludeAuthContext(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupExcludeAuthContextOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeAuthContextOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6dd22640557a54ab7fac4583ccb93edc2832b8c72e5155b0d4ce99f8c1bf928a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="acIdInput")
    def ac_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "acIdInput"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderIdInput")
    def identity_provider_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityProviderIdInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="acId")
    def ac_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "acId"))

    @ac_id.setter
    def ac_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff9626f35b818801ef5a726a3d0fd4a00d9f202d481c740bfa286df2f10929b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "acId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41ba3b0d759efac495885a0ccdc2fd401a70cda628054bffaafade842d9296d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d35ade58ab0cccfa3613fdf797e90cbfd9cd732c0e4151e769e3b82ba6f48fef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeAuthContext]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeAuthContext]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeAuthContext]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93ddf7ca01f2f3d49c5bf469447796f9b20e0f4a99ce4b18757942d9af92d88c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeAuthMethod",
    jsii_struct_bases=[],
    name_mapping={"auth_method": "authMethod"},
)
class ZeroTrustAccessGroupExcludeAuthMethod:
    def __init__(self, *, auth_method: builtins.str) -> None:
        '''
        :param auth_method: The type of authentication method https://datatracker.ietf.org/doc/html/rfc8176#section-2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#auth_method ZeroTrustAccessGroup#auth_method}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1200353abb6ec161d0dbd9f248423674b76fe99ed357ccc477539176da562d7a)
            check_type(argname="argument auth_method", value=auth_method, expected_type=type_hints["auth_method"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "auth_method": auth_method,
        }

    @builtins.property
    def auth_method(self) -> builtins.str:
        '''The type of authentication method https://datatracker.ietf.org/doc/html/rfc8176#section-2.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#auth_method ZeroTrustAccessGroup#auth_method}
        '''
        result = self._values.get("auth_method")
        assert result is not None, "Required property 'auth_method' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupExcludeAuthMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupExcludeAuthMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeAuthMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e9ddc42dc13d4633beca2261583536ec7bd881ad94faab066729bfb7fd776e30)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="authMethodInput")
    def auth_method_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authMethodInput"))

    @builtins.property
    @jsii.member(jsii_name="authMethod")
    def auth_method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authMethod"))

    @auth_method.setter
    def auth_method(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0af2d9992d402a20041fcb644ab6cbbe65472a307fbd2e2dc37d9dc3e89d6b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authMethod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeAuthMethod]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeAuthMethod]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeAuthMethod]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e72a250949a0051233d514e140acc3de44c9d87676721324d7f8e2130bcc061)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeAzureAd",
    jsii_struct_bases=[],
    name_mapping={"id": "id", "identity_provider_id": "identityProviderId"},
)
class ZeroTrustAccessGroupExcludeAzureAd:
    def __init__(self, *, id: builtins.str, identity_provider_id: builtins.str) -> None:
        '''
        :param id: The ID of an Azure group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider_id: The ID of your Azure identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3744c8fb1d9f353274bb499b904237207c1273f3656d94e049081c8c2dd688d)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
            "identity_provider_id": identity_provider_id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of an Azure group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your Azure identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupExcludeAzureAd(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupExcludeAzureAdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeAzureAdOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__30c4a3685fd1af6908ab2692e9c182aa04ad0e2def3e62264b8595a352ddbf1c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="identityProviderIdInput")
    def identity_provider_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityProviderIdInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__2b801892c185da43f27bfd13838bafe8fcf2790ddbd522898f53cc99a680e77e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df8feb9fe194f2f44f56eff00d5a0efade4927292139c09e6b7e7f0073a3fc5a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeAzureAd]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeAzureAd]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeAzureAd]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f11e3788152dbaf7c4828dd3185f6382b68a488ad9e3a7e42b82e2433a82f647)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeCertificate",
    jsii_struct_bases=[],
    name_mapping={},
)
class ZeroTrustAccessGroupExcludeCertificate:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupExcludeCertificate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupExcludeCertificateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeCertificateOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__146eb8023db98ca40a5304138ba6abb6ae1ee9293e21ea52506055ad30de116c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeCertificate]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeCertificate]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeCertificate]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__605e747e896e2ed359b2fd2ec176e62c5685434a9737b91e97e0073b5b756311)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeCommonName",
    jsii_struct_bases=[],
    name_mapping={"common_name": "commonName"},
)
class ZeroTrustAccessGroupExcludeCommonName:
    def __init__(self, *, common_name: builtins.str) -> None:
        '''
        :param common_name: The common name to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#common_name ZeroTrustAccessGroup#common_name}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__accc5120f60d9ccfa24b9e622fb1b26500accca9e590b7e386ff483bfd8d4ed4)
            check_type(argname="argument common_name", value=common_name, expected_type=type_hints["common_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "common_name": common_name,
        }

    @builtins.property
    def common_name(self) -> builtins.str:
        '''The common name to match.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#common_name ZeroTrustAccessGroup#common_name}
        '''
        result = self._values.get("common_name")
        assert result is not None, "Required property 'common_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupExcludeCommonName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupExcludeCommonNameOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeCommonNameOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__996f09c281dcfa1f2f16f81c4c16dcfaafc58a9739299d1d651597b07d95c6c7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="commonNameInput")
    def common_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commonNameInput"))

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commonName"))

    @common_name.setter
    def common_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67ae12af20ef0135c2fc8e2ee3a7b7b6d454aac7dbf54b8f4967420e9aed0a81)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "commonName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeCommonName]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeCommonName]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeCommonName]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36416a503632058b032f459db8f6cab6d6174dee796755a79f9862ce3fc4bec5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeDevicePosture",
    jsii_struct_bases=[],
    name_mapping={"integration_uid": "integrationUid"},
)
class ZeroTrustAccessGroupExcludeDevicePosture:
    def __init__(self, *, integration_uid: builtins.str) -> None:
        '''
        :param integration_uid: The ID of a device posture integration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#integration_uid ZeroTrustAccessGroup#integration_uid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__160d77c5441f46a67750849aa960c7eef0202d13b0836f94bad5e3b8e2ab0043)
            check_type(argname="argument integration_uid", value=integration_uid, expected_type=type_hints["integration_uid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "integration_uid": integration_uid,
        }

    @builtins.property
    def integration_uid(self) -> builtins.str:
        '''The ID of a device posture integration.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#integration_uid ZeroTrustAccessGroup#integration_uid}
        '''
        result = self._values.get("integration_uid")
        assert result is not None, "Required property 'integration_uid' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupExcludeDevicePosture(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupExcludeDevicePostureOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeDevicePostureOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b31d60e2593f19d04d172dcb6cae6dad6ae95594a9d7a2d4eef212f0fd9af84f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="integrationUidInput")
    def integration_uid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "integrationUidInput"))

    @builtins.property
    @jsii.member(jsii_name="integrationUid")
    def integration_uid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "integrationUid"))

    @integration_uid.setter
    def integration_uid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3aeaf4c435249afb602d861a3bb0f29fc20f758affb7ee86fde01474d91c9faa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "integrationUid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeDevicePosture]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeDevicePosture]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeDevicePosture]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63b7229ae81bde4a793135d72f93d72b00a5003014214cff0fd5ba1b1bc9f034)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeEmail",
    jsii_struct_bases=[],
    name_mapping={"email": "email"},
)
class ZeroTrustAccessGroupExcludeEmail:
    def __init__(self, *, email: builtins.str) -> None:
        '''
        :param email: The email of the user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email ZeroTrustAccessGroup#email}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__270a7553b6190577c72c8e027ce925220c81188fa6958d30a92a23daefd3a3b7)
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "email": email,
        }

    @builtins.property
    def email(self) -> builtins.str:
        '''The email of the user.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email ZeroTrustAccessGroup#email}
        '''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupExcludeEmail(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeEmailDomain",
    jsii_struct_bases=[],
    name_mapping={"domain": "domain"},
)
class ZeroTrustAccessGroupExcludeEmailDomain:
    def __init__(self, *, domain: builtins.str) -> None:
        '''
        :param domain: The email domain to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#domain ZeroTrustAccessGroup#domain}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5bdd8569958685703c4fb629f4b10ff30c42dc2af03c82652dcebbc318eee1fd)
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain": domain,
        }

    @builtins.property
    def domain(self) -> builtins.str:
        '''The email domain to match.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#domain ZeroTrustAccessGroup#domain}
        '''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupExcludeEmailDomain(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupExcludeEmailDomainOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeEmailDomainOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7baae55896e69a0cb02e5b0fc5fe491c74438dedd3a3c32d282387f9fb1d2a6a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="domainInput")
    def domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainInput"))

    @builtins.property
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a92567f2020f38b16805def89ea996c075c29f415f5e8a2c0779d7b4d8f601d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "domain", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeEmailDomain]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeEmailDomain]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeEmailDomain]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e706ed7afcf439cd7e339c0fe4756716168cb747b92149bb674bc7d675d7473a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeEmailListStruct",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class ZeroTrustAccessGroupExcludeEmailListStruct:
    def __init__(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created email list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6de40a82dfc181c8d23c361da662c99a155975deb30660eda198e8f7ec7eaaab)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of a previously created email list.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupExcludeEmailListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupExcludeEmailListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeEmailListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ca61e0490017f566ea471a553f163c427b65b761bffcec9579b5430a90ee0eb4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

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
            type_hints = typing.get_type_hints(_typecheckingstub__4270f9452eb4d21d78aceac58c13b38b8d02bbe7618fb7b3c93d999062de409a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeEmailListStruct]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeEmailListStruct]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeEmailListStruct]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d749e3243a6a43fe23641d464371a067774145eeef093cab8493c67a3a8b7ba5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustAccessGroupExcludeEmailOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeEmailOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__246b58e2ced1a4c3d0467a7492149080d3786a1058489bca4d97b0c23702c4cc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="emailInput")
    def email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailInput"))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "email"))

    @email.setter
    def email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b970f64e351753faa7f6befb13841ee29856734c45729e91dfa19e95f68667bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "email", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeEmail]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeEmail]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeEmail]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fddc62d901fba6a7dfa50b4215af128eb9b702edb81d9046fc27b974388e35dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeEveryone",
    jsii_struct_bases=[],
    name_mapping={},
)
class ZeroTrustAccessGroupExcludeEveryone:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupExcludeEveryone(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupExcludeEveryoneOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeEveryoneOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__be198755e080e3a690b60a36e504967c1687d837a4c105a9282f0973462610c2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeEveryone]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeEveryone]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeEveryone]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61063a3d1d4a439e27a77bc728b5332557ef1ad5e47e5a08fb5c8c278a3395d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeExternalEvaluation",
    jsii_struct_bases=[],
    name_mapping={"evaluate_url": "evaluateUrl", "keys_url": "keysUrl"},
)
class ZeroTrustAccessGroupExcludeExternalEvaluation:
    def __init__(self, *, evaluate_url: builtins.str, keys_url: builtins.str) -> None:
        '''
        :param evaluate_url: The API endpoint containing your business logic. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#evaluate_url ZeroTrustAccessGroup#evaluate_url}
        :param keys_url: The API endpoint containing the key that Access uses to verify that the response came from your API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#keys_url ZeroTrustAccessGroup#keys_url}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11bf297a714aa6d94ffe063800a14c72a69840fdb56198d4adb79eff26f69c2f)
            check_type(argname="argument evaluate_url", value=evaluate_url, expected_type=type_hints["evaluate_url"])
            check_type(argname="argument keys_url", value=keys_url, expected_type=type_hints["keys_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "evaluate_url": evaluate_url,
            "keys_url": keys_url,
        }

    @builtins.property
    def evaluate_url(self) -> builtins.str:
        '''The API endpoint containing your business logic.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#evaluate_url ZeroTrustAccessGroup#evaluate_url}
        '''
        result = self._values.get("evaluate_url")
        assert result is not None, "Required property 'evaluate_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def keys_url(self) -> builtins.str:
        '''The API endpoint containing the key that Access uses to verify that the response came from your API.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#keys_url ZeroTrustAccessGroup#keys_url}
        '''
        result = self._values.get("keys_url")
        assert result is not None, "Required property 'keys_url' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupExcludeExternalEvaluation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupExcludeExternalEvaluationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeExternalEvaluationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8478f07e3dea1f7e685facfa1fed6ae9c865545464a0f43fa51ef16897c2f341)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="evaluateUrlInput")
    def evaluate_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "evaluateUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="keysUrlInput")
    def keys_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keysUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="evaluateUrl")
    def evaluate_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "evaluateUrl"))

    @evaluate_url.setter
    def evaluate_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a11ec9f783db507b9752a711afa9b9eb50565aa85a48e66fd6028261a62d9ff3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "evaluateUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keysUrl")
    def keys_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keysUrl"))

    @keys_url.setter
    def keys_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__174bef4741f53a3bddb4ab181eea32856330f9b422602a5fb835100e73c6556f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keysUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeExternalEvaluation]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeExternalEvaluation]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeExternalEvaluation]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67848a68a24af28c4911613dadae81eee5b19255eec1f41ada7a895fd7b5e4bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeGeo",
    jsii_struct_bases=[],
    name_mapping={"country_code": "countryCode"},
)
class ZeroTrustAccessGroupExcludeGeo:
    def __init__(self, *, country_code: builtins.str) -> None:
        '''
        :param country_code: The country code that should be matched. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#country_code ZeroTrustAccessGroup#country_code}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__294387a4eb3fd83634f806f54265c44b57bc3d901c633a6bb9b81b0d6f57a4c9)
            check_type(argname="argument country_code", value=country_code, expected_type=type_hints["country_code"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "country_code": country_code,
        }

    @builtins.property
    def country_code(self) -> builtins.str:
        '''The country code that should be matched.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#country_code ZeroTrustAccessGroup#country_code}
        '''
        result = self._values.get("country_code")
        assert result is not None, "Required property 'country_code' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupExcludeGeo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupExcludeGeoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeGeoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4bf465c7898416e0e1562a3de193be6aae996f58f1a534aa924abe6ba43d5b1c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="countryCodeInput")
    def country_code_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "countryCodeInput"))

    @builtins.property
    @jsii.member(jsii_name="countryCode")
    def country_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "countryCode"))

    @country_code.setter
    def country_code(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2295b9041a3bf9cb1b7be1ff7de5b17db4624d144cc836f8b3f1d73e38d730a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "countryCode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeGeo]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeGeo]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeGeo]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67f007b0f1b6edbdbb16110f3b56f3c22013603015475add0e4210248bc53e14)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeGithubOrganization",
    jsii_struct_bases=[],
    name_mapping={
        "identity_provider_id": "identityProviderId",
        "name": "name",
        "team": "team",
    },
)
class ZeroTrustAccessGroupExcludeGithubOrganization:
    def __init__(
        self,
        *,
        identity_provider_id: builtins.str,
        name: builtins.str,
        team: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param identity_provider_id: The ID of your Github identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        :param name: The name of the organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#name ZeroTrustAccessGroup#name}
        :param team: The name of the team. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#team ZeroTrustAccessGroup#team}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__636563947a854027f528173dbc4440bb3b197e4ef7be60856f143f98baf09a7f)
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument team", value=team, expected_type=type_hints["team"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "identity_provider_id": identity_provider_id,
            "name": name,
        }
        if team is not None:
            self._values["team"] = team

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your Github identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the organization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#name ZeroTrustAccessGroup#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def team(self) -> typing.Optional[builtins.str]:
        '''The name of the team.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#team ZeroTrustAccessGroup#team}
        '''
        result = self._values.get("team")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupExcludeGithubOrganization(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupExcludeGithubOrganizationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeGithubOrganizationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1e11746d6485aa30e8b021a6d0a050e45a6e0db23d6baaefe210f5f212343e45)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetTeam")
    def reset_team(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTeam", []))

    @builtins.property
    @jsii.member(jsii_name="identityProviderIdInput")
    def identity_provider_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityProviderIdInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="teamInput")
    def team_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "teamInput"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c01ef7a2a8f08f3629caa8101a826a9e9fbfa5cd746d4083eb4c8d7423f0951)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc1977e14aa3e0b9a9f8e87f34205cd7612ba21a60b581f960618e0a2294ac16)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="team")
    def team(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "team"))

    @team.setter
    def team(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba4e4d96bf69754c1d823078923f6394d002d2c3597efa78a7a7d80ebbeb8a7e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "team", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeGithubOrganization]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeGithubOrganization]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeGithubOrganization]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__916dce5c1988e5f5c667bc136f09ac38a036d40c809c708b117b50d3eab80d5d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeGroup",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class ZeroTrustAccessGroupExcludeGroup:
    def __init__(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created Access group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38de8e4eb76b109f549021f4cf5d99e32d01dd5f534c26546ef95cd57cbf978a)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of a previously created Access group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupExcludeGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupExcludeGroupOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeGroupOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6a5a60ec94c7f49c543b43d1541ab519e801d3b8d6e8fcfc35ad1e29040015ca)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

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
            type_hints = typing.get_type_hints(_typecheckingstub__fb0ec263cf9a3c6b807a43dd29934a9c2388dccbff683b2da3ad4b101c91fac3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeGroup]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeGroup]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeGroup]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55f9bf5e45af69b410274d9c27b3388a063a2c542f5df4e4356503b425b37182)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeGsuite",
    jsii_struct_bases=[],
    name_mapping={"email": "email", "identity_provider_id": "identityProviderId"},
)
class ZeroTrustAccessGroupExcludeGsuite:
    def __init__(
        self,
        *,
        email: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param email: The email of the Google Workspace group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email ZeroTrustAccessGroup#email}
        :param identity_provider_id: The ID of your Google Workspace identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffb34b648f7f4daa84d07451089872b139bb0d4a88a50b3ef5f77e1ead22767f)
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "email": email,
            "identity_provider_id": identity_provider_id,
        }

    @builtins.property
    def email(self) -> builtins.str:
        '''The email of the Google Workspace group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email ZeroTrustAccessGroup#email}
        '''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your Google Workspace identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupExcludeGsuite(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupExcludeGsuiteOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeGsuiteOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0628fe08d009cbb07858ed1ea5665442ca751a0ac847112a09c584c07a89b99d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="emailInput")
    def email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailInput"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderIdInput")
    def identity_provider_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityProviderIdInput"))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "email"))

    @email.setter
    def email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28ca7443cb330aecae10632b6eb1016452473e8777d0d63bdbacde98cac275ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "email", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f6e14bbf9729e4309aeb5ad5ea2e1a4a8bd7e2c6e1e2b5a5c49a310c6f83a60)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeGsuite]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeGsuite]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeGsuite]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c52ab16ffdf90d1e163f4ecc952a5886bf2c0fdb4603d8cf597b377c03f81a99)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeIp",
    jsii_struct_bases=[],
    name_mapping={"ip": "ip"},
)
class ZeroTrustAccessGroupExcludeIp:
    def __init__(self, *, ip: builtins.str) -> None:
        '''
        :param ip: An IPv4 or IPv6 CIDR block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ip ZeroTrustAccessGroup#ip}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f6cbd3121a4916ffdb4106c9f9f6dd51bb41b4946f7d465741f772bd7f6a73e)
            check_type(argname="argument ip", value=ip, expected_type=type_hints["ip"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "ip": ip,
        }

    @builtins.property
    def ip(self) -> builtins.str:
        '''An IPv4 or IPv6 CIDR block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ip ZeroTrustAccessGroup#ip}
        '''
        result = self._values.get("ip")
        assert result is not None, "Required property 'ip' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupExcludeIp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeIpListStruct",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class ZeroTrustAccessGroupExcludeIpListStruct:
    def __init__(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created IP list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b509a51f05d6b53ddf9e8fbf2844e71f230758e34da849d30be1bd82e570748)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of a previously created IP list.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupExcludeIpListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupExcludeIpListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeIpListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__43bfc1d804e1a2bd12d57dda8556239155e987bc1c2d46a0ab37177002770806)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

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
            type_hints = typing.get_type_hints(_typecheckingstub__626526143dc24391fde4d30e8cc09d7b02377c634749843898b7b686a6d7570a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeIpListStruct]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeIpListStruct]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeIpListStruct]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__056425386a1a9cf5ff39bc99f205872faadab23b140534b4d39fe8ce930b8be3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustAccessGroupExcludeIpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeIpOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9e9e0bff52678eea8ecb491dea7d697e8802345c85d204da22c7c2b0490d9276)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="ipInput")
    def ip_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipInput"))

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ip"))

    @ip.setter
    def ip(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f3344ee582bc6e6165625d7335231d0fbaee766044cbeec4e4eeb4149043e05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ip", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeIp]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeIp]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeIp]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0cf1f276dfbb478c22c579e2285e4c9bf6e98db4a40760f13ce09d1ea5f0b0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeLinkedAppToken",
    jsii_struct_bases=[],
    name_mapping={"app_uid": "appUid"},
)
class ZeroTrustAccessGroupExcludeLinkedAppToken:
    def __init__(self, *, app_uid: builtins.str) -> None:
        '''
        :param app_uid: The ID of an Access OIDC SaaS application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#app_uid ZeroTrustAccessGroup#app_uid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99c89e2c46ebeffbbddcb847c1034cdc6379a0fd094c819aacf4011cc11657bb)
            check_type(argname="argument app_uid", value=app_uid, expected_type=type_hints["app_uid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "app_uid": app_uid,
        }

    @builtins.property
    def app_uid(self) -> builtins.str:
        '''The ID of an Access OIDC SaaS application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#app_uid ZeroTrustAccessGroup#app_uid}
        '''
        result = self._values.get("app_uid")
        assert result is not None, "Required property 'app_uid' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupExcludeLinkedAppToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupExcludeLinkedAppTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeLinkedAppTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5f878a04f1d28bf9b0f56fe50261bd48c6705eedf79a04b47e8fdb600de423c4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="appUidInput")
    def app_uid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "appUidInput"))

    @builtins.property
    @jsii.member(jsii_name="appUid")
    def app_uid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appUid"))

    @app_uid.setter
    def app_uid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54e89aae73dc741b9da5141d0f2d3c71fe1a1f84f4a24a8a41c1176b2c542689)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "appUid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeLinkedAppToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeLinkedAppToken]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeLinkedAppToken]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__165d5dbf66380150b25661f9fea660fb5511d1ac39a6e59456e15d160516b010)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustAccessGroupExcludeList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b77c54da83bd3b408ee8289f1301b7e3f190551e2e9b4664fba554e022cea757)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ZeroTrustAccessGroupExcludeOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c212254999bd6660fd03d9c87384d20e460710483b2d2af13b2d8a3f15860adf)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ZeroTrustAccessGroupExcludeOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c22af34b04416ee82772858d5bd728d97fa453f42bae8563b912aaee73ee4a15)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c5a09c2a31285e158380fb014be9270b28ade6c0b36a75799dadd7ec9f8499a4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__469bfb30df797816979515686755a719c0fcd89dfc032fe11d6d301a92958c40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessGroupExclude]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessGroupExclude]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessGroupExclude]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__190bbf3cbae94699614fa5050f10a4923991770ff514248530f78f729ef26b69)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeLoginMethod",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class ZeroTrustAccessGroupExcludeLoginMethod:
    def __init__(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of an identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c324ff4cc5f6e2956442b12a0c49d6783e543c5ea0b46adafccb130adb91b0d)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of an identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupExcludeLoginMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupExcludeLoginMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeLoginMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cda414be08ec9c9e9118870eb28fe55ad38a907a06024efda5ce7f115c64cbac)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

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
            type_hints = typing.get_type_hints(_typecheckingstub__5f7fcfd534135a78f570c5aed1854a53fa1036d247398eb5b0b15b6a73e51534)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeLoginMethod]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeLoginMethod]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeLoginMethod]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dea16de9e26c07ce627e70bfadf8590981aa3e648ceab90756d50bf26f647f69)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeOidc",
    jsii_struct_bases=[],
    name_mapping={
        "claim_name": "claimName",
        "claim_value": "claimValue",
        "identity_provider_id": "identityProviderId",
    },
)
class ZeroTrustAccessGroupExcludeOidc:
    def __init__(
        self,
        *,
        claim_name: builtins.str,
        claim_value: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param claim_name: The name of the OIDC claim. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#claim_name ZeroTrustAccessGroup#claim_name}
        :param claim_value: The OIDC claim value to look for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#claim_value ZeroTrustAccessGroup#claim_value}
        :param identity_provider_id: The ID of your OIDC identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8bbf4d3a2757d5e3908a48833ab5cf3837e77672e028ae5ded7b64f53bbe2f72)
            check_type(argname="argument claim_name", value=claim_name, expected_type=type_hints["claim_name"])
            check_type(argname="argument claim_value", value=claim_value, expected_type=type_hints["claim_value"])
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "claim_name": claim_name,
            "claim_value": claim_value,
            "identity_provider_id": identity_provider_id,
        }

    @builtins.property
    def claim_name(self) -> builtins.str:
        '''The name of the OIDC claim.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#claim_name ZeroTrustAccessGroup#claim_name}
        '''
        result = self._values.get("claim_name")
        assert result is not None, "Required property 'claim_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def claim_value(self) -> builtins.str:
        '''The OIDC claim value to look for.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#claim_value ZeroTrustAccessGroup#claim_value}
        '''
        result = self._values.get("claim_value")
        assert result is not None, "Required property 'claim_value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your OIDC identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupExcludeOidc(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupExcludeOidcOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeOidcOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8097387d117aa834c762e75e51326662799dff7c09fb53b0ba1cec52c625f67f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="claimNameInput")
    def claim_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "claimNameInput"))

    @builtins.property
    @jsii.member(jsii_name="claimValueInput")
    def claim_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "claimValueInput"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderIdInput")
    def identity_provider_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityProviderIdInput"))

    @builtins.property
    @jsii.member(jsii_name="claimName")
    def claim_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "claimName"))

    @claim_name.setter
    def claim_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01da39a5d1ada3fdc5fc752e4ff06beda4524f71d8a5748714ebc1746fc5ff33)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "claimName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="claimValue")
    def claim_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "claimValue"))

    @claim_value.setter
    def claim_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f918b9385168f76b897c650fd78e12b2a3432ecc91fbe08b7c1f175c5600da90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "claimValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__534b8906690852568c4c06a4f0ad63f832f9e11871c0d874ad955b509a66e166)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeOidc]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeOidc]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeOidc]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__831dd4dcf23463afb2dd838a88f9e33205f1304f76753829b5e6529db3bd37b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeOkta",
    jsii_struct_bases=[],
    name_mapping={"identity_provider_id": "identityProviderId", "name": "name"},
)
class ZeroTrustAccessGroupExcludeOkta:
    def __init__(
        self,
        *,
        identity_provider_id: builtins.str,
        name: builtins.str,
    ) -> None:
        '''
        :param identity_provider_id: The ID of your Okta identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        :param name: The name of the Okta group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#name ZeroTrustAccessGroup#name}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48e66bfe25d6980c043638db52e3f4edabe40234a1f0a052e6a0012b764d5a2a)
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "identity_provider_id": identity_provider_id,
            "name": name,
        }

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your Okta identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the Okta group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#name ZeroTrustAccessGroup#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupExcludeOkta(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupExcludeOktaOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeOktaOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__86cd7adfa749d596a8f6e9fa7d6e30f6ecad9bc346d881cd4f4f0e2ed8451f08)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="identityProviderIdInput")
    def identity_provider_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityProviderIdInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f0f6963d65bbd34d7b25b7e254b1876b19049fd6375063676ff9441efec7284)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3eab82c02411b7522a58fbc379aac94781178b515c3cd69fd131734d996705c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeOkta]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeOkta]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeOkta]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5845877720642a8521e13e6469f12a61382f07b36e5894a8232b1043b80d29fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustAccessGroupExcludeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2ab2f6499db644fbdd5b98d0f3bfcba17b41fb64cee95234b9b068bbf236ca03)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putAnyValidServiceToken")
    def put_any_valid_service_token(self) -> None:
        value = ZeroTrustAccessGroupExcludeAnyValidServiceToken()

        return typing.cast(None, jsii.invoke(self, "putAnyValidServiceToken", [value]))

    @jsii.member(jsii_name="putAuthContext")
    def put_auth_context(
        self,
        *,
        ac_id: builtins.str,
        id: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param ac_id: The ACID of an Authentication context. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ac_id ZeroTrustAccessGroup#ac_id}
        :param id: The ID of an Authentication context. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider_id: The ID of your Azure identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        value = ZeroTrustAccessGroupExcludeAuthContext(
            ac_id=ac_id, id=id, identity_provider_id=identity_provider_id
        )

        return typing.cast(None, jsii.invoke(self, "putAuthContext", [value]))

    @jsii.member(jsii_name="putAuthMethod")
    def put_auth_method(self, *, auth_method: builtins.str) -> None:
        '''
        :param auth_method: The type of authentication method https://datatracker.ietf.org/doc/html/rfc8176#section-2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#auth_method ZeroTrustAccessGroup#auth_method}
        '''
        value = ZeroTrustAccessGroupExcludeAuthMethod(auth_method=auth_method)

        return typing.cast(None, jsii.invoke(self, "putAuthMethod", [value]))

    @jsii.member(jsii_name="putAzureAd")
    def put_azure_ad(
        self,
        *,
        id: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param id: The ID of an Azure group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider_id: The ID of your Azure identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        value = ZeroTrustAccessGroupExcludeAzureAd(
            id=id, identity_provider_id=identity_provider_id
        )

        return typing.cast(None, jsii.invoke(self, "putAzureAd", [value]))

    @jsii.member(jsii_name="putCertificate")
    def put_certificate(self) -> None:
        value = ZeroTrustAccessGroupExcludeCertificate()

        return typing.cast(None, jsii.invoke(self, "putCertificate", [value]))

    @jsii.member(jsii_name="putCommonName")
    def put_common_name(self, *, common_name: builtins.str) -> None:
        '''
        :param common_name: The common name to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#common_name ZeroTrustAccessGroup#common_name}
        '''
        value = ZeroTrustAccessGroupExcludeCommonName(common_name=common_name)

        return typing.cast(None, jsii.invoke(self, "putCommonName", [value]))

    @jsii.member(jsii_name="putDevicePosture")
    def put_device_posture(self, *, integration_uid: builtins.str) -> None:
        '''
        :param integration_uid: The ID of a device posture integration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#integration_uid ZeroTrustAccessGroup#integration_uid}
        '''
        value = ZeroTrustAccessGroupExcludeDevicePosture(
            integration_uid=integration_uid
        )

        return typing.cast(None, jsii.invoke(self, "putDevicePosture", [value]))

    @jsii.member(jsii_name="putEmail")
    def put_email(self, *, email: builtins.str) -> None:
        '''
        :param email: The email of the user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email ZeroTrustAccessGroup#email}
        '''
        value = ZeroTrustAccessGroupExcludeEmail(email=email)

        return typing.cast(None, jsii.invoke(self, "putEmail", [value]))

    @jsii.member(jsii_name="putEmailDomain")
    def put_email_domain(self, *, domain: builtins.str) -> None:
        '''
        :param domain: The email domain to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#domain ZeroTrustAccessGroup#domain}
        '''
        value = ZeroTrustAccessGroupExcludeEmailDomain(domain=domain)

        return typing.cast(None, jsii.invoke(self, "putEmailDomain", [value]))

    @jsii.member(jsii_name="putEmailList")
    def put_email_list(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created email list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        value = ZeroTrustAccessGroupExcludeEmailListStruct(id=id)

        return typing.cast(None, jsii.invoke(self, "putEmailList", [value]))

    @jsii.member(jsii_name="putEveryone")
    def put_everyone(self) -> None:
        value = ZeroTrustAccessGroupExcludeEveryone()

        return typing.cast(None, jsii.invoke(self, "putEveryone", [value]))

    @jsii.member(jsii_name="putExternalEvaluation")
    def put_external_evaluation(
        self,
        *,
        evaluate_url: builtins.str,
        keys_url: builtins.str,
    ) -> None:
        '''
        :param evaluate_url: The API endpoint containing your business logic. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#evaluate_url ZeroTrustAccessGroup#evaluate_url}
        :param keys_url: The API endpoint containing the key that Access uses to verify that the response came from your API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#keys_url ZeroTrustAccessGroup#keys_url}
        '''
        value = ZeroTrustAccessGroupExcludeExternalEvaluation(
            evaluate_url=evaluate_url, keys_url=keys_url
        )

        return typing.cast(None, jsii.invoke(self, "putExternalEvaluation", [value]))

    @jsii.member(jsii_name="putGeo")
    def put_geo(self, *, country_code: builtins.str) -> None:
        '''
        :param country_code: The country code that should be matched. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#country_code ZeroTrustAccessGroup#country_code}
        '''
        value = ZeroTrustAccessGroupExcludeGeo(country_code=country_code)

        return typing.cast(None, jsii.invoke(self, "putGeo", [value]))

    @jsii.member(jsii_name="putGithubOrganization")
    def put_github_organization(
        self,
        *,
        identity_provider_id: builtins.str,
        name: builtins.str,
        team: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param identity_provider_id: The ID of your Github identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        :param name: The name of the organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#name ZeroTrustAccessGroup#name}
        :param team: The name of the team. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#team ZeroTrustAccessGroup#team}
        '''
        value = ZeroTrustAccessGroupExcludeGithubOrganization(
            identity_provider_id=identity_provider_id, name=name, team=team
        )

        return typing.cast(None, jsii.invoke(self, "putGithubOrganization", [value]))

    @jsii.member(jsii_name="putGroup")
    def put_group(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created Access group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        value = ZeroTrustAccessGroupExcludeGroup(id=id)

        return typing.cast(None, jsii.invoke(self, "putGroup", [value]))

    @jsii.member(jsii_name="putGsuite")
    def put_gsuite(
        self,
        *,
        email: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param email: The email of the Google Workspace group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email ZeroTrustAccessGroup#email}
        :param identity_provider_id: The ID of your Google Workspace identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        value = ZeroTrustAccessGroupExcludeGsuite(
            email=email, identity_provider_id=identity_provider_id
        )

        return typing.cast(None, jsii.invoke(self, "putGsuite", [value]))

    @jsii.member(jsii_name="putIp")
    def put_ip(self, *, ip: builtins.str) -> None:
        '''
        :param ip: An IPv4 or IPv6 CIDR block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ip ZeroTrustAccessGroup#ip}
        '''
        value = ZeroTrustAccessGroupExcludeIp(ip=ip)

        return typing.cast(None, jsii.invoke(self, "putIp", [value]))

    @jsii.member(jsii_name="putIpList")
    def put_ip_list(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created IP list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        value = ZeroTrustAccessGroupExcludeIpListStruct(id=id)

        return typing.cast(None, jsii.invoke(self, "putIpList", [value]))

    @jsii.member(jsii_name="putLinkedAppToken")
    def put_linked_app_token(self, *, app_uid: builtins.str) -> None:
        '''
        :param app_uid: The ID of an Access OIDC SaaS application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#app_uid ZeroTrustAccessGroup#app_uid}
        '''
        value = ZeroTrustAccessGroupExcludeLinkedAppToken(app_uid=app_uid)

        return typing.cast(None, jsii.invoke(self, "putLinkedAppToken", [value]))

    @jsii.member(jsii_name="putLoginMethod")
    def put_login_method(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of an identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        value = ZeroTrustAccessGroupExcludeLoginMethod(id=id)

        return typing.cast(None, jsii.invoke(self, "putLoginMethod", [value]))

    @jsii.member(jsii_name="putOidc")
    def put_oidc(
        self,
        *,
        claim_name: builtins.str,
        claim_value: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param claim_name: The name of the OIDC claim. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#claim_name ZeroTrustAccessGroup#claim_name}
        :param claim_value: The OIDC claim value to look for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#claim_value ZeroTrustAccessGroup#claim_value}
        :param identity_provider_id: The ID of your OIDC identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        value = ZeroTrustAccessGroupExcludeOidc(
            claim_name=claim_name,
            claim_value=claim_value,
            identity_provider_id=identity_provider_id,
        )

        return typing.cast(None, jsii.invoke(self, "putOidc", [value]))

    @jsii.member(jsii_name="putOkta")
    def put_okta(
        self,
        *,
        identity_provider_id: builtins.str,
        name: builtins.str,
    ) -> None:
        '''
        :param identity_provider_id: The ID of your Okta identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        :param name: The name of the Okta group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#name ZeroTrustAccessGroup#name}
        '''
        value = ZeroTrustAccessGroupExcludeOkta(
            identity_provider_id=identity_provider_id, name=name
        )

        return typing.cast(None, jsii.invoke(self, "putOkta", [value]))

    @jsii.member(jsii_name="putSaml")
    def put_saml(
        self,
        *,
        attribute_name: builtins.str,
        attribute_value: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param attribute_name: The name of the SAML attribute. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#attribute_name ZeroTrustAccessGroup#attribute_name}
        :param attribute_value: The SAML attribute value to look for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#attribute_value ZeroTrustAccessGroup#attribute_value}
        :param identity_provider_id: The ID of your SAML identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        value = ZeroTrustAccessGroupExcludeSaml(
            attribute_name=attribute_name,
            attribute_value=attribute_value,
            identity_provider_id=identity_provider_id,
        )

        return typing.cast(None, jsii.invoke(self, "putSaml", [value]))

    @jsii.member(jsii_name="putServiceToken")
    def put_service_token(self, *, token_id: builtins.str) -> None:
        '''
        :param token_id: The ID of a Service Token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#token_id ZeroTrustAccessGroup#token_id}
        '''
        value = ZeroTrustAccessGroupExcludeServiceToken(token_id=token_id)

        return typing.cast(None, jsii.invoke(self, "putServiceToken", [value]))

    @jsii.member(jsii_name="resetAnyValidServiceToken")
    def reset_any_valid_service_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAnyValidServiceToken", []))

    @jsii.member(jsii_name="resetAuthContext")
    def reset_auth_context(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthContext", []))

    @jsii.member(jsii_name="resetAuthMethod")
    def reset_auth_method(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthMethod", []))

    @jsii.member(jsii_name="resetAzureAd")
    def reset_azure_ad(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureAd", []))

    @jsii.member(jsii_name="resetCertificate")
    def reset_certificate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificate", []))

    @jsii.member(jsii_name="resetCommonName")
    def reset_common_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCommonName", []))

    @jsii.member(jsii_name="resetDevicePosture")
    def reset_device_posture(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDevicePosture", []))

    @jsii.member(jsii_name="resetEmail")
    def reset_email(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmail", []))

    @jsii.member(jsii_name="resetEmailDomain")
    def reset_email_domain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailDomain", []))

    @jsii.member(jsii_name="resetEmailList")
    def reset_email_list(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailList", []))

    @jsii.member(jsii_name="resetEveryone")
    def reset_everyone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEveryone", []))

    @jsii.member(jsii_name="resetExternalEvaluation")
    def reset_external_evaluation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExternalEvaluation", []))

    @jsii.member(jsii_name="resetGeo")
    def reset_geo(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGeo", []))

    @jsii.member(jsii_name="resetGithubOrganization")
    def reset_github_organization(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGithubOrganization", []))

    @jsii.member(jsii_name="resetGroup")
    def reset_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGroup", []))

    @jsii.member(jsii_name="resetGsuite")
    def reset_gsuite(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGsuite", []))

    @jsii.member(jsii_name="resetIp")
    def reset_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIp", []))

    @jsii.member(jsii_name="resetIpList")
    def reset_ip_list(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpList", []))

    @jsii.member(jsii_name="resetLinkedAppToken")
    def reset_linked_app_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLinkedAppToken", []))

    @jsii.member(jsii_name="resetLoginMethod")
    def reset_login_method(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLoginMethod", []))

    @jsii.member(jsii_name="resetOidc")
    def reset_oidc(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOidc", []))

    @jsii.member(jsii_name="resetOkta")
    def reset_okta(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOkta", []))

    @jsii.member(jsii_name="resetSaml")
    def reset_saml(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSaml", []))

    @jsii.member(jsii_name="resetServiceToken")
    def reset_service_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceToken", []))

    @builtins.property
    @jsii.member(jsii_name="anyValidServiceToken")
    def any_valid_service_token(
        self,
    ) -> ZeroTrustAccessGroupExcludeAnyValidServiceTokenOutputReference:
        return typing.cast(ZeroTrustAccessGroupExcludeAnyValidServiceTokenOutputReference, jsii.get(self, "anyValidServiceToken"))

    @builtins.property
    @jsii.member(jsii_name="authContext")
    def auth_context(self) -> ZeroTrustAccessGroupExcludeAuthContextOutputReference:
        return typing.cast(ZeroTrustAccessGroupExcludeAuthContextOutputReference, jsii.get(self, "authContext"))

    @builtins.property
    @jsii.member(jsii_name="authMethod")
    def auth_method(self) -> ZeroTrustAccessGroupExcludeAuthMethodOutputReference:
        return typing.cast(ZeroTrustAccessGroupExcludeAuthMethodOutputReference, jsii.get(self, "authMethod"))

    @builtins.property
    @jsii.member(jsii_name="azureAd")
    def azure_ad(self) -> ZeroTrustAccessGroupExcludeAzureAdOutputReference:
        return typing.cast(ZeroTrustAccessGroupExcludeAzureAdOutputReference, jsii.get(self, "azureAd"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> ZeroTrustAccessGroupExcludeCertificateOutputReference:
        return typing.cast(ZeroTrustAccessGroupExcludeCertificateOutputReference, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(self) -> ZeroTrustAccessGroupExcludeCommonNameOutputReference:
        return typing.cast(ZeroTrustAccessGroupExcludeCommonNameOutputReference, jsii.get(self, "commonName"))

    @builtins.property
    @jsii.member(jsii_name="devicePosture")
    def device_posture(self) -> ZeroTrustAccessGroupExcludeDevicePostureOutputReference:
        return typing.cast(ZeroTrustAccessGroupExcludeDevicePostureOutputReference, jsii.get(self, "devicePosture"))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(self) -> ZeroTrustAccessGroupExcludeEmailOutputReference:
        return typing.cast(ZeroTrustAccessGroupExcludeEmailOutputReference, jsii.get(self, "email"))

    @builtins.property
    @jsii.member(jsii_name="emailDomain")
    def email_domain(self) -> ZeroTrustAccessGroupExcludeEmailDomainOutputReference:
        return typing.cast(ZeroTrustAccessGroupExcludeEmailDomainOutputReference, jsii.get(self, "emailDomain"))

    @builtins.property
    @jsii.member(jsii_name="emailList")
    def email_list(self) -> ZeroTrustAccessGroupExcludeEmailListStructOutputReference:
        return typing.cast(ZeroTrustAccessGroupExcludeEmailListStructOutputReference, jsii.get(self, "emailList"))

    @builtins.property
    @jsii.member(jsii_name="everyone")
    def everyone(self) -> ZeroTrustAccessGroupExcludeEveryoneOutputReference:
        return typing.cast(ZeroTrustAccessGroupExcludeEveryoneOutputReference, jsii.get(self, "everyone"))

    @builtins.property
    @jsii.member(jsii_name="externalEvaluation")
    def external_evaluation(
        self,
    ) -> ZeroTrustAccessGroupExcludeExternalEvaluationOutputReference:
        return typing.cast(ZeroTrustAccessGroupExcludeExternalEvaluationOutputReference, jsii.get(self, "externalEvaluation"))

    @builtins.property
    @jsii.member(jsii_name="geo")
    def geo(self) -> ZeroTrustAccessGroupExcludeGeoOutputReference:
        return typing.cast(ZeroTrustAccessGroupExcludeGeoOutputReference, jsii.get(self, "geo"))

    @builtins.property
    @jsii.member(jsii_name="githubOrganization")
    def github_organization(
        self,
    ) -> ZeroTrustAccessGroupExcludeGithubOrganizationOutputReference:
        return typing.cast(ZeroTrustAccessGroupExcludeGithubOrganizationOutputReference, jsii.get(self, "githubOrganization"))

    @builtins.property
    @jsii.member(jsii_name="group")
    def group(self) -> ZeroTrustAccessGroupExcludeGroupOutputReference:
        return typing.cast(ZeroTrustAccessGroupExcludeGroupOutputReference, jsii.get(self, "group"))

    @builtins.property
    @jsii.member(jsii_name="gsuite")
    def gsuite(self) -> ZeroTrustAccessGroupExcludeGsuiteOutputReference:
        return typing.cast(ZeroTrustAccessGroupExcludeGsuiteOutputReference, jsii.get(self, "gsuite"))

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> ZeroTrustAccessGroupExcludeIpOutputReference:
        return typing.cast(ZeroTrustAccessGroupExcludeIpOutputReference, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="ipList")
    def ip_list(self) -> ZeroTrustAccessGroupExcludeIpListStructOutputReference:
        return typing.cast(ZeroTrustAccessGroupExcludeIpListStructOutputReference, jsii.get(self, "ipList"))

    @builtins.property
    @jsii.member(jsii_name="linkedAppToken")
    def linked_app_token(
        self,
    ) -> ZeroTrustAccessGroupExcludeLinkedAppTokenOutputReference:
        return typing.cast(ZeroTrustAccessGroupExcludeLinkedAppTokenOutputReference, jsii.get(self, "linkedAppToken"))

    @builtins.property
    @jsii.member(jsii_name="loginMethod")
    def login_method(self) -> ZeroTrustAccessGroupExcludeLoginMethodOutputReference:
        return typing.cast(ZeroTrustAccessGroupExcludeLoginMethodOutputReference, jsii.get(self, "loginMethod"))

    @builtins.property
    @jsii.member(jsii_name="oidc")
    def oidc(self) -> ZeroTrustAccessGroupExcludeOidcOutputReference:
        return typing.cast(ZeroTrustAccessGroupExcludeOidcOutputReference, jsii.get(self, "oidc"))

    @builtins.property
    @jsii.member(jsii_name="okta")
    def okta(self) -> ZeroTrustAccessGroupExcludeOktaOutputReference:
        return typing.cast(ZeroTrustAccessGroupExcludeOktaOutputReference, jsii.get(self, "okta"))

    @builtins.property
    @jsii.member(jsii_name="saml")
    def saml(self) -> "ZeroTrustAccessGroupExcludeSamlOutputReference":
        return typing.cast("ZeroTrustAccessGroupExcludeSamlOutputReference", jsii.get(self, "saml"))

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(self) -> "ZeroTrustAccessGroupExcludeServiceTokenOutputReference":
        return typing.cast("ZeroTrustAccessGroupExcludeServiceTokenOutputReference", jsii.get(self, "serviceToken"))

    @builtins.property
    @jsii.member(jsii_name="anyValidServiceTokenInput")
    def any_valid_service_token_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeAnyValidServiceToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeAnyValidServiceToken]], jsii.get(self, "anyValidServiceTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="authContextInput")
    def auth_context_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeAuthContext]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeAuthContext]], jsii.get(self, "authContextInput"))

    @builtins.property
    @jsii.member(jsii_name="authMethodInput")
    def auth_method_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeAuthMethod]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeAuthMethod]], jsii.get(self, "authMethodInput"))

    @builtins.property
    @jsii.member(jsii_name="azureAdInput")
    def azure_ad_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeAzureAd]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeAzureAd]], jsii.get(self, "azureAdInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateInput")
    def certificate_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeCertificate]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeCertificate]], jsii.get(self, "certificateInput"))

    @builtins.property
    @jsii.member(jsii_name="commonNameInput")
    def common_name_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeCommonName]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeCommonName]], jsii.get(self, "commonNameInput"))

    @builtins.property
    @jsii.member(jsii_name="devicePostureInput")
    def device_posture_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeDevicePosture]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeDevicePosture]], jsii.get(self, "devicePostureInput"))

    @builtins.property
    @jsii.member(jsii_name="emailDomainInput")
    def email_domain_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeEmailDomain]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeEmailDomain]], jsii.get(self, "emailDomainInput"))

    @builtins.property
    @jsii.member(jsii_name="emailInput")
    def email_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeEmail]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeEmail]], jsii.get(self, "emailInput"))

    @builtins.property
    @jsii.member(jsii_name="emailListInput")
    def email_list_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeEmailListStruct]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeEmailListStruct]], jsii.get(self, "emailListInput"))

    @builtins.property
    @jsii.member(jsii_name="everyoneInput")
    def everyone_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeEveryone]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeEveryone]], jsii.get(self, "everyoneInput"))

    @builtins.property
    @jsii.member(jsii_name="externalEvaluationInput")
    def external_evaluation_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeExternalEvaluation]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeExternalEvaluation]], jsii.get(self, "externalEvaluationInput"))

    @builtins.property
    @jsii.member(jsii_name="geoInput")
    def geo_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeGeo]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeGeo]], jsii.get(self, "geoInput"))

    @builtins.property
    @jsii.member(jsii_name="githubOrganizationInput")
    def github_organization_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeGithubOrganization]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeGithubOrganization]], jsii.get(self, "githubOrganizationInput"))

    @builtins.property
    @jsii.member(jsii_name="groupInput")
    def group_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeGroup]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeGroup]], jsii.get(self, "groupInput"))

    @builtins.property
    @jsii.member(jsii_name="gsuiteInput")
    def gsuite_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeGsuite]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeGsuite]], jsii.get(self, "gsuiteInput"))

    @builtins.property
    @jsii.member(jsii_name="ipInput")
    def ip_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeIp]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeIp]], jsii.get(self, "ipInput"))

    @builtins.property
    @jsii.member(jsii_name="ipListInput")
    def ip_list_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeIpListStruct]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeIpListStruct]], jsii.get(self, "ipListInput"))

    @builtins.property
    @jsii.member(jsii_name="linkedAppTokenInput")
    def linked_app_token_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeLinkedAppToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeLinkedAppToken]], jsii.get(self, "linkedAppTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="loginMethodInput")
    def login_method_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeLoginMethod]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeLoginMethod]], jsii.get(self, "loginMethodInput"))

    @builtins.property
    @jsii.member(jsii_name="oidcInput")
    def oidc_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeOidc]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeOidc]], jsii.get(self, "oidcInput"))

    @builtins.property
    @jsii.member(jsii_name="oktaInput")
    def okta_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeOkta]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeOkta]], jsii.get(self, "oktaInput"))

    @builtins.property
    @jsii.member(jsii_name="samlInput")
    def saml_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustAccessGroupExcludeSaml"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustAccessGroupExcludeSaml"]], jsii.get(self, "samlInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceTokenInput")
    def service_token_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustAccessGroupExcludeServiceToken"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustAccessGroupExcludeServiceToken"]], jsii.get(self, "serviceTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExclude]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExclude]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExclude]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3db3d458057f4cf7c4b02a96e7c95016026b85d677ab0583d7a2668f0363227)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeSaml",
    jsii_struct_bases=[],
    name_mapping={
        "attribute_name": "attributeName",
        "attribute_value": "attributeValue",
        "identity_provider_id": "identityProviderId",
    },
)
class ZeroTrustAccessGroupExcludeSaml:
    def __init__(
        self,
        *,
        attribute_name: builtins.str,
        attribute_value: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param attribute_name: The name of the SAML attribute. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#attribute_name ZeroTrustAccessGroup#attribute_name}
        :param attribute_value: The SAML attribute value to look for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#attribute_value ZeroTrustAccessGroup#attribute_value}
        :param identity_provider_id: The ID of your SAML identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49d44189fe35ab616fc776ce7dda9c4278169153a9f7ca74c67294704979db31)
            check_type(argname="argument attribute_name", value=attribute_name, expected_type=type_hints["attribute_name"])
            check_type(argname="argument attribute_value", value=attribute_value, expected_type=type_hints["attribute_value"])
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "attribute_name": attribute_name,
            "attribute_value": attribute_value,
            "identity_provider_id": identity_provider_id,
        }

    @builtins.property
    def attribute_name(self) -> builtins.str:
        '''The name of the SAML attribute.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#attribute_name ZeroTrustAccessGroup#attribute_name}
        '''
        result = self._values.get("attribute_name")
        assert result is not None, "Required property 'attribute_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attribute_value(self) -> builtins.str:
        '''The SAML attribute value to look for.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#attribute_value ZeroTrustAccessGroup#attribute_value}
        '''
        result = self._values.get("attribute_value")
        assert result is not None, "Required property 'attribute_value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your SAML identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupExcludeSaml(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupExcludeSamlOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeSamlOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c8c5dab710b854fd42bd545e8c8017797cab33136954c7c30ab51333d1cf0344)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="attributeNameInput")
    def attribute_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "attributeNameInput"))

    @builtins.property
    @jsii.member(jsii_name="attributeValueInput")
    def attribute_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "attributeValueInput"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderIdInput")
    def identity_provider_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityProviderIdInput"))

    @builtins.property
    @jsii.member(jsii_name="attributeName")
    def attribute_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "attributeName"))

    @attribute_name.setter
    def attribute_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52c6d1f02b42129e63d5bca47fc4394501d75ca187dcd3774993cf266c52c847)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attributeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="attributeValue")
    def attribute_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "attributeValue"))

    @attribute_value.setter
    def attribute_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__039756dc908334313a8f79c693dd67b6129ed02ec3c6a731e3437e1eebee9bdf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attributeValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f63c10399255da050a10266dc318ddada2706a686f5a79a4085c4f765d33a145)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeSaml]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeSaml]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeSaml]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63b38329866908ae61bdf797c6ce894c0d99640f14276e9f1f31b15b107bad16)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeServiceToken",
    jsii_struct_bases=[],
    name_mapping={"token_id": "tokenId"},
)
class ZeroTrustAccessGroupExcludeServiceToken:
    def __init__(self, *, token_id: builtins.str) -> None:
        '''
        :param token_id: The ID of a Service Token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#token_id ZeroTrustAccessGroup#token_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61ed69d302dfc105adddaddc8736526b3c1944e3bad95541160d5babfe6e9d1d)
            check_type(argname="argument token_id", value=token_id, expected_type=type_hints["token_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "token_id": token_id,
        }

    @builtins.property
    def token_id(self) -> builtins.str:
        '''The ID of a Service Token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#token_id ZeroTrustAccessGroup#token_id}
        '''
        result = self._values.get("token_id")
        assert result is not None, "Required property 'token_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupExcludeServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupExcludeServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupExcludeServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ff079afa1eb2555a3e3a9977693af494b15d94fef2d2b004e3745fc2576fdcd2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="tokenIdInput")
    def token_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenIdInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenId")
    def token_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tokenId"))

    @token_id.setter
    def token_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df7c847784f01909bd57857b4a61ab2f7c24ac15a3d2b65552756a074b73c1c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeServiceToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeServiceToken]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeServiceToken]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea9c4058747fad67350b0140e2f24bdcb6249c49be6216d228457792efc7ef7d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupInclude",
    jsii_struct_bases=[],
    name_mapping={
        "any_valid_service_token": "anyValidServiceToken",
        "auth_context": "authContext",
        "auth_method": "authMethod",
        "azure_ad": "azureAd",
        "certificate": "certificate",
        "common_name": "commonName",
        "device_posture": "devicePosture",
        "email": "email",
        "email_domain": "emailDomain",
        "email_list": "emailList",
        "everyone": "everyone",
        "external_evaluation": "externalEvaluation",
        "geo": "geo",
        "github_organization": "githubOrganization",
        "group": "group",
        "gsuite": "gsuite",
        "ip": "ip",
        "ip_list": "ipList",
        "linked_app_token": "linkedAppToken",
        "login_method": "loginMethod",
        "oidc": "oidc",
        "okta": "okta",
        "saml": "saml",
        "service_token": "serviceToken",
    },
)
class ZeroTrustAccessGroupInclude:
    def __init__(
        self,
        *,
        any_valid_service_token: typing.Optional[typing.Union["ZeroTrustAccessGroupIncludeAnyValidServiceToken", typing.Dict[builtins.str, typing.Any]]] = None,
        auth_context: typing.Optional[typing.Union["ZeroTrustAccessGroupIncludeAuthContext", typing.Dict[builtins.str, typing.Any]]] = None,
        auth_method: typing.Optional[typing.Union["ZeroTrustAccessGroupIncludeAuthMethod", typing.Dict[builtins.str, typing.Any]]] = None,
        azure_ad: typing.Optional[typing.Union["ZeroTrustAccessGroupIncludeAzureAd", typing.Dict[builtins.str, typing.Any]]] = None,
        certificate: typing.Optional[typing.Union["ZeroTrustAccessGroupIncludeCertificate", typing.Dict[builtins.str, typing.Any]]] = None,
        common_name: typing.Optional[typing.Union["ZeroTrustAccessGroupIncludeCommonName", typing.Dict[builtins.str, typing.Any]]] = None,
        device_posture: typing.Optional[typing.Union["ZeroTrustAccessGroupIncludeDevicePosture", typing.Dict[builtins.str, typing.Any]]] = None,
        email: typing.Optional[typing.Union["ZeroTrustAccessGroupIncludeEmail", typing.Dict[builtins.str, typing.Any]]] = None,
        email_domain: typing.Optional[typing.Union["ZeroTrustAccessGroupIncludeEmailDomain", typing.Dict[builtins.str, typing.Any]]] = None,
        email_list: typing.Optional[typing.Union["ZeroTrustAccessGroupIncludeEmailListStruct", typing.Dict[builtins.str, typing.Any]]] = None,
        everyone: typing.Optional[typing.Union["ZeroTrustAccessGroupIncludeEveryone", typing.Dict[builtins.str, typing.Any]]] = None,
        external_evaluation: typing.Optional[typing.Union["ZeroTrustAccessGroupIncludeExternalEvaluation", typing.Dict[builtins.str, typing.Any]]] = None,
        geo: typing.Optional[typing.Union["ZeroTrustAccessGroupIncludeGeo", typing.Dict[builtins.str, typing.Any]]] = None,
        github_organization: typing.Optional[typing.Union["ZeroTrustAccessGroupIncludeGithubOrganization", typing.Dict[builtins.str, typing.Any]]] = None,
        group: typing.Optional[typing.Union["ZeroTrustAccessGroupIncludeGroup", typing.Dict[builtins.str, typing.Any]]] = None,
        gsuite: typing.Optional[typing.Union["ZeroTrustAccessGroupIncludeGsuite", typing.Dict[builtins.str, typing.Any]]] = None,
        ip: typing.Optional[typing.Union["ZeroTrustAccessGroupIncludeIp", typing.Dict[builtins.str, typing.Any]]] = None,
        ip_list: typing.Optional[typing.Union["ZeroTrustAccessGroupIncludeIpListStruct", typing.Dict[builtins.str, typing.Any]]] = None,
        linked_app_token: typing.Optional[typing.Union["ZeroTrustAccessGroupIncludeLinkedAppToken", typing.Dict[builtins.str, typing.Any]]] = None,
        login_method: typing.Optional[typing.Union["ZeroTrustAccessGroupIncludeLoginMethod", typing.Dict[builtins.str, typing.Any]]] = None,
        oidc: typing.Optional[typing.Union["ZeroTrustAccessGroupIncludeOidc", typing.Dict[builtins.str, typing.Any]]] = None,
        okta: typing.Optional[typing.Union["ZeroTrustAccessGroupIncludeOkta", typing.Dict[builtins.str, typing.Any]]] = None,
        saml: typing.Optional[typing.Union["ZeroTrustAccessGroupIncludeSaml", typing.Dict[builtins.str, typing.Any]]] = None,
        service_token: typing.Optional[typing.Union["ZeroTrustAccessGroupIncludeServiceToken", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param any_valid_service_token: An empty object which matches on all service tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#any_valid_service_token ZeroTrustAccessGroup#any_valid_service_token}
        :param auth_context: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#auth_context ZeroTrustAccessGroup#auth_context}.
        :param auth_method: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#auth_method ZeroTrustAccessGroup#auth_method}.
        :param azure_ad: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#azure_ad ZeroTrustAccessGroup#azure_ad}.
        :param certificate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#certificate ZeroTrustAccessGroup#certificate}.
        :param common_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#common_name ZeroTrustAccessGroup#common_name}.
        :param device_posture: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#device_posture ZeroTrustAccessGroup#device_posture}.
        :param email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email ZeroTrustAccessGroup#email}.
        :param email_domain: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email_domain ZeroTrustAccessGroup#email_domain}.
        :param email_list: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email_list ZeroTrustAccessGroup#email_list}.
        :param everyone: An empty object which matches on all users. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#everyone ZeroTrustAccessGroup#everyone}
        :param external_evaluation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#external_evaluation ZeroTrustAccessGroup#external_evaluation}.
        :param geo: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#geo ZeroTrustAccessGroup#geo}.
        :param github_organization: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#github_organization ZeroTrustAccessGroup#github_organization}.
        :param group: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#group ZeroTrustAccessGroup#group}.
        :param gsuite: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#gsuite ZeroTrustAccessGroup#gsuite}.
        :param ip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ip ZeroTrustAccessGroup#ip}.
        :param ip_list: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ip_list ZeroTrustAccessGroup#ip_list}.
        :param linked_app_token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#linked_app_token ZeroTrustAccessGroup#linked_app_token}.
        :param login_method: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#login_method ZeroTrustAccessGroup#login_method}.
        :param oidc: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#oidc ZeroTrustAccessGroup#oidc}.
        :param okta: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#okta ZeroTrustAccessGroup#okta}.
        :param saml: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#saml ZeroTrustAccessGroup#saml}.
        :param service_token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#service_token ZeroTrustAccessGroup#service_token}.
        '''
        if isinstance(any_valid_service_token, dict):
            any_valid_service_token = ZeroTrustAccessGroupIncludeAnyValidServiceToken(**any_valid_service_token)
        if isinstance(auth_context, dict):
            auth_context = ZeroTrustAccessGroupIncludeAuthContext(**auth_context)
        if isinstance(auth_method, dict):
            auth_method = ZeroTrustAccessGroupIncludeAuthMethod(**auth_method)
        if isinstance(azure_ad, dict):
            azure_ad = ZeroTrustAccessGroupIncludeAzureAd(**azure_ad)
        if isinstance(certificate, dict):
            certificate = ZeroTrustAccessGroupIncludeCertificate(**certificate)
        if isinstance(common_name, dict):
            common_name = ZeroTrustAccessGroupIncludeCommonName(**common_name)
        if isinstance(device_posture, dict):
            device_posture = ZeroTrustAccessGroupIncludeDevicePosture(**device_posture)
        if isinstance(email, dict):
            email = ZeroTrustAccessGroupIncludeEmail(**email)
        if isinstance(email_domain, dict):
            email_domain = ZeroTrustAccessGroupIncludeEmailDomain(**email_domain)
        if isinstance(email_list, dict):
            email_list = ZeroTrustAccessGroupIncludeEmailListStruct(**email_list)
        if isinstance(everyone, dict):
            everyone = ZeroTrustAccessGroupIncludeEveryone(**everyone)
        if isinstance(external_evaluation, dict):
            external_evaluation = ZeroTrustAccessGroupIncludeExternalEvaluation(**external_evaluation)
        if isinstance(geo, dict):
            geo = ZeroTrustAccessGroupIncludeGeo(**geo)
        if isinstance(github_organization, dict):
            github_organization = ZeroTrustAccessGroupIncludeGithubOrganization(**github_organization)
        if isinstance(group, dict):
            group = ZeroTrustAccessGroupIncludeGroup(**group)
        if isinstance(gsuite, dict):
            gsuite = ZeroTrustAccessGroupIncludeGsuite(**gsuite)
        if isinstance(ip, dict):
            ip = ZeroTrustAccessGroupIncludeIp(**ip)
        if isinstance(ip_list, dict):
            ip_list = ZeroTrustAccessGroupIncludeIpListStruct(**ip_list)
        if isinstance(linked_app_token, dict):
            linked_app_token = ZeroTrustAccessGroupIncludeLinkedAppToken(**linked_app_token)
        if isinstance(login_method, dict):
            login_method = ZeroTrustAccessGroupIncludeLoginMethod(**login_method)
        if isinstance(oidc, dict):
            oidc = ZeroTrustAccessGroupIncludeOidc(**oidc)
        if isinstance(okta, dict):
            okta = ZeroTrustAccessGroupIncludeOkta(**okta)
        if isinstance(saml, dict):
            saml = ZeroTrustAccessGroupIncludeSaml(**saml)
        if isinstance(service_token, dict):
            service_token = ZeroTrustAccessGroupIncludeServiceToken(**service_token)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3887537ed22b563df2b0db3721f11ebfd2bcf03355110c7054a2ab30fba016e7)
            check_type(argname="argument any_valid_service_token", value=any_valid_service_token, expected_type=type_hints["any_valid_service_token"])
            check_type(argname="argument auth_context", value=auth_context, expected_type=type_hints["auth_context"])
            check_type(argname="argument auth_method", value=auth_method, expected_type=type_hints["auth_method"])
            check_type(argname="argument azure_ad", value=azure_ad, expected_type=type_hints["azure_ad"])
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument common_name", value=common_name, expected_type=type_hints["common_name"])
            check_type(argname="argument device_posture", value=device_posture, expected_type=type_hints["device_posture"])
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
            check_type(argname="argument email_domain", value=email_domain, expected_type=type_hints["email_domain"])
            check_type(argname="argument email_list", value=email_list, expected_type=type_hints["email_list"])
            check_type(argname="argument everyone", value=everyone, expected_type=type_hints["everyone"])
            check_type(argname="argument external_evaluation", value=external_evaluation, expected_type=type_hints["external_evaluation"])
            check_type(argname="argument geo", value=geo, expected_type=type_hints["geo"])
            check_type(argname="argument github_organization", value=github_organization, expected_type=type_hints["github_organization"])
            check_type(argname="argument group", value=group, expected_type=type_hints["group"])
            check_type(argname="argument gsuite", value=gsuite, expected_type=type_hints["gsuite"])
            check_type(argname="argument ip", value=ip, expected_type=type_hints["ip"])
            check_type(argname="argument ip_list", value=ip_list, expected_type=type_hints["ip_list"])
            check_type(argname="argument linked_app_token", value=linked_app_token, expected_type=type_hints["linked_app_token"])
            check_type(argname="argument login_method", value=login_method, expected_type=type_hints["login_method"])
            check_type(argname="argument oidc", value=oidc, expected_type=type_hints["oidc"])
            check_type(argname="argument okta", value=okta, expected_type=type_hints["okta"])
            check_type(argname="argument saml", value=saml, expected_type=type_hints["saml"])
            check_type(argname="argument service_token", value=service_token, expected_type=type_hints["service_token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if any_valid_service_token is not None:
            self._values["any_valid_service_token"] = any_valid_service_token
        if auth_context is not None:
            self._values["auth_context"] = auth_context
        if auth_method is not None:
            self._values["auth_method"] = auth_method
        if azure_ad is not None:
            self._values["azure_ad"] = azure_ad
        if certificate is not None:
            self._values["certificate"] = certificate
        if common_name is not None:
            self._values["common_name"] = common_name
        if device_posture is not None:
            self._values["device_posture"] = device_posture
        if email is not None:
            self._values["email"] = email
        if email_domain is not None:
            self._values["email_domain"] = email_domain
        if email_list is not None:
            self._values["email_list"] = email_list
        if everyone is not None:
            self._values["everyone"] = everyone
        if external_evaluation is not None:
            self._values["external_evaluation"] = external_evaluation
        if geo is not None:
            self._values["geo"] = geo
        if github_organization is not None:
            self._values["github_organization"] = github_organization
        if group is not None:
            self._values["group"] = group
        if gsuite is not None:
            self._values["gsuite"] = gsuite
        if ip is not None:
            self._values["ip"] = ip
        if ip_list is not None:
            self._values["ip_list"] = ip_list
        if linked_app_token is not None:
            self._values["linked_app_token"] = linked_app_token
        if login_method is not None:
            self._values["login_method"] = login_method
        if oidc is not None:
            self._values["oidc"] = oidc
        if okta is not None:
            self._values["okta"] = okta
        if saml is not None:
            self._values["saml"] = saml
        if service_token is not None:
            self._values["service_token"] = service_token

    @builtins.property
    def any_valid_service_token(
        self,
    ) -> typing.Optional["ZeroTrustAccessGroupIncludeAnyValidServiceToken"]:
        '''An empty object which matches on all service tokens.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#any_valid_service_token ZeroTrustAccessGroup#any_valid_service_token}
        '''
        result = self._values.get("any_valid_service_token")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupIncludeAnyValidServiceToken"], result)

    @builtins.property
    def auth_context(self) -> typing.Optional["ZeroTrustAccessGroupIncludeAuthContext"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#auth_context ZeroTrustAccessGroup#auth_context}.'''
        result = self._values.get("auth_context")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupIncludeAuthContext"], result)

    @builtins.property
    def auth_method(self) -> typing.Optional["ZeroTrustAccessGroupIncludeAuthMethod"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#auth_method ZeroTrustAccessGroup#auth_method}.'''
        result = self._values.get("auth_method")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupIncludeAuthMethod"], result)

    @builtins.property
    def azure_ad(self) -> typing.Optional["ZeroTrustAccessGroupIncludeAzureAd"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#azure_ad ZeroTrustAccessGroup#azure_ad}.'''
        result = self._values.get("azure_ad")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupIncludeAzureAd"], result)

    @builtins.property
    def certificate(self) -> typing.Optional["ZeroTrustAccessGroupIncludeCertificate"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#certificate ZeroTrustAccessGroup#certificate}.'''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupIncludeCertificate"], result)

    @builtins.property
    def common_name(self) -> typing.Optional["ZeroTrustAccessGroupIncludeCommonName"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#common_name ZeroTrustAccessGroup#common_name}.'''
        result = self._values.get("common_name")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupIncludeCommonName"], result)

    @builtins.property
    def device_posture(
        self,
    ) -> typing.Optional["ZeroTrustAccessGroupIncludeDevicePosture"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#device_posture ZeroTrustAccessGroup#device_posture}.'''
        result = self._values.get("device_posture")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupIncludeDevicePosture"], result)

    @builtins.property
    def email(self) -> typing.Optional["ZeroTrustAccessGroupIncludeEmail"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email ZeroTrustAccessGroup#email}.'''
        result = self._values.get("email")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupIncludeEmail"], result)

    @builtins.property
    def email_domain(self) -> typing.Optional["ZeroTrustAccessGroupIncludeEmailDomain"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email_domain ZeroTrustAccessGroup#email_domain}.'''
        result = self._values.get("email_domain")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupIncludeEmailDomain"], result)

    @builtins.property
    def email_list(
        self,
    ) -> typing.Optional["ZeroTrustAccessGroupIncludeEmailListStruct"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email_list ZeroTrustAccessGroup#email_list}.'''
        result = self._values.get("email_list")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupIncludeEmailListStruct"], result)

    @builtins.property
    def everyone(self) -> typing.Optional["ZeroTrustAccessGroupIncludeEveryone"]:
        '''An empty object which matches on all users.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#everyone ZeroTrustAccessGroup#everyone}
        '''
        result = self._values.get("everyone")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupIncludeEveryone"], result)

    @builtins.property
    def external_evaluation(
        self,
    ) -> typing.Optional["ZeroTrustAccessGroupIncludeExternalEvaluation"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#external_evaluation ZeroTrustAccessGroup#external_evaluation}.'''
        result = self._values.get("external_evaluation")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupIncludeExternalEvaluation"], result)

    @builtins.property
    def geo(self) -> typing.Optional["ZeroTrustAccessGroupIncludeGeo"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#geo ZeroTrustAccessGroup#geo}.'''
        result = self._values.get("geo")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupIncludeGeo"], result)

    @builtins.property
    def github_organization(
        self,
    ) -> typing.Optional["ZeroTrustAccessGroupIncludeGithubOrganization"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#github_organization ZeroTrustAccessGroup#github_organization}.'''
        result = self._values.get("github_organization")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupIncludeGithubOrganization"], result)

    @builtins.property
    def group(self) -> typing.Optional["ZeroTrustAccessGroupIncludeGroup"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#group ZeroTrustAccessGroup#group}.'''
        result = self._values.get("group")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupIncludeGroup"], result)

    @builtins.property
    def gsuite(self) -> typing.Optional["ZeroTrustAccessGroupIncludeGsuite"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#gsuite ZeroTrustAccessGroup#gsuite}.'''
        result = self._values.get("gsuite")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupIncludeGsuite"], result)

    @builtins.property
    def ip(self) -> typing.Optional["ZeroTrustAccessGroupIncludeIp"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ip ZeroTrustAccessGroup#ip}.'''
        result = self._values.get("ip")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupIncludeIp"], result)

    @builtins.property
    def ip_list(self) -> typing.Optional["ZeroTrustAccessGroupIncludeIpListStruct"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ip_list ZeroTrustAccessGroup#ip_list}.'''
        result = self._values.get("ip_list")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupIncludeIpListStruct"], result)

    @builtins.property
    def linked_app_token(
        self,
    ) -> typing.Optional["ZeroTrustAccessGroupIncludeLinkedAppToken"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#linked_app_token ZeroTrustAccessGroup#linked_app_token}.'''
        result = self._values.get("linked_app_token")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupIncludeLinkedAppToken"], result)

    @builtins.property
    def login_method(self) -> typing.Optional["ZeroTrustAccessGroupIncludeLoginMethod"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#login_method ZeroTrustAccessGroup#login_method}.'''
        result = self._values.get("login_method")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupIncludeLoginMethod"], result)

    @builtins.property
    def oidc(self) -> typing.Optional["ZeroTrustAccessGroupIncludeOidc"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#oidc ZeroTrustAccessGroup#oidc}.'''
        result = self._values.get("oidc")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupIncludeOidc"], result)

    @builtins.property
    def okta(self) -> typing.Optional["ZeroTrustAccessGroupIncludeOkta"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#okta ZeroTrustAccessGroup#okta}.'''
        result = self._values.get("okta")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupIncludeOkta"], result)

    @builtins.property
    def saml(self) -> typing.Optional["ZeroTrustAccessGroupIncludeSaml"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#saml ZeroTrustAccessGroup#saml}.'''
        result = self._values.get("saml")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupIncludeSaml"], result)

    @builtins.property
    def service_token(
        self,
    ) -> typing.Optional["ZeroTrustAccessGroupIncludeServiceToken"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#service_token ZeroTrustAccessGroup#service_token}.'''
        result = self._values.get("service_token")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupIncludeServiceToken"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupInclude(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeAnyValidServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class ZeroTrustAccessGroupIncludeAnyValidServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupIncludeAnyValidServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupIncludeAnyValidServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeAnyValidServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__aaa0c39719b482c6fe419a3745e381d11c43d4455bfb401c1dea90ee4a14aaab)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeAnyValidServiceToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeAnyValidServiceToken]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeAnyValidServiceToken]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11c0f22d6b5718350ef9d3aeb5ec3d76afe81092b3a67163e29943bb9bef9528)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeAuthContext",
    jsii_struct_bases=[],
    name_mapping={
        "ac_id": "acId",
        "id": "id",
        "identity_provider_id": "identityProviderId",
    },
)
class ZeroTrustAccessGroupIncludeAuthContext:
    def __init__(
        self,
        *,
        ac_id: builtins.str,
        id: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param ac_id: The ACID of an Authentication context. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ac_id ZeroTrustAccessGroup#ac_id}
        :param id: The ID of an Authentication context. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider_id: The ID of your Azure identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74a06468f4b695c7f1cc645d73f503dc110f3b3c5ab6cd7d61c068ef615ec561)
            check_type(argname="argument ac_id", value=ac_id, expected_type=type_hints["ac_id"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "ac_id": ac_id,
            "id": id,
            "identity_provider_id": identity_provider_id,
        }

    @builtins.property
    def ac_id(self) -> builtins.str:
        '''The ACID of an Authentication context.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ac_id ZeroTrustAccessGroup#ac_id}
        '''
        result = self._values.get("ac_id")
        assert result is not None, "Required property 'ac_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of an Authentication context.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your Azure identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupIncludeAuthContext(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupIncludeAuthContextOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeAuthContextOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e8374cf44b09ce7fd7f4135630f7e14a6ebed5c745106da59755346ebe927de8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="acIdInput")
    def ac_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "acIdInput"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderIdInput")
    def identity_provider_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityProviderIdInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="acId")
    def ac_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "acId"))

    @ac_id.setter
    def ac_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25a12c7ca1e888b3e3f242e996883fb13941ff7bc3647651a8a0ad22b270d6df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "acId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15a3ee534bd67dc800ab29d75dc98cf46972d359ff7700ef770e7bc907e63323)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2680a61bef4cceda940e3571b97fcbfca1a592783d6ad2c500533811674822a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeAuthContext]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeAuthContext]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeAuthContext]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e45ec04b55ddf6f910bc2edd3bd63eb6ee4fb16b17ccdb28c585cd33366c589d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeAuthMethod",
    jsii_struct_bases=[],
    name_mapping={"auth_method": "authMethod"},
)
class ZeroTrustAccessGroupIncludeAuthMethod:
    def __init__(self, *, auth_method: builtins.str) -> None:
        '''
        :param auth_method: The type of authentication method https://datatracker.ietf.org/doc/html/rfc8176#section-2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#auth_method ZeroTrustAccessGroup#auth_method}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05b06280d4e60396c5cd1f12d90f39f6016d9042ed597988b75cc93b95e87d61)
            check_type(argname="argument auth_method", value=auth_method, expected_type=type_hints["auth_method"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "auth_method": auth_method,
        }

    @builtins.property
    def auth_method(self) -> builtins.str:
        '''The type of authentication method https://datatracker.ietf.org/doc/html/rfc8176#section-2.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#auth_method ZeroTrustAccessGroup#auth_method}
        '''
        result = self._values.get("auth_method")
        assert result is not None, "Required property 'auth_method' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupIncludeAuthMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupIncludeAuthMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeAuthMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f16e56d90abe72c8910575375bdd6a2becfb2d7ee888769ae9802831123fd200)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="authMethodInput")
    def auth_method_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authMethodInput"))

    @builtins.property
    @jsii.member(jsii_name="authMethod")
    def auth_method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authMethod"))

    @auth_method.setter
    def auth_method(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e1352c6b5078492f55b0550adbfd38cbfd197367574f9bc0cb63d40ec5fbd1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authMethod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeAuthMethod]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeAuthMethod]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeAuthMethod]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3d105767e2db760ff738b0b0ce6c96280549dfab99de6258d770abb7863ee72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeAzureAd",
    jsii_struct_bases=[],
    name_mapping={"id": "id", "identity_provider_id": "identityProviderId"},
)
class ZeroTrustAccessGroupIncludeAzureAd:
    def __init__(self, *, id: builtins.str, identity_provider_id: builtins.str) -> None:
        '''
        :param id: The ID of an Azure group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider_id: The ID of your Azure identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__faac070969b3ac9df090a5f35e87885d96958c9d80031279a62169a954d1581a)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
            "identity_provider_id": identity_provider_id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of an Azure group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your Azure identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupIncludeAzureAd(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupIncludeAzureAdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeAzureAdOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1958cc0fac9c777f0356cebecb641bd5e94e5687631e2b8fd4bc381173cb674c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="identityProviderIdInput")
    def identity_provider_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityProviderIdInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__2e01ca993424c0f79b04f67df0d929fffe6deda6e1ac0c3bb40a9176064d9c5c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbb981441556d1ecfd4c93101d96918e6d53dc238ea04d7753db9d6cf69b37d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeAzureAd]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeAzureAd]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeAzureAd]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30bfcbbc0172b06f8520f5b6e5347b3b8e0f36874152bfef79babcff192a919b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeCertificate",
    jsii_struct_bases=[],
    name_mapping={},
)
class ZeroTrustAccessGroupIncludeCertificate:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupIncludeCertificate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupIncludeCertificateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeCertificateOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c7c1285f6a4cb0168b5b1e2206592d58ce0a45ed4d6f4b91caeeb0ff32164f69)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeCertificate]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeCertificate]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeCertificate]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d4558cf6fbd86eeb52f2eaccaacc5e13e94221aec772a487e9e5b95a19b44f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeCommonName",
    jsii_struct_bases=[],
    name_mapping={"common_name": "commonName"},
)
class ZeroTrustAccessGroupIncludeCommonName:
    def __init__(self, *, common_name: builtins.str) -> None:
        '''
        :param common_name: The common name to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#common_name ZeroTrustAccessGroup#common_name}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40d6f36e39ffac36f46c87ee9f349db01253be99470fdb06c70a8478bcf77867)
            check_type(argname="argument common_name", value=common_name, expected_type=type_hints["common_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "common_name": common_name,
        }

    @builtins.property
    def common_name(self) -> builtins.str:
        '''The common name to match.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#common_name ZeroTrustAccessGroup#common_name}
        '''
        result = self._values.get("common_name")
        assert result is not None, "Required property 'common_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupIncludeCommonName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupIncludeCommonNameOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeCommonNameOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ce644bd393c544bf554f028496d7e88b5c3a536a12d6bf310a13066cce899934)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="commonNameInput")
    def common_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commonNameInput"))

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commonName"))

    @common_name.setter
    def common_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f1a4a6219744d794b4a3de4b7075a9c84dd7962724b1256f6074ece1719a322)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "commonName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeCommonName]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeCommonName]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeCommonName]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54e88ce53351da3a6f19046b2335d71154d4bf98ff69d9862af58f4aa8249ecd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeDevicePosture",
    jsii_struct_bases=[],
    name_mapping={"integration_uid": "integrationUid"},
)
class ZeroTrustAccessGroupIncludeDevicePosture:
    def __init__(self, *, integration_uid: builtins.str) -> None:
        '''
        :param integration_uid: The ID of a device posture integration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#integration_uid ZeroTrustAccessGroup#integration_uid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d41dfee38e98135d2c333195911dc9155235d8919fef46e447a61abb97a1d86)
            check_type(argname="argument integration_uid", value=integration_uid, expected_type=type_hints["integration_uid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "integration_uid": integration_uid,
        }

    @builtins.property
    def integration_uid(self) -> builtins.str:
        '''The ID of a device posture integration.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#integration_uid ZeroTrustAccessGroup#integration_uid}
        '''
        result = self._values.get("integration_uid")
        assert result is not None, "Required property 'integration_uid' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupIncludeDevicePosture(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupIncludeDevicePostureOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeDevicePostureOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c9aaef6f157ed3e7302bc69792ee9f0612e05338082ce02219effb81121081aa)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="integrationUidInput")
    def integration_uid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "integrationUidInput"))

    @builtins.property
    @jsii.member(jsii_name="integrationUid")
    def integration_uid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "integrationUid"))

    @integration_uid.setter
    def integration_uid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c866faa3a7ccd3723072cb6f1f5ee860db98014652a0236de4a8c6a414d056d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "integrationUid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeDevicePosture]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeDevicePosture]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeDevicePosture]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdfa92c16139da3fe257989526dbf1480b09af7259793d4c3703c66994f76c0f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeEmail",
    jsii_struct_bases=[],
    name_mapping={"email": "email"},
)
class ZeroTrustAccessGroupIncludeEmail:
    def __init__(self, *, email: builtins.str) -> None:
        '''
        :param email: The email of the user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email ZeroTrustAccessGroup#email}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af5458947becd541b6f9f485fc68850562ee30a89388c1898e717c03b151a3e3)
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "email": email,
        }

    @builtins.property
    def email(self) -> builtins.str:
        '''The email of the user.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email ZeroTrustAccessGroup#email}
        '''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupIncludeEmail(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeEmailDomain",
    jsii_struct_bases=[],
    name_mapping={"domain": "domain"},
)
class ZeroTrustAccessGroupIncludeEmailDomain:
    def __init__(self, *, domain: builtins.str) -> None:
        '''
        :param domain: The email domain to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#domain ZeroTrustAccessGroup#domain}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae45d0202f5514c60c9985066e3acb4426ab8f49604ef1914b2b7271ffef6503)
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain": domain,
        }

    @builtins.property
    def domain(self) -> builtins.str:
        '''The email domain to match.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#domain ZeroTrustAccessGroup#domain}
        '''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupIncludeEmailDomain(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupIncludeEmailDomainOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeEmailDomainOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bea89ec867b02e400c5574bc080f98c64e6188fca1531fbac425d53a3d505893)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="domainInput")
    def domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainInput"))

    @builtins.property
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d95f344b36336d3ecbb34ea55eceadbe9019b7f60df6b590c36b345e8a186f57)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "domain", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeEmailDomain]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeEmailDomain]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeEmailDomain]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a784db61f3ce87530ad71b931c8789abedc897486dee7a9c318a3275c43650b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeEmailListStruct",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class ZeroTrustAccessGroupIncludeEmailListStruct:
    def __init__(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created email list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3d82cb88450e7e4d9d7bfb776ae08d5cc1d38f66b77feefff6ceb45379521ca)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of a previously created email list.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupIncludeEmailListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupIncludeEmailListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeEmailListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f5fd1c8494565ab0517ee7b0bdf92e4e273838ceb0851cb46218bf8e1003c82d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

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
            type_hints = typing.get_type_hints(_typecheckingstub__d7ce13d22b128abb827fd8f529fdfaaaed04fd994017e852c6d5c9fdb85a459e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeEmailListStruct]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeEmailListStruct]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeEmailListStruct]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5737e9e9bd7084a9017725427ae92b482d7d3e4df2ffaa9a0a6a6c4d8470edd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustAccessGroupIncludeEmailOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeEmailOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__876664c5a0211870835bfd3b4662efe0c7ef2b82d9473ee46f5b05e4bf562203)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="emailInput")
    def email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailInput"))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "email"))

    @email.setter
    def email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97518f467578b2350b12d54b9017b6f17da9815868a36f6380f58569e2dbbffc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "email", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeEmail]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeEmail]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeEmail]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e89017e8963228a0836d43517b26090ee106dcf0b670d3dcb67b8b269c0db0d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeEveryone",
    jsii_struct_bases=[],
    name_mapping={},
)
class ZeroTrustAccessGroupIncludeEveryone:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupIncludeEveryone(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupIncludeEveryoneOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeEveryoneOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7d4908222fb5b2b9a5c44fe04c75ae9460b1afa269b71cda04fa872bb63383cf)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeEveryone]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeEveryone]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeEveryone]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f39a05aeb7f8a2c41b287c03783d346ab1cc8eb009692e6b2b96e487372a1ca9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeExternalEvaluation",
    jsii_struct_bases=[],
    name_mapping={"evaluate_url": "evaluateUrl", "keys_url": "keysUrl"},
)
class ZeroTrustAccessGroupIncludeExternalEvaluation:
    def __init__(self, *, evaluate_url: builtins.str, keys_url: builtins.str) -> None:
        '''
        :param evaluate_url: The API endpoint containing your business logic. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#evaluate_url ZeroTrustAccessGroup#evaluate_url}
        :param keys_url: The API endpoint containing the key that Access uses to verify that the response came from your API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#keys_url ZeroTrustAccessGroup#keys_url}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96f838d128454a4265ac355d5b21627304aa32654907b668f5ceb404c61220d9)
            check_type(argname="argument evaluate_url", value=evaluate_url, expected_type=type_hints["evaluate_url"])
            check_type(argname="argument keys_url", value=keys_url, expected_type=type_hints["keys_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "evaluate_url": evaluate_url,
            "keys_url": keys_url,
        }

    @builtins.property
    def evaluate_url(self) -> builtins.str:
        '''The API endpoint containing your business logic.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#evaluate_url ZeroTrustAccessGroup#evaluate_url}
        '''
        result = self._values.get("evaluate_url")
        assert result is not None, "Required property 'evaluate_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def keys_url(self) -> builtins.str:
        '''The API endpoint containing the key that Access uses to verify that the response came from your API.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#keys_url ZeroTrustAccessGroup#keys_url}
        '''
        result = self._values.get("keys_url")
        assert result is not None, "Required property 'keys_url' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupIncludeExternalEvaluation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupIncludeExternalEvaluationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeExternalEvaluationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__34a76e3a903d77dc11169d21d331439c35bc0ac1325355f45fb0d81fdea091e9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="evaluateUrlInput")
    def evaluate_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "evaluateUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="keysUrlInput")
    def keys_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keysUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="evaluateUrl")
    def evaluate_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "evaluateUrl"))

    @evaluate_url.setter
    def evaluate_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75097247409fda28a339084d6f31c0c738ea0b9de6f930db43f40ffd1e0ced51)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "evaluateUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keysUrl")
    def keys_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keysUrl"))

    @keys_url.setter
    def keys_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c524c7e6210a5ca6ea75119a289cb6469f7487e7806597708555bdb046cecd6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keysUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeExternalEvaluation]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeExternalEvaluation]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeExternalEvaluation]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cae5c44410b8c107f4018ae82f641a21260b1c619a0cba86d65ede38ac71113)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeGeo",
    jsii_struct_bases=[],
    name_mapping={"country_code": "countryCode"},
)
class ZeroTrustAccessGroupIncludeGeo:
    def __init__(self, *, country_code: builtins.str) -> None:
        '''
        :param country_code: The country code that should be matched. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#country_code ZeroTrustAccessGroup#country_code}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7b8e60e1bfb1f8fadd0d819a2893ac4d9facf882f1677893da0a6968177247e)
            check_type(argname="argument country_code", value=country_code, expected_type=type_hints["country_code"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "country_code": country_code,
        }

    @builtins.property
    def country_code(self) -> builtins.str:
        '''The country code that should be matched.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#country_code ZeroTrustAccessGroup#country_code}
        '''
        result = self._values.get("country_code")
        assert result is not None, "Required property 'country_code' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupIncludeGeo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupIncludeGeoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeGeoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__be6c4cacc9755576137c09e2dd5394848e4701c224ede71abd5bfe3b13ed4cdd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="countryCodeInput")
    def country_code_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "countryCodeInput"))

    @builtins.property
    @jsii.member(jsii_name="countryCode")
    def country_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "countryCode"))

    @country_code.setter
    def country_code(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__089270c0e6b3189f31dfb0512eb54ea2e454c2b9f0b852a6fc8d5354ba0be915)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "countryCode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeGeo]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeGeo]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeGeo]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe7b2638beb8a716f4adf5ac186f0f0ee67ba82a2879cdd4aa2ff5fe39f43812)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeGithubOrganization",
    jsii_struct_bases=[],
    name_mapping={
        "identity_provider_id": "identityProviderId",
        "name": "name",
        "team": "team",
    },
)
class ZeroTrustAccessGroupIncludeGithubOrganization:
    def __init__(
        self,
        *,
        identity_provider_id: builtins.str,
        name: builtins.str,
        team: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param identity_provider_id: The ID of your Github identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        :param name: The name of the organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#name ZeroTrustAccessGroup#name}
        :param team: The name of the team. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#team ZeroTrustAccessGroup#team}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9234d0c4bdcf3462a10bdd10c33b90fc124f3752bbe67d2caa45be7379b03c1)
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument team", value=team, expected_type=type_hints["team"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "identity_provider_id": identity_provider_id,
            "name": name,
        }
        if team is not None:
            self._values["team"] = team

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your Github identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the organization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#name ZeroTrustAccessGroup#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def team(self) -> typing.Optional[builtins.str]:
        '''The name of the team.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#team ZeroTrustAccessGroup#team}
        '''
        result = self._values.get("team")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupIncludeGithubOrganization(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupIncludeGithubOrganizationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeGithubOrganizationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__81d52d49711c02bde31d8e1b0ea30d379604d7a6b2d0571cb8dbf065eb4bf14f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetTeam")
    def reset_team(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTeam", []))

    @builtins.property
    @jsii.member(jsii_name="identityProviderIdInput")
    def identity_provider_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityProviderIdInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="teamInput")
    def team_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "teamInput"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b838a7d287e9b73b5f18f32f841d3c900e6a4501b455682fda0ca8fe4532ce9a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7be89d6eb799b745dada016ac3c9275e57d146809f206729b360d73fa8830207)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="team")
    def team(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "team"))

    @team.setter
    def team(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8be3a76dd9eb7409a30396468486a8c09181bc903144f93d73cf59736c55a168)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "team", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeGithubOrganization]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeGithubOrganization]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeGithubOrganization]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ba16bf425daffb436642a36d3ba675dbc06ba9c1422a94991baeb9559b3ff8a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeGroup",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class ZeroTrustAccessGroupIncludeGroup:
    def __init__(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created Access group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34f067d98af1a8c45eccb4cf41e3521166bba527a1ce6da5776453bb2c5ea29c)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of a previously created Access group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupIncludeGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupIncludeGroupOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeGroupOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__307fade54f0f8b46b9cf000aad247f24219edefd15cfe3cbbdd3cc3ab825694f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

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
            type_hints = typing.get_type_hints(_typecheckingstub__56f979661ef90ac293e3ec01ac949208fa8920cf9da54dfc424780a12ff9fbd2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeGroup]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeGroup]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeGroup]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8403514ce78f263a5ecf193cd1707d872e94d0c50e2291d5348f04495ed0ee64)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeGsuite",
    jsii_struct_bases=[],
    name_mapping={"email": "email", "identity_provider_id": "identityProviderId"},
)
class ZeroTrustAccessGroupIncludeGsuite:
    def __init__(
        self,
        *,
        email: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param email: The email of the Google Workspace group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email ZeroTrustAccessGroup#email}
        :param identity_provider_id: The ID of your Google Workspace identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5284f6e6b03b6171353c31a15187f3b27b00a1d6eaf7172b60c9e0a74fbf853c)
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "email": email,
            "identity_provider_id": identity_provider_id,
        }

    @builtins.property
    def email(self) -> builtins.str:
        '''The email of the Google Workspace group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email ZeroTrustAccessGroup#email}
        '''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your Google Workspace identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupIncludeGsuite(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupIncludeGsuiteOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeGsuiteOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8f8f302d0176e7592311bbde6d3c893cf5c5fa68a0f15eb61e07374bf36757e2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="emailInput")
    def email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailInput"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderIdInput")
    def identity_provider_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityProviderIdInput"))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "email"))

    @email.setter
    def email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbb631921b8f6e3b39a52c03cbe1e72c0ecc1f2b292cf9f4f8ee4d19a5590002)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "email", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50ed4624ab5d0be0e45357a05460a1385d8b9e566b81342a79a4b2eb4507c8d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeGsuite]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeGsuite]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeGsuite]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5630f14a647d65560b027205944d59ec923b2b06906c7ac3a90dbb11e7a17af7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeIp",
    jsii_struct_bases=[],
    name_mapping={"ip": "ip"},
)
class ZeroTrustAccessGroupIncludeIp:
    def __init__(self, *, ip: builtins.str) -> None:
        '''
        :param ip: An IPv4 or IPv6 CIDR block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ip ZeroTrustAccessGroup#ip}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f77dc0b84d7d405ea91e15bfa65d3d2bc18afeb68086a99147cad96e29b26cb)
            check_type(argname="argument ip", value=ip, expected_type=type_hints["ip"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "ip": ip,
        }

    @builtins.property
    def ip(self) -> builtins.str:
        '''An IPv4 or IPv6 CIDR block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ip ZeroTrustAccessGroup#ip}
        '''
        result = self._values.get("ip")
        assert result is not None, "Required property 'ip' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupIncludeIp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeIpListStruct",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class ZeroTrustAccessGroupIncludeIpListStruct:
    def __init__(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created IP list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3bb4f43282431180c89e6f844f11e55e7633a27240e1b083e5c10d501a69e1f)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of a previously created IP list.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupIncludeIpListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupIncludeIpListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeIpListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6f899f721b76c07c50a6f2dd04113f559a5de2e452f8b44dbb683f943dbcba1e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

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
            type_hints = typing.get_type_hints(_typecheckingstub__a565002e1574fe688145f9e4f8d983f19a10a9c69a92343cd315e2180c6218e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeIpListStruct]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeIpListStruct]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeIpListStruct]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ec57c79ad3d986058cfdff9e622be044e990daa138651662b5c90025cdcdb11)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustAccessGroupIncludeIpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeIpOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8e79fd293f85ddb0190314748a460d14e2b7f7b7a6bf77bc8f46216d50508f62)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="ipInput")
    def ip_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipInput"))

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ip"))

    @ip.setter
    def ip(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5bc5e627508fbd361035a2e2bae724103ee3c08ec8c8f5ea1c9c7f604b6d6010)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ip", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeIp]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeIp]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeIp]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cde4bd7bbb505518ab24fdad83386a0544905141f0c7851281fe86eeecbcdb8b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeLinkedAppToken",
    jsii_struct_bases=[],
    name_mapping={"app_uid": "appUid"},
)
class ZeroTrustAccessGroupIncludeLinkedAppToken:
    def __init__(self, *, app_uid: builtins.str) -> None:
        '''
        :param app_uid: The ID of an Access OIDC SaaS application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#app_uid ZeroTrustAccessGroup#app_uid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0edf8a08d2bb0cf67bbd3937cefee7b7b1c08d3b43b1dc0edf0474285f9ab7d)
            check_type(argname="argument app_uid", value=app_uid, expected_type=type_hints["app_uid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "app_uid": app_uid,
        }

    @builtins.property
    def app_uid(self) -> builtins.str:
        '''The ID of an Access OIDC SaaS application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#app_uid ZeroTrustAccessGroup#app_uid}
        '''
        result = self._values.get("app_uid")
        assert result is not None, "Required property 'app_uid' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupIncludeLinkedAppToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupIncludeLinkedAppTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeLinkedAppTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__290d57f7ab344e19e01161df311a20b584380e652247a1c9d069f32fa4c04fb9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="appUidInput")
    def app_uid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "appUidInput"))

    @builtins.property
    @jsii.member(jsii_name="appUid")
    def app_uid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appUid"))

    @app_uid.setter
    def app_uid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5f0e0fc866a565c2069dd60216edaa607ee106f24fb6c74b2e59cd8270e1ad9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "appUid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeLinkedAppToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeLinkedAppToken]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeLinkedAppToken]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__261f6e6ad0d67f45776e2d6037b32d5c63970a2c5c511cb2366cf19d9b5bd598)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustAccessGroupIncludeList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__41ed12438e0c29548e6982fd8229954fa3ad800f05f56fb78cadbdad2e01939f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ZeroTrustAccessGroupIncludeOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78fd7b2161debcdf010f64c9adbc2b6e77f969b6a06d73a37e5002d3bff6835f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ZeroTrustAccessGroupIncludeOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f73f9ad7c0f9514cd35ee8c94b9725147b22ba6176c0e56d216eaf66f6854ce0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3b430e79b3d9fb220270e63e44a0417609e532eb4ea03f60bce0736f6bea32b2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4cf2d1837419f8e2d302dcc40ce4b7ce158087ec9e3cba035dd0dda37b933f8b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessGroupInclude]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessGroupInclude]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessGroupInclude]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db8495c2c7688b8b50a2fdda66d8644ba6cfb12aafa4382e9cb7631b015a4d8d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeLoginMethod",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class ZeroTrustAccessGroupIncludeLoginMethod:
    def __init__(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of an identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46d8bd705f76cb263aa91f4d3402367c67a346e4623a1ea1fcea0ec7ee1f6497)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of an identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupIncludeLoginMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupIncludeLoginMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeLoginMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6fa78c3154c4e1451d75f3b2c8cf266c2f97e03eab69031bff4501fb3a8c7d0c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

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
            type_hints = typing.get_type_hints(_typecheckingstub__ed8bb869a875b338e4acd176747b34c298e29d46b1dbeaf7d4b06a4403f7b4ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeLoginMethod]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeLoginMethod]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeLoginMethod]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3639c748d863e8075971ad52f610307ad6d2116b088fa17b328fe736d5ad8ce1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeOidc",
    jsii_struct_bases=[],
    name_mapping={
        "claim_name": "claimName",
        "claim_value": "claimValue",
        "identity_provider_id": "identityProviderId",
    },
)
class ZeroTrustAccessGroupIncludeOidc:
    def __init__(
        self,
        *,
        claim_name: builtins.str,
        claim_value: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param claim_name: The name of the OIDC claim. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#claim_name ZeroTrustAccessGroup#claim_name}
        :param claim_value: The OIDC claim value to look for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#claim_value ZeroTrustAccessGroup#claim_value}
        :param identity_provider_id: The ID of your OIDC identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b3a24487e0933a51cd7e53ae03d57b4ff30b9afdad9c1486088b5695d097599)
            check_type(argname="argument claim_name", value=claim_name, expected_type=type_hints["claim_name"])
            check_type(argname="argument claim_value", value=claim_value, expected_type=type_hints["claim_value"])
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "claim_name": claim_name,
            "claim_value": claim_value,
            "identity_provider_id": identity_provider_id,
        }

    @builtins.property
    def claim_name(self) -> builtins.str:
        '''The name of the OIDC claim.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#claim_name ZeroTrustAccessGroup#claim_name}
        '''
        result = self._values.get("claim_name")
        assert result is not None, "Required property 'claim_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def claim_value(self) -> builtins.str:
        '''The OIDC claim value to look for.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#claim_value ZeroTrustAccessGroup#claim_value}
        '''
        result = self._values.get("claim_value")
        assert result is not None, "Required property 'claim_value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your OIDC identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupIncludeOidc(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupIncludeOidcOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeOidcOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9741cd18fdb4a1cbf256715b59a7a76a9ce27a3e663e43cd62d61e154c77615f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="claimNameInput")
    def claim_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "claimNameInput"))

    @builtins.property
    @jsii.member(jsii_name="claimValueInput")
    def claim_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "claimValueInput"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderIdInput")
    def identity_provider_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityProviderIdInput"))

    @builtins.property
    @jsii.member(jsii_name="claimName")
    def claim_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "claimName"))

    @claim_name.setter
    def claim_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab58da6b80e2d776f20a074572832fcc1eedaa03c4364c02e79a4b188d2ec92a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "claimName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="claimValue")
    def claim_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "claimValue"))

    @claim_value.setter
    def claim_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8dcdef9c86847ce69e376954cf3ab6434d4816dc6ff1f89e3dcac06fc2085fb2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "claimValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b88adaeb440e92d8e1587d4b6bd6fb32e59734e47fee618187c83531b6415c8e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeOidc]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeOidc]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeOidc]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82f328f8d19ac7d2dec4c49c428e06a0bd56f6f355dbbe6056f46da1713439f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeOkta",
    jsii_struct_bases=[],
    name_mapping={"identity_provider_id": "identityProviderId", "name": "name"},
)
class ZeroTrustAccessGroupIncludeOkta:
    def __init__(
        self,
        *,
        identity_provider_id: builtins.str,
        name: builtins.str,
    ) -> None:
        '''
        :param identity_provider_id: The ID of your Okta identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        :param name: The name of the Okta group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#name ZeroTrustAccessGroup#name}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c40ba7154f26c03d5c4da5e9154bb876230c1ac60353838b131a965a9f3c5ab6)
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "identity_provider_id": identity_provider_id,
            "name": name,
        }

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your Okta identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the Okta group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#name ZeroTrustAccessGroup#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupIncludeOkta(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupIncludeOktaOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeOktaOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1d5c9acf6c84cb793f250d1d72abf2e89401620cf8e2cb35ddd58957c4104df9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="identityProviderIdInput")
    def identity_provider_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityProviderIdInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42fae6ff38df6963de22281303891f6a789d866730d47a59fcd071a18499f777)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__729110212c0344b1755aebf9a8c86dd2779963e9e9c7a5d67b68ad23ba956d52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeOkta]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeOkta]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeOkta]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__717f2234936f6a8acfa87ff556fe0a86d55754ade9aebdcb0f432984a74498e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustAccessGroupIncludeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5f03d0c41e56e160e26fc2ffd4ebe6696155cc65caa89556330810157a7f4d1f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putAnyValidServiceToken")
    def put_any_valid_service_token(self) -> None:
        value = ZeroTrustAccessGroupIncludeAnyValidServiceToken()

        return typing.cast(None, jsii.invoke(self, "putAnyValidServiceToken", [value]))

    @jsii.member(jsii_name="putAuthContext")
    def put_auth_context(
        self,
        *,
        ac_id: builtins.str,
        id: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param ac_id: The ACID of an Authentication context. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ac_id ZeroTrustAccessGroup#ac_id}
        :param id: The ID of an Authentication context. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider_id: The ID of your Azure identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        value = ZeroTrustAccessGroupIncludeAuthContext(
            ac_id=ac_id, id=id, identity_provider_id=identity_provider_id
        )

        return typing.cast(None, jsii.invoke(self, "putAuthContext", [value]))

    @jsii.member(jsii_name="putAuthMethod")
    def put_auth_method(self, *, auth_method: builtins.str) -> None:
        '''
        :param auth_method: The type of authentication method https://datatracker.ietf.org/doc/html/rfc8176#section-2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#auth_method ZeroTrustAccessGroup#auth_method}
        '''
        value = ZeroTrustAccessGroupIncludeAuthMethod(auth_method=auth_method)

        return typing.cast(None, jsii.invoke(self, "putAuthMethod", [value]))

    @jsii.member(jsii_name="putAzureAd")
    def put_azure_ad(
        self,
        *,
        id: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param id: The ID of an Azure group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider_id: The ID of your Azure identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        value = ZeroTrustAccessGroupIncludeAzureAd(
            id=id, identity_provider_id=identity_provider_id
        )

        return typing.cast(None, jsii.invoke(self, "putAzureAd", [value]))

    @jsii.member(jsii_name="putCertificate")
    def put_certificate(self) -> None:
        value = ZeroTrustAccessGroupIncludeCertificate()

        return typing.cast(None, jsii.invoke(self, "putCertificate", [value]))

    @jsii.member(jsii_name="putCommonName")
    def put_common_name(self, *, common_name: builtins.str) -> None:
        '''
        :param common_name: The common name to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#common_name ZeroTrustAccessGroup#common_name}
        '''
        value = ZeroTrustAccessGroupIncludeCommonName(common_name=common_name)

        return typing.cast(None, jsii.invoke(self, "putCommonName", [value]))

    @jsii.member(jsii_name="putDevicePosture")
    def put_device_posture(self, *, integration_uid: builtins.str) -> None:
        '''
        :param integration_uid: The ID of a device posture integration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#integration_uid ZeroTrustAccessGroup#integration_uid}
        '''
        value = ZeroTrustAccessGroupIncludeDevicePosture(
            integration_uid=integration_uid
        )

        return typing.cast(None, jsii.invoke(self, "putDevicePosture", [value]))

    @jsii.member(jsii_name="putEmail")
    def put_email(self, *, email: builtins.str) -> None:
        '''
        :param email: The email of the user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email ZeroTrustAccessGroup#email}
        '''
        value = ZeroTrustAccessGroupIncludeEmail(email=email)

        return typing.cast(None, jsii.invoke(self, "putEmail", [value]))

    @jsii.member(jsii_name="putEmailDomain")
    def put_email_domain(self, *, domain: builtins.str) -> None:
        '''
        :param domain: The email domain to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#domain ZeroTrustAccessGroup#domain}
        '''
        value = ZeroTrustAccessGroupIncludeEmailDomain(domain=domain)

        return typing.cast(None, jsii.invoke(self, "putEmailDomain", [value]))

    @jsii.member(jsii_name="putEmailList")
    def put_email_list(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created email list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        value = ZeroTrustAccessGroupIncludeEmailListStruct(id=id)

        return typing.cast(None, jsii.invoke(self, "putEmailList", [value]))

    @jsii.member(jsii_name="putEveryone")
    def put_everyone(self) -> None:
        value = ZeroTrustAccessGroupIncludeEveryone()

        return typing.cast(None, jsii.invoke(self, "putEveryone", [value]))

    @jsii.member(jsii_name="putExternalEvaluation")
    def put_external_evaluation(
        self,
        *,
        evaluate_url: builtins.str,
        keys_url: builtins.str,
    ) -> None:
        '''
        :param evaluate_url: The API endpoint containing your business logic. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#evaluate_url ZeroTrustAccessGroup#evaluate_url}
        :param keys_url: The API endpoint containing the key that Access uses to verify that the response came from your API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#keys_url ZeroTrustAccessGroup#keys_url}
        '''
        value = ZeroTrustAccessGroupIncludeExternalEvaluation(
            evaluate_url=evaluate_url, keys_url=keys_url
        )

        return typing.cast(None, jsii.invoke(self, "putExternalEvaluation", [value]))

    @jsii.member(jsii_name="putGeo")
    def put_geo(self, *, country_code: builtins.str) -> None:
        '''
        :param country_code: The country code that should be matched. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#country_code ZeroTrustAccessGroup#country_code}
        '''
        value = ZeroTrustAccessGroupIncludeGeo(country_code=country_code)

        return typing.cast(None, jsii.invoke(self, "putGeo", [value]))

    @jsii.member(jsii_name="putGithubOrganization")
    def put_github_organization(
        self,
        *,
        identity_provider_id: builtins.str,
        name: builtins.str,
        team: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param identity_provider_id: The ID of your Github identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        :param name: The name of the organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#name ZeroTrustAccessGroup#name}
        :param team: The name of the team. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#team ZeroTrustAccessGroup#team}
        '''
        value = ZeroTrustAccessGroupIncludeGithubOrganization(
            identity_provider_id=identity_provider_id, name=name, team=team
        )

        return typing.cast(None, jsii.invoke(self, "putGithubOrganization", [value]))

    @jsii.member(jsii_name="putGroup")
    def put_group(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created Access group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        value = ZeroTrustAccessGroupIncludeGroup(id=id)

        return typing.cast(None, jsii.invoke(self, "putGroup", [value]))

    @jsii.member(jsii_name="putGsuite")
    def put_gsuite(
        self,
        *,
        email: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param email: The email of the Google Workspace group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email ZeroTrustAccessGroup#email}
        :param identity_provider_id: The ID of your Google Workspace identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        value = ZeroTrustAccessGroupIncludeGsuite(
            email=email, identity_provider_id=identity_provider_id
        )

        return typing.cast(None, jsii.invoke(self, "putGsuite", [value]))

    @jsii.member(jsii_name="putIp")
    def put_ip(self, *, ip: builtins.str) -> None:
        '''
        :param ip: An IPv4 or IPv6 CIDR block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ip ZeroTrustAccessGroup#ip}
        '''
        value = ZeroTrustAccessGroupIncludeIp(ip=ip)

        return typing.cast(None, jsii.invoke(self, "putIp", [value]))

    @jsii.member(jsii_name="putIpList")
    def put_ip_list(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created IP list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        value = ZeroTrustAccessGroupIncludeIpListStruct(id=id)

        return typing.cast(None, jsii.invoke(self, "putIpList", [value]))

    @jsii.member(jsii_name="putLinkedAppToken")
    def put_linked_app_token(self, *, app_uid: builtins.str) -> None:
        '''
        :param app_uid: The ID of an Access OIDC SaaS application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#app_uid ZeroTrustAccessGroup#app_uid}
        '''
        value = ZeroTrustAccessGroupIncludeLinkedAppToken(app_uid=app_uid)

        return typing.cast(None, jsii.invoke(self, "putLinkedAppToken", [value]))

    @jsii.member(jsii_name="putLoginMethod")
    def put_login_method(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of an identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        value = ZeroTrustAccessGroupIncludeLoginMethod(id=id)

        return typing.cast(None, jsii.invoke(self, "putLoginMethod", [value]))

    @jsii.member(jsii_name="putOidc")
    def put_oidc(
        self,
        *,
        claim_name: builtins.str,
        claim_value: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param claim_name: The name of the OIDC claim. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#claim_name ZeroTrustAccessGroup#claim_name}
        :param claim_value: The OIDC claim value to look for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#claim_value ZeroTrustAccessGroup#claim_value}
        :param identity_provider_id: The ID of your OIDC identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        value = ZeroTrustAccessGroupIncludeOidc(
            claim_name=claim_name,
            claim_value=claim_value,
            identity_provider_id=identity_provider_id,
        )

        return typing.cast(None, jsii.invoke(self, "putOidc", [value]))

    @jsii.member(jsii_name="putOkta")
    def put_okta(
        self,
        *,
        identity_provider_id: builtins.str,
        name: builtins.str,
    ) -> None:
        '''
        :param identity_provider_id: The ID of your Okta identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        :param name: The name of the Okta group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#name ZeroTrustAccessGroup#name}
        '''
        value = ZeroTrustAccessGroupIncludeOkta(
            identity_provider_id=identity_provider_id, name=name
        )

        return typing.cast(None, jsii.invoke(self, "putOkta", [value]))

    @jsii.member(jsii_name="putSaml")
    def put_saml(
        self,
        *,
        attribute_name: builtins.str,
        attribute_value: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param attribute_name: The name of the SAML attribute. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#attribute_name ZeroTrustAccessGroup#attribute_name}
        :param attribute_value: The SAML attribute value to look for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#attribute_value ZeroTrustAccessGroup#attribute_value}
        :param identity_provider_id: The ID of your SAML identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        value = ZeroTrustAccessGroupIncludeSaml(
            attribute_name=attribute_name,
            attribute_value=attribute_value,
            identity_provider_id=identity_provider_id,
        )

        return typing.cast(None, jsii.invoke(self, "putSaml", [value]))

    @jsii.member(jsii_name="putServiceToken")
    def put_service_token(self, *, token_id: builtins.str) -> None:
        '''
        :param token_id: The ID of a Service Token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#token_id ZeroTrustAccessGroup#token_id}
        '''
        value = ZeroTrustAccessGroupIncludeServiceToken(token_id=token_id)

        return typing.cast(None, jsii.invoke(self, "putServiceToken", [value]))

    @jsii.member(jsii_name="resetAnyValidServiceToken")
    def reset_any_valid_service_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAnyValidServiceToken", []))

    @jsii.member(jsii_name="resetAuthContext")
    def reset_auth_context(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthContext", []))

    @jsii.member(jsii_name="resetAuthMethod")
    def reset_auth_method(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthMethod", []))

    @jsii.member(jsii_name="resetAzureAd")
    def reset_azure_ad(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureAd", []))

    @jsii.member(jsii_name="resetCertificate")
    def reset_certificate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificate", []))

    @jsii.member(jsii_name="resetCommonName")
    def reset_common_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCommonName", []))

    @jsii.member(jsii_name="resetDevicePosture")
    def reset_device_posture(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDevicePosture", []))

    @jsii.member(jsii_name="resetEmail")
    def reset_email(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmail", []))

    @jsii.member(jsii_name="resetEmailDomain")
    def reset_email_domain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailDomain", []))

    @jsii.member(jsii_name="resetEmailList")
    def reset_email_list(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailList", []))

    @jsii.member(jsii_name="resetEveryone")
    def reset_everyone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEveryone", []))

    @jsii.member(jsii_name="resetExternalEvaluation")
    def reset_external_evaluation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExternalEvaluation", []))

    @jsii.member(jsii_name="resetGeo")
    def reset_geo(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGeo", []))

    @jsii.member(jsii_name="resetGithubOrganization")
    def reset_github_organization(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGithubOrganization", []))

    @jsii.member(jsii_name="resetGroup")
    def reset_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGroup", []))

    @jsii.member(jsii_name="resetGsuite")
    def reset_gsuite(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGsuite", []))

    @jsii.member(jsii_name="resetIp")
    def reset_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIp", []))

    @jsii.member(jsii_name="resetIpList")
    def reset_ip_list(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpList", []))

    @jsii.member(jsii_name="resetLinkedAppToken")
    def reset_linked_app_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLinkedAppToken", []))

    @jsii.member(jsii_name="resetLoginMethod")
    def reset_login_method(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLoginMethod", []))

    @jsii.member(jsii_name="resetOidc")
    def reset_oidc(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOidc", []))

    @jsii.member(jsii_name="resetOkta")
    def reset_okta(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOkta", []))

    @jsii.member(jsii_name="resetSaml")
    def reset_saml(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSaml", []))

    @jsii.member(jsii_name="resetServiceToken")
    def reset_service_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceToken", []))

    @builtins.property
    @jsii.member(jsii_name="anyValidServiceToken")
    def any_valid_service_token(
        self,
    ) -> ZeroTrustAccessGroupIncludeAnyValidServiceTokenOutputReference:
        return typing.cast(ZeroTrustAccessGroupIncludeAnyValidServiceTokenOutputReference, jsii.get(self, "anyValidServiceToken"))

    @builtins.property
    @jsii.member(jsii_name="authContext")
    def auth_context(self) -> ZeroTrustAccessGroupIncludeAuthContextOutputReference:
        return typing.cast(ZeroTrustAccessGroupIncludeAuthContextOutputReference, jsii.get(self, "authContext"))

    @builtins.property
    @jsii.member(jsii_name="authMethod")
    def auth_method(self) -> ZeroTrustAccessGroupIncludeAuthMethodOutputReference:
        return typing.cast(ZeroTrustAccessGroupIncludeAuthMethodOutputReference, jsii.get(self, "authMethod"))

    @builtins.property
    @jsii.member(jsii_name="azureAd")
    def azure_ad(self) -> ZeroTrustAccessGroupIncludeAzureAdOutputReference:
        return typing.cast(ZeroTrustAccessGroupIncludeAzureAdOutputReference, jsii.get(self, "azureAd"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> ZeroTrustAccessGroupIncludeCertificateOutputReference:
        return typing.cast(ZeroTrustAccessGroupIncludeCertificateOutputReference, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(self) -> ZeroTrustAccessGroupIncludeCommonNameOutputReference:
        return typing.cast(ZeroTrustAccessGroupIncludeCommonNameOutputReference, jsii.get(self, "commonName"))

    @builtins.property
    @jsii.member(jsii_name="devicePosture")
    def device_posture(self) -> ZeroTrustAccessGroupIncludeDevicePostureOutputReference:
        return typing.cast(ZeroTrustAccessGroupIncludeDevicePostureOutputReference, jsii.get(self, "devicePosture"))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(self) -> ZeroTrustAccessGroupIncludeEmailOutputReference:
        return typing.cast(ZeroTrustAccessGroupIncludeEmailOutputReference, jsii.get(self, "email"))

    @builtins.property
    @jsii.member(jsii_name="emailDomain")
    def email_domain(self) -> ZeroTrustAccessGroupIncludeEmailDomainOutputReference:
        return typing.cast(ZeroTrustAccessGroupIncludeEmailDomainOutputReference, jsii.get(self, "emailDomain"))

    @builtins.property
    @jsii.member(jsii_name="emailList")
    def email_list(self) -> ZeroTrustAccessGroupIncludeEmailListStructOutputReference:
        return typing.cast(ZeroTrustAccessGroupIncludeEmailListStructOutputReference, jsii.get(self, "emailList"))

    @builtins.property
    @jsii.member(jsii_name="everyone")
    def everyone(self) -> ZeroTrustAccessGroupIncludeEveryoneOutputReference:
        return typing.cast(ZeroTrustAccessGroupIncludeEveryoneOutputReference, jsii.get(self, "everyone"))

    @builtins.property
    @jsii.member(jsii_name="externalEvaluation")
    def external_evaluation(
        self,
    ) -> ZeroTrustAccessGroupIncludeExternalEvaluationOutputReference:
        return typing.cast(ZeroTrustAccessGroupIncludeExternalEvaluationOutputReference, jsii.get(self, "externalEvaluation"))

    @builtins.property
    @jsii.member(jsii_name="geo")
    def geo(self) -> ZeroTrustAccessGroupIncludeGeoOutputReference:
        return typing.cast(ZeroTrustAccessGroupIncludeGeoOutputReference, jsii.get(self, "geo"))

    @builtins.property
    @jsii.member(jsii_name="githubOrganization")
    def github_organization(
        self,
    ) -> ZeroTrustAccessGroupIncludeGithubOrganizationOutputReference:
        return typing.cast(ZeroTrustAccessGroupIncludeGithubOrganizationOutputReference, jsii.get(self, "githubOrganization"))

    @builtins.property
    @jsii.member(jsii_name="group")
    def group(self) -> ZeroTrustAccessGroupIncludeGroupOutputReference:
        return typing.cast(ZeroTrustAccessGroupIncludeGroupOutputReference, jsii.get(self, "group"))

    @builtins.property
    @jsii.member(jsii_name="gsuite")
    def gsuite(self) -> ZeroTrustAccessGroupIncludeGsuiteOutputReference:
        return typing.cast(ZeroTrustAccessGroupIncludeGsuiteOutputReference, jsii.get(self, "gsuite"))

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> ZeroTrustAccessGroupIncludeIpOutputReference:
        return typing.cast(ZeroTrustAccessGroupIncludeIpOutputReference, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="ipList")
    def ip_list(self) -> ZeroTrustAccessGroupIncludeIpListStructOutputReference:
        return typing.cast(ZeroTrustAccessGroupIncludeIpListStructOutputReference, jsii.get(self, "ipList"))

    @builtins.property
    @jsii.member(jsii_name="linkedAppToken")
    def linked_app_token(
        self,
    ) -> ZeroTrustAccessGroupIncludeLinkedAppTokenOutputReference:
        return typing.cast(ZeroTrustAccessGroupIncludeLinkedAppTokenOutputReference, jsii.get(self, "linkedAppToken"))

    @builtins.property
    @jsii.member(jsii_name="loginMethod")
    def login_method(self) -> ZeroTrustAccessGroupIncludeLoginMethodOutputReference:
        return typing.cast(ZeroTrustAccessGroupIncludeLoginMethodOutputReference, jsii.get(self, "loginMethod"))

    @builtins.property
    @jsii.member(jsii_name="oidc")
    def oidc(self) -> ZeroTrustAccessGroupIncludeOidcOutputReference:
        return typing.cast(ZeroTrustAccessGroupIncludeOidcOutputReference, jsii.get(self, "oidc"))

    @builtins.property
    @jsii.member(jsii_name="okta")
    def okta(self) -> ZeroTrustAccessGroupIncludeOktaOutputReference:
        return typing.cast(ZeroTrustAccessGroupIncludeOktaOutputReference, jsii.get(self, "okta"))

    @builtins.property
    @jsii.member(jsii_name="saml")
    def saml(self) -> "ZeroTrustAccessGroupIncludeSamlOutputReference":
        return typing.cast("ZeroTrustAccessGroupIncludeSamlOutputReference", jsii.get(self, "saml"))

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(self) -> "ZeroTrustAccessGroupIncludeServiceTokenOutputReference":
        return typing.cast("ZeroTrustAccessGroupIncludeServiceTokenOutputReference", jsii.get(self, "serviceToken"))

    @builtins.property
    @jsii.member(jsii_name="anyValidServiceTokenInput")
    def any_valid_service_token_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeAnyValidServiceToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeAnyValidServiceToken]], jsii.get(self, "anyValidServiceTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="authContextInput")
    def auth_context_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeAuthContext]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeAuthContext]], jsii.get(self, "authContextInput"))

    @builtins.property
    @jsii.member(jsii_name="authMethodInput")
    def auth_method_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeAuthMethod]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeAuthMethod]], jsii.get(self, "authMethodInput"))

    @builtins.property
    @jsii.member(jsii_name="azureAdInput")
    def azure_ad_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeAzureAd]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeAzureAd]], jsii.get(self, "azureAdInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateInput")
    def certificate_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeCertificate]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeCertificate]], jsii.get(self, "certificateInput"))

    @builtins.property
    @jsii.member(jsii_name="commonNameInput")
    def common_name_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeCommonName]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeCommonName]], jsii.get(self, "commonNameInput"))

    @builtins.property
    @jsii.member(jsii_name="devicePostureInput")
    def device_posture_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeDevicePosture]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeDevicePosture]], jsii.get(self, "devicePostureInput"))

    @builtins.property
    @jsii.member(jsii_name="emailDomainInput")
    def email_domain_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeEmailDomain]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeEmailDomain]], jsii.get(self, "emailDomainInput"))

    @builtins.property
    @jsii.member(jsii_name="emailInput")
    def email_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeEmail]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeEmail]], jsii.get(self, "emailInput"))

    @builtins.property
    @jsii.member(jsii_name="emailListInput")
    def email_list_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeEmailListStruct]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeEmailListStruct]], jsii.get(self, "emailListInput"))

    @builtins.property
    @jsii.member(jsii_name="everyoneInput")
    def everyone_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeEveryone]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeEveryone]], jsii.get(self, "everyoneInput"))

    @builtins.property
    @jsii.member(jsii_name="externalEvaluationInput")
    def external_evaluation_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeExternalEvaluation]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeExternalEvaluation]], jsii.get(self, "externalEvaluationInput"))

    @builtins.property
    @jsii.member(jsii_name="geoInput")
    def geo_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeGeo]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeGeo]], jsii.get(self, "geoInput"))

    @builtins.property
    @jsii.member(jsii_name="githubOrganizationInput")
    def github_organization_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeGithubOrganization]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeGithubOrganization]], jsii.get(self, "githubOrganizationInput"))

    @builtins.property
    @jsii.member(jsii_name="groupInput")
    def group_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeGroup]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeGroup]], jsii.get(self, "groupInput"))

    @builtins.property
    @jsii.member(jsii_name="gsuiteInput")
    def gsuite_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeGsuite]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeGsuite]], jsii.get(self, "gsuiteInput"))

    @builtins.property
    @jsii.member(jsii_name="ipInput")
    def ip_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeIp]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeIp]], jsii.get(self, "ipInput"))

    @builtins.property
    @jsii.member(jsii_name="ipListInput")
    def ip_list_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeIpListStruct]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeIpListStruct]], jsii.get(self, "ipListInput"))

    @builtins.property
    @jsii.member(jsii_name="linkedAppTokenInput")
    def linked_app_token_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeLinkedAppToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeLinkedAppToken]], jsii.get(self, "linkedAppTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="loginMethodInput")
    def login_method_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeLoginMethod]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeLoginMethod]], jsii.get(self, "loginMethodInput"))

    @builtins.property
    @jsii.member(jsii_name="oidcInput")
    def oidc_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeOidc]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeOidc]], jsii.get(self, "oidcInput"))

    @builtins.property
    @jsii.member(jsii_name="oktaInput")
    def okta_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeOkta]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeOkta]], jsii.get(self, "oktaInput"))

    @builtins.property
    @jsii.member(jsii_name="samlInput")
    def saml_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustAccessGroupIncludeSaml"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustAccessGroupIncludeSaml"]], jsii.get(self, "samlInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceTokenInput")
    def service_token_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustAccessGroupIncludeServiceToken"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustAccessGroupIncludeServiceToken"]], jsii.get(self, "serviceTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupInclude]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupInclude]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupInclude]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa81b8349bb7c5cc9053ca6907036a8696421116232558d9ca891441e11e3321)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeSaml",
    jsii_struct_bases=[],
    name_mapping={
        "attribute_name": "attributeName",
        "attribute_value": "attributeValue",
        "identity_provider_id": "identityProviderId",
    },
)
class ZeroTrustAccessGroupIncludeSaml:
    def __init__(
        self,
        *,
        attribute_name: builtins.str,
        attribute_value: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param attribute_name: The name of the SAML attribute. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#attribute_name ZeroTrustAccessGroup#attribute_name}
        :param attribute_value: The SAML attribute value to look for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#attribute_value ZeroTrustAccessGroup#attribute_value}
        :param identity_provider_id: The ID of your SAML identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37a791ad73e5781d793b796bbc41cac48a8f7e8fb14929bbfcc3ff2eb0466d6d)
            check_type(argname="argument attribute_name", value=attribute_name, expected_type=type_hints["attribute_name"])
            check_type(argname="argument attribute_value", value=attribute_value, expected_type=type_hints["attribute_value"])
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "attribute_name": attribute_name,
            "attribute_value": attribute_value,
            "identity_provider_id": identity_provider_id,
        }

    @builtins.property
    def attribute_name(self) -> builtins.str:
        '''The name of the SAML attribute.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#attribute_name ZeroTrustAccessGroup#attribute_name}
        '''
        result = self._values.get("attribute_name")
        assert result is not None, "Required property 'attribute_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attribute_value(self) -> builtins.str:
        '''The SAML attribute value to look for.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#attribute_value ZeroTrustAccessGroup#attribute_value}
        '''
        result = self._values.get("attribute_value")
        assert result is not None, "Required property 'attribute_value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your SAML identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupIncludeSaml(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupIncludeSamlOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeSamlOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__eddce6f9b3b126bc38f26239a3006ded9635824fc7af913d2401d4da2691b47a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="attributeNameInput")
    def attribute_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "attributeNameInput"))

    @builtins.property
    @jsii.member(jsii_name="attributeValueInput")
    def attribute_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "attributeValueInput"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderIdInput")
    def identity_provider_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityProviderIdInput"))

    @builtins.property
    @jsii.member(jsii_name="attributeName")
    def attribute_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "attributeName"))

    @attribute_name.setter
    def attribute_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbce3108276d15251ab8fe8aea75e96bad2f42318d118448f78cd26ef5ffbfbb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attributeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="attributeValue")
    def attribute_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "attributeValue"))

    @attribute_value.setter
    def attribute_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d92b4846287ff98f952ff32549635421b9bf7ac3b590bdefef9cb3bb016498b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attributeValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4746288e77f1665cb7fe6b988f0c6b6fc12f46954c90c48cf88dff4cde66d4cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeSaml]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeSaml]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeSaml]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdd561d4bddcc457b29c2f18886861bbcfd5093b5d37f3d9b011368e44c096e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeServiceToken",
    jsii_struct_bases=[],
    name_mapping={"token_id": "tokenId"},
)
class ZeroTrustAccessGroupIncludeServiceToken:
    def __init__(self, *, token_id: builtins.str) -> None:
        '''
        :param token_id: The ID of a Service Token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#token_id ZeroTrustAccessGroup#token_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2c8341b0fb3b78b03223c18b1b3515c3e8ad67e122ddfe34acf411b3f9afd12)
            check_type(argname="argument token_id", value=token_id, expected_type=type_hints["token_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "token_id": token_id,
        }

    @builtins.property
    def token_id(self) -> builtins.str:
        '''The ID of a Service Token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#token_id ZeroTrustAccessGroup#token_id}
        '''
        result = self._values.get("token_id")
        assert result is not None, "Required property 'token_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupIncludeServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupIncludeServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupIncludeServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__79ec6bf8685db53c8dd52545e816f32959ed917e48cb3ef029a8b0dc27907019)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="tokenIdInput")
    def token_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenIdInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenId")
    def token_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tokenId"))

    @token_id.setter
    def token_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba3de18f40d6b2f1a5514220b574a9e8a33c4466d97e8db5d70c73ce89508e95)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeServiceToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeServiceToken]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeServiceToken]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfd09f85fe42eba35e1e6fc8eeb71eb9a708a54cfa1c8b519652929d5a8cadda)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequire",
    jsii_struct_bases=[],
    name_mapping={
        "any_valid_service_token": "anyValidServiceToken",
        "auth_context": "authContext",
        "auth_method": "authMethod",
        "azure_ad": "azureAd",
        "certificate": "certificate",
        "common_name": "commonName",
        "device_posture": "devicePosture",
        "email": "email",
        "email_domain": "emailDomain",
        "email_list": "emailList",
        "everyone": "everyone",
        "external_evaluation": "externalEvaluation",
        "geo": "geo",
        "github_organization": "githubOrganization",
        "group": "group",
        "gsuite": "gsuite",
        "ip": "ip",
        "ip_list": "ipList",
        "linked_app_token": "linkedAppToken",
        "login_method": "loginMethod",
        "oidc": "oidc",
        "okta": "okta",
        "saml": "saml",
        "service_token": "serviceToken",
    },
)
class ZeroTrustAccessGroupRequire:
    def __init__(
        self,
        *,
        any_valid_service_token: typing.Optional[typing.Union["ZeroTrustAccessGroupRequireAnyValidServiceToken", typing.Dict[builtins.str, typing.Any]]] = None,
        auth_context: typing.Optional[typing.Union["ZeroTrustAccessGroupRequireAuthContext", typing.Dict[builtins.str, typing.Any]]] = None,
        auth_method: typing.Optional[typing.Union["ZeroTrustAccessGroupRequireAuthMethod", typing.Dict[builtins.str, typing.Any]]] = None,
        azure_ad: typing.Optional[typing.Union["ZeroTrustAccessGroupRequireAzureAd", typing.Dict[builtins.str, typing.Any]]] = None,
        certificate: typing.Optional[typing.Union["ZeroTrustAccessGroupRequireCertificate", typing.Dict[builtins.str, typing.Any]]] = None,
        common_name: typing.Optional[typing.Union["ZeroTrustAccessGroupRequireCommonName", typing.Dict[builtins.str, typing.Any]]] = None,
        device_posture: typing.Optional[typing.Union["ZeroTrustAccessGroupRequireDevicePosture", typing.Dict[builtins.str, typing.Any]]] = None,
        email: typing.Optional[typing.Union["ZeroTrustAccessGroupRequireEmail", typing.Dict[builtins.str, typing.Any]]] = None,
        email_domain: typing.Optional[typing.Union["ZeroTrustAccessGroupRequireEmailDomain", typing.Dict[builtins.str, typing.Any]]] = None,
        email_list: typing.Optional[typing.Union["ZeroTrustAccessGroupRequireEmailListStruct", typing.Dict[builtins.str, typing.Any]]] = None,
        everyone: typing.Optional[typing.Union["ZeroTrustAccessGroupRequireEveryone", typing.Dict[builtins.str, typing.Any]]] = None,
        external_evaluation: typing.Optional[typing.Union["ZeroTrustAccessGroupRequireExternalEvaluation", typing.Dict[builtins.str, typing.Any]]] = None,
        geo: typing.Optional[typing.Union["ZeroTrustAccessGroupRequireGeo", typing.Dict[builtins.str, typing.Any]]] = None,
        github_organization: typing.Optional[typing.Union["ZeroTrustAccessGroupRequireGithubOrganization", typing.Dict[builtins.str, typing.Any]]] = None,
        group: typing.Optional[typing.Union["ZeroTrustAccessGroupRequireGroup", typing.Dict[builtins.str, typing.Any]]] = None,
        gsuite: typing.Optional[typing.Union["ZeroTrustAccessGroupRequireGsuite", typing.Dict[builtins.str, typing.Any]]] = None,
        ip: typing.Optional[typing.Union["ZeroTrustAccessGroupRequireIp", typing.Dict[builtins.str, typing.Any]]] = None,
        ip_list: typing.Optional[typing.Union["ZeroTrustAccessGroupRequireIpListStruct", typing.Dict[builtins.str, typing.Any]]] = None,
        linked_app_token: typing.Optional[typing.Union["ZeroTrustAccessGroupRequireLinkedAppToken", typing.Dict[builtins.str, typing.Any]]] = None,
        login_method: typing.Optional[typing.Union["ZeroTrustAccessGroupRequireLoginMethod", typing.Dict[builtins.str, typing.Any]]] = None,
        oidc: typing.Optional[typing.Union["ZeroTrustAccessGroupRequireOidc", typing.Dict[builtins.str, typing.Any]]] = None,
        okta: typing.Optional[typing.Union["ZeroTrustAccessGroupRequireOkta", typing.Dict[builtins.str, typing.Any]]] = None,
        saml: typing.Optional[typing.Union["ZeroTrustAccessGroupRequireSaml", typing.Dict[builtins.str, typing.Any]]] = None,
        service_token: typing.Optional[typing.Union["ZeroTrustAccessGroupRequireServiceToken", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param any_valid_service_token: An empty object which matches on all service tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#any_valid_service_token ZeroTrustAccessGroup#any_valid_service_token}
        :param auth_context: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#auth_context ZeroTrustAccessGroup#auth_context}.
        :param auth_method: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#auth_method ZeroTrustAccessGroup#auth_method}.
        :param azure_ad: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#azure_ad ZeroTrustAccessGroup#azure_ad}.
        :param certificate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#certificate ZeroTrustAccessGroup#certificate}.
        :param common_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#common_name ZeroTrustAccessGroup#common_name}.
        :param device_posture: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#device_posture ZeroTrustAccessGroup#device_posture}.
        :param email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email ZeroTrustAccessGroup#email}.
        :param email_domain: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email_domain ZeroTrustAccessGroup#email_domain}.
        :param email_list: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email_list ZeroTrustAccessGroup#email_list}.
        :param everyone: An empty object which matches on all users. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#everyone ZeroTrustAccessGroup#everyone}
        :param external_evaluation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#external_evaluation ZeroTrustAccessGroup#external_evaluation}.
        :param geo: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#geo ZeroTrustAccessGroup#geo}.
        :param github_organization: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#github_organization ZeroTrustAccessGroup#github_organization}.
        :param group: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#group ZeroTrustAccessGroup#group}.
        :param gsuite: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#gsuite ZeroTrustAccessGroup#gsuite}.
        :param ip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ip ZeroTrustAccessGroup#ip}.
        :param ip_list: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ip_list ZeroTrustAccessGroup#ip_list}.
        :param linked_app_token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#linked_app_token ZeroTrustAccessGroup#linked_app_token}.
        :param login_method: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#login_method ZeroTrustAccessGroup#login_method}.
        :param oidc: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#oidc ZeroTrustAccessGroup#oidc}.
        :param okta: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#okta ZeroTrustAccessGroup#okta}.
        :param saml: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#saml ZeroTrustAccessGroup#saml}.
        :param service_token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#service_token ZeroTrustAccessGroup#service_token}.
        '''
        if isinstance(any_valid_service_token, dict):
            any_valid_service_token = ZeroTrustAccessGroupRequireAnyValidServiceToken(**any_valid_service_token)
        if isinstance(auth_context, dict):
            auth_context = ZeroTrustAccessGroupRequireAuthContext(**auth_context)
        if isinstance(auth_method, dict):
            auth_method = ZeroTrustAccessGroupRequireAuthMethod(**auth_method)
        if isinstance(azure_ad, dict):
            azure_ad = ZeroTrustAccessGroupRequireAzureAd(**azure_ad)
        if isinstance(certificate, dict):
            certificate = ZeroTrustAccessGroupRequireCertificate(**certificate)
        if isinstance(common_name, dict):
            common_name = ZeroTrustAccessGroupRequireCommonName(**common_name)
        if isinstance(device_posture, dict):
            device_posture = ZeroTrustAccessGroupRequireDevicePosture(**device_posture)
        if isinstance(email, dict):
            email = ZeroTrustAccessGroupRequireEmail(**email)
        if isinstance(email_domain, dict):
            email_domain = ZeroTrustAccessGroupRequireEmailDomain(**email_domain)
        if isinstance(email_list, dict):
            email_list = ZeroTrustAccessGroupRequireEmailListStruct(**email_list)
        if isinstance(everyone, dict):
            everyone = ZeroTrustAccessGroupRequireEveryone(**everyone)
        if isinstance(external_evaluation, dict):
            external_evaluation = ZeroTrustAccessGroupRequireExternalEvaluation(**external_evaluation)
        if isinstance(geo, dict):
            geo = ZeroTrustAccessGroupRequireGeo(**geo)
        if isinstance(github_organization, dict):
            github_organization = ZeroTrustAccessGroupRequireGithubOrganization(**github_organization)
        if isinstance(group, dict):
            group = ZeroTrustAccessGroupRequireGroup(**group)
        if isinstance(gsuite, dict):
            gsuite = ZeroTrustAccessGroupRequireGsuite(**gsuite)
        if isinstance(ip, dict):
            ip = ZeroTrustAccessGroupRequireIp(**ip)
        if isinstance(ip_list, dict):
            ip_list = ZeroTrustAccessGroupRequireIpListStruct(**ip_list)
        if isinstance(linked_app_token, dict):
            linked_app_token = ZeroTrustAccessGroupRequireLinkedAppToken(**linked_app_token)
        if isinstance(login_method, dict):
            login_method = ZeroTrustAccessGroupRequireLoginMethod(**login_method)
        if isinstance(oidc, dict):
            oidc = ZeroTrustAccessGroupRequireOidc(**oidc)
        if isinstance(okta, dict):
            okta = ZeroTrustAccessGroupRequireOkta(**okta)
        if isinstance(saml, dict):
            saml = ZeroTrustAccessGroupRequireSaml(**saml)
        if isinstance(service_token, dict):
            service_token = ZeroTrustAccessGroupRequireServiceToken(**service_token)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ca19dcea861c64afc9ab364a01bd40e90c208f30429ca3b586da0ba0d7cfeed)
            check_type(argname="argument any_valid_service_token", value=any_valid_service_token, expected_type=type_hints["any_valid_service_token"])
            check_type(argname="argument auth_context", value=auth_context, expected_type=type_hints["auth_context"])
            check_type(argname="argument auth_method", value=auth_method, expected_type=type_hints["auth_method"])
            check_type(argname="argument azure_ad", value=azure_ad, expected_type=type_hints["azure_ad"])
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument common_name", value=common_name, expected_type=type_hints["common_name"])
            check_type(argname="argument device_posture", value=device_posture, expected_type=type_hints["device_posture"])
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
            check_type(argname="argument email_domain", value=email_domain, expected_type=type_hints["email_domain"])
            check_type(argname="argument email_list", value=email_list, expected_type=type_hints["email_list"])
            check_type(argname="argument everyone", value=everyone, expected_type=type_hints["everyone"])
            check_type(argname="argument external_evaluation", value=external_evaluation, expected_type=type_hints["external_evaluation"])
            check_type(argname="argument geo", value=geo, expected_type=type_hints["geo"])
            check_type(argname="argument github_organization", value=github_organization, expected_type=type_hints["github_organization"])
            check_type(argname="argument group", value=group, expected_type=type_hints["group"])
            check_type(argname="argument gsuite", value=gsuite, expected_type=type_hints["gsuite"])
            check_type(argname="argument ip", value=ip, expected_type=type_hints["ip"])
            check_type(argname="argument ip_list", value=ip_list, expected_type=type_hints["ip_list"])
            check_type(argname="argument linked_app_token", value=linked_app_token, expected_type=type_hints["linked_app_token"])
            check_type(argname="argument login_method", value=login_method, expected_type=type_hints["login_method"])
            check_type(argname="argument oidc", value=oidc, expected_type=type_hints["oidc"])
            check_type(argname="argument okta", value=okta, expected_type=type_hints["okta"])
            check_type(argname="argument saml", value=saml, expected_type=type_hints["saml"])
            check_type(argname="argument service_token", value=service_token, expected_type=type_hints["service_token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if any_valid_service_token is not None:
            self._values["any_valid_service_token"] = any_valid_service_token
        if auth_context is not None:
            self._values["auth_context"] = auth_context
        if auth_method is not None:
            self._values["auth_method"] = auth_method
        if azure_ad is not None:
            self._values["azure_ad"] = azure_ad
        if certificate is not None:
            self._values["certificate"] = certificate
        if common_name is not None:
            self._values["common_name"] = common_name
        if device_posture is not None:
            self._values["device_posture"] = device_posture
        if email is not None:
            self._values["email"] = email
        if email_domain is not None:
            self._values["email_domain"] = email_domain
        if email_list is not None:
            self._values["email_list"] = email_list
        if everyone is not None:
            self._values["everyone"] = everyone
        if external_evaluation is not None:
            self._values["external_evaluation"] = external_evaluation
        if geo is not None:
            self._values["geo"] = geo
        if github_organization is not None:
            self._values["github_organization"] = github_organization
        if group is not None:
            self._values["group"] = group
        if gsuite is not None:
            self._values["gsuite"] = gsuite
        if ip is not None:
            self._values["ip"] = ip
        if ip_list is not None:
            self._values["ip_list"] = ip_list
        if linked_app_token is not None:
            self._values["linked_app_token"] = linked_app_token
        if login_method is not None:
            self._values["login_method"] = login_method
        if oidc is not None:
            self._values["oidc"] = oidc
        if okta is not None:
            self._values["okta"] = okta
        if saml is not None:
            self._values["saml"] = saml
        if service_token is not None:
            self._values["service_token"] = service_token

    @builtins.property
    def any_valid_service_token(
        self,
    ) -> typing.Optional["ZeroTrustAccessGroupRequireAnyValidServiceToken"]:
        '''An empty object which matches on all service tokens.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#any_valid_service_token ZeroTrustAccessGroup#any_valid_service_token}
        '''
        result = self._values.get("any_valid_service_token")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupRequireAnyValidServiceToken"], result)

    @builtins.property
    def auth_context(self) -> typing.Optional["ZeroTrustAccessGroupRequireAuthContext"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#auth_context ZeroTrustAccessGroup#auth_context}.'''
        result = self._values.get("auth_context")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupRequireAuthContext"], result)

    @builtins.property
    def auth_method(self) -> typing.Optional["ZeroTrustAccessGroupRequireAuthMethod"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#auth_method ZeroTrustAccessGroup#auth_method}.'''
        result = self._values.get("auth_method")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupRequireAuthMethod"], result)

    @builtins.property
    def azure_ad(self) -> typing.Optional["ZeroTrustAccessGroupRequireAzureAd"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#azure_ad ZeroTrustAccessGroup#azure_ad}.'''
        result = self._values.get("azure_ad")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupRequireAzureAd"], result)

    @builtins.property
    def certificate(self) -> typing.Optional["ZeroTrustAccessGroupRequireCertificate"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#certificate ZeroTrustAccessGroup#certificate}.'''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupRequireCertificate"], result)

    @builtins.property
    def common_name(self) -> typing.Optional["ZeroTrustAccessGroupRequireCommonName"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#common_name ZeroTrustAccessGroup#common_name}.'''
        result = self._values.get("common_name")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupRequireCommonName"], result)

    @builtins.property
    def device_posture(
        self,
    ) -> typing.Optional["ZeroTrustAccessGroupRequireDevicePosture"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#device_posture ZeroTrustAccessGroup#device_posture}.'''
        result = self._values.get("device_posture")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupRequireDevicePosture"], result)

    @builtins.property
    def email(self) -> typing.Optional["ZeroTrustAccessGroupRequireEmail"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email ZeroTrustAccessGroup#email}.'''
        result = self._values.get("email")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupRequireEmail"], result)

    @builtins.property
    def email_domain(self) -> typing.Optional["ZeroTrustAccessGroupRequireEmailDomain"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email_domain ZeroTrustAccessGroup#email_domain}.'''
        result = self._values.get("email_domain")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupRequireEmailDomain"], result)

    @builtins.property
    def email_list(
        self,
    ) -> typing.Optional["ZeroTrustAccessGroupRequireEmailListStruct"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email_list ZeroTrustAccessGroup#email_list}.'''
        result = self._values.get("email_list")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupRequireEmailListStruct"], result)

    @builtins.property
    def everyone(self) -> typing.Optional["ZeroTrustAccessGroupRequireEveryone"]:
        '''An empty object which matches on all users.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#everyone ZeroTrustAccessGroup#everyone}
        '''
        result = self._values.get("everyone")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupRequireEveryone"], result)

    @builtins.property
    def external_evaluation(
        self,
    ) -> typing.Optional["ZeroTrustAccessGroupRequireExternalEvaluation"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#external_evaluation ZeroTrustAccessGroup#external_evaluation}.'''
        result = self._values.get("external_evaluation")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupRequireExternalEvaluation"], result)

    @builtins.property
    def geo(self) -> typing.Optional["ZeroTrustAccessGroupRequireGeo"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#geo ZeroTrustAccessGroup#geo}.'''
        result = self._values.get("geo")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupRequireGeo"], result)

    @builtins.property
    def github_organization(
        self,
    ) -> typing.Optional["ZeroTrustAccessGroupRequireGithubOrganization"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#github_organization ZeroTrustAccessGroup#github_organization}.'''
        result = self._values.get("github_organization")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupRequireGithubOrganization"], result)

    @builtins.property
    def group(self) -> typing.Optional["ZeroTrustAccessGroupRequireGroup"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#group ZeroTrustAccessGroup#group}.'''
        result = self._values.get("group")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupRequireGroup"], result)

    @builtins.property
    def gsuite(self) -> typing.Optional["ZeroTrustAccessGroupRequireGsuite"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#gsuite ZeroTrustAccessGroup#gsuite}.'''
        result = self._values.get("gsuite")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupRequireGsuite"], result)

    @builtins.property
    def ip(self) -> typing.Optional["ZeroTrustAccessGroupRequireIp"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ip ZeroTrustAccessGroup#ip}.'''
        result = self._values.get("ip")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupRequireIp"], result)

    @builtins.property
    def ip_list(self) -> typing.Optional["ZeroTrustAccessGroupRequireIpListStruct"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ip_list ZeroTrustAccessGroup#ip_list}.'''
        result = self._values.get("ip_list")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupRequireIpListStruct"], result)

    @builtins.property
    def linked_app_token(
        self,
    ) -> typing.Optional["ZeroTrustAccessGroupRequireLinkedAppToken"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#linked_app_token ZeroTrustAccessGroup#linked_app_token}.'''
        result = self._values.get("linked_app_token")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupRequireLinkedAppToken"], result)

    @builtins.property
    def login_method(self) -> typing.Optional["ZeroTrustAccessGroupRequireLoginMethod"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#login_method ZeroTrustAccessGroup#login_method}.'''
        result = self._values.get("login_method")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupRequireLoginMethod"], result)

    @builtins.property
    def oidc(self) -> typing.Optional["ZeroTrustAccessGroupRequireOidc"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#oidc ZeroTrustAccessGroup#oidc}.'''
        result = self._values.get("oidc")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupRequireOidc"], result)

    @builtins.property
    def okta(self) -> typing.Optional["ZeroTrustAccessGroupRequireOkta"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#okta ZeroTrustAccessGroup#okta}.'''
        result = self._values.get("okta")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupRequireOkta"], result)

    @builtins.property
    def saml(self) -> typing.Optional["ZeroTrustAccessGroupRequireSaml"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#saml ZeroTrustAccessGroup#saml}.'''
        result = self._values.get("saml")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupRequireSaml"], result)

    @builtins.property
    def service_token(
        self,
    ) -> typing.Optional["ZeroTrustAccessGroupRequireServiceToken"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#service_token ZeroTrustAccessGroup#service_token}.'''
        result = self._values.get("service_token")
        return typing.cast(typing.Optional["ZeroTrustAccessGroupRequireServiceToken"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupRequire(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireAnyValidServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class ZeroTrustAccessGroupRequireAnyValidServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupRequireAnyValidServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupRequireAnyValidServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireAnyValidServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b4a515cf1dbe3c3135069d2f75983154d2bedf67e34d3ab5d2dd8554ccdf9154)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireAnyValidServiceToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireAnyValidServiceToken]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireAnyValidServiceToken]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a3dc1c51ce914c3f639bad4004b67f3cb34f10f1668e1ebee76d5114817c0d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireAuthContext",
    jsii_struct_bases=[],
    name_mapping={
        "ac_id": "acId",
        "id": "id",
        "identity_provider_id": "identityProviderId",
    },
)
class ZeroTrustAccessGroupRequireAuthContext:
    def __init__(
        self,
        *,
        ac_id: builtins.str,
        id: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param ac_id: The ACID of an Authentication context. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ac_id ZeroTrustAccessGroup#ac_id}
        :param id: The ID of an Authentication context. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider_id: The ID of your Azure identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce0fc6b2610c6f1422cafec22630d3fbc8a1b0f10ba60cec5f3056df94ae3a3b)
            check_type(argname="argument ac_id", value=ac_id, expected_type=type_hints["ac_id"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "ac_id": ac_id,
            "id": id,
            "identity_provider_id": identity_provider_id,
        }

    @builtins.property
    def ac_id(self) -> builtins.str:
        '''The ACID of an Authentication context.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ac_id ZeroTrustAccessGroup#ac_id}
        '''
        result = self._values.get("ac_id")
        assert result is not None, "Required property 'ac_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of an Authentication context.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your Azure identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupRequireAuthContext(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupRequireAuthContextOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireAuthContextOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__84c377e5ce845c585924cff621dd58e85e0fd8bc879c9d265b89aa2a2089ba30)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="acIdInput")
    def ac_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "acIdInput"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderIdInput")
    def identity_provider_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityProviderIdInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="acId")
    def ac_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "acId"))

    @ac_id.setter
    def ac_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b2c743e985d304300d2a878b06402253d10da141c2c4baed255913204650a68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "acId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fccf9716862581d9d8c1a09f13eaea809748b197722ca793325632e82855b92)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__619129d7ce1c8ef416984007525c59353b0df51a3db8a5584443691df04ac5ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireAuthContext]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireAuthContext]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireAuthContext]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c35bdbed74abe93d2af4e9bdae98cb38a6df15a57a2dacf40f598865081cf2c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireAuthMethod",
    jsii_struct_bases=[],
    name_mapping={"auth_method": "authMethod"},
)
class ZeroTrustAccessGroupRequireAuthMethod:
    def __init__(self, *, auth_method: builtins.str) -> None:
        '''
        :param auth_method: The type of authentication method https://datatracker.ietf.org/doc/html/rfc8176#section-2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#auth_method ZeroTrustAccessGroup#auth_method}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0faeec880030568277dcd5c3e28d65292ce185892bd5a45ef3f9953c66001300)
            check_type(argname="argument auth_method", value=auth_method, expected_type=type_hints["auth_method"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "auth_method": auth_method,
        }

    @builtins.property
    def auth_method(self) -> builtins.str:
        '''The type of authentication method https://datatracker.ietf.org/doc/html/rfc8176#section-2.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#auth_method ZeroTrustAccessGroup#auth_method}
        '''
        result = self._values.get("auth_method")
        assert result is not None, "Required property 'auth_method' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupRequireAuthMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupRequireAuthMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireAuthMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7728bdb7025f06e7e2ae223567fe747af3dd9fb0ebf63f3598aad50ac0a2078c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="authMethodInput")
    def auth_method_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authMethodInput"))

    @builtins.property
    @jsii.member(jsii_name="authMethod")
    def auth_method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authMethod"))

    @auth_method.setter
    def auth_method(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd0f3da7a88eccdd4305f06a1c550bbe35cb5b80f01d76d642047f1519157035)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authMethod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireAuthMethod]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireAuthMethod]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireAuthMethod]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89fb04a8fe770d0b8997b9c00e8c99049369f9e9bbc911ea57a79f158906fa16)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireAzureAd",
    jsii_struct_bases=[],
    name_mapping={"id": "id", "identity_provider_id": "identityProviderId"},
)
class ZeroTrustAccessGroupRequireAzureAd:
    def __init__(self, *, id: builtins.str, identity_provider_id: builtins.str) -> None:
        '''
        :param id: The ID of an Azure group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider_id: The ID of your Azure identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a34c50bf571e6958ae08518f412176c0504ea4a547d6b4182ea0350e6b672a48)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
            "identity_provider_id": identity_provider_id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of an Azure group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your Azure identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupRequireAzureAd(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupRequireAzureAdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireAzureAdOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b027ad9b6057d0e83ce146e48720a886e079f96e05d8604f048ed311ee854d9c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="identityProviderIdInput")
    def identity_provider_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityProviderIdInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__82e922e1b634897af7da404781a027f39159d74cb715fb8cdb067c7a247ef045)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80bfa15b621192769649a785727be93be86c2f2026aa15252ff2a0e4b3592f6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireAzureAd]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireAzureAd]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireAzureAd]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d44f6ecac6d8074abf29e85b33d131ab0aaa3779ccdc828674f19d66a5c1bbfa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireCertificate",
    jsii_struct_bases=[],
    name_mapping={},
)
class ZeroTrustAccessGroupRequireCertificate:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupRequireCertificate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupRequireCertificateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireCertificateOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__937f275f760304be7812bc9fbf44977ffce6912741c2e975913dc6ff83d0b59b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireCertificate]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireCertificate]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireCertificate]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5772979871b744c76a93b66c0b3e89fd4164c02069478bdf9555c49b782e802)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireCommonName",
    jsii_struct_bases=[],
    name_mapping={"common_name": "commonName"},
)
class ZeroTrustAccessGroupRequireCommonName:
    def __init__(self, *, common_name: builtins.str) -> None:
        '''
        :param common_name: The common name to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#common_name ZeroTrustAccessGroup#common_name}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47b1a032c05095635c3a32835499a8e7fe718e3f08d4f6e7d68a89fc37b98c9a)
            check_type(argname="argument common_name", value=common_name, expected_type=type_hints["common_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "common_name": common_name,
        }

    @builtins.property
    def common_name(self) -> builtins.str:
        '''The common name to match.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#common_name ZeroTrustAccessGroup#common_name}
        '''
        result = self._values.get("common_name")
        assert result is not None, "Required property 'common_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupRequireCommonName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupRequireCommonNameOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireCommonNameOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4d4732eecf93894672ee276c331e37112d211223bb8913bb15dcd8c4a10ebab7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="commonNameInput")
    def common_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commonNameInput"))

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commonName"))

    @common_name.setter
    def common_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de972ef932d4d81d3b0f5d898da913563d4786ecd47bd228df2244e3b5a9b940)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "commonName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireCommonName]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireCommonName]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireCommonName]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e7568a84d60171a865d5d950cb5fec3c14bb6e571cbd2b880522602f82740da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireDevicePosture",
    jsii_struct_bases=[],
    name_mapping={"integration_uid": "integrationUid"},
)
class ZeroTrustAccessGroupRequireDevicePosture:
    def __init__(self, *, integration_uid: builtins.str) -> None:
        '''
        :param integration_uid: The ID of a device posture integration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#integration_uid ZeroTrustAccessGroup#integration_uid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92303702f5467f33189f0989ad602089fb38b9a9d6cc9bb72cb1498a1d24904c)
            check_type(argname="argument integration_uid", value=integration_uid, expected_type=type_hints["integration_uid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "integration_uid": integration_uid,
        }

    @builtins.property
    def integration_uid(self) -> builtins.str:
        '''The ID of a device posture integration.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#integration_uid ZeroTrustAccessGroup#integration_uid}
        '''
        result = self._values.get("integration_uid")
        assert result is not None, "Required property 'integration_uid' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupRequireDevicePosture(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupRequireDevicePostureOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireDevicePostureOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__932f0963cf0693ca5a90cbf3e6a8aa461238ffe4e9ffe8cc630df3ddd9a0cf46)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="integrationUidInput")
    def integration_uid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "integrationUidInput"))

    @builtins.property
    @jsii.member(jsii_name="integrationUid")
    def integration_uid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "integrationUid"))

    @integration_uid.setter
    def integration_uid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8fcab31b6860c238ae242536143e87fed77bbad0f80d94c8d2013e5eae4d0ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "integrationUid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireDevicePosture]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireDevicePosture]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireDevicePosture]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__400035a1eb0ee75096259c80ad1db33bc76c2353f02a5248f0b49679a70e473b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireEmail",
    jsii_struct_bases=[],
    name_mapping={"email": "email"},
)
class ZeroTrustAccessGroupRequireEmail:
    def __init__(self, *, email: builtins.str) -> None:
        '''
        :param email: The email of the user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email ZeroTrustAccessGroup#email}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fffb84bd3b6d730000be38b5736f3862c01bfceade7e44e7ebd56bf2a3daf624)
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "email": email,
        }

    @builtins.property
    def email(self) -> builtins.str:
        '''The email of the user.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email ZeroTrustAccessGroup#email}
        '''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupRequireEmail(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireEmailDomain",
    jsii_struct_bases=[],
    name_mapping={"domain": "domain"},
)
class ZeroTrustAccessGroupRequireEmailDomain:
    def __init__(self, *, domain: builtins.str) -> None:
        '''
        :param domain: The email domain to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#domain ZeroTrustAccessGroup#domain}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19ad94635a19768b7f0aaaf0b17e2d4776d3ba60983bd4102ca9efeea3307c87)
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain": domain,
        }

    @builtins.property
    def domain(self) -> builtins.str:
        '''The email domain to match.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#domain ZeroTrustAccessGroup#domain}
        '''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupRequireEmailDomain(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupRequireEmailDomainOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireEmailDomainOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__309331e2e869f1df70bd5228619f98424e6633b19f6f662af18d0ac0369778f1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="domainInput")
    def domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainInput"))

    @builtins.property
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92030698db5f922af068273a735fcc0b39acb14fe9b68408a9c4feda09ebd82f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "domain", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireEmailDomain]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireEmailDomain]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireEmailDomain]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__903ce4c2c74c7e27d2fa02a488c37ab4b13da13f895fdcd3a335357a6d5ed1e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireEmailListStruct",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class ZeroTrustAccessGroupRequireEmailListStruct:
    def __init__(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created email list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9f1c0cfa9b8d302a71c142c21164da561318d1df2e4bbbfead0b9cced303b09)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of a previously created email list.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupRequireEmailListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupRequireEmailListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireEmailListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2a1be8de9f990e5fe827769afa635768c8a95394bfc2b7dd3164f3fb8477af69)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

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
            type_hints = typing.get_type_hints(_typecheckingstub__06bfda9340cab4b52eb5d4eaa8af5461d8af0b6b00a7e5eae6ca75645e7b65e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireEmailListStruct]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireEmailListStruct]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireEmailListStruct]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89f38160266f3de9a9dfe4157475a0b072b6cf616ab29c73104f559d770c09fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustAccessGroupRequireEmailOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireEmailOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__56e82c184749e0b1c6623a9f2fec07469367031ee031487835c148722550cec1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="emailInput")
    def email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailInput"))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "email"))

    @email.setter
    def email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__853589f41bf2e251eb8e6d7089407806ce3d97aba4be945efe5a7c3362823fa9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "email", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireEmail]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireEmail]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireEmail]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f46c6b9feddfd8c63f008148bb59f569514f077002185fe020df880b8de921cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireEveryone",
    jsii_struct_bases=[],
    name_mapping={},
)
class ZeroTrustAccessGroupRequireEveryone:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupRequireEveryone(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupRequireEveryoneOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireEveryoneOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__97a71b3e3638ffacf116e9c7b7c9364d8bb297dba78b099a6a2ab0dc0b665f7c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireEveryone]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireEveryone]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireEveryone]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4d2131cbfbc3237b69e133bd4bd3461fb960b5d7272108db4c019141ca04dc9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireExternalEvaluation",
    jsii_struct_bases=[],
    name_mapping={"evaluate_url": "evaluateUrl", "keys_url": "keysUrl"},
)
class ZeroTrustAccessGroupRequireExternalEvaluation:
    def __init__(self, *, evaluate_url: builtins.str, keys_url: builtins.str) -> None:
        '''
        :param evaluate_url: The API endpoint containing your business logic. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#evaluate_url ZeroTrustAccessGroup#evaluate_url}
        :param keys_url: The API endpoint containing the key that Access uses to verify that the response came from your API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#keys_url ZeroTrustAccessGroup#keys_url}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbaadad45bea772c3552c28c1f8ede410759dad3730311811e05637a105ccc2f)
            check_type(argname="argument evaluate_url", value=evaluate_url, expected_type=type_hints["evaluate_url"])
            check_type(argname="argument keys_url", value=keys_url, expected_type=type_hints["keys_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "evaluate_url": evaluate_url,
            "keys_url": keys_url,
        }

    @builtins.property
    def evaluate_url(self) -> builtins.str:
        '''The API endpoint containing your business logic.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#evaluate_url ZeroTrustAccessGroup#evaluate_url}
        '''
        result = self._values.get("evaluate_url")
        assert result is not None, "Required property 'evaluate_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def keys_url(self) -> builtins.str:
        '''The API endpoint containing the key that Access uses to verify that the response came from your API.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#keys_url ZeroTrustAccessGroup#keys_url}
        '''
        result = self._values.get("keys_url")
        assert result is not None, "Required property 'keys_url' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupRequireExternalEvaluation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupRequireExternalEvaluationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireExternalEvaluationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2f4b3e39df3c43dd1ee3296e5c5c97ca0a622cff94282978c12d22ab1d759d0e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="evaluateUrlInput")
    def evaluate_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "evaluateUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="keysUrlInput")
    def keys_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keysUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="evaluateUrl")
    def evaluate_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "evaluateUrl"))

    @evaluate_url.setter
    def evaluate_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__700c9210b51851ba3e94b2cc4a429f0dee175d92322172a19446577e2ebe039d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "evaluateUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keysUrl")
    def keys_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keysUrl"))

    @keys_url.setter
    def keys_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43ac1b59efaee65323d91f1ce5ff693480e2406dbff0b4b9302f65610648af33)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keysUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireExternalEvaluation]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireExternalEvaluation]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireExternalEvaluation]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47464751094d1b2968da48b331f3a0f4b6db7961edaa16647e91b1346e495a19)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireGeo",
    jsii_struct_bases=[],
    name_mapping={"country_code": "countryCode"},
)
class ZeroTrustAccessGroupRequireGeo:
    def __init__(self, *, country_code: builtins.str) -> None:
        '''
        :param country_code: The country code that should be matched. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#country_code ZeroTrustAccessGroup#country_code}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27479650673b751c4173a789412fe74b9c57eeb68fb6a6e9e0f538bc24066353)
            check_type(argname="argument country_code", value=country_code, expected_type=type_hints["country_code"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "country_code": country_code,
        }

    @builtins.property
    def country_code(self) -> builtins.str:
        '''The country code that should be matched.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#country_code ZeroTrustAccessGroup#country_code}
        '''
        result = self._values.get("country_code")
        assert result is not None, "Required property 'country_code' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupRequireGeo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupRequireGeoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireGeoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f11abb57b1516a28aae0c8b72d5db96d330099cd6ee7a5c8a7fabf21cf870e69)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="countryCodeInput")
    def country_code_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "countryCodeInput"))

    @builtins.property
    @jsii.member(jsii_name="countryCode")
    def country_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "countryCode"))

    @country_code.setter
    def country_code(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67abdf3b4bba37d94a27f360595b42e2765f645b4bc6fc7bb987ad672673e1ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "countryCode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireGeo]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireGeo]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireGeo]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6cb0de53a39f44b5b51093a394d62bab77752dc3da604c2df92c96ce00b87570)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireGithubOrganization",
    jsii_struct_bases=[],
    name_mapping={
        "identity_provider_id": "identityProviderId",
        "name": "name",
        "team": "team",
    },
)
class ZeroTrustAccessGroupRequireGithubOrganization:
    def __init__(
        self,
        *,
        identity_provider_id: builtins.str,
        name: builtins.str,
        team: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param identity_provider_id: The ID of your Github identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        :param name: The name of the organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#name ZeroTrustAccessGroup#name}
        :param team: The name of the team. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#team ZeroTrustAccessGroup#team}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9911fa1853cc16f9e54fff942ad7faa66f8d3253361db397e368ca0784518a47)
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument team", value=team, expected_type=type_hints["team"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "identity_provider_id": identity_provider_id,
            "name": name,
        }
        if team is not None:
            self._values["team"] = team

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your Github identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the organization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#name ZeroTrustAccessGroup#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def team(self) -> typing.Optional[builtins.str]:
        '''The name of the team.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#team ZeroTrustAccessGroup#team}
        '''
        result = self._values.get("team")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupRequireGithubOrganization(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupRequireGithubOrganizationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireGithubOrganizationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5fcbde6856020df97d4b6ec94392f1eb72879b5987ec5563728ef527a773ce2e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetTeam")
    def reset_team(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTeam", []))

    @builtins.property
    @jsii.member(jsii_name="identityProviderIdInput")
    def identity_provider_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityProviderIdInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="teamInput")
    def team_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "teamInput"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8da626c8480e109a8d305159f484c79fe3c1ba411b34699ffc1924b283355c45)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8257b63974106089b31cddb83b9b026da00850b7f0fb02f611b3df4d189db4f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="team")
    def team(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "team"))

    @team.setter
    def team(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d258b7a7c96a4aaeaa5bb540acec2f8ada80b26d2ceba715f758f5117253e0bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "team", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireGithubOrganization]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireGithubOrganization]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireGithubOrganization]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5972fbdc406c40b43c47445505064d97eba39c339d625fa6f3d1ed73de42161)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireGroup",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class ZeroTrustAccessGroupRequireGroup:
    def __init__(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created Access group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__440c6cb84b42fe507c19832800cf18f602cf1fb4b6d9ed2658755d60610d3325)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of a previously created Access group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupRequireGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupRequireGroupOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireGroupOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__557433e537d2e8c7d33ccb713ce4ee8f4d59efd4cdf4dd2eca91bddaf29548d3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

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
            type_hints = typing.get_type_hints(_typecheckingstub__562483f508e2d95b5908b87997daf7084e92af0c3a37714c4594a8c0cdf3c362)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireGroup]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireGroup]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireGroup]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d27c487511f8942e9bbdb1dfd29c9be2f22fc67a56a230baacd92fde80df23f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireGsuite",
    jsii_struct_bases=[],
    name_mapping={"email": "email", "identity_provider_id": "identityProviderId"},
)
class ZeroTrustAccessGroupRequireGsuite:
    def __init__(
        self,
        *,
        email: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param email: The email of the Google Workspace group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email ZeroTrustAccessGroup#email}
        :param identity_provider_id: The ID of your Google Workspace identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8685d3ac6b8d937119be8f424a61e7921147190b5496b44c2880daf7a5c7ae9)
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "email": email,
            "identity_provider_id": identity_provider_id,
        }

    @builtins.property
    def email(self) -> builtins.str:
        '''The email of the Google Workspace group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email ZeroTrustAccessGroup#email}
        '''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your Google Workspace identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupRequireGsuite(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupRequireGsuiteOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireGsuiteOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__61b28151f3a33e7beaf67c03e71e932e1f89cde1100242fe2979af2453f5b6e7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="emailInput")
    def email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailInput"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderIdInput")
    def identity_provider_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityProviderIdInput"))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "email"))

    @email.setter
    def email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eae01777313b663c299be3d342c25c2fd24343a123501fcbfa7ea8a6bb02ac98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "email", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af7dc98ff142a0541173bc9599e35678734e5b020950252bcbcf720eea91705c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireGsuite]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireGsuite]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireGsuite]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03e7c2a80294cc819dd78bc4122fe7ff922da1f55aeec7a65bb64f0ffcdb9aa3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireIp",
    jsii_struct_bases=[],
    name_mapping={"ip": "ip"},
)
class ZeroTrustAccessGroupRequireIp:
    def __init__(self, *, ip: builtins.str) -> None:
        '''
        :param ip: An IPv4 or IPv6 CIDR block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ip ZeroTrustAccessGroup#ip}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2f705cd4f8783e03e5111674c787111d9d68d2d1ca0b12f1e465f990c81b5d1)
            check_type(argname="argument ip", value=ip, expected_type=type_hints["ip"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "ip": ip,
        }

    @builtins.property
    def ip(self) -> builtins.str:
        '''An IPv4 or IPv6 CIDR block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ip ZeroTrustAccessGroup#ip}
        '''
        result = self._values.get("ip")
        assert result is not None, "Required property 'ip' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupRequireIp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireIpListStruct",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class ZeroTrustAccessGroupRequireIpListStruct:
    def __init__(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created IP list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a520ca9a350168774877fee702c4906017ae9fe6178e247dbc2a626d3a75b08)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of a previously created IP list.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupRequireIpListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupRequireIpListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireIpListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__57c6b0355a4865ec155a85e51480702b4e6be09e832642e873a104a0bd3e1ac0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

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
            type_hints = typing.get_type_hints(_typecheckingstub__695c539aa55b49cdd56a3272bd441cf655fa3554b54554fc64b8bd71ef57cfca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireIpListStruct]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireIpListStruct]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireIpListStruct]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d3366e1c9107ecfe499be8c0ccd340accfae606ff3aa1dd634d3b842f19ad6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustAccessGroupRequireIpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireIpOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__65a100274e866289666c7ad9ece14c741536f4a1a621276eb808a007ac089b48)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="ipInput")
    def ip_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipInput"))

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ip"))

    @ip.setter
    def ip(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8643f90e4c3c2c135a47f3f17045cc2d27d1d52e1b510a6b3b8346667a3ca3eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ip", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireIp]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireIp]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireIp]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f4584319602f68c573d705d279bb7dc5ca05d1fe5942f319c86ad7bb6b563f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireLinkedAppToken",
    jsii_struct_bases=[],
    name_mapping={"app_uid": "appUid"},
)
class ZeroTrustAccessGroupRequireLinkedAppToken:
    def __init__(self, *, app_uid: builtins.str) -> None:
        '''
        :param app_uid: The ID of an Access OIDC SaaS application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#app_uid ZeroTrustAccessGroup#app_uid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40b238bc761fe258fbbf604e084d504d2d605c322d7fa20da5252e21930c2263)
            check_type(argname="argument app_uid", value=app_uid, expected_type=type_hints["app_uid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "app_uid": app_uid,
        }

    @builtins.property
    def app_uid(self) -> builtins.str:
        '''The ID of an Access OIDC SaaS application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#app_uid ZeroTrustAccessGroup#app_uid}
        '''
        result = self._values.get("app_uid")
        assert result is not None, "Required property 'app_uid' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupRequireLinkedAppToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupRequireLinkedAppTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireLinkedAppTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0a68bf5e80be45e1c17e469dad4ad884fba77346021b1daef6c116df7e0a8c6b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="appUidInput")
    def app_uid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "appUidInput"))

    @builtins.property
    @jsii.member(jsii_name="appUid")
    def app_uid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appUid"))

    @app_uid.setter
    def app_uid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0ac374c6e1270ac9cc9b044549916dca7acf56cb5beb9e03aa32eae32bae423)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "appUid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireLinkedAppToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireLinkedAppToken]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireLinkedAppToken]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0475a10c091aadbe60c875eab4826afd80f6b8beb67170a9dab4d78bb4974c6f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustAccessGroupRequireList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6fa00056a098356a1ae19708403471340b9c001f470c23e2fb86dc6756341d1e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ZeroTrustAccessGroupRequireOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12abdf2c6c1cf70d62d05b78d68e4f68d17592abdf1c09338267075c395584ae)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ZeroTrustAccessGroupRequireOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61e534485bc1a0ad3822b37c3cd3a0691ba2a4cb06087436b2d54a1a48ed2a7a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__80345b5525f385fbcec11480ebdd07630b9d296fcfa56ee73f01fcc0a5c83357)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2f42369e5cbfcc9915d1e1490fb80ad67ff70daf9a1210d3bf08ac4771e39dc3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessGroupRequire]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessGroupRequire]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessGroupRequire]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b356ec6f08bc59e0ee3fe7c488c7f7aa4d187ebd0ecb6fe47e340c4bfdc3c53)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireLoginMethod",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class ZeroTrustAccessGroupRequireLoginMethod:
    def __init__(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of an identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fb3b4846cee2afa4b1b543c8662fdb839fa8c34c99a3b712aa236c1d1178646)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of an identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupRequireLoginMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupRequireLoginMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireLoginMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c9e540d0251497d4c7dcb5d0b8c543be771c286d17f5c6bbaf9da1fed0ec0fd1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

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
            type_hints = typing.get_type_hints(_typecheckingstub__4cf566d2f85f0675d1b321b4ac32c688710ffb4341ff9574252e1452c7b6c80e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireLoginMethod]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireLoginMethod]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireLoginMethod]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bee2175879d78c60af7c82693cc1b6d6675565833e8cacfc1a69e0adb4e38fa6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireOidc",
    jsii_struct_bases=[],
    name_mapping={
        "claim_name": "claimName",
        "claim_value": "claimValue",
        "identity_provider_id": "identityProviderId",
    },
)
class ZeroTrustAccessGroupRequireOidc:
    def __init__(
        self,
        *,
        claim_name: builtins.str,
        claim_value: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param claim_name: The name of the OIDC claim. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#claim_name ZeroTrustAccessGroup#claim_name}
        :param claim_value: The OIDC claim value to look for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#claim_value ZeroTrustAccessGroup#claim_value}
        :param identity_provider_id: The ID of your OIDC identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__748f0d146ba164a2af8aa776d45a546ba63c4100c73a4bd37785a2f0544fd303)
            check_type(argname="argument claim_name", value=claim_name, expected_type=type_hints["claim_name"])
            check_type(argname="argument claim_value", value=claim_value, expected_type=type_hints["claim_value"])
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "claim_name": claim_name,
            "claim_value": claim_value,
            "identity_provider_id": identity_provider_id,
        }

    @builtins.property
    def claim_name(self) -> builtins.str:
        '''The name of the OIDC claim.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#claim_name ZeroTrustAccessGroup#claim_name}
        '''
        result = self._values.get("claim_name")
        assert result is not None, "Required property 'claim_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def claim_value(self) -> builtins.str:
        '''The OIDC claim value to look for.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#claim_value ZeroTrustAccessGroup#claim_value}
        '''
        result = self._values.get("claim_value")
        assert result is not None, "Required property 'claim_value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your OIDC identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupRequireOidc(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupRequireOidcOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireOidcOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7c98fa47604d73dbedcabb1099942b12cc8104fae064acb677f7113f213cd4f3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="claimNameInput")
    def claim_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "claimNameInput"))

    @builtins.property
    @jsii.member(jsii_name="claimValueInput")
    def claim_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "claimValueInput"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderIdInput")
    def identity_provider_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityProviderIdInput"))

    @builtins.property
    @jsii.member(jsii_name="claimName")
    def claim_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "claimName"))

    @claim_name.setter
    def claim_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38e717770418a922ded0d550b333d6091240293110e5d7a36fe75f03cd70189b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "claimName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="claimValue")
    def claim_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "claimValue"))

    @claim_value.setter
    def claim_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2e8e8f42514a5785db74dec2dcf4bad053062a326a31ca36900943ac43cf270)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "claimValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d0af12600d1714b4db27099ab1ed9d884cc97ffc86478678a85334940edc055)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireOidc]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireOidc]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireOidc]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea0652d9eebae8a321cec4796344cc72cbc34031f77833478f958e9985b26487)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireOkta",
    jsii_struct_bases=[],
    name_mapping={"identity_provider_id": "identityProviderId", "name": "name"},
)
class ZeroTrustAccessGroupRequireOkta:
    def __init__(
        self,
        *,
        identity_provider_id: builtins.str,
        name: builtins.str,
    ) -> None:
        '''
        :param identity_provider_id: The ID of your Okta identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        :param name: The name of the Okta group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#name ZeroTrustAccessGroup#name}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__596d2d5ee2f2cc5f7fc9d74eede2ffc5f802656fbca444f9584573dfe9f3fc88)
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "identity_provider_id": identity_provider_id,
            "name": name,
        }

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your Okta identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the Okta group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#name ZeroTrustAccessGroup#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupRequireOkta(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupRequireOktaOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireOktaOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f9fc487bb8b95b652cc667b2de83b7a33889373303445057e6e4ddd28886ef14)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="identityProviderIdInput")
    def identity_provider_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityProviderIdInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d536862c1b9a64aff291d628354459a298e13c649d0d42fdcb114951e01bf6a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2bad6ca07f1f3f2579b493036b5eec198d8800c74e468b5212da00770d1c3c68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireOkta]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireOkta]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireOkta]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ebde3cd98b9155d9fb01d20f01b87661807c3617f5bd108ed00978322cd2700)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustAccessGroupRequireOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__32a4dd748855cd6983554ca74604a33b3e22a100cd0cb4a406668abd7be1d85a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putAnyValidServiceToken")
    def put_any_valid_service_token(self) -> None:
        value = ZeroTrustAccessGroupRequireAnyValidServiceToken()

        return typing.cast(None, jsii.invoke(self, "putAnyValidServiceToken", [value]))

    @jsii.member(jsii_name="putAuthContext")
    def put_auth_context(
        self,
        *,
        ac_id: builtins.str,
        id: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param ac_id: The ACID of an Authentication context. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ac_id ZeroTrustAccessGroup#ac_id}
        :param id: The ID of an Authentication context. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider_id: The ID of your Azure identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        value = ZeroTrustAccessGroupRequireAuthContext(
            ac_id=ac_id, id=id, identity_provider_id=identity_provider_id
        )

        return typing.cast(None, jsii.invoke(self, "putAuthContext", [value]))

    @jsii.member(jsii_name="putAuthMethod")
    def put_auth_method(self, *, auth_method: builtins.str) -> None:
        '''
        :param auth_method: The type of authentication method https://datatracker.ietf.org/doc/html/rfc8176#section-2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#auth_method ZeroTrustAccessGroup#auth_method}
        '''
        value = ZeroTrustAccessGroupRequireAuthMethod(auth_method=auth_method)

        return typing.cast(None, jsii.invoke(self, "putAuthMethod", [value]))

    @jsii.member(jsii_name="putAzureAd")
    def put_azure_ad(
        self,
        *,
        id: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param id: The ID of an Azure group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider_id: The ID of your Azure identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        value = ZeroTrustAccessGroupRequireAzureAd(
            id=id, identity_provider_id=identity_provider_id
        )

        return typing.cast(None, jsii.invoke(self, "putAzureAd", [value]))

    @jsii.member(jsii_name="putCertificate")
    def put_certificate(self) -> None:
        value = ZeroTrustAccessGroupRequireCertificate()

        return typing.cast(None, jsii.invoke(self, "putCertificate", [value]))

    @jsii.member(jsii_name="putCommonName")
    def put_common_name(self, *, common_name: builtins.str) -> None:
        '''
        :param common_name: The common name to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#common_name ZeroTrustAccessGroup#common_name}
        '''
        value = ZeroTrustAccessGroupRequireCommonName(common_name=common_name)

        return typing.cast(None, jsii.invoke(self, "putCommonName", [value]))

    @jsii.member(jsii_name="putDevicePosture")
    def put_device_posture(self, *, integration_uid: builtins.str) -> None:
        '''
        :param integration_uid: The ID of a device posture integration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#integration_uid ZeroTrustAccessGroup#integration_uid}
        '''
        value = ZeroTrustAccessGroupRequireDevicePosture(
            integration_uid=integration_uid
        )

        return typing.cast(None, jsii.invoke(self, "putDevicePosture", [value]))

    @jsii.member(jsii_name="putEmail")
    def put_email(self, *, email: builtins.str) -> None:
        '''
        :param email: The email of the user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email ZeroTrustAccessGroup#email}
        '''
        value = ZeroTrustAccessGroupRequireEmail(email=email)

        return typing.cast(None, jsii.invoke(self, "putEmail", [value]))

    @jsii.member(jsii_name="putEmailDomain")
    def put_email_domain(self, *, domain: builtins.str) -> None:
        '''
        :param domain: The email domain to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#domain ZeroTrustAccessGroup#domain}
        '''
        value = ZeroTrustAccessGroupRequireEmailDomain(domain=domain)

        return typing.cast(None, jsii.invoke(self, "putEmailDomain", [value]))

    @jsii.member(jsii_name="putEmailList")
    def put_email_list(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created email list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        value = ZeroTrustAccessGroupRequireEmailListStruct(id=id)

        return typing.cast(None, jsii.invoke(self, "putEmailList", [value]))

    @jsii.member(jsii_name="putEveryone")
    def put_everyone(self) -> None:
        value = ZeroTrustAccessGroupRequireEveryone()

        return typing.cast(None, jsii.invoke(self, "putEveryone", [value]))

    @jsii.member(jsii_name="putExternalEvaluation")
    def put_external_evaluation(
        self,
        *,
        evaluate_url: builtins.str,
        keys_url: builtins.str,
    ) -> None:
        '''
        :param evaluate_url: The API endpoint containing your business logic. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#evaluate_url ZeroTrustAccessGroup#evaluate_url}
        :param keys_url: The API endpoint containing the key that Access uses to verify that the response came from your API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#keys_url ZeroTrustAccessGroup#keys_url}
        '''
        value = ZeroTrustAccessGroupRequireExternalEvaluation(
            evaluate_url=evaluate_url, keys_url=keys_url
        )

        return typing.cast(None, jsii.invoke(self, "putExternalEvaluation", [value]))

    @jsii.member(jsii_name="putGeo")
    def put_geo(self, *, country_code: builtins.str) -> None:
        '''
        :param country_code: The country code that should be matched. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#country_code ZeroTrustAccessGroup#country_code}
        '''
        value = ZeroTrustAccessGroupRequireGeo(country_code=country_code)

        return typing.cast(None, jsii.invoke(self, "putGeo", [value]))

    @jsii.member(jsii_name="putGithubOrganization")
    def put_github_organization(
        self,
        *,
        identity_provider_id: builtins.str,
        name: builtins.str,
        team: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param identity_provider_id: The ID of your Github identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        :param name: The name of the organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#name ZeroTrustAccessGroup#name}
        :param team: The name of the team. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#team ZeroTrustAccessGroup#team}
        '''
        value = ZeroTrustAccessGroupRequireGithubOrganization(
            identity_provider_id=identity_provider_id, name=name, team=team
        )

        return typing.cast(None, jsii.invoke(self, "putGithubOrganization", [value]))

    @jsii.member(jsii_name="putGroup")
    def put_group(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created Access group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        value = ZeroTrustAccessGroupRequireGroup(id=id)

        return typing.cast(None, jsii.invoke(self, "putGroup", [value]))

    @jsii.member(jsii_name="putGsuite")
    def put_gsuite(
        self,
        *,
        email: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param email: The email of the Google Workspace group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#email ZeroTrustAccessGroup#email}
        :param identity_provider_id: The ID of your Google Workspace identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        value = ZeroTrustAccessGroupRequireGsuite(
            email=email, identity_provider_id=identity_provider_id
        )

        return typing.cast(None, jsii.invoke(self, "putGsuite", [value]))

    @jsii.member(jsii_name="putIp")
    def put_ip(self, *, ip: builtins.str) -> None:
        '''
        :param ip: An IPv4 or IPv6 CIDR block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#ip ZeroTrustAccessGroup#ip}
        '''
        value = ZeroTrustAccessGroupRequireIp(ip=ip)

        return typing.cast(None, jsii.invoke(self, "putIp", [value]))

    @jsii.member(jsii_name="putIpList")
    def put_ip_list(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created IP list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        value = ZeroTrustAccessGroupRequireIpListStruct(id=id)

        return typing.cast(None, jsii.invoke(self, "putIpList", [value]))

    @jsii.member(jsii_name="putLinkedAppToken")
    def put_linked_app_token(self, *, app_uid: builtins.str) -> None:
        '''
        :param app_uid: The ID of an Access OIDC SaaS application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#app_uid ZeroTrustAccessGroup#app_uid}
        '''
        value = ZeroTrustAccessGroupRequireLinkedAppToken(app_uid=app_uid)

        return typing.cast(None, jsii.invoke(self, "putLinkedAppToken", [value]))

    @jsii.member(jsii_name="putLoginMethod")
    def put_login_method(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of an identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#id ZeroTrustAccessGroup#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        value = ZeroTrustAccessGroupRequireLoginMethod(id=id)

        return typing.cast(None, jsii.invoke(self, "putLoginMethod", [value]))

    @jsii.member(jsii_name="putOidc")
    def put_oidc(
        self,
        *,
        claim_name: builtins.str,
        claim_value: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param claim_name: The name of the OIDC claim. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#claim_name ZeroTrustAccessGroup#claim_name}
        :param claim_value: The OIDC claim value to look for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#claim_value ZeroTrustAccessGroup#claim_value}
        :param identity_provider_id: The ID of your OIDC identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        value = ZeroTrustAccessGroupRequireOidc(
            claim_name=claim_name,
            claim_value=claim_value,
            identity_provider_id=identity_provider_id,
        )

        return typing.cast(None, jsii.invoke(self, "putOidc", [value]))

    @jsii.member(jsii_name="putOkta")
    def put_okta(
        self,
        *,
        identity_provider_id: builtins.str,
        name: builtins.str,
    ) -> None:
        '''
        :param identity_provider_id: The ID of your Okta identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        :param name: The name of the Okta group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#name ZeroTrustAccessGroup#name}
        '''
        value = ZeroTrustAccessGroupRequireOkta(
            identity_provider_id=identity_provider_id, name=name
        )

        return typing.cast(None, jsii.invoke(self, "putOkta", [value]))

    @jsii.member(jsii_name="putSaml")
    def put_saml(
        self,
        *,
        attribute_name: builtins.str,
        attribute_value: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param attribute_name: The name of the SAML attribute. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#attribute_name ZeroTrustAccessGroup#attribute_name}
        :param attribute_value: The SAML attribute value to look for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#attribute_value ZeroTrustAccessGroup#attribute_value}
        :param identity_provider_id: The ID of your SAML identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        value = ZeroTrustAccessGroupRequireSaml(
            attribute_name=attribute_name,
            attribute_value=attribute_value,
            identity_provider_id=identity_provider_id,
        )

        return typing.cast(None, jsii.invoke(self, "putSaml", [value]))

    @jsii.member(jsii_name="putServiceToken")
    def put_service_token(self, *, token_id: builtins.str) -> None:
        '''
        :param token_id: The ID of a Service Token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#token_id ZeroTrustAccessGroup#token_id}
        '''
        value = ZeroTrustAccessGroupRequireServiceToken(token_id=token_id)

        return typing.cast(None, jsii.invoke(self, "putServiceToken", [value]))

    @jsii.member(jsii_name="resetAnyValidServiceToken")
    def reset_any_valid_service_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAnyValidServiceToken", []))

    @jsii.member(jsii_name="resetAuthContext")
    def reset_auth_context(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthContext", []))

    @jsii.member(jsii_name="resetAuthMethod")
    def reset_auth_method(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthMethod", []))

    @jsii.member(jsii_name="resetAzureAd")
    def reset_azure_ad(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureAd", []))

    @jsii.member(jsii_name="resetCertificate")
    def reset_certificate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificate", []))

    @jsii.member(jsii_name="resetCommonName")
    def reset_common_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCommonName", []))

    @jsii.member(jsii_name="resetDevicePosture")
    def reset_device_posture(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDevicePosture", []))

    @jsii.member(jsii_name="resetEmail")
    def reset_email(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmail", []))

    @jsii.member(jsii_name="resetEmailDomain")
    def reset_email_domain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailDomain", []))

    @jsii.member(jsii_name="resetEmailList")
    def reset_email_list(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailList", []))

    @jsii.member(jsii_name="resetEveryone")
    def reset_everyone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEveryone", []))

    @jsii.member(jsii_name="resetExternalEvaluation")
    def reset_external_evaluation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExternalEvaluation", []))

    @jsii.member(jsii_name="resetGeo")
    def reset_geo(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGeo", []))

    @jsii.member(jsii_name="resetGithubOrganization")
    def reset_github_organization(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGithubOrganization", []))

    @jsii.member(jsii_name="resetGroup")
    def reset_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGroup", []))

    @jsii.member(jsii_name="resetGsuite")
    def reset_gsuite(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGsuite", []))

    @jsii.member(jsii_name="resetIp")
    def reset_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIp", []))

    @jsii.member(jsii_name="resetIpList")
    def reset_ip_list(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpList", []))

    @jsii.member(jsii_name="resetLinkedAppToken")
    def reset_linked_app_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLinkedAppToken", []))

    @jsii.member(jsii_name="resetLoginMethod")
    def reset_login_method(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLoginMethod", []))

    @jsii.member(jsii_name="resetOidc")
    def reset_oidc(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOidc", []))

    @jsii.member(jsii_name="resetOkta")
    def reset_okta(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOkta", []))

    @jsii.member(jsii_name="resetSaml")
    def reset_saml(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSaml", []))

    @jsii.member(jsii_name="resetServiceToken")
    def reset_service_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceToken", []))

    @builtins.property
    @jsii.member(jsii_name="anyValidServiceToken")
    def any_valid_service_token(
        self,
    ) -> ZeroTrustAccessGroupRequireAnyValidServiceTokenOutputReference:
        return typing.cast(ZeroTrustAccessGroupRequireAnyValidServiceTokenOutputReference, jsii.get(self, "anyValidServiceToken"))

    @builtins.property
    @jsii.member(jsii_name="authContext")
    def auth_context(self) -> ZeroTrustAccessGroupRequireAuthContextOutputReference:
        return typing.cast(ZeroTrustAccessGroupRequireAuthContextOutputReference, jsii.get(self, "authContext"))

    @builtins.property
    @jsii.member(jsii_name="authMethod")
    def auth_method(self) -> ZeroTrustAccessGroupRequireAuthMethodOutputReference:
        return typing.cast(ZeroTrustAccessGroupRequireAuthMethodOutputReference, jsii.get(self, "authMethod"))

    @builtins.property
    @jsii.member(jsii_name="azureAd")
    def azure_ad(self) -> ZeroTrustAccessGroupRequireAzureAdOutputReference:
        return typing.cast(ZeroTrustAccessGroupRequireAzureAdOutputReference, jsii.get(self, "azureAd"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> ZeroTrustAccessGroupRequireCertificateOutputReference:
        return typing.cast(ZeroTrustAccessGroupRequireCertificateOutputReference, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(self) -> ZeroTrustAccessGroupRequireCommonNameOutputReference:
        return typing.cast(ZeroTrustAccessGroupRequireCommonNameOutputReference, jsii.get(self, "commonName"))

    @builtins.property
    @jsii.member(jsii_name="devicePosture")
    def device_posture(self) -> ZeroTrustAccessGroupRequireDevicePostureOutputReference:
        return typing.cast(ZeroTrustAccessGroupRequireDevicePostureOutputReference, jsii.get(self, "devicePosture"))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(self) -> ZeroTrustAccessGroupRequireEmailOutputReference:
        return typing.cast(ZeroTrustAccessGroupRequireEmailOutputReference, jsii.get(self, "email"))

    @builtins.property
    @jsii.member(jsii_name="emailDomain")
    def email_domain(self) -> ZeroTrustAccessGroupRequireEmailDomainOutputReference:
        return typing.cast(ZeroTrustAccessGroupRequireEmailDomainOutputReference, jsii.get(self, "emailDomain"))

    @builtins.property
    @jsii.member(jsii_name="emailList")
    def email_list(self) -> ZeroTrustAccessGroupRequireEmailListStructOutputReference:
        return typing.cast(ZeroTrustAccessGroupRequireEmailListStructOutputReference, jsii.get(self, "emailList"))

    @builtins.property
    @jsii.member(jsii_name="everyone")
    def everyone(self) -> ZeroTrustAccessGroupRequireEveryoneOutputReference:
        return typing.cast(ZeroTrustAccessGroupRequireEveryoneOutputReference, jsii.get(self, "everyone"))

    @builtins.property
    @jsii.member(jsii_name="externalEvaluation")
    def external_evaluation(
        self,
    ) -> ZeroTrustAccessGroupRequireExternalEvaluationOutputReference:
        return typing.cast(ZeroTrustAccessGroupRequireExternalEvaluationOutputReference, jsii.get(self, "externalEvaluation"))

    @builtins.property
    @jsii.member(jsii_name="geo")
    def geo(self) -> ZeroTrustAccessGroupRequireGeoOutputReference:
        return typing.cast(ZeroTrustAccessGroupRequireGeoOutputReference, jsii.get(self, "geo"))

    @builtins.property
    @jsii.member(jsii_name="githubOrganization")
    def github_organization(
        self,
    ) -> ZeroTrustAccessGroupRequireGithubOrganizationOutputReference:
        return typing.cast(ZeroTrustAccessGroupRequireGithubOrganizationOutputReference, jsii.get(self, "githubOrganization"))

    @builtins.property
    @jsii.member(jsii_name="group")
    def group(self) -> ZeroTrustAccessGroupRequireGroupOutputReference:
        return typing.cast(ZeroTrustAccessGroupRequireGroupOutputReference, jsii.get(self, "group"))

    @builtins.property
    @jsii.member(jsii_name="gsuite")
    def gsuite(self) -> ZeroTrustAccessGroupRequireGsuiteOutputReference:
        return typing.cast(ZeroTrustAccessGroupRequireGsuiteOutputReference, jsii.get(self, "gsuite"))

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> ZeroTrustAccessGroupRequireIpOutputReference:
        return typing.cast(ZeroTrustAccessGroupRequireIpOutputReference, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="ipList")
    def ip_list(self) -> ZeroTrustAccessGroupRequireIpListStructOutputReference:
        return typing.cast(ZeroTrustAccessGroupRequireIpListStructOutputReference, jsii.get(self, "ipList"))

    @builtins.property
    @jsii.member(jsii_name="linkedAppToken")
    def linked_app_token(
        self,
    ) -> ZeroTrustAccessGroupRequireLinkedAppTokenOutputReference:
        return typing.cast(ZeroTrustAccessGroupRequireLinkedAppTokenOutputReference, jsii.get(self, "linkedAppToken"))

    @builtins.property
    @jsii.member(jsii_name="loginMethod")
    def login_method(self) -> ZeroTrustAccessGroupRequireLoginMethodOutputReference:
        return typing.cast(ZeroTrustAccessGroupRequireLoginMethodOutputReference, jsii.get(self, "loginMethod"))

    @builtins.property
    @jsii.member(jsii_name="oidc")
    def oidc(self) -> ZeroTrustAccessGroupRequireOidcOutputReference:
        return typing.cast(ZeroTrustAccessGroupRequireOidcOutputReference, jsii.get(self, "oidc"))

    @builtins.property
    @jsii.member(jsii_name="okta")
    def okta(self) -> ZeroTrustAccessGroupRequireOktaOutputReference:
        return typing.cast(ZeroTrustAccessGroupRequireOktaOutputReference, jsii.get(self, "okta"))

    @builtins.property
    @jsii.member(jsii_name="saml")
    def saml(self) -> "ZeroTrustAccessGroupRequireSamlOutputReference":
        return typing.cast("ZeroTrustAccessGroupRequireSamlOutputReference", jsii.get(self, "saml"))

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(self) -> "ZeroTrustAccessGroupRequireServiceTokenOutputReference":
        return typing.cast("ZeroTrustAccessGroupRequireServiceTokenOutputReference", jsii.get(self, "serviceToken"))

    @builtins.property
    @jsii.member(jsii_name="anyValidServiceTokenInput")
    def any_valid_service_token_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireAnyValidServiceToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireAnyValidServiceToken]], jsii.get(self, "anyValidServiceTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="authContextInput")
    def auth_context_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireAuthContext]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireAuthContext]], jsii.get(self, "authContextInput"))

    @builtins.property
    @jsii.member(jsii_name="authMethodInput")
    def auth_method_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireAuthMethod]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireAuthMethod]], jsii.get(self, "authMethodInput"))

    @builtins.property
    @jsii.member(jsii_name="azureAdInput")
    def azure_ad_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireAzureAd]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireAzureAd]], jsii.get(self, "azureAdInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateInput")
    def certificate_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireCertificate]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireCertificate]], jsii.get(self, "certificateInput"))

    @builtins.property
    @jsii.member(jsii_name="commonNameInput")
    def common_name_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireCommonName]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireCommonName]], jsii.get(self, "commonNameInput"))

    @builtins.property
    @jsii.member(jsii_name="devicePostureInput")
    def device_posture_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireDevicePosture]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireDevicePosture]], jsii.get(self, "devicePostureInput"))

    @builtins.property
    @jsii.member(jsii_name="emailDomainInput")
    def email_domain_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireEmailDomain]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireEmailDomain]], jsii.get(self, "emailDomainInput"))

    @builtins.property
    @jsii.member(jsii_name="emailInput")
    def email_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireEmail]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireEmail]], jsii.get(self, "emailInput"))

    @builtins.property
    @jsii.member(jsii_name="emailListInput")
    def email_list_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireEmailListStruct]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireEmailListStruct]], jsii.get(self, "emailListInput"))

    @builtins.property
    @jsii.member(jsii_name="everyoneInput")
    def everyone_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireEveryone]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireEveryone]], jsii.get(self, "everyoneInput"))

    @builtins.property
    @jsii.member(jsii_name="externalEvaluationInput")
    def external_evaluation_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireExternalEvaluation]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireExternalEvaluation]], jsii.get(self, "externalEvaluationInput"))

    @builtins.property
    @jsii.member(jsii_name="geoInput")
    def geo_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireGeo]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireGeo]], jsii.get(self, "geoInput"))

    @builtins.property
    @jsii.member(jsii_name="githubOrganizationInput")
    def github_organization_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireGithubOrganization]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireGithubOrganization]], jsii.get(self, "githubOrganizationInput"))

    @builtins.property
    @jsii.member(jsii_name="groupInput")
    def group_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireGroup]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireGroup]], jsii.get(self, "groupInput"))

    @builtins.property
    @jsii.member(jsii_name="gsuiteInput")
    def gsuite_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireGsuite]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireGsuite]], jsii.get(self, "gsuiteInput"))

    @builtins.property
    @jsii.member(jsii_name="ipInput")
    def ip_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireIp]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireIp]], jsii.get(self, "ipInput"))

    @builtins.property
    @jsii.member(jsii_name="ipListInput")
    def ip_list_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireIpListStruct]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireIpListStruct]], jsii.get(self, "ipListInput"))

    @builtins.property
    @jsii.member(jsii_name="linkedAppTokenInput")
    def linked_app_token_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireLinkedAppToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireLinkedAppToken]], jsii.get(self, "linkedAppTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="loginMethodInput")
    def login_method_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireLoginMethod]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireLoginMethod]], jsii.get(self, "loginMethodInput"))

    @builtins.property
    @jsii.member(jsii_name="oidcInput")
    def oidc_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireOidc]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireOidc]], jsii.get(self, "oidcInput"))

    @builtins.property
    @jsii.member(jsii_name="oktaInput")
    def okta_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireOkta]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireOkta]], jsii.get(self, "oktaInput"))

    @builtins.property
    @jsii.member(jsii_name="samlInput")
    def saml_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustAccessGroupRequireSaml"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustAccessGroupRequireSaml"]], jsii.get(self, "samlInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceTokenInput")
    def service_token_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustAccessGroupRequireServiceToken"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustAccessGroupRequireServiceToken"]], jsii.get(self, "serviceTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequire]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequire]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequire]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__782f3c3257a2c495484cf4b68698125a6bf9a47908f2f31af7a9589ca283699d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireSaml",
    jsii_struct_bases=[],
    name_mapping={
        "attribute_name": "attributeName",
        "attribute_value": "attributeValue",
        "identity_provider_id": "identityProviderId",
    },
)
class ZeroTrustAccessGroupRequireSaml:
    def __init__(
        self,
        *,
        attribute_name: builtins.str,
        attribute_value: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param attribute_name: The name of the SAML attribute. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#attribute_name ZeroTrustAccessGroup#attribute_name}
        :param attribute_value: The SAML attribute value to look for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#attribute_value ZeroTrustAccessGroup#attribute_value}
        :param identity_provider_id: The ID of your SAML identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80a7cf643df910694eccec445014db3d18bfd3c78e3e383deb0346e4c9d81e98)
            check_type(argname="argument attribute_name", value=attribute_name, expected_type=type_hints["attribute_name"])
            check_type(argname="argument attribute_value", value=attribute_value, expected_type=type_hints["attribute_value"])
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "attribute_name": attribute_name,
            "attribute_value": attribute_value,
            "identity_provider_id": identity_provider_id,
        }

    @builtins.property
    def attribute_name(self) -> builtins.str:
        '''The name of the SAML attribute.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#attribute_name ZeroTrustAccessGroup#attribute_name}
        '''
        result = self._values.get("attribute_name")
        assert result is not None, "Required property 'attribute_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attribute_value(self) -> builtins.str:
        '''The SAML attribute value to look for.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#attribute_value ZeroTrustAccessGroup#attribute_value}
        '''
        result = self._values.get("attribute_value")
        assert result is not None, "Required property 'attribute_value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your SAML identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#identity_provider_id ZeroTrustAccessGroup#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupRequireSaml(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupRequireSamlOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireSamlOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c42f1729a5e90171eab14013f86a44d468948fca3c92c1a685a3c8c1afccf6de)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="attributeNameInput")
    def attribute_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "attributeNameInput"))

    @builtins.property
    @jsii.member(jsii_name="attributeValueInput")
    def attribute_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "attributeValueInput"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderIdInput")
    def identity_provider_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityProviderIdInput"))

    @builtins.property
    @jsii.member(jsii_name="attributeName")
    def attribute_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "attributeName"))

    @attribute_name.setter
    def attribute_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41b93d70d600bba40fecf7cd59cbe8d38de61b8b0238fbc931c327338ffc0e7d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attributeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="attributeValue")
    def attribute_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "attributeValue"))

    @attribute_value.setter
    def attribute_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53c2eed3237d89dfa90839da4d602e18e5e9ec84b4d874b0f32850b06e9948ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attributeValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80cb8192e0e33995c10c861debcd79de90de8876ee603b415bcf59cf6fdd535f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireSaml]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireSaml]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireSaml]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__719bcc7f6e4779e45570275a22f8d5fa3ea67a04fcc03938b1f90ffedd7ee290)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireServiceToken",
    jsii_struct_bases=[],
    name_mapping={"token_id": "tokenId"},
)
class ZeroTrustAccessGroupRequireServiceToken:
    def __init__(self, *, token_id: builtins.str) -> None:
        '''
        :param token_id: The ID of a Service Token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#token_id ZeroTrustAccessGroup#token_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54d73e737db65201846c0ace501e34528b03a26a2bd178b9755302a0713bd9a4)
            check_type(argname="argument token_id", value=token_id, expected_type=type_hints["token_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "token_id": token_id,
        }

    @builtins.property
    def token_id(self) -> builtins.str:
        '''The ID of a Service Token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_group#token_id ZeroTrustAccessGroup#token_id}
        '''
        result = self._values.get("token_id")
        assert result is not None, "Required property 'token_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessGroupRequireServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessGroupRequireServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessGroup.ZeroTrustAccessGroupRequireServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__268f35bde87425d85df9ba82bcdc14c1f384fb24a444d216818aa41d3320b8f5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="tokenIdInput")
    def token_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenIdInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenId")
    def token_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tokenId"))

    @token_id.setter
    def token_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fe8032d860a2bcb55df53a073379217739ce6740a63155a89752b2ae9eea648)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireServiceToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireServiceToken]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireServiceToken]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a81a1b88ff228ba1875005a9c9223b15e31497a2c78537ee167ab79545eb1b8a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ZeroTrustAccessGroup",
    "ZeroTrustAccessGroupConfig",
    "ZeroTrustAccessGroupExclude",
    "ZeroTrustAccessGroupExcludeAnyValidServiceToken",
    "ZeroTrustAccessGroupExcludeAnyValidServiceTokenOutputReference",
    "ZeroTrustAccessGroupExcludeAuthContext",
    "ZeroTrustAccessGroupExcludeAuthContextOutputReference",
    "ZeroTrustAccessGroupExcludeAuthMethod",
    "ZeroTrustAccessGroupExcludeAuthMethodOutputReference",
    "ZeroTrustAccessGroupExcludeAzureAd",
    "ZeroTrustAccessGroupExcludeAzureAdOutputReference",
    "ZeroTrustAccessGroupExcludeCertificate",
    "ZeroTrustAccessGroupExcludeCertificateOutputReference",
    "ZeroTrustAccessGroupExcludeCommonName",
    "ZeroTrustAccessGroupExcludeCommonNameOutputReference",
    "ZeroTrustAccessGroupExcludeDevicePosture",
    "ZeroTrustAccessGroupExcludeDevicePostureOutputReference",
    "ZeroTrustAccessGroupExcludeEmail",
    "ZeroTrustAccessGroupExcludeEmailDomain",
    "ZeroTrustAccessGroupExcludeEmailDomainOutputReference",
    "ZeroTrustAccessGroupExcludeEmailListStruct",
    "ZeroTrustAccessGroupExcludeEmailListStructOutputReference",
    "ZeroTrustAccessGroupExcludeEmailOutputReference",
    "ZeroTrustAccessGroupExcludeEveryone",
    "ZeroTrustAccessGroupExcludeEveryoneOutputReference",
    "ZeroTrustAccessGroupExcludeExternalEvaluation",
    "ZeroTrustAccessGroupExcludeExternalEvaluationOutputReference",
    "ZeroTrustAccessGroupExcludeGeo",
    "ZeroTrustAccessGroupExcludeGeoOutputReference",
    "ZeroTrustAccessGroupExcludeGithubOrganization",
    "ZeroTrustAccessGroupExcludeGithubOrganizationOutputReference",
    "ZeroTrustAccessGroupExcludeGroup",
    "ZeroTrustAccessGroupExcludeGroupOutputReference",
    "ZeroTrustAccessGroupExcludeGsuite",
    "ZeroTrustAccessGroupExcludeGsuiteOutputReference",
    "ZeroTrustAccessGroupExcludeIp",
    "ZeroTrustAccessGroupExcludeIpListStruct",
    "ZeroTrustAccessGroupExcludeIpListStructOutputReference",
    "ZeroTrustAccessGroupExcludeIpOutputReference",
    "ZeroTrustAccessGroupExcludeLinkedAppToken",
    "ZeroTrustAccessGroupExcludeLinkedAppTokenOutputReference",
    "ZeroTrustAccessGroupExcludeList",
    "ZeroTrustAccessGroupExcludeLoginMethod",
    "ZeroTrustAccessGroupExcludeLoginMethodOutputReference",
    "ZeroTrustAccessGroupExcludeOidc",
    "ZeroTrustAccessGroupExcludeOidcOutputReference",
    "ZeroTrustAccessGroupExcludeOkta",
    "ZeroTrustAccessGroupExcludeOktaOutputReference",
    "ZeroTrustAccessGroupExcludeOutputReference",
    "ZeroTrustAccessGroupExcludeSaml",
    "ZeroTrustAccessGroupExcludeSamlOutputReference",
    "ZeroTrustAccessGroupExcludeServiceToken",
    "ZeroTrustAccessGroupExcludeServiceTokenOutputReference",
    "ZeroTrustAccessGroupInclude",
    "ZeroTrustAccessGroupIncludeAnyValidServiceToken",
    "ZeroTrustAccessGroupIncludeAnyValidServiceTokenOutputReference",
    "ZeroTrustAccessGroupIncludeAuthContext",
    "ZeroTrustAccessGroupIncludeAuthContextOutputReference",
    "ZeroTrustAccessGroupIncludeAuthMethod",
    "ZeroTrustAccessGroupIncludeAuthMethodOutputReference",
    "ZeroTrustAccessGroupIncludeAzureAd",
    "ZeroTrustAccessGroupIncludeAzureAdOutputReference",
    "ZeroTrustAccessGroupIncludeCertificate",
    "ZeroTrustAccessGroupIncludeCertificateOutputReference",
    "ZeroTrustAccessGroupIncludeCommonName",
    "ZeroTrustAccessGroupIncludeCommonNameOutputReference",
    "ZeroTrustAccessGroupIncludeDevicePosture",
    "ZeroTrustAccessGroupIncludeDevicePostureOutputReference",
    "ZeroTrustAccessGroupIncludeEmail",
    "ZeroTrustAccessGroupIncludeEmailDomain",
    "ZeroTrustAccessGroupIncludeEmailDomainOutputReference",
    "ZeroTrustAccessGroupIncludeEmailListStruct",
    "ZeroTrustAccessGroupIncludeEmailListStructOutputReference",
    "ZeroTrustAccessGroupIncludeEmailOutputReference",
    "ZeroTrustAccessGroupIncludeEveryone",
    "ZeroTrustAccessGroupIncludeEveryoneOutputReference",
    "ZeroTrustAccessGroupIncludeExternalEvaluation",
    "ZeroTrustAccessGroupIncludeExternalEvaluationOutputReference",
    "ZeroTrustAccessGroupIncludeGeo",
    "ZeroTrustAccessGroupIncludeGeoOutputReference",
    "ZeroTrustAccessGroupIncludeGithubOrganization",
    "ZeroTrustAccessGroupIncludeGithubOrganizationOutputReference",
    "ZeroTrustAccessGroupIncludeGroup",
    "ZeroTrustAccessGroupIncludeGroupOutputReference",
    "ZeroTrustAccessGroupIncludeGsuite",
    "ZeroTrustAccessGroupIncludeGsuiteOutputReference",
    "ZeroTrustAccessGroupIncludeIp",
    "ZeroTrustAccessGroupIncludeIpListStruct",
    "ZeroTrustAccessGroupIncludeIpListStructOutputReference",
    "ZeroTrustAccessGroupIncludeIpOutputReference",
    "ZeroTrustAccessGroupIncludeLinkedAppToken",
    "ZeroTrustAccessGroupIncludeLinkedAppTokenOutputReference",
    "ZeroTrustAccessGroupIncludeList",
    "ZeroTrustAccessGroupIncludeLoginMethod",
    "ZeroTrustAccessGroupIncludeLoginMethodOutputReference",
    "ZeroTrustAccessGroupIncludeOidc",
    "ZeroTrustAccessGroupIncludeOidcOutputReference",
    "ZeroTrustAccessGroupIncludeOkta",
    "ZeroTrustAccessGroupIncludeOktaOutputReference",
    "ZeroTrustAccessGroupIncludeOutputReference",
    "ZeroTrustAccessGroupIncludeSaml",
    "ZeroTrustAccessGroupIncludeSamlOutputReference",
    "ZeroTrustAccessGroupIncludeServiceToken",
    "ZeroTrustAccessGroupIncludeServiceTokenOutputReference",
    "ZeroTrustAccessGroupRequire",
    "ZeroTrustAccessGroupRequireAnyValidServiceToken",
    "ZeroTrustAccessGroupRequireAnyValidServiceTokenOutputReference",
    "ZeroTrustAccessGroupRequireAuthContext",
    "ZeroTrustAccessGroupRequireAuthContextOutputReference",
    "ZeroTrustAccessGroupRequireAuthMethod",
    "ZeroTrustAccessGroupRequireAuthMethodOutputReference",
    "ZeroTrustAccessGroupRequireAzureAd",
    "ZeroTrustAccessGroupRequireAzureAdOutputReference",
    "ZeroTrustAccessGroupRequireCertificate",
    "ZeroTrustAccessGroupRequireCertificateOutputReference",
    "ZeroTrustAccessGroupRequireCommonName",
    "ZeroTrustAccessGroupRequireCommonNameOutputReference",
    "ZeroTrustAccessGroupRequireDevicePosture",
    "ZeroTrustAccessGroupRequireDevicePostureOutputReference",
    "ZeroTrustAccessGroupRequireEmail",
    "ZeroTrustAccessGroupRequireEmailDomain",
    "ZeroTrustAccessGroupRequireEmailDomainOutputReference",
    "ZeroTrustAccessGroupRequireEmailListStruct",
    "ZeroTrustAccessGroupRequireEmailListStructOutputReference",
    "ZeroTrustAccessGroupRequireEmailOutputReference",
    "ZeroTrustAccessGroupRequireEveryone",
    "ZeroTrustAccessGroupRequireEveryoneOutputReference",
    "ZeroTrustAccessGroupRequireExternalEvaluation",
    "ZeroTrustAccessGroupRequireExternalEvaluationOutputReference",
    "ZeroTrustAccessGroupRequireGeo",
    "ZeroTrustAccessGroupRequireGeoOutputReference",
    "ZeroTrustAccessGroupRequireGithubOrganization",
    "ZeroTrustAccessGroupRequireGithubOrganizationOutputReference",
    "ZeroTrustAccessGroupRequireGroup",
    "ZeroTrustAccessGroupRequireGroupOutputReference",
    "ZeroTrustAccessGroupRequireGsuite",
    "ZeroTrustAccessGroupRequireGsuiteOutputReference",
    "ZeroTrustAccessGroupRequireIp",
    "ZeroTrustAccessGroupRequireIpListStruct",
    "ZeroTrustAccessGroupRequireIpListStructOutputReference",
    "ZeroTrustAccessGroupRequireIpOutputReference",
    "ZeroTrustAccessGroupRequireLinkedAppToken",
    "ZeroTrustAccessGroupRequireLinkedAppTokenOutputReference",
    "ZeroTrustAccessGroupRequireList",
    "ZeroTrustAccessGroupRequireLoginMethod",
    "ZeroTrustAccessGroupRequireLoginMethodOutputReference",
    "ZeroTrustAccessGroupRequireOidc",
    "ZeroTrustAccessGroupRequireOidcOutputReference",
    "ZeroTrustAccessGroupRequireOkta",
    "ZeroTrustAccessGroupRequireOktaOutputReference",
    "ZeroTrustAccessGroupRequireOutputReference",
    "ZeroTrustAccessGroupRequireSaml",
    "ZeroTrustAccessGroupRequireSamlOutputReference",
    "ZeroTrustAccessGroupRequireServiceToken",
    "ZeroTrustAccessGroupRequireServiceTokenOutputReference",
]

publication.publish()

def _typecheckingstub__23b8565a975674909f1ebeeedba58fe2284efca31d92de03bb26e485aed38248(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    include: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustAccessGroupInclude, typing.Dict[builtins.str, typing.Any]]]],
    name: builtins.str,
    account_id: typing.Optional[builtins.str] = None,
    exclude: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustAccessGroupExclude, typing.Dict[builtins.str, typing.Any]]]]] = None,
    is_default: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    require: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustAccessGroupRequire, typing.Dict[builtins.str, typing.Any]]]]] = None,
    zone_id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__d4d01177b10c75fce53a506600ccbffd4b52eee31889acab160899dd38bf86ec(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c70d0a9b35ff4cb45f933520027bca1ea4b9848c771ee8281912a577183440d(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustAccessGroupExclude, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0319cb7c9c38b726f1a9534fcb6772539470bf867a4ee6a9b136bc1fd5e10dad(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustAccessGroupInclude, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7daedfd2ebb78dd4e0b2e900469d546570d7b583e431877505ade16cea987bc7(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustAccessGroupRequire, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__913e3ba7c5a4e602e693172256207d474beaa5a445dc60fdc1d5bfdf7c53f088(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b6759beba719c0e4ef03e39964f38b4307e3c6fa1a0df5a5431059e60195d73(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2ba14b8b09b8022bc34a4d18d1fe27a0c37fdfe75f1a088d0095acad31084d7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2815e3f53d5045dcacb219cb791a53f83ea3a08be166953061bbbfbdcecb73f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ceb08f483d09781f38c84657e26fa8b9c737c1ab7375a4373ef7e726ccdb6fcd(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    include: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustAccessGroupInclude, typing.Dict[builtins.str, typing.Any]]]],
    name: builtins.str,
    account_id: typing.Optional[builtins.str] = None,
    exclude: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustAccessGroupExclude, typing.Dict[builtins.str, typing.Any]]]]] = None,
    is_default: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    require: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustAccessGroupRequire, typing.Dict[builtins.str, typing.Any]]]]] = None,
    zone_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__032a7b58f7e87dcd85c1e29db2bd7d9c98c3061cadf55e8a8b5a9dae1359b75e(
    *,
    any_valid_service_token: typing.Optional[typing.Union[ZeroTrustAccessGroupExcludeAnyValidServiceToken, typing.Dict[builtins.str, typing.Any]]] = None,
    auth_context: typing.Optional[typing.Union[ZeroTrustAccessGroupExcludeAuthContext, typing.Dict[builtins.str, typing.Any]]] = None,
    auth_method: typing.Optional[typing.Union[ZeroTrustAccessGroupExcludeAuthMethod, typing.Dict[builtins.str, typing.Any]]] = None,
    azure_ad: typing.Optional[typing.Union[ZeroTrustAccessGroupExcludeAzureAd, typing.Dict[builtins.str, typing.Any]]] = None,
    certificate: typing.Optional[typing.Union[ZeroTrustAccessGroupExcludeCertificate, typing.Dict[builtins.str, typing.Any]]] = None,
    common_name: typing.Optional[typing.Union[ZeroTrustAccessGroupExcludeCommonName, typing.Dict[builtins.str, typing.Any]]] = None,
    device_posture: typing.Optional[typing.Union[ZeroTrustAccessGroupExcludeDevicePosture, typing.Dict[builtins.str, typing.Any]]] = None,
    email: typing.Optional[typing.Union[ZeroTrustAccessGroupExcludeEmail, typing.Dict[builtins.str, typing.Any]]] = None,
    email_domain: typing.Optional[typing.Union[ZeroTrustAccessGroupExcludeEmailDomain, typing.Dict[builtins.str, typing.Any]]] = None,
    email_list: typing.Optional[typing.Union[ZeroTrustAccessGroupExcludeEmailListStruct, typing.Dict[builtins.str, typing.Any]]] = None,
    everyone: typing.Optional[typing.Union[ZeroTrustAccessGroupExcludeEveryone, typing.Dict[builtins.str, typing.Any]]] = None,
    external_evaluation: typing.Optional[typing.Union[ZeroTrustAccessGroupExcludeExternalEvaluation, typing.Dict[builtins.str, typing.Any]]] = None,
    geo: typing.Optional[typing.Union[ZeroTrustAccessGroupExcludeGeo, typing.Dict[builtins.str, typing.Any]]] = None,
    github_organization: typing.Optional[typing.Union[ZeroTrustAccessGroupExcludeGithubOrganization, typing.Dict[builtins.str, typing.Any]]] = None,
    group: typing.Optional[typing.Union[ZeroTrustAccessGroupExcludeGroup, typing.Dict[builtins.str, typing.Any]]] = None,
    gsuite: typing.Optional[typing.Union[ZeroTrustAccessGroupExcludeGsuite, typing.Dict[builtins.str, typing.Any]]] = None,
    ip: typing.Optional[typing.Union[ZeroTrustAccessGroupExcludeIp, typing.Dict[builtins.str, typing.Any]]] = None,
    ip_list: typing.Optional[typing.Union[ZeroTrustAccessGroupExcludeIpListStruct, typing.Dict[builtins.str, typing.Any]]] = None,
    linked_app_token: typing.Optional[typing.Union[ZeroTrustAccessGroupExcludeLinkedAppToken, typing.Dict[builtins.str, typing.Any]]] = None,
    login_method: typing.Optional[typing.Union[ZeroTrustAccessGroupExcludeLoginMethod, typing.Dict[builtins.str, typing.Any]]] = None,
    oidc: typing.Optional[typing.Union[ZeroTrustAccessGroupExcludeOidc, typing.Dict[builtins.str, typing.Any]]] = None,
    okta: typing.Optional[typing.Union[ZeroTrustAccessGroupExcludeOkta, typing.Dict[builtins.str, typing.Any]]] = None,
    saml: typing.Optional[typing.Union[ZeroTrustAccessGroupExcludeSaml, typing.Dict[builtins.str, typing.Any]]] = None,
    service_token: typing.Optional[typing.Union[ZeroTrustAccessGroupExcludeServiceToken, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94507dfda0f4ea3199e55b6428ebe1f9134b35b8e5db63367dfa8f8713ae6bbd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22b5307473370c0fbc7e4bff0bca6e703b64c05daf636d5c08fb5c82c901f6cc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeAnyValidServiceToken]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b692cbf7c9373b74e90abe89cdf54fae7d7570d85f2c806a667fe0327c61d441(
    *,
    ac_id: builtins.str,
    id: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6dd22640557a54ab7fac4583ccb93edc2832b8c72e5155b0d4ce99f8c1bf928a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff9626f35b818801ef5a726a3d0fd4a00d9f202d481c740bfa286df2f10929b0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41ba3b0d759efac495885a0ccdc2fd401a70cda628054bffaafade842d9296d3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d35ade58ab0cccfa3613fdf797e90cbfd9cd732c0e4151e769e3b82ba6f48fef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93ddf7ca01f2f3d49c5bf469447796f9b20e0f4a99ce4b18757942d9af92d88c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeAuthContext]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1200353abb6ec161d0dbd9f248423674b76fe99ed357ccc477539176da562d7a(
    *,
    auth_method: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9ddc42dc13d4633beca2261583536ec7bd881ad94faab066729bfb7fd776e30(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0af2d9992d402a20041fcb644ab6cbbe65472a307fbd2e2dc37d9dc3e89d6b0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e72a250949a0051233d514e140acc3de44c9d87676721324d7f8e2130bcc061(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeAuthMethod]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3744c8fb1d9f353274bb499b904237207c1273f3656d94e049081c8c2dd688d(
    *,
    id: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30c4a3685fd1af6908ab2692e9c182aa04ad0e2def3e62264b8595a352ddbf1c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b801892c185da43f27bfd13838bafe8fcf2790ddbd522898f53cc99a680e77e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df8feb9fe194f2f44f56eff00d5a0efade4927292139c09e6b7e7f0073a3fc5a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f11e3788152dbaf7c4828dd3185f6382b68a488ad9e3a7e42b82e2433a82f647(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeAzureAd]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__146eb8023db98ca40a5304138ba6abb6ae1ee9293e21ea52506055ad30de116c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__605e747e896e2ed359b2fd2ec176e62c5685434a9737b91e97e0073b5b756311(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeCertificate]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__accc5120f60d9ccfa24b9e622fb1b26500accca9e590b7e386ff483bfd8d4ed4(
    *,
    common_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__996f09c281dcfa1f2f16f81c4c16dcfaafc58a9739299d1d651597b07d95c6c7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67ae12af20ef0135c2fc8e2ee3a7b7b6d454aac7dbf54b8f4967420e9aed0a81(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36416a503632058b032f459db8f6cab6d6174dee796755a79f9862ce3fc4bec5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeCommonName]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__160d77c5441f46a67750849aa960c7eef0202d13b0836f94bad5e3b8e2ab0043(
    *,
    integration_uid: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b31d60e2593f19d04d172dcb6cae6dad6ae95594a9d7a2d4eef212f0fd9af84f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3aeaf4c435249afb602d861a3bb0f29fc20f758affb7ee86fde01474d91c9faa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63b7229ae81bde4a793135d72f93d72b00a5003014214cff0fd5ba1b1bc9f034(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeDevicePosture]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__270a7553b6190577c72c8e027ce925220c81188fa6958d30a92a23daefd3a3b7(
    *,
    email: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bdd8569958685703c4fb629f4b10ff30c42dc2af03c82652dcebbc318eee1fd(
    *,
    domain: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7baae55896e69a0cb02e5b0fc5fe491c74438dedd3a3c32d282387f9fb1d2a6a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a92567f2020f38b16805def89ea996c075c29f415f5e8a2c0779d7b4d8f601d9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e706ed7afcf439cd7e339c0fe4756716168cb747b92149bb674bc7d675d7473a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeEmailDomain]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6de40a82dfc181c8d23c361da662c99a155975deb30660eda198e8f7ec7eaaab(
    *,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca61e0490017f566ea471a553f163c427b65b761bffcec9579b5430a90ee0eb4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4270f9452eb4d21d78aceac58c13b38b8d02bbe7618fb7b3c93d999062de409a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d749e3243a6a43fe23641d464371a067774145eeef093cab8493c67a3a8b7ba5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeEmailListStruct]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__246b58e2ced1a4c3d0467a7492149080d3786a1058489bca4d97b0c23702c4cc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b970f64e351753faa7f6befb13841ee29856734c45729e91dfa19e95f68667bc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fddc62d901fba6a7dfa50b4215af128eb9b702edb81d9046fc27b974388e35dd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeEmail]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be198755e080e3a690b60a36e504967c1687d837a4c105a9282f0973462610c2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61063a3d1d4a439e27a77bc728b5332557ef1ad5e47e5a08fb5c8c278a3395d6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeEveryone]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11bf297a714aa6d94ffe063800a14c72a69840fdb56198d4adb79eff26f69c2f(
    *,
    evaluate_url: builtins.str,
    keys_url: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8478f07e3dea1f7e685facfa1fed6ae9c865545464a0f43fa51ef16897c2f341(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a11ec9f783db507b9752a711afa9b9eb50565aa85a48e66fd6028261a62d9ff3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__174bef4741f53a3bddb4ab181eea32856330f9b422602a5fb835100e73c6556f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67848a68a24af28c4911613dadae81eee5b19255eec1f41ada7a895fd7b5e4bf(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeExternalEvaluation]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__294387a4eb3fd83634f806f54265c44b57bc3d901c633a6bb9b81b0d6f57a4c9(
    *,
    country_code: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4bf465c7898416e0e1562a3de193be6aae996f58f1a534aa924abe6ba43d5b1c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2295b9041a3bf9cb1b7be1ff7de5b17db4624d144cc836f8b3f1d73e38d730a9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67f007b0f1b6edbdbb16110f3b56f3c22013603015475add0e4210248bc53e14(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeGeo]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__636563947a854027f528173dbc4440bb3b197e4ef7be60856f143f98baf09a7f(
    *,
    identity_provider_id: builtins.str,
    name: builtins.str,
    team: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e11746d6485aa30e8b021a6d0a050e45a6e0db23d6baaefe210f5f212343e45(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c01ef7a2a8f08f3629caa8101a826a9e9fbfa5cd746d4083eb4c8d7423f0951(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc1977e14aa3e0b9a9f8e87f34205cd7612ba21a60b581f960618e0a2294ac16(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba4e4d96bf69754c1d823078923f6394d002d2c3597efa78a7a7d80ebbeb8a7e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__916dce5c1988e5f5c667bc136f09ac38a036d40c809c708b117b50d3eab80d5d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeGithubOrganization]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38de8e4eb76b109f549021f4cf5d99e32d01dd5f534c26546ef95cd57cbf978a(
    *,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a5a60ec94c7f49c543b43d1541ab519e801d3b8d6e8fcfc35ad1e29040015ca(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb0ec263cf9a3c6b807a43dd29934a9c2388dccbff683b2da3ad4b101c91fac3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55f9bf5e45af69b410274d9c27b3388a063a2c542f5df4e4356503b425b37182(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeGroup]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffb34b648f7f4daa84d07451089872b139bb0d4a88a50b3ef5f77e1ead22767f(
    *,
    email: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0628fe08d009cbb07858ed1ea5665442ca751a0ac847112a09c584c07a89b99d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28ca7443cb330aecae10632b6eb1016452473e8777d0d63bdbacde98cac275ae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f6e14bbf9729e4309aeb5ad5ea2e1a4a8bd7e2c6e1e2b5a5c49a310c6f83a60(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c52ab16ffdf90d1e163f4ecc952a5886bf2c0fdb4603d8cf597b377c03f81a99(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeGsuite]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f6cbd3121a4916ffdb4106c9f9f6dd51bb41b4946f7d465741f772bd7f6a73e(
    *,
    ip: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b509a51f05d6b53ddf9e8fbf2844e71f230758e34da849d30be1bd82e570748(
    *,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43bfc1d804e1a2bd12d57dda8556239155e987bc1c2d46a0ab37177002770806(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__626526143dc24391fde4d30e8cc09d7b02377c634749843898b7b686a6d7570a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__056425386a1a9cf5ff39bc99f205872faadab23b140534b4d39fe8ce930b8be3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeIpListStruct]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e9e0bff52678eea8ecb491dea7d697e8802345c85d204da22c7c2b0490d9276(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f3344ee582bc6e6165625d7335231d0fbaee766044cbeec4e4eeb4149043e05(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0cf1f276dfbb478c22c579e2285e4c9bf6e98db4a40760f13ce09d1ea5f0b0a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeIp]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99c89e2c46ebeffbbddcb847c1034cdc6379a0fd094c819aacf4011cc11657bb(
    *,
    app_uid: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f878a04f1d28bf9b0f56fe50261bd48c6705eedf79a04b47e8fdb600de423c4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54e89aae73dc741b9da5141d0f2d3c71fe1a1f84f4a24a8a41c1176b2c542689(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__165d5dbf66380150b25661f9fea660fb5511d1ac39a6e59456e15d160516b010(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeLinkedAppToken]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b77c54da83bd3b408ee8289f1301b7e3f190551e2e9b4664fba554e022cea757(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c212254999bd6660fd03d9c87384d20e460710483b2d2af13b2d8a3f15860adf(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c22af34b04416ee82772858d5bd728d97fa453f42bae8563b912aaee73ee4a15(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5a09c2a31285e158380fb014be9270b28ade6c0b36a75799dadd7ec9f8499a4(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__469bfb30df797816979515686755a719c0fcd89dfc032fe11d6d301a92958c40(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__190bbf3cbae94699614fa5050f10a4923991770ff514248530f78f729ef26b69(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessGroupExclude]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c324ff4cc5f6e2956442b12a0c49d6783e543c5ea0b46adafccb130adb91b0d(
    *,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cda414be08ec9c9e9118870eb28fe55ad38a907a06024efda5ce7f115c64cbac(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f7fcfd534135a78f570c5aed1854a53fa1036d247398eb5b0b15b6a73e51534(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dea16de9e26c07ce627e70bfadf8590981aa3e648ceab90756d50bf26f647f69(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeLoginMethod]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8bbf4d3a2757d5e3908a48833ab5cf3837e77672e028ae5ded7b64f53bbe2f72(
    *,
    claim_name: builtins.str,
    claim_value: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8097387d117aa834c762e75e51326662799dff7c09fb53b0ba1cec52c625f67f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01da39a5d1ada3fdc5fc752e4ff06beda4524f71d8a5748714ebc1746fc5ff33(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f918b9385168f76b897c650fd78e12b2a3432ecc91fbe08b7c1f175c5600da90(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__534b8906690852568c4c06a4f0ad63f832f9e11871c0d874ad955b509a66e166(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__831dd4dcf23463afb2dd838a88f9e33205f1304f76753829b5e6529db3bd37b7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeOidc]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48e66bfe25d6980c043638db52e3f4edabe40234a1f0a052e6a0012b764d5a2a(
    *,
    identity_provider_id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86cd7adfa749d596a8f6e9fa7d6e30f6ecad9bc346d881cd4f4f0e2ed8451f08(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f0f6963d65bbd34d7b25b7e254b1876b19049fd6375063676ff9441efec7284(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3eab82c02411b7522a58fbc379aac94781178b515c3cd69fd131734d996705c6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5845877720642a8521e13e6469f12a61382f07b36e5894a8232b1043b80d29fc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeOkta]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ab2f6499db644fbdd5b98d0f3bfcba17b41fb64cee95234b9b068bbf236ca03(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3db3d458057f4cf7c4b02a96e7c95016026b85d677ab0583d7a2668f0363227(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExclude]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49d44189fe35ab616fc776ce7dda9c4278169153a9f7ca74c67294704979db31(
    *,
    attribute_name: builtins.str,
    attribute_value: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8c5dab710b854fd42bd545e8c8017797cab33136954c7c30ab51333d1cf0344(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52c6d1f02b42129e63d5bca47fc4394501d75ca187dcd3774993cf266c52c847(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__039756dc908334313a8f79c693dd67b6129ed02ec3c6a731e3437e1eebee9bdf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f63c10399255da050a10266dc318ddada2706a686f5a79a4085c4f765d33a145(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63b38329866908ae61bdf797c6ce894c0d99640f14276e9f1f31b15b107bad16(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeSaml]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61ed69d302dfc105adddaddc8736526b3c1944e3bad95541160d5babfe6e9d1d(
    *,
    token_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff079afa1eb2555a3e3a9977693af494b15d94fef2d2b004e3745fc2576fdcd2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df7c847784f01909bd57857b4a61ab2f7c24ac15a3d2b65552756a074b73c1c5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea9c4058747fad67350b0140e2f24bdcb6249c49be6216d228457792efc7ef7d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupExcludeServiceToken]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3887537ed22b563df2b0db3721f11ebfd2bcf03355110c7054a2ab30fba016e7(
    *,
    any_valid_service_token: typing.Optional[typing.Union[ZeroTrustAccessGroupIncludeAnyValidServiceToken, typing.Dict[builtins.str, typing.Any]]] = None,
    auth_context: typing.Optional[typing.Union[ZeroTrustAccessGroupIncludeAuthContext, typing.Dict[builtins.str, typing.Any]]] = None,
    auth_method: typing.Optional[typing.Union[ZeroTrustAccessGroupIncludeAuthMethod, typing.Dict[builtins.str, typing.Any]]] = None,
    azure_ad: typing.Optional[typing.Union[ZeroTrustAccessGroupIncludeAzureAd, typing.Dict[builtins.str, typing.Any]]] = None,
    certificate: typing.Optional[typing.Union[ZeroTrustAccessGroupIncludeCertificate, typing.Dict[builtins.str, typing.Any]]] = None,
    common_name: typing.Optional[typing.Union[ZeroTrustAccessGroupIncludeCommonName, typing.Dict[builtins.str, typing.Any]]] = None,
    device_posture: typing.Optional[typing.Union[ZeroTrustAccessGroupIncludeDevicePosture, typing.Dict[builtins.str, typing.Any]]] = None,
    email: typing.Optional[typing.Union[ZeroTrustAccessGroupIncludeEmail, typing.Dict[builtins.str, typing.Any]]] = None,
    email_domain: typing.Optional[typing.Union[ZeroTrustAccessGroupIncludeEmailDomain, typing.Dict[builtins.str, typing.Any]]] = None,
    email_list: typing.Optional[typing.Union[ZeroTrustAccessGroupIncludeEmailListStruct, typing.Dict[builtins.str, typing.Any]]] = None,
    everyone: typing.Optional[typing.Union[ZeroTrustAccessGroupIncludeEveryone, typing.Dict[builtins.str, typing.Any]]] = None,
    external_evaluation: typing.Optional[typing.Union[ZeroTrustAccessGroupIncludeExternalEvaluation, typing.Dict[builtins.str, typing.Any]]] = None,
    geo: typing.Optional[typing.Union[ZeroTrustAccessGroupIncludeGeo, typing.Dict[builtins.str, typing.Any]]] = None,
    github_organization: typing.Optional[typing.Union[ZeroTrustAccessGroupIncludeGithubOrganization, typing.Dict[builtins.str, typing.Any]]] = None,
    group: typing.Optional[typing.Union[ZeroTrustAccessGroupIncludeGroup, typing.Dict[builtins.str, typing.Any]]] = None,
    gsuite: typing.Optional[typing.Union[ZeroTrustAccessGroupIncludeGsuite, typing.Dict[builtins.str, typing.Any]]] = None,
    ip: typing.Optional[typing.Union[ZeroTrustAccessGroupIncludeIp, typing.Dict[builtins.str, typing.Any]]] = None,
    ip_list: typing.Optional[typing.Union[ZeroTrustAccessGroupIncludeIpListStruct, typing.Dict[builtins.str, typing.Any]]] = None,
    linked_app_token: typing.Optional[typing.Union[ZeroTrustAccessGroupIncludeLinkedAppToken, typing.Dict[builtins.str, typing.Any]]] = None,
    login_method: typing.Optional[typing.Union[ZeroTrustAccessGroupIncludeLoginMethod, typing.Dict[builtins.str, typing.Any]]] = None,
    oidc: typing.Optional[typing.Union[ZeroTrustAccessGroupIncludeOidc, typing.Dict[builtins.str, typing.Any]]] = None,
    okta: typing.Optional[typing.Union[ZeroTrustAccessGroupIncludeOkta, typing.Dict[builtins.str, typing.Any]]] = None,
    saml: typing.Optional[typing.Union[ZeroTrustAccessGroupIncludeSaml, typing.Dict[builtins.str, typing.Any]]] = None,
    service_token: typing.Optional[typing.Union[ZeroTrustAccessGroupIncludeServiceToken, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aaa0c39719b482c6fe419a3745e381d11c43d4455bfb401c1dea90ee4a14aaab(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11c0f22d6b5718350ef9d3aeb5ec3d76afe81092b3a67163e29943bb9bef9528(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeAnyValidServiceToken]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74a06468f4b695c7f1cc645d73f503dc110f3b3c5ab6cd7d61c068ef615ec561(
    *,
    ac_id: builtins.str,
    id: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8374cf44b09ce7fd7f4135630f7e14a6ebed5c745106da59755346ebe927de8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25a12c7ca1e888b3e3f242e996883fb13941ff7bc3647651a8a0ad22b270d6df(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15a3ee534bd67dc800ab29d75dc98cf46972d359ff7700ef770e7bc907e63323(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2680a61bef4cceda940e3571b97fcbfca1a592783d6ad2c500533811674822a9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e45ec04b55ddf6f910bc2edd3bd63eb6ee4fb16b17ccdb28c585cd33366c589d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeAuthContext]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05b06280d4e60396c5cd1f12d90f39f6016d9042ed597988b75cc93b95e87d61(
    *,
    auth_method: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f16e56d90abe72c8910575375bdd6a2becfb2d7ee888769ae9802831123fd200(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e1352c6b5078492f55b0550adbfd38cbfd197367574f9bc0cb63d40ec5fbd1f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3d105767e2db760ff738b0b0ce6c96280549dfab99de6258d770abb7863ee72(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeAuthMethod]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__faac070969b3ac9df090a5f35e87885d96958c9d80031279a62169a954d1581a(
    *,
    id: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1958cc0fac9c777f0356cebecb641bd5e94e5687631e2b8fd4bc381173cb674c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e01ca993424c0f79b04f67df0d929fffe6deda6e1ac0c3bb40a9176064d9c5c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbb981441556d1ecfd4c93101d96918e6d53dc238ea04d7753db9d6cf69b37d1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30bfcbbc0172b06f8520f5b6e5347b3b8e0f36874152bfef79babcff192a919b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeAzureAd]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7c1285f6a4cb0168b5b1e2206592d58ce0a45ed4d6f4b91caeeb0ff32164f69(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d4558cf6fbd86eeb52f2eaccaacc5e13e94221aec772a487e9e5b95a19b44f3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeCertificate]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40d6f36e39ffac36f46c87ee9f349db01253be99470fdb06c70a8478bcf77867(
    *,
    common_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce644bd393c544bf554f028496d7e88b5c3a536a12d6bf310a13066cce899934(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f1a4a6219744d794b4a3de4b7075a9c84dd7962724b1256f6074ece1719a322(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54e88ce53351da3a6f19046b2335d71154d4bf98ff69d9862af58f4aa8249ecd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeCommonName]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d41dfee38e98135d2c333195911dc9155235d8919fef46e447a61abb97a1d86(
    *,
    integration_uid: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9aaef6f157ed3e7302bc69792ee9f0612e05338082ce02219effb81121081aa(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c866faa3a7ccd3723072cb6f1f5ee860db98014652a0236de4a8c6a414d056d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdfa92c16139da3fe257989526dbf1480b09af7259793d4c3703c66994f76c0f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeDevicePosture]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af5458947becd541b6f9f485fc68850562ee30a89388c1898e717c03b151a3e3(
    *,
    email: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae45d0202f5514c60c9985066e3acb4426ab8f49604ef1914b2b7271ffef6503(
    *,
    domain: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bea89ec867b02e400c5574bc080f98c64e6188fca1531fbac425d53a3d505893(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d95f344b36336d3ecbb34ea55eceadbe9019b7f60df6b590c36b345e8a186f57(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a784db61f3ce87530ad71b931c8789abedc897486dee7a9c318a3275c43650b3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeEmailDomain]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3d82cb88450e7e4d9d7bfb776ae08d5cc1d38f66b77feefff6ceb45379521ca(
    *,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5fd1c8494565ab0517ee7b0bdf92e4e273838ceb0851cb46218bf8e1003c82d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7ce13d22b128abb827fd8f529fdfaaaed04fd994017e852c6d5c9fdb85a459e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5737e9e9bd7084a9017725427ae92b482d7d3e4df2ffaa9a0a6a6c4d8470edd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeEmailListStruct]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__876664c5a0211870835bfd3b4662efe0c7ef2b82d9473ee46f5b05e4bf562203(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97518f467578b2350b12d54b9017b6f17da9815868a36f6380f58569e2dbbffc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e89017e8963228a0836d43517b26090ee106dcf0b670d3dcb67b8b269c0db0d1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeEmail]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d4908222fb5b2b9a5c44fe04c75ae9460b1afa269b71cda04fa872bb63383cf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f39a05aeb7f8a2c41b287c03783d346ab1cc8eb009692e6b2b96e487372a1ca9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeEveryone]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96f838d128454a4265ac355d5b21627304aa32654907b668f5ceb404c61220d9(
    *,
    evaluate_url: builtins.str,
    keys_url: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34a76e3a903d77dc11169d21d331439c35bc0ac1325355f45fb0d81fdea091e9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75097247409fda28a339084d6f31c0c738ea0b9de6f930db43f40ffd1e0ced51(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c524c7e6210a5ca6ea75119a289cb6469f7487e7806597708555bdb046cecd6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cae5c44410b8c107f4018ae82f641a21260b1c619a0cba86d65ede38ac71113(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeExternalEvaluation]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7b8e60e1bfb1f8fadd0d819a2893ac4d9facf882f1677893da0a6968177247e(
    *,
    country_code: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be6c4cacc9755576137c09e2dd5394848e4701c224ede71abd5bfe3b13ed4cdd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__089270c0e6b3189f31dfb0512eb54ea2e454c2b9f0b852a6fc8d5354ba0be915(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe7b2638beb8a716f4adf5ac186f0f0ee67ba82a2879cdd4aa2ff5fe39f43812(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeGeo]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9234d0c4bdcf3462a10bdd10c33b90fc124f3752bbe67d2caa45be7379b03c1(
    *,
    identity_provider_id: builtins.str,
    name: builtins.str,
    team: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81d52d49711c02bde31d8e1b0ea30d379604d7a6b2d0571cb8dbf065eb4bf14f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b838a7d287e9b73b5f18f32f841d3c900e6a4501b455682fda0ca8fe4532ce9a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7be89d6eb799b745dada016ac3c9275e57d146809f206729b360d73fa8830207(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8be3a76dd9eb7409a30396468486a8c09181bc903144f93d73cf59736c55a168(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ba16bf425daffb436642a36d3ba675dbc06ba9c1422a94991baeb9559b3ff8a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeGithubOrganization]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34f067d98af1a8c45eccb4cf41e3521166bba527a1ce6da5776453bb2c5ea29c(
    *,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__307fade54f0f8b46b9cf000aad247f24219edefd15cfe3cbbdd3cc3ab825694f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56f979661ef90ac293e3ec01ac949208fa8920cf9da54dfc424780a12ff9fbd2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8403514ce78f263a5ecf193cd1707d872e94d0c50e2291d5348f04495ed0ee64(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeGroup]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5284f6e6b03b6171353c31a15187f3b27b00a1d6eaf7172b60c9e0a74fbf853c(
    *,
    email: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f8f302d0176e7592311bbde6d3c893cf5c5fa68a0f15eb61e07374bf36757e2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbb631921b8f6e3b39a52c03cbe1e72c0ecc1f2b292cf9f4f8ee4d19a5590002(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50ed4624ab5d0be0e45357a05460a1385d8b9e566b81342a79a4b2eb4507c8d1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5630f14a647d65560b027205944d59ec923b2b06906c7ac3a90dbb11e7a17af7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeGsuite]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f77dc0b84d7d405ea91e15bfa65d3d2bc18afeb68086a99147cad96e29b26cb(
    *,
    ip: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3bb4f43282431180c89e6f844f11e55e7633a27240e1b083e5c10d501a69e1f(
    *,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f899f721b76c07c50a6f2dd04113f559a5de2e452f8b44dbb683f943dbcba1e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a565002e1574fe688145f9e4f8d983f19a10a9c69a92343cd315e2180c6218e1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ec57c79ad3d986058cfdff9e622be044e990daa138651662b5c90025cdcdb11(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeIpListStruct]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e79fd293f85ddb0190314748a460d14e2b7f7b7a6bf77bc8f46216d50508f62(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bc5e627508fbd361035a2e2bae724103ee3c08ec8c8f5ea1c9c7f604b6d6010(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cde4bd7bbb505518ab24fdad83386a0544905141f0c7851281fe86eeecbcdb8b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeIp]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0edf8a08d2bb0cf67bbd3937cefee7b7b1c08d3b43b1dc0edf0474285f9ab7d(
    *,
    app_uid: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__290d57f7ab344e19e01161df311a20b584380e652247a1c9d069f32fa4c04fb9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5f0e0fc866a565c2069dd60216edaa607ee106f24fb6c74b2e59cd8270e1ad9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__261f6e6ad0d67f45776e2d6037b32d5c63970a2c5c511cb2366cf19d9b5bd598(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeLinkedAppToken]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41ed12438e0c29548e6982fd8229954fa3ad800f05f56fb78cadbdad2e01939f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78fd7b2161debcdf010f64c9adbc2b6e77f969b6a06d73a37e5002d3bff6835f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f73f9ad7c0f9514cd35ee8c94b9725147b22ba6176c0e56d216eaf66f6854ce0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b430e79b3d9fb220270e63e44a0417609e532eb4ea03f60bce0736f6bea32b2(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4cf2d1837419f8e2d302dcc40ce4b7ce158087ec9e3cba035dd0dda37b933f8b(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db8495c2c7688b8b50a2fdda66d8644ba6cfb12aafa4382e9cb7631b015a4d8d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessGroupInclude]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46d8bd705f76cb263aa91f4d3402367c67a346e4623a1ea1fcea0ec7ee1f6497(
    *,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fa78c3154c4e1451d75f3b2c8cf266c2f97e03eab69031bff4501fb3a8c7d0c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed8bb869a875b338e4acd176747b34c298e29d46b1dbeaf7d4b06a4403f7b4ef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3639c748d863e8075971ad52f610307ad6d2116b088fa17b328fe736d5ad8ce1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeLoginMethod]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b3a24487e0933a51cd7e53ae03d57b4ff30b9afdad9c1486088b5695d097599(
    *,
    claim_name: builtins.str,
    claim_value: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9741cd18fdb4a1cbf256715b59a7a76a9ce27a3e663e43cd62d61e154c77615f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab58da6b80e2d776f20a074572832fcc1eedaa03c4364c02e79a4b188d2ec92a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8dcdef9c86847ce69e376954cf3ab6434d4816dc6ff1f89e3dcac06fc2085fb2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b88adaeb440e92d8e1587d4b6bd6fb32e59734e47fee618187c83531b6415c8e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82f328f8d19ac7d2dec4c49c428e06a0bd56f6f355dbbe6056f46da1713439f1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeOidc]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c40ba7154f26c03d5c4da5e9154bb876230c1ac60353838b131a965a9f3c5ab6(
    *,
    identity_provider_id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d5c9acf6c84cb793f250d1d72abf2e89401620cf8e2cb35ddd58957c4104df9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42fae6ff38df6963de22281303891f6a789d866730d47a59fcd071a18499f777(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__729110212c0344b1755aebf9a8c86dd2779963e9e9c7a5d67b68ad23ba956d52(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__717f2234936f6a8acfa87ff556fe0a86d55754ade9aebdcb0f432984a74498e6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeOkta]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f03d0c41e56e160e26fc2ffd4ebe6696155cc65caa89556330810157a7f4d1f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa81b8349bb7c5cc9053ca6907036a8696421116232558d9ca891441e11e3321(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupInclude]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37a791ad73e5781d793b796bbc41cac48a8f7e8fb14929bbfcc3ff2eb0466d6d(
    *,
    attribute_name: builtins.str,
    attribute_value: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eddce6f9b3b126bc38f26239a3006ded9635824fc7af913d2401d4da2691b47a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbce3108276d15251ab8fe8aea75e96bad2f42318d118448f78cd26ef5ffbfbb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d92b4846287ff98f952ff32549635421b9bf7ac3b590bdefef9cb3bb016498b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4746288e77f1665cb7fe6b988f0c6b6fc12f46954c90c48cf88dff4cde66d4cc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdd561d4bddcc457b29c2f18886861bbcfd5093b5d37f3d9b011368e44c096e3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeSaml]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2c8341b0fb3b78b03223c18b1b3515c3e8ad67e122ddfe34acf411b3f9afd12(
    *,
    token_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79ec6bf8685db53c8dd52545e816f32959ed917e48cb3ef029a8b0dc27907019(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba3de18f40d6b2f1a5514220b574a9e8a33c4466d97e8db5d70c73ce89508e95(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfd09f85fe42eba35e1e6fc8eeb71eb9a708a54cfa1c8b519652929d5a8cadda(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupIncludeServiceToken]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ca19dcea861c64afc9ab364a01bd40e90c208f30429ca3b586da0ba0d7cfeed(
    *,
    any_valid_service_token: typing.Optional[typing.Union[ZeroTrustAccessGroupRequireAnyValidServiceToken, typing.Dict[builtins.str, typing.Any]]] = None,
    auth_context: typing.Optional[typing.Union[ZeroTrustAccessGroupRequireAuthContext, typing.Dict[builtins.str, typing.Any]]] = None,
    auth_method: typing.Optional[typing.Union[ZeroTrustAccessGroupRequireAuthMethod, typing.Dict[builtins.str, typing.Any]]] = None,
    azure_ad: typing.Optional[typing.Union[ZeroTrustAccessGroupRequireAzureAd, typing.Dict[builtins.str, typing.Any]]] = None,
    certificate: typing.Optional[typing.Union[ZeroTrustAccessGroupRequireCertificate, typing.Dict[builtins.str, typing.Any]]] = None,
    common_name: typing.Optional[typing.Union[ZeroTrustAccessGroupRequireCommonName, typing.Dict[builtins.str, typing.Any]]] = None,
    device_posture: typing.Optional[typing.Union[ZeroTrustAccessGroupRequireDevicePosture, typing.Dict[builtins.str, typing.Any]]] = None,
    email: typing.Optional[typing.Union[ZeroTrustAccessGroupRequireEmail, typing.Dict[builtins.str, typing.Any]]] = None,
    email_domain: typing.Optional[typing.Union[ZeroTrustAccessGroupRequireEmailDomain, typing.Dict[builtins.str, typing.Any]]] = None,
    email_list: typing.Optional[typing.Union[ZeroTrustAccessGroupRequireEmailListStruct, typing.Dict[builtins.str, typing.Any]]] = None,
    everyone: typing.Optional[typing.Union[ZeroTrustAccessGroupRequireEveryone, typing.Dict[builtins.str, typing.Any]]] = None,
    external_evaluation: typing.Optional[typing.Union[ZeroTrustAccessGroupRequireExternalEvaluation, typing.Dict[builtins.str, typing.Any]]] = None,
    geo: typing.Optional[typing.Union[ZeroTrustAccessGroupRequireGeo, typing.Dict[builtins.str, typing.Any]]] = None,
    github_organization: typing.Optional[typing.Union[ZeroTrustAccessGroupRequireGithubOrganization, typing.Dict[builtins.str, typing.Any]]] = None,
    group: typing.Optional[typing.Union[ZeroTrustAccessGroupRequireGroup, typing.Dict[builtins.str, typing.Any]]] = None,
    gsuite: typing.Optional[typing.Union[ZeroTrustAccessGroupRequireGsuite, typing.Dict[builtins.str, typing.Any]]] = None,
    ip: typing.Optional[typing.Union[ZeroTrustAccessGroupRequireIp, typing.Dict[builtins.str, typing.Any]]] = None,
    ip_list: typing.Optional[typing.Union[ZeroTrustAccessGroupRequireIpListStruct, typing.Dict[builtins.str, typing.Any]]] = None,
    linked_app_token: typing.Optional[typing.Union[ZeroTrustAccessGroupRequireLinkedAppToken, typing.Dict[builtins.str, typing.Any]]] = None,
    login_method: typing.Optional[typing.Union[ZeroTrustAccessGroupRequireLoginMethod, typing.Dict[builtins.str, typing.Any]]] = None,
    oidc: typing.Optional[typing.Union[ZeroTrustAccessGroupRequireOidc, typing.Dict[builtins.str, typing.Any]]] = None,
    okta: typing.Optional[typing.Union[ZeroTrustAccessGroupRequireOkta, typing.Dict[builtins.str, typing.Any]]] = None,
    saml: typing.Optional[typing.Union[ZeroTrustAccessGroupRequireSaml, typing.Dict[builtins.str, typing.Any]]] = None,
    service_token: typing.Optional[typing.Union[ZeroTrustAccessGroupRequireServiceToken, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4a515cf1dbe3c3135069d2f75983154d2bedf67e34d3ab5d2dd8554ccdf9154(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a3dc1c51ce914c3f639bad4004b67f3cb34f10f1668e1ebee76d5114817c0d6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireAnyValidServiceToken]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce0fc6b2610c6f1422cafec22630d3fbc8a1b0f10ba60cec5f3056df94ae3a3b(
    *,
    ac_id: builtins.str,
    id: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84c377e5ce845c585924cff621dd58e85e0fd8bc879c9d265b89aa2a2089ba30(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b2c743e985d304300d2a878b06402253d10da141c2c4baed255913204650a68(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fccf9716862581d9d8c1a09f13eaea809748b197722ca793325632e82855b92(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__619129d7ce1c8ef416984007525c59353b0df51a3db8a5584443691df04ac5ee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c35bdbed74abe93d2af4e9bdae98cb38a6df15a57a2dacf40f598865081cf2c0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireAuthContext]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0faeec880030568277dcd5c3e28d65292ce185892bd5a45ef3f9953c66001300(
    *,
    auth_method: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7728bdb7025f06e7e2ae223567fe747af3dd9fb0ebf63f3598aad50ac0a2078c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd0f3da7a88eccdd4305f06a1c550bbe35cb5b80f01d76d642047f1519157035(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89fb04a8fe770d0b8997b9c00e8c99049369f9e9bbc911ea57a79f158906fa16(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireAuthMethod]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a34c50bf571e6958ae08518f412176c0504ea4a547d6b4182ea0350e6b672a48(
    *,
    id: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b027ad9b6057d0e83ce146e48720a886e079f96e05d8604f048ed311ee854d9c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82e922e1b634897af7da404781a027f39159d74cb715fb8cdb067c7a247ef045(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80bfa15b621192769649a785727be93be86c2f2026aa15252ff2a0e4b3592f6d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d44f6ecac6d8074abf29e85b33d131ab0aaa3779ccdc828674f19d66a5c1bbfa(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireAzureAd]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__937f275f760304be7812bc9fbf44977ffce6912741c2e975913dc6ff83d0b59b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5772979871b744c76a93b66c0b3e89fd4164c02069478bdf9555c49b782e802(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireCertificate]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47b1a032c05095635c3a32835499a8e7fe718e3f08d4f6e7d68a89fc37b98c9a(
    *,
    common_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d4732eecf93894672ee276c331e37112d211223bb8913bb15dcd8c4a10ebab7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de972ef932d4d81d3b0f5d898da913563d4786ecd47bd228df2244e3b5a9b940(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e7568a84d60171a865d5d950cb5fec3c14bb6e571cbd2b880522602f82740da(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireCommonName]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92303702f5467f33189f0989ad602089fb38b9a9d6cc9bb72cb1498a1d24904c(
    *,
    integration_uid: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__932f0963cf0693ca5a90cbf3e6a8aa461238ffe4e9ffe8cc630df3ddd9a0cf46(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8fcab31b6860c238ae242536143e87fed77bbad0f80d94c8d2013e5eae4d0ac(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__400035a1eb0ee75096259c80ad1db33bc76c2353f02a5248f0b49679a70e473b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireDevicePosture]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fffb84bd3b6d730000be38b5736f3862c01bfceade7e44e7ebd56bf2a3daf624(
    *,
    email: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19ad94635a19768b7f0aaaf0b17e2d4776d3ba60983bd4102ca9efeea3307c87(
    *,
    domain: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__309331e2e869f1df70bd5228619f98424e6633b19f6f662af18d0ac0369778f1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92030698db5f922af068273a735fcc0b39acb14fe9b68408a9c4feda09ebd82f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__903ce4c2c74c7e27d2fa02a488c37ab4b13da13f895fdcd3a335357a6d5ed1e9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireEmailDomain]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9f1c0cfa9b8d302a71c142c21164da561318d1df2e4bbbfead0b9cced303b09(
    *,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a1be8de9f990e5fe827769afa635768c8a95394bfc2b7dd3164f3fb8477af69(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06bfda9340cab4b52eb5d4eaa8af5461d8af0b6b00a7e5eae6ca75645e7b65e4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89f38160266f3de9a9dfe4157475a0b072b6cf616ab29c73104f559d770c09fa(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireEmailListStruct]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56e82c184749e0b1c6623a9f2fec07469367031ee031487835c148722550cec1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__853589f41bf2e251eb8e6d7089407806ce3d97aba4be945efe5a7c3362823fa9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f46c6b9feddfd8c63f008148bb59f569514f077002185fe020df880b8de921cb(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireEmail]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97a71b3e3638ffacf116e9c7b7c9364d8bb297dba78b099a6a2ab0dc0b665f7c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4d2131cbfbc3237b69e133bd4bd3461fb960b5d7272108db4c019141ca04dc9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireEveryone]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbaadad45bea772c3552c28c1f8ede410759dad3730311811e05637a105ccc2f(
    *,
    evaluate_url: builtins.str,
    keys_url: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f4b3e39df3c43dd1ee3296e5c5c97ca0a622cff94282978c12d22ab1d759d0e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__700c9210b51851ba3e94b2cc4a429f0dee175d92322172a19446577e2ebe039d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43ac1b59efaee65323d91f1ce5ff693480e2406dbff0b4b9302f65610648af33(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47464751094d1b2968da48b331f3a0f4b6db7961edaa16647e91b1346e495a19(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireExternalEvaluation]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27479650673b751c4173a789412fe74b9c57eeb68fb6a6e9e0f538bc24066353(
    *,
    country_code: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f11abb57b1516a28aae0c8b72d5db96d330099cd6ee7a5c8a7fabf21cf870e69(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67abdf3b4bba37d94a27f360595b42e2765f645b4bc6fc7bb987ad672673e1ab(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cb0de53a39f44b5b51093a394d62bab77752dc3da604c2df92c96ce00b87570(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireGeo]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9911fa1853cc16f9e54fff942ad7faa66f8d3253361db397e368ca0784518a47(
    *,
    identity_provider_id: builtins.str,
    name: builtins.str,
    team: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fcbde6856020df97d4b6ec94392f1eb72879b5987ec5563728ef527a773ce2e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8da626c8480e109a8d305159f484c79fe3c1ba411b34699ffc1924b283355c45(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8257b63974106089b31cddb83b9b026da00850b7f0fb02f611b3df4d189db4f8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d258b7a7c96a4aaeaa5bb540acec2f8ada80b26d2ceba715f758f5117253e0bc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5972fbdc406c40b43c47445505064d97eba39c339d625fa6f3d1ed73de42161(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireGithubOrganization]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__440c6cb84b42fe507c19832800cf18f602cf1fb4b6d9ed2658755d60610d3325(
    *,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__557433e537d2e8c7d33ccb713ce4ee8f4d59efd4cdf4dd2eca91bddaf29548d3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__562483f508e2d95b5908b87997daf7084e92af0c3a37714c4594a8c0cdf3c362(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d27c487511f8942e9bbdb1dfd29c9be2f22fc67a56a230baacd92fde80df23f7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireGroup]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8685d3ac6b8d937119be8f424a61e7921147190b5496b44c2880daf7a5c7ae9(
    *,
    email: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61b28151f3a33e7beaf67c03e71e932e1f89cde1100242fe2979af2453f5b6e7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eae01777313b663c299be3d342c25c2fd24343a123501fcbfa7ea8a6bb02ac98(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af7dc98ff142a0541173bc9599e35678734e5b020950252bcbcf720eea91705c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03e7c2a80294cc819dd78bc4122fe7ff922da1f55aeec7a65bb64f0ffcdb9aa3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireGsuite]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2f705cd4f8783e03e5111674c787111d9d68d2d1ca0b12f1e465f990c81b5d1(
    *,
    ip: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a520ca9a350168774877fee702c4906017ae9fe6178e247dbc2a626d3a75b08(
    *,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57c6b0355a4865ec155a85e51480702b4e6be09e832642e873a104a0bd3e1ac0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__695c539aa55b49cdd56a3272bd441cf655fa3554b54554fc64b8bd71ef57cfca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d3366e1c9107ecfe499be8c0ccd340accfae606ff3aa1dd634d3b842f19ad6d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireIpListStruct]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65a100274e866289666c7ad9ece14c741536f4a1a621276eb808a007ac089b48(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8643f90e4c3c2c135a47f3f17045cc2d27d1d52e1b510a6b3b8346667a3ca3eb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f4584319602f68c573d705d279bb7dc5ca05d1fe5942f319c86ad7bb6b563f0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireIp]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40b238bc761fe258fbbf604e084d504d2d605c322d7fa20da5252e21930c2263(
    *,
    app_uid: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a68bf5e80be45e1c17e469dad4ad884fba77346021b1daef6c116df7e0a8c6b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0ac374c6e1270ac9cc9b044549916dca7acf56cb5beb9e03aa32eae32bae423(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0475a10c091aadbe60c875eab4826afd80f6b8beb67170a9dab4d78bb4974c6f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireLinkedAppToken]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fa00056a098356a1ae19708403471340b9c001f470c23e2fb86dc6756341d1e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12abdf2c6c1cf70d62d05b78d68e4f68d17592abdf1c09338267075c395584ae(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61e534485bc1a0ad3822b37c3cd3a0691ba2a4cb06087436b2d54a1a48ed2a7a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80345b5525f385fbcec11480ebdd07630b9d296fcfa56ee73f01fcc0a5c83357(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f42369e5cbfcc9915d1e1490fb80ad67ff70daf9a1210d3bf08ac4771e39dc3(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b356ec6f08bc59e0ee3fe7c488c7f7aa4d187ebd0ecb6fe47e340c4bfdc3c53(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessGroupRequire]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fb3b4846cee2afa4b1b543c8662fdb839fa8c34c99a3b712aa236c1d1178646(
    *,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9e540d0251497d4c7dcb5d0b8c543be771c286d17f5c6bbaf9da1fed0ec0fd1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4cf566d2f85f0675d1b321b4ac32c688710ffb4341ff9574252e1452c7b6c80e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bee2175879d78c60af7c82693cc1b6d6675565833e8cacfc1a69e0adb4e38fa6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireLoginMethod]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__748f0d146ba164a2af8aa776d45a546ba63c4100c73a4bd37785a2f0544fd303(
    *,
    claim_name: builtins.str,
    claim_value: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c98fa47604d73dbedcabb1099942b12cc8104fae064acb677f7113f213cd4f3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38e717770418a922ded0d550b333d6091240293110e5d7a36fe75f03cd70189b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2e8e8f42514a5785db74dec2dcf4bad053062a326a31ca36900943ac43cf270(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d0af12600d1714b4db27099ab1ed9d884cc97ffc86478678a85334940edc055(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea0652d9eebae8a321cec4796344cc72cbc34031f77833478f958e9985b26487(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireOidc]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__596d2d5ee2f2cc5f7fc9d74eede2ffc5f802656fbca444f9584573dfe9f3fc88(
    *,
    identity_provider_id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9fc487bb8b95b652cc667b2de83b7a33889373303445057e6e4ddd28886ef14(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d536862c1b9a64aff291d628354459a298e13c649d0d42fdcb114951e01bf6a0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bad6ca07f1f3f2579b493036b5eec198d8800c74e468b5212da00770d1c3c68(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ebde3cd98b9155d9fb01d20f01b87661807c3617f5bd108ed00978322cd2700(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireOkta]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32a4dd748855cd6983554ca74604a33b3e22a100cd0cb4a406668abd7be1d85a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__782f3c3257a2c495484cf4b68698125a6bf9a47908f2f31af7a9589ca283699d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequire]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80a7cf643df910694eccec445014db3d18bfd3c78e3e383deb0346e4c9d81e98(
    *,
    attribute_name: builtins.str,
    attribute_value: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c42f1729a5e90171eab14013f86a44d468948fca3c92c1a685a3c8c1afccf6de(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41b93d70d600bba40fecf7cd59cbe8d38de61b8b0238fbc931c327338ffc0e7d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53c2eed3237d89dfa90839da4d602e18e5e9ec84b4d874b0f32850b06e9948ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80cb8192e0e33995c10c861debcd79de90de8876ee603b415bcf59cf6fdd535f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__719bcc7f6e4779e45570275a22f8d5fa3ea67a04fcc03938b1f90ffedd7ee290(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireSaml]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54d73e737db65201846c0ace501e34528b03a26a2bd178b9755302a0713bd9a4(
    *,
    token_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__268f35bde87425d85df9ba82bcdc14c1f384fb24a444d216818aa41d3320b8f5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fe8032d860a2bcb55df53a073379217739ce6740a63155a89752b2ae9eea648(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a81a1b88ff228ba1875005a9c9223b15e31497a2c78537ee167ab79545eb1b8a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessGroupRequireServiceToken]],
) -> None:
    """Type checking stubs"""
    pass
