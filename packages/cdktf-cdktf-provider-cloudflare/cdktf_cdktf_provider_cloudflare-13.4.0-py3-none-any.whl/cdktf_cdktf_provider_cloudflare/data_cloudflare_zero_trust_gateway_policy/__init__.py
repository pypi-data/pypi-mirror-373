r'''
# `data_cloudflare_zero_trust_gateway_policy`

Refer to the Terraform Registry for docs: [`data_cloudflare_zero_trust_gateway_policy`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_gateway_policy).
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


class DataCloudflareZeroTrustGatewayPolicy(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicy",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_gateway_policy cloudflare_zero_trust_gateway_policy}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        rule_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_gateway_policy cloudflare_zero_trust_gateway_policy} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_gateway_policy#account_id DataCloudflareZeroTrustGatewayPolicy#account_id}.
        :param rule_id: The API resource UUID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_gateway_policy#rule_id DataCloudflareZeroTrustGatewayPolicy#rule_id}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f24cbf0cffd6893721db1085940f90cf5f4d71a9c4aa1325618c8a3850a50cc)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataCloudflareZeroTrustGatewayPolicyConfig(
            account_id=account_id,
            rule_id=rule_id,
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
        '''Generates CDKTF code for importing a DataCloudflareZeroTrustGatewayPolicy resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataCloudflareZeroTrustGatewayPolicy to import.
        :param import_from_id: The id of the existing DataCloudflareZeroTrustGatewayPolicy that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_gateway_policy#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataCloudflareZeroTrustGatewayPolicy to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0de6de178a356e7c31627e9f0e2adc130dd978afff79199c5c3a153cfb18151)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetRuleId")
    def reset_rule_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRuleId", []))

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
    @jsii.member(jsii_name="action")
    def action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "action"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="deletedAt")
    def deleted_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deletedAt"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="devicePosture")
    def device_posture(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "devicePosture"))

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "enabled"))

    @builtins.property
    @jsii.member(jsii_name="expiration")
    def expiration(
        self,
    ) -> "DataCloudflareZeroTrustGatewayPolicyExpirationOutputReference":
        return typing.cast("DataCloudflareZeroTrustGatewayPolicyExpirationOutputReference", jsii.get(self, "expiration"))

    @builtins.property
    @jsii.member(jsii_name="filters")
    def filters(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "filters"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="identity")
    def identity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identity"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="notSharable")
    def not_sharable(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "notSharable"))

    @builtins.property
    @jsii.member(jsii_name="precedence")
    def precedence(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "precedence"))

    @builtins.property
    @jsii.member(jsii_name="readOnly")
    def read_only(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "readOnly"))

    @builtins.property
    @jsii.member(jsii_name="ruleSettings")
    def rule_settings(
        self,
    ) -> "DataCloudflareZeroTrustGatewayPolicyRuleSettingsOutputReference":
        return typing.cast("DataCloudflareZeroTrustGatewayPolicyRuleSettingsOutputReference", jsii.get(self, "ruleSettings"))

    @builtins.property
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> "DataCloudflareZeroTrustGatewayPolicyScheduleOutputReference":
        return typing.cast("DataCloudflareZeroTrustGatewayPolicyScheduleOutputReference", jsii.get(self, "schedule"))

    @builtins.property
    @jsii.member(jsii_name="sourceAccount")
    def source_account(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceAccount"))

    @builtins.property
    @jsii.member(jsii_name="traffic")
    def traffic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "traffic"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "version"))

    @builtins.property
    @jsii.member(jsii_name="warningStatus")
    def warning_status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "warningStatus"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="ruleIdInput")
    def rule_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ruleIdInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0bfc76d6e9a1e61c147cccc0b9ca5dafd3dd02a5addaba9c0b4290f38f9bb71)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ruleId")
    def rule_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ruleId"))

    @rule_id.setter
    def rule_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6595b478e03d987aa56e181ff37de52dc7a7a48ddfbf4d193e75184f335ce3e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ruleId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyConfig",
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
        "rule_id": "ruleId",
    },
)
class DataCloudflareZeroTrustGatewayPolicyConfig(
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
        rule_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_gateway_policy#account_id DataCloudflareZeroTrustGatewayPolicy#account_id}.
        :param rule_id: The API resource UUID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_gateway_policy#rule_id DataCloudflareZeroTrustGatewayPolicy#rule_id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fb94ee976981924ba676dbe647a764b65bcffd94a5dccb4e51b6aea174fbb3c)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument rule_id", value=rule_id, expected_type=type_hints["rule_id"])
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
        if rule_id is not None:
            self._values["rule_id"] = rule_id

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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_gateway_policy#account_id DataCloudflareZeroTrustGatewayPolicy#account_id}.'''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rule_id(self) -> typing.Optional[builtins.str]:
        '''The API resource UUID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_gateway_policy#rule_id DataCloudflareZeroTrustGatewayPolicy#rule_id}
        '''
        result = self._values.get("rule_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyExpiration",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPolicyExpiration:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPolicyExpiration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPolicyExpirationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyExpirationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9e5e790895ab797cf8c4d44eb6f565ec54b57c4595fcc1915afaebb2d5f3b991)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="duration")
    def duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "duration"))

    @builtins.property
    @jsii.member(jsii_name="expired")
    def expired(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "expired"))

    @builtins.property
    @jsii.member(jsii_name="expiresAt")
    def expires_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "expiresAt"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPolicyExpiration]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPolicyExpiration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyExpiration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b863212905eb120b1c0986704dffacfb2a690361ba69b4ccffbd2da5bacc35b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettings",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPolicyRuleSettings:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPolicyRuleSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsAuditSsh",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPolicyRuleSettingsAuditSsh:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPolicyRuleSettingsAuditSsh(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPolicyRuleSettingsAuditSshOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsAuditSshOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__344b349caecda084830991cff004d66287735041ff77d41a09f0f111c14fa715)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="commandLogging")
    def command_logging(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "commandLogging"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsAuditSsh]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsAuditSsh], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsAuditSsh],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a1f895b9101ef28664c32b693801726a2cadc9471e812f0e7c80663adb00550)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsBisoAdminControls",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPolicyRuleSettingsBisoAdminControls:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPolicyRuleSettingsBisoAdminControls(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPolicyRuleSettingsBisoAdminControlsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsBisoAdminControlsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fdfafba495d739fba9eb148095536119ab3523ef793d9e777ff47f4675faba80)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="copy")
    def copy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "copy"))

    @builtins.property
    @jsii.member(jsii_name="dcp")
    def dcp(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "dcp"))

    @builtins.property
    @jsii.member(jsii_name="dd")
    def dd(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "dd"))

    @builtins.property
    @jsii.member(jsii_name="dk")
    def dk(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "dk"))

    @builtins.property
    @jsii.member(jsii_name="download")
    def download(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "download"))

    @builtins.property
    @jsii.member(jsii_name="dp")
    def dp(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "dp"))

    @builtins.property
    @jsii.member(jsii_name="du")
    def du(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "du"))

    @builtins.property
    @jsii.member(jsii_name="keyboard")
    def keyboard(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyboard"))

    @builtins.property
    @jsii.member(jsii_name="paste")
    def paste(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "paste"))

    @builtins.property
    @jsii.member(jsii_name="printing")
    def printing(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "printing"))

    @builtins.property
    @jsii.member(jsii_name="upload")
    def upload(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "upload"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsBisoAdminControls]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsBisoAdminControls], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsBisoAdminControls],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5da64159be9fabf522abe3deb69242071899a5264f15b38cc6726d4ca4e7f885)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsBlockPage",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPolicyRuleSettingsBlockPage:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPolicyRuleSettingsBlockPage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPolicyRuleSettingsBlockPageOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsBlockPageOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__af5bbf3ef9309903a14a82446bfa205f837efddca5a41b0485526c43f86749ab)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="includeContext")
    def include_context(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "includeContext"))

    @builtins.property
    @jsii.member(jsii_name="targetUri")
    def target_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetUri"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsBlockPage]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsBlockPage], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsBlockPage],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1a58a5dda2adbaebb895c752a6baca8417d8c964953117ab3f05569deb27a4d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsCheckSession",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPolicyRuleSettingsCheckSession:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPolicyRuleSettingsCheckSession(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPolicyRuleSettingsCheckSessionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsCheckSessionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__98f9f932ff1a1ba8a3d1884f75f96de0b847f1209f11b74e90ce6c32b847c59c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="duration")
    def duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "duration"))

    @builtins.property
    @jsii.member(jsii_name="enforce")
    def enforce(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "enforce"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsCheckSession]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsCheckSession], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsCheckSession],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54bebc964a1fae23bc16f1069331753c0bcdeb0667ebe9311439ada309e70399)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolvers",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolvers:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolvers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4List(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4List",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a5b8839f6063f8e80d40a3f212455bb10e66962cb56280a891f97528cf20d823)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4OutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76c1843f4f12d3c2c852177e41cf15cd7e0729a415cc82a847a11f52e2cd2e26)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4OutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1664fd4c5320f08b6c682f1b9dc856d72cd456bcd614c28b4d7a6ef5c75d83b6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__db8c1e98bce96015d70344c7c864f5fa288faa98438258fd04bd2329499967a0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__078e3f67890b2f886ae20ca2ca532dc64579ebd98f15f7f13ed4358fa741d948)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4OutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4OutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3424bba33bef19c420dbad3f6ab8008266237e9f717cfefd986f9545ed88852b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @builtins.property
    @jsii.member(jsii_name="routeThroughPrivateNetwork")
    def route_through_private_network(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "routeThroughPrivateNetwork"))

    @builtins.property
    @jsii.member(jsii_name="vnetId")
    def vnet_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vnetId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__118e26d71a62eeb1085a306d688f9de92bf5dec0542efb431c074d2b8ea9c24a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6List(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6List",
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
            type_hints = typing.get_type_hints(_typecheckingstub__69b53af6c5108e2d12729fad7a01d8fd8a26cdfa913a968eec600bbfd88c167d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6OutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1615e1b36757b3cc862a93c55c3d52a557e140663bb41b0a1fb2a8c4fde6f8cd)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6OutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__959a131c522003c5e204e6f0b3e59ca937d918e8d37e74f6e63a4f3f1f818842)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d5b582a95a91f084ef45a2f8e8d7d7e24a5ac8d35c9f284522175a9ade5db736)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ad75b88b97902312fe535d73924e9c7bf1132e8e2a535ef6a38e21520a266445)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6OutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6OutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5c5b49c44b9e9f63e8b04c73852600a49534139819d722ae3c5253d1207be30c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @builtins.property
    @jsii.member(jsii_name="routeThroughPrivateNetwork")
    def route_through_private_network(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "routeThroughPrivateNetwork"))

    @builtins.property
    @jsii.member(jsii_name="vnetId")
    def vnet_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vnetId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90f1367b2ba697074643be7a04137b3d954ad243b8b7d8b31feeea62ff303b6c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__18aa93c56fb1490b9140a47a95f743ac3ed4845aa5515383ec3da029161a2f0b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="ipv4")
    def ipv4(
        self,
    ) -> DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4List:
        return typing.cast(DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4List, jsii.get(self, "ipv4"))

    @builtins.property
    @jsii.member(jsii_name="ipv6")
    def ipv6(
        self,
    ) -> DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6List:
        return typing.cast(DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6List, jsii.get(self, "ipv6"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolvers]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolvers], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolvers],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1eedbdeb50e1f1402bb91a5ea55774daff9f75f3b1d4b8d58d3ca916b5fc9ed7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsEgress",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPolicyRuleSettingsEgress:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPolicyRuleSettingsEgress(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPolicyRuleSettingsEgressOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsEgressOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7bc678ea0ded3a4b23fedc37f6669c3e9cffac842a6d17efe515c036655471a3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="ipv4")
    def ipv4(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv4"))

    @builtins.property
    @jsii.member(jsii_name="ipv4Fallback")
    def ipv4_fallback(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv4Fallback"))

    @builtins.property
    @jsii.member(jsii_name="ipv6")
    def ipv6(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv6"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsEgress]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsEgress], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsEgress],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9047946c7dcf8e7af19a07be4482a5c506a265d5efacea8323cee4769b2592f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsL4Override",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPolicyRuleSettingsL4Override:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPolicyRuleSettingsL4Override(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPolicyRuleSettingsL4OverrideOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsL4OverrideOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__459ad6d2ec56656acdd79ee6c17688aece136ac5a698ac281e5ee6fc20e31d27)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsL4Override]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsL4Override], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsL4Override],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c539d20a4df45b95e31bcf7e32bc8e5d75c4c046579778362111cac1144f9d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsNotificationSettings",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPolicyRuleSettingsNotificationSettings:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPolicyRuleSettingsNotificationSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPolicyRuleSettingsNotificationSettingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsNotificationSettingsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2b54db2f6ac2cedce8aae6052a48120770ca49d9aadc1fb177e4feea2fb44623)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "enabled"))

    @builtins.property
    @jsii.member(jsii_name="includeContext")
    def include_context(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "includeContext"))

    @builtins.property
    @jsii.member(jsii_name="msg")
    def msg(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "msg"))

    @builtins.property
    @jsii.member(jsii_name="supportUrl")
    def support_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "supportUrl"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsNotificationSettings]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsNotificationSettings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsNotificationSettings],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64f911a5bee024f48423ecbfce1077f1d4e56b1b9b79a837d8fc11d80dd025e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustGatewayPolicyRuleSettingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3ec398dddfbd6072f7beeef113972f12587cd891c76ba03d9f044186be6346a8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="addHeaders")
    def add_headers(self) -> _cdktf_9a9027ec.StringListMap:
        return typing.cast(_cdktf_9a9027ec.StringListMap, jsii.get(self, "addHeaders"))

    @builtins.property
    @jsii.member(jsii_name="allowChildBypass")
    def allow_child_bypass(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "allowChildBypass"))

    @builtins.property
    @jsii.member(jsii_name="auditSsh")
    def audit_ssh(
        self,
    ) -> DataCloudflareZeroTrustGatewayPolicyRuleSettingsAuditSshOutputReference:
        return typing.cast(DataCloudflareZeroTrustGatewayPolicyRuleSettingsAuditSshOutputReference, jsii.get(self, "auditSsh"))

    @builtins.property
    @jsii.member(jsii_name="bisoAdminControls")
    def biso_admin_controls(
        self,
    ) -> DataCloudflareZeroTrustGatewayPolicyRuleSettingsBisoAdminControlsOutputReference:
        return typing.cast(DataCloudflareZeroTrustGatewayPolicyRuleSettingsBisoAdminControlsOutputReference, jsii.get(self, "bisoAdminControls"))

    @builtins.property
    @jsii.member(jsii_name="blockPage")
    def block_page(
        self,
    ) -> DataCloudflareZeroTrustGatewayPolicyRuleSettingsBlockPageOutputReference:
        return typing.cast(DataCloudflareZeroTrustGatewayPolicyRuleSettingsBlockPageOutputReference, jsii.get(self, "blockPage"))

    @builtins.property
    @jsii.member(jsii_name="blockPageEnabled")
    def block_page_enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "blockPageEnabled"))

    @builtins.property
    @jsii.member(jsii_name="blockReason")
    def block_reason(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "blockReason"))

    @builtins.property
    @jsii.member(jsii_name="bypassParentRule")
    def bypass_parent_rule(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "bypassParentRule"))

    @builtins.property
    @jsii.member(jsii_name="checkSession")
    def check_session(
        self,
    ) -> DataCloudflareZeroTrustGatewayPolicyRuleSettingsCheckSessionOutputReference:
        return typing.cast(DataCloudflareZeroTrustGatewayPolicyRuleSettingsCheckSessionOutputReference, jsii.get(self, "checkSession"))

    @builtins.property
    @jsii.member(jsii_name="dnsResolvers")
    def dns_resolvers(
        self,
    ) -> DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversOutputReference:
        return typing.cast(DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversOutputReference, jsii.get(self, "dnsResolvers"))

    @builtins.property
    @jsii.member(jsii_name="egress")
    def egress(
        self,
    ) -> DataCloudflareZeroTrustGatewayPolicyRuleSettingsEgressOutputReference:
        return typing.cast(DataCloudflareZeroTrustGatewayPolicyRuleSettingsEgressOutputReference, jsii.get(self, "egress"))

    @builtins.property
    @jsii.member(jsii_name="ignoreCnameCategoryMatches")
    def ignore_cname_category_matches(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "ignoreCnameCategoryMatches"))

    @builtins.property
    @jsii.member(jsii_name="insecureDisableDnssecValidation")
    def insecure_disable_dnssec_validation(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "insecureDisableDnssecValidation"))

    @builtins.property
    @jsii.member(jsii_name="ipCategories")
    def ip_categories(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "ipCategories"))

    @builtins.property
    @jsii.member(jsii_name="ipIndicatorFeeds")
    def ip_indicator_feeds(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "ipIndicatorFeeds"))

    @builtins.property
    @jsii.member(jsii_name="l4Override")
    def l4_override(
        self,
    ) -> DataCloudflareZeroTrustGatewayPolicyRuleSettingsL4OverrideOutputReference:
        return typing.cast(DataCloudflareZeroTrustGatewayPolicyRuleSettingsL4OverrideOutputReference, jsii.get(self, "l4Override"))

    @builtins.property
    @jsii.member(jsii_name="notificationSettings")
    def notification_settings(
        self,
    ) -> DataCloudflareZeroTrustGatewayPolicyRuleSettingsNotificationSettingsOutputReference:
        return typing.cast(DataCloudflareZeroTrustGatewayPolicyRuleSettingsNotificationSettingsOutputReference, jsii.get(self, "notificationSettings"))

    @builtins.property
    @jsii.member(jsii_name="overrideHost")
    def override_host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "overrideHost"))

    @builtins.property
    @jsii.member(jsii_name="overrideIps")
    def override_ips(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "overrideIps"))

    @builtins.property
    @jsii.member(jsii_name="payloadLog")
    def payload_log(
        self,
    ) -> "DataCloudflareZeroTrustGatewayPolicyRuleSettingsPayloadLogOutputReference":
        return typing.cast("DataCloudflareZeroTrustGatewayPolicyRuleSettingsPayloadLogOutputReference", jsii.get(self, "payloadLog"))

    @builtins.property
    @jsii.member(jsii_name="quarantine")
    def quarantine(
        self,
    ) -> "DataCloudflareZeroTrustGatewayPolicyRuleSettingsQuarantineOutputReference":
        return typing.cast("DataCloudflareZeroTrustGatewayPolicyRuleSettingsQuarantineOutputReference", jsii.get(self, "quarantine"))

    @builtins.property
    @jsii.member(jsii_name="redirect")
    def redirect(
        self,
    ) -> "DataCloudflareZeroTrustGatewayPolicyRuleSettingsRedirectOutputReference":
        return typing.cast("DataCloudflareZeroTrustGatewayPolicyRuleSettingsRedirectOutputReference", jsii.get(self, "redirect"))

    @builtins.property
    @jsii.member(jsii_name="resolveDnsInternally")
    def resolve_dns_internally(
        self,
    ) -> "DataCloudflareZeroTrustGatewayPolicyRuleSettingsResolveDnsInternallyOutputReference":
        return typing.cast("DataCloudflareZeroTrustGatewayPolicyRuleSettingsResolveDnsInternallyOutputReference", jsii.get(self, "resolveDnsInternally"))

    @builtins.property
    @jsii.member(jsii_name="resolveDnsThroughCloudflare")
    def resolve_dns_through_cloudflare(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "resolveDnsThroughCloudflare"))

    @builtins.property
    @jsii.member(jsii_name="untrustedCert")
    def untrusted_cert(
        self,
    ) -> "DataCloudflareZeroTrustGatewayPolicyRuleSettingsUntrustedCertOutputReference":
        return typing.cast("DataCloudflareZeroTrustGatewayPolicyRuleSettingsUntrustedCertOutputReference", jsii.get(self, "untrustedCert"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettings]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettings],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__781e66bdcaebb109fe0978315ec52a0b3ea05a77f92825a3e2ac01e73a6e5ad3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsPayloadLog",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPolicyRuleSettingsPayloadLog:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPolicyRuleSettingsPayloadLog(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPolicyRuleSettingsPayloadLogOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsPayloadLogOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__42ba8788ef31bed58b8eead8567db2a116d3644a028daef5e2bb925cc8718cb3)
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
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsPayloadLog]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsPayloadLog], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsPayloadLog],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bbc3e2d8f770fd9caf5238d981def34ee5a07451897aafc09879abc15df756b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsQuarantine",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPolicyRuleSettingsQuarantine:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPolicyRuleSettingsQuarantine(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPolicyRuleSettingsQuarantineOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsQuarantineOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2bec7f7f703b52689c61472c2ac8687683545df26ed5311ea5c59402f3919e97)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="fileTypes")
    def file_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "fileTypes"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsQuarantine]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsQuarantine], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsQuarantine],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c28d59ed2eba55ecf0f7ff6c0d4ce7a641c1dacca16f01cede623785d4bb535f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsRedirect",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPolicyRuleSettingsRedirect:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPolicyRuleSettingsRedirect(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPolicyRuleSettingsRedirectOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsRedirectOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f657f57befbdf22469af56ea8d03df92002399ab52c1517d686e586ba2c36911)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="includeContext")
    def include_context(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "includeContext"))

    @builtins.property
    @jsii.member(jsii_name="preservePathAndQuery")
    def preserve_path_and_query(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "preservePathAndQuery"))

    @builtins.property
    @jsii.member(jsii_name="targetUri")
    def target_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetUri"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsRedirect]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsRedirect], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsRedirect],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7aed2cf51276412efc5099f514f086632411a36c9113bd06de6981b428196a58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsResolveDnsInternally",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPolicyRuleSettingsResolveDnsInternally:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPolicyRuleSettingsResolveDnsInternally(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPolicyRuleSettingsResolveDnsInternallyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsResolveDnsInternallyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__61f1ac4d938dfc9fafb1783fd1af34dc999f47833c8183db8c11c80865c63ac8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="fallback")
    def fallback(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fallback"))

    @builtins.property
    @jsii.member(jsii_name="viewId")
    def view_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "viewId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsResolveDnsInternally]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsResolveDnsInternally], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsResolveDnsInternally],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45aff61ac4450af603f56501f001902a36fcf1e813c998eeb4a778732da97391)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsUntrustedCert",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPolicyRuleSettingsUntrustedCert:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPolicyRuleSettingsUntrustedCert(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPolicyRuleSettingsUntrustedCertOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyRuleSettingsUntrustedCertOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__12fed257eba07bcf14e6fa76e3cd43960b4ebc83a54ea242ba868ae8b6b46a25)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="action")
    def action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "action"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsUntrustedCert]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsUntrustedCert], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsUntrustedCert],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ef420dfac78d46eb5c4f29330c5a6ef0bdf0e304c4688e4483bf79648e255ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicySchedule",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustGatewayPolicySchedule:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustGatewayPolicySchedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustGatewayPolicyScheduleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustGatewayPolicy.DataCloudflareZeroTrustGatewayPolicyScheduleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d316a68c7e155e98b929f6b89a7f52f62a5af76e1d0809df3ceff132c0b98674)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="fri")
    def fri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fri"))

    @builtins.property
    @jsii.member(jsii_name="mon")
    def mon(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mon"))

    @builtins.property
    @jsii.member(jsii_name="sat")
    def sat(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sat"))

    @builtins.property
    @jsii.member(jsii_name="sun")
    def sun(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sun"))

    @builtins.property
    @jsii.member(jsii_name="thu")
    def thu(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "thu"))

    @builtins.property
    @jsii.member(jsii_name="timeZone")
    def time_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeZone"))

    @builtins.property
    @jsii.member(jsii_name="tue")
    def tue(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tue"))

    @builtins.property
    @jsii.member(jsii_name="wed")
    def wed(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "wed"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustGatewayPolicySchedule]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustGatewayPolicySchedule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustGatewayPolicySchedule],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c93e48ff759654f00f68e2b7a8f264de313b2772b373852220c51de4d3420fa8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataCloudflareZeroTrustGatewayPolicy",
    "DataCloudflareZeroTrustGatewayPolicyConfig",
    "DataCloudflareZeroTrustGatewayPolicyExpiration",
    "DataCloudflareZeroTrustGatewayPolicyExpirationOutputReference",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettings",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsAuditSsh",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsAuditSshOutputReference",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsBisoAdminControls",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsBisoAdminControlsOutputReference",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsBlockPage",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsBlockPageOutputReference",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsCheckSession",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsCheckSessionOutputReference",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolvers",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4List",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4OutputReference",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6List",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6OutputReference",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversOutputReference",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsEgress",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsEgressOutputReference",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsL4Override",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsL4OverrideOutputReference",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsNotificationSettings",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsNotificationSettingsOutputReference",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsOutputReference",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsPayloadLog",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsPayloadLogOutputReference",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsQuarantine",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsQuarantineOutputReference",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsRedirect",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsRedirectOutputReference",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsResolveDnsInternally",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsResolveDnsInternallyOutputReference",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsUntrustedCert",
    "DataCloudflareZeroTrustGatewayPolicyRuleSettingsUntrustedCertOutputReference",
    "DataCloudflareZeroTrustGatewayPolicySchedule",
    "DataCloudflareZeroTrustGatewayPolicyScheduleOutputReference",
]

publication.publish()

def _typecheckingstub__2f24cbf0cffd6893721db1085940f90cf5f4d71a9c4aa1325618c8a3850a50cc(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    rule_id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__d0de6de178a356e7c31627e9f0e2adc130dd978afff79199c5c3a153cfb18151(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0bfc76d6e9a1e61c147cccc0b9ca5dafd3dd02a5addaba9c0b4290f38f9bb71(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6595b478e03d987aa56e181ff37de52dc7a7a48ddfbf4d193e75184f335ce3e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fb94ee976981924ba676dbe647a764b65bcffd94a5dccb4e51b6aea174fbb3c(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    rule_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e5e790895ab797cf8c4d44eb6f565ec54b57c4595fcc1915afaebb2d5f3b991(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b863212905eb120b1c0986704dffacfb2a690361ba69b4ccffbd2da5bacc35b(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyExpiration],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__344b349caecda084830991cff004d66287735041ff77d41a09f0f111c14fa715(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a1f895b9101ef28664c32b693801726a2cadc9471e812f0e7c80663adb00550(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsAuditSsh],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdfafba495d739fba9eb148095536119ab3523ef793d9e777ff47f4675faba80(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5da64159be9fabf522abe3deb69242071899a5264f15b38cc6726d4ca4e7f885(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsBisoAdminControls],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af5bbf3ef9309903a14a82446bfa205f837efddca5a41b0485526c43f86749ab(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1a58a5dda2adbaebb895c752a6baca8417d8c964953117ab3f05569deb27a4d(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsBlockPage],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98f9f932ff1a1ba8a3d1884f75f96de0b847f1209f11b74e90ce6c32b847c59c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54bebc964a1fae23bc16f1069331753c0bcdeb0667ebe9311439ada309e70399(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsCheckSession],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5b8839f6063f8e80d40a3f212455bb10e66962cb56280a891f97528cf20d823(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76c1843f4f12d3c2c852177e41cf15cd7e0729a415cc82a847a11f52e2cd2e26(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1664fd4c5320f08b6c682f1b9dc856d72cd456bcd614c28b4d7a6ef5c75d83b6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db8c1e98bce96015d70344c7c864f5fa288faa98438258fd04bd2329499967a0(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__078e3f67890b2f886ae20ca2ca532dc64579ebd98f15f7f13ed4358fa741d948(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3424bba33bef19c420dbad3f6ab8008266237e9f717cfefd986f9545ed88852b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__118e26d71a62eeb1085a306d688f9de92bf5dec0542efb431c074d2b8ea9c24a(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv4],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69b53af6c5108e2d12729fad7a01d8fd8a26cdfa913a968eec600bbfd88c167d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1615e1b36757b3cc862a93c55c3d52a557e140663bb41b0a1fb2a8c4fde6f8cd(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__959a131c522003c5e204e6f0b3e59ca937d918e8d37e74f6e63a4f3f1f818842(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5b582a95a91f084ef45a2f8e8d7d7e24a5ac8d35c9f284522175a9ade5db736(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad75b88b97902312fe535d73924e9c7bf1132e8e2a535ef6a38e21520a266445(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c5b49c44b9e9f63e8b04c73852600a49534139819d722ae3c5253d1207be30c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90f1367b2ba697074643be7a04137b3d954ad243b8b7d8b31feeea62ff303b6c(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolversIpv6],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18aa93c56fb1490b9140a47a95f743ac3ed4845aa5515383ec3da029161a2f0b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1eedbdeb50e1f1402bb91a5ea55774daff9f75f3b1d4b8d58d3ca916b5fc9ed7(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsDnsResolvers],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bc678ea0ded3a4b23fedc37f6669c3e9cffac842a6d17efe515c036655471a3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9047946c7dcf8e7af19a07be4482a5c506a265d5efacea8323cee4769b2592f3(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsEgress],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__459ad6d2ec56656acdd79ee6c17688aece136ac5a698ac281e5ee6fc20e31d27(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c539d20a4df45b95e31bcf7e32bc8e5d75c4c046579778362111cac1144f9d0(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsL4Override],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b54db2f6ac2cedce8aae6052a48120770ca49d9aadc1fb177e4feea2fb44623(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64f911a5bee024f48423ecbfce1077f1d4e56b1b9b79a837d8fc11d80dd025e9(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsNotificationSettings],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ec398dddfbd6072f7beeef113972f12587cd891c76ba03d9f044186be6346a8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__781e66bdcaebb109fe0978315ec52a0b3ea05a77f92825a3e2ac01e73a6e5ad3(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettings],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42ba8788ef31bed58b8eead8567db2a116d3644a028daef5e2bb925cc8718cb3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bbc3e2d8f770fd9caf5238d981def34ee5a07451897aafc09879abc15df756b(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsPayloadLog],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bec7f7f703b52689c61472c2ac8687683545df26ed5311ea5c59402f3919e97(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c28d59ed2eba55ecf0f7ff6c0d4ce7a641c1dacca16f01cede623785d4bb535f(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsQuarantine],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f657f57befbdf22469af56ea8d03df92002399ab52c1517d686e586ba2c36911(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7aed2cf51276412efc5099f514f086632411a36c9113bd06de6981b428196a58(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsRedirect],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61f1ac4d938dfc9fafb1783fd1af34dc999f47833c8183db8c11c80865c63ac8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45aff61ac4450af603f56501f001902a36fcf1e813c998eeb4a778732da97391(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsResolveDnsInternally],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12fed257eba07bcf14e6fa76e3cd43960b4ebc83a54ea242ba868ae8b6b46a25(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ef420dfac78d46eb5c4f29330c5a6ef0bdf0e304c4688e4483bf79648e255ca(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPolicyRuleSettingsUntrustedCert],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d316a68c7e155e98b929f6b89a7f52f62a5af76e1d0809df3ceff132c0b98674(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c93e48ff759654f00f68e2b7a8f264de313b2772b373852220c51de4d3420fa8(
    value: typing.Optional[DataCloudflareZeroTrustGatewayPolicySchedule],
) -> None:
    """Type checking stubs"""
    pass
