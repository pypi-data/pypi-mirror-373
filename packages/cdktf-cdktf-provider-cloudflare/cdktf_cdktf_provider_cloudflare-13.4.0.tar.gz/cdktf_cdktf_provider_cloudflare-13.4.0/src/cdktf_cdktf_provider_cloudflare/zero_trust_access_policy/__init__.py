r'''
# `cloudflare_zero_trust_access_policy`

Refer to the Terraform Registry for docs: [`cloudflare_zero_trust_access_policy`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy).
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


class ZeroTrustAccessPolicy(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicy",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy cloudflare_zero_trust_access_policy}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        decision: builtins.str,
        name: builtins.str,
        approval_groups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustAccessPolicyApprovalGroups", typing.Dict[builtins.str, typing.Any]]]]] = None,
        approval_required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        exclude: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustAccessPolicyExclude", typing.Dict[builtins.str, typing.Any]]]]] = None,
        include: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustAccessPolicyInclude", typing.Dict[builtins.str, typing.Any]]]]] = None,
        isolation_required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        purpose_justification_prompt: typing.Optional[builtins.str] = None,
        purpose_justification_required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        require: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustAccessPolicyRequire", typing.Dict[builtins.str, typing.Any]]]]] = None,
        session_duration: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy cloudflare_zero_trust_access_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#account_id ZeroTrustAccessPolicy#account_id}
        :param decision: The action Access will take if a user matches this policy. Infrastructure application policies can only use the Allow action. Available values: "allow", "deny", "non_identity", "bypass". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#decision ZeroTrustAccessPolicy#decision}
        :param name: The name of the Access policy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#name ZeroTrustAccessPolicy#name}
        :param approval_groups: Administrators who can approve a temporary authentication request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#approval_groups ZeroTrustAccessPolicy#approval_groups}
        :param approval_required: Requires the user to request access from an administrator at the start of each session. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#approval_required ZeroTrustAccessPolicy#approval_required}
        :param exclude: Rules evaluated with a NOT logical operator. To match the policy, a user cannot meet any of the Exclude rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#exclude ZeroTrustAccessPolicy#exclude}
        :param include: Rules evaluated with an OR logical operator. A user needs to meet only one of the Include rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#include ZeroTrustAccessPolicy#include}
        :param isolation_required: Require this application to be served in an isolated browser for users matching this policy. 'Client Web Isolation' must be on for the account in order to use this feature. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#isolation_required ZeroTrustAccessPolicy#isolation_required}
        :param purpose_justification_prompt: A custom message that will appear on the purpose justification screen. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#purpose_justification_prompt ZeroTrustAccessPolicy#purpose_justification_prompt}
        :param purpose_justification_required: Require users to enter a justification when they log in to the application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#purpose_justification_required ZeroTrustAccessPolicy#purpose_justification_required}
        :param require: Rules evaluated with an AND logical operator. To match the policy, a user must meet all of the Require rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#require ZeroTrustAccessPolicy#require}
        :param session_duration: The amount of time that tokens issued for the application will be valid. Must be in the format ``300ms`` or ``2h45m``. Valid time units are: ns, us (or µs), ms, s, m, h. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#session_duration ZeroTrustAccessPolicy#session_duration}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d70830b701fa21bbe3097e3ce85383f1c5172780596ccae55d9e71390a0b5c83)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = ZeroTrustAccessPolicyConfig(
            account_id=account_id,
            decision=decision,
            name=name,
            approval_groups=approval_groups,
            approval_required=approval_required,
            exclude=exclude,
            include=include,
            isolation_required=isolation_required,
            purpose_justification_prompt=purpose_justification_prompt,
            purpose_justification_required=purpose_justification_required,
            require=require,
            session_duration=session_duration,
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
        '''Generates CDKTF code for importing a ZeroTrustAccessPolicy resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ZeroTrustAccessPolicy to import.
        :param import_from_id: The id of the existing ZeroTrustAccessPolicy that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ZeroTrustAccessPolicy to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__103d4924d25381220a059d6856d206bd9ca0af15f9e4ab5371afd16acf97cc2f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putApprovalGroups")
    def put_approval_groups(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustAccessPolicyApprovalGroups", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97e5936063f8543a55f835bd59b166e189210684b93e5d7b5dd2da09ffd91343)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putApprovalGroups", [value]))

    @jsii.member(jsii_name="putExclude")
    def put_exclude(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustAccessPolicyExclude", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c42102dd1d8b5019e25d4f8e55ec147664c6162d1586a969cb77f1fd7a6b5b12)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putExclude", [value]))

    @jsii.member(jsii_name="putInclude")
    def put_include(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustAccessPolicyInclude", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7eefe6d5ef3b21987cbacb6cfd625d26f7880e61dd069b42a00872eac2c961d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putInclude", [value]))

    @jsii.member(jsii_name="putRequire")
    def put_require(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustAccessPolicyRequire", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f91846a3e5cfe024f97ba5b88ecb39d6ab64c64418a1cdce2326098d53fe3558)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRequire", [value]))

    @jsii.member(jsii_name="resetApprovalGroups")
    def reset_approval_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApprovalGroups", []))

    @jsii.member(jsii_name="resetApprovalRequired")
    def reset_approval_required(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApprovalRequired", []))

    @jsii.member(jsii_name="resetExclude")
    def reset_exclude(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExclude", []))

    @jsii.member(jsii_name="resetInclude")
    def reset_include(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInclude", []))

    @jsii.member(jsii_name="resetIsolationRequired")
    def reset_isolation_required(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsolationRequired", []))

    @jsii.member(jsii_name="resetPurposeJustificationPrompt")
    def reset_purpose_justification_prompt(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPurposeJustificationPrompt", []))

    @jsii.member(jsii_name="resetPurposeJustificationRequired")
    def reset_purpose_justification_required(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPurposeJustificationRequired", []))

    @jsii.member(jsii_name="resetRequire")
    def reset_require(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequire", []))

    @jsii.member(jsii_name="resetSessionDuration")
    def reset_session_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSessionDuration", []))

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
    @jsii.member(jsii_name="approvalGroups")
    def approval_groups(self) -> "ZeroTrustAccessPolicyApprovalGroupsList":
        return typing.cast("ZeroTrustAccessPolicyApprovalGroupsList", jsii.get(self, "approvalGroups"))

    @builtins.property
    @jsii.member(jsii_name="exclude")
    def exclude(self) -> "ZeroTrustAccessPolicyExcludeList":
        return typing.cast("ZeroTrustAccessPolicyExcludeList", jsii.get(self, "exclude"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="include")
    def include(self) -> "ZeroTrustAccessPolicyIncludeList":
        return typing.cast("ZeroTrustAccessPolicyIncludeList", jsii.get(self, "include"))

    @builtins.property
    @jsii.member(jsii_name="require")
    def require(self) -> "ZeroTrustAccessPolicyRequireList":
        return typing.cast("ZeroTrustAccessPolicyRequireList", jsii.get(self, "require"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="approvalGroupsInput")
    def approval_groups_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessPolicyApprovalGroups"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessPolicyApprovalGroups"]]], jsii.get(self, "approvalGroupsInput"))

    @builtins.property
    @jsii.member(jsii_name="approvalRequiredInput")
    def approval_required_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "approvalRequiredInput"))

    @builtins.property
    @jsii.member(jsii_name="decisionInput")
    def decision_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "decisionInput"))

    @builtins.property
    @jsii.member(jsii_name="excludeInput")
    def exclude_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessPolicyExclude"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessPolicyExclude"]]], jsii.get(self, "excludeInput"))

    @builtins.property
    @jsii.member(jsii_name="includeInput")
    def include_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessPolicyInclude"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessPolicyInclude"]]], jsii.get(self, "includeInput"))

    @builtins.property
    @jsii.member(jsii_name="isolationRequiredInput")
    def isolation_required_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isolationRequiredInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="purposeJustificationPromptInput")
    def purpose_justification_prompt_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "purposeJustificationPromptInput"))

    @builtins.property
    @jsii.member(jsii_name="purposeJustificationRequiredInput")
    def purpose_justification_required_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "purposeJustificationRequiredInput"))

    @builtins.property
    @jsii.member(jsii_name="requireInput")
    def require_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessPolicyRequire"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessPolicyRequire"]]], jsii.get(self, "requireInput"))

    @builtins.property
    @jsii.member(jsii_name="sessionDurationInput")
    def session_duration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sessionDurationInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e6d8254b5fac529f599e7382dc614282357239e541ba2f429392a8781f7adf7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="approvalRequired")
    def approval_required(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "approvalRequired"))

    @approval_required.setter
    def approval_required(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c72aca090dca014edbce31c869cedbe59d52c721b468e5e329da2f34a9e0325c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "approvalRequired", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="decision")
    def decision(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "decision"))

    @decision.setter
    def decision(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4833cac024c32ee344b1b7291f07a5bb3feab51085514c71bd41c4864c326f76)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "decision", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isolationRequired")
    def isolation_required(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isolationRequired"))

    @isolation_required.setter
    def isolation_required(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__711aa0a4df834b4579ec0ab636b699ce0d56fe8642f1a327da3e74ae869f9a8c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isolationRequired", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9675c9ce6ab73ad2e8d9e890440bb8ced121ec187d2a2e94112b6251003de283)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="purposeJustificationPrompt")
    def purpose_justification_prompt(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "purposeJustificationPrompt"))

    @purpose_justification_prompt.setter
    def purpose_justification_prompt(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c770cef1a421a715549246cc86649bbde00ec7553d7664a3922ff2734b51d3e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "purposeJustificationPrompt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="purposeJustificationRequired")
    def purpose_justification_required(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "purposeJustificationRequired"))

    @purpose_justification_required.setter
    def purpose_justification_required(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0e8698c87c24aded5d3110e9e104243e6b5fce2f23bb7aeb58ded25ebd6328c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "purposeJustificationRequired", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sessionDuration")
    def session_duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sessionDuration"))

    @session_duration.setter
    def session_duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a6b1ed10b68bddf566328fdd936fd040cf78628c6daf76f0cd5335e26ffa76e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sessionDuration", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyApprovalGroups",
    jsii_struct_bases=[],
    name_mapping={
        "approvals_needed": "approvalsNeeded",
        "email_addresses": "emailAddresses",
        "email_list_uuid": "emailListUuid",
    },
)
class ZeroTrustAccessPolicyApprovalGroups:
    def __init__(
        self,
        *,
        approvals_needed: jsii.Number,
        email_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
        email_list_uuid: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param approvals_needed: The number of approvals needed to obtain access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#approvals_needed ZeroTrustAccessPolicy#approvals_needed}
        :param email_addresses: A list of emails that can approve the access request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email_addresses ZeroTrustAccessPolicy#email_addresses}
        :param email_list_uuid: The UUID of an re-usable email list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email_list_uuid ZeroTrustAccessPolicy#email_list_uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff4f4f1a2a58ee8e9cdde159bfb04f70ef04e438b77b2ffdeeb16f09f231696a)
            check_type(argname="argument approvals_needed", value=approvals_needed, expected_type=type_hints["approvals_needed"])
            check_type(argname="argument email_addresses", value=email_addresses, expected_type=type_hints["email_addresses"])
            check_type(argname="argument email_list_uuid", value=email_list_uuid, expected_type=type_hints["email_list_uuid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "approvals_needed": approvals_needed,
        }
        if email_addresses is not None:
            self._values["email_addresses"] = email_addresses
        if email_list_uuid is not None:
            self._values["email_list_uuid"] = email_list_uuid

    @builtins.property
    def approvals_needed(self) -> jsii.Number:
        '''The number of approvals needed to obtain access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#approvals_needed ZeroTrustAccessPolicy#approvals_needed}
        '''
        result = self._values.get("approvals_needed")
        assert result is not None, "Required property 'approvals_needed' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def email_addresses(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of emails that can approve the access request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email_addresses ZeroTrustAccessPolicy#email_addresses}
        '''
        result = self._values.get("email_addresses")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def email_list_uuid(self) -> typing.Optional[builtins.str]:
        '''The UUID of an re-usable email list.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email_list_uuid ZeroTrustAccessPolicy#email_list_uuid}
        '''
        result = self._values.get("email_list_uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyApprovalGroups(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyApprovalGroupsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyApprovalGroupsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e316f0e0ab35c0bd923e8f1d5dcfb135ac19a8d2a61a70d1251fe3b07188361d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ZeroTrustAccessPolicyApprovalGroupsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77ff6acba382fb8ac99c314a3bf713a9d972ae20d7cc66564d991d487dd06925)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ZeroTrustAccessPolicyApprovalGroupsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3b41d610a9c6159e872411e70ed00077819e3b22becf2e81b9e4f5412bda726)
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
            type_hints = typing.get_type_hints(_typecheckingstub__574c033ebd3cf42f1565d092b5ef513755b3077f208eba2890981d139af0a625)
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
            type_hints = typing.get_type_hints(_typecheckingstub__84ca3ac07d37f53057891ff1a8d1a416bdb4981f327b39d15983399865308337)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessPolicyApprovalGroups]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessPolicyApprovalGroups]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessPolicyApprovalGroups]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9519fd3c2ca362307587a40f0be5eeea3de99d1e40d2f79c208f4be7e4b05f74)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustAccessPolicyApprovalGroupsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyApprovalGroupsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3506a0c26fe09cbfdd02d9902a6854e1ccfec5611a1e4e45397b2cb5df189f87)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetEmailAddresses")
    def reset_email_addresses(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailAddresses", []))

    @jsii.member(jsii_name="resetEmailListUuid")
    def reset_email_list_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailListUuid", []))

    @builtins.property
    @jsii.member(jsii_name="approvalsNeededInput")
    def approvals_needed_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "approvalsNeededInput"))

    @builtins.property
    @jsii.member(jsii_name="emailAddressesInput")
    def email_addresses_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "emailAddressesInput"))

    @builtins.property
    @jsii.member(jsii_name="emailListUuidInput")
    def email_list_uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailListUuidInput"))

    @builtins.property
    @jsii.member(jsii_name="approvalsNeeded")
    def approvals_needed(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "approvalsNeeded"))

    @approvals_needed.setter
    def approvals_needed(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd4f59379c2124ce0c508ef79810953b9b4139dda309afcde19881a5762d2d66)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "approvalsNeeded", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="emailAddresses")
    def email_addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "emailAddresses"))

    @email_addresses.setter
    def email_addresses(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7719394293a74ce0926b4c4da9295339a59e1485fdb68b35ee4608ad43ffd922)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailAddresses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="emailListUuid")
    def email_list_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailListUuid"))

    @email_list_uuid.setter
    def email_list_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3b285206e1087e666dcdf0012079b70e4eebc60b1f60a6fb7ba7bdb0ad423dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailListUuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyApprovalGroups]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyApprovalGroups]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyApprovalGroups]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b4a9aab03cda8da1a3b925dc458c3824a3b4a4120419595eab2aca1d2c37f02)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyConfig",
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
        "decision": "decision",
        "name": "name",
        "approval_groups": "approvalGroups",
        "approval_required": "approvalRequired",
        "exclude": "exclude",
        "include": "include",
        "isolation_required": "isolationRequired",
        "purpose_justification_prompt": "purposeJustificationPrompt",
        "purpose_justification_required": "purposeJustificationRequired",
        "require": "require",
        "session_duration": "sessionDuration",
    },
)
class ZeroTrustAccessPolicyConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        decision: builtins.str,
        name: builtins.str,
        approval_groups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustAccessPolicyApprovalGroups, typing.Dict[builtins.str, typing.Any]]]]] = None,
        approval_required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        exclude: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustAccessPolicyExclude", typing.Dict[builtins.str, typing.Any]]]]] = None,
        include: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustAccessPolicyInclude", typing.Dict[builtins.str, typing.Any]]]]] = None,
        isolation_required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        purpose_justification_prompt: typing.Optional[builtins.str] = None,
        purpose_justification_required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        require: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustAccessPolicyRequire", typing.Dict[builtins.str, typing.Any]]]]] = None,
        session_duration: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#account_id ZeroTrustAccessPolicy#account_id}
        :param decision: The action Access will take if a user matches this policy. Infrastructure application policies can only use the Allow action. Available values: "allow", "deny", "non_identity", "bypass". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#decision ZeroTrustAccessPolicy#decision}
        :param name: The name of the Access policy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#name ZeroTrustAccessPolicy#name}
        :param approval_groups: Administrators who can approve a temporary authentication request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#approval_groups ZeroTrustAccessPolicy#approval_groups}
        :param approval_required: Requires the user to request access from an administrator at the start of each session. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#approval_required ZeroTrustAccessPolicy#approval_required}
        :param exclude: Rules evaluated with a NOT logical operator. To match the policy, a user cannot meet any of the Exclude rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#exclude ZeroTrustAccessPolicy#exclude}
        :param include: Rules evaluated with an OR logical operator. A user needs to meet only one of the Include rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#include ZeroTrustAccessPolicy#include}
        :param isolation_required: Require this application to be served in an isolated browser for users matching this policy. 'Client Web Isolation' must be on for the account in order to use this feature. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#isolation_required ZeroTrustAccessPolicy#isolation_required}
        :param purpose_justification_prompt: A custom message that will appear on the purpose justification screen. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#purpose_justification_prompt ZeroTrustAccessPolicy#purpose_justification_prompt}
        :param purpose_justification_required: Require users to enter a justification when they log in to the application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#purpose_justification_required ZeroTrustAccessPolicy#purpose_justification_required}
        :param require: Rules evaluated with an AND logical operator. To match the policy, a user must meet all of the Require rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#require ZeroTrustAccessPolicy#require}
        :param session_duration: The amount of time that tokens issued for the application will be valid. Must be in the format ``300ms`` or ``2h45m``. Valid time units are: ns, us (or µs), ms, s, m, h. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#session_duration ZeroTrustAccessPolicy#session_duration}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42bd77d29aedbebe7fe114c3db69a254776c577afb59e10e4296bb00cb90027f)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument decision", value=decision, expected_type=type_hints["decision"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument approval_groups", value=approval_groups, expected_type=type_hints["approval_groups"])
            check_type(argname="argument approval_required", value=approval_required, expected_type=type_hints["approval_required"])
            check_type(argname="argument exclude", value=exclude, expected_type=type_hints["exclude"])
            check_type(argname="argument include", value=include, expected_type=type_hints["include"])
            check_type(argname="argument isolation_required", value=isolation_required, expected_type=type_hints["isolation_required"])
            check_type(argname="argument purpose_justification_prompt", value=purpose_justification_prompt, expected_type=type_hints["purpose_justification_prompt"])
            check_type(argname="argument purpose_justification_required", value=purpose_justification_required, expected_type=type_hints["purpose_justification_required"])
            check_type(argname="argument require", value=require, expected_type=type_hints["require"])
            check_type(argname="argument session_duration", value=session_duration, expected_type=type_hints["session_duration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
            "decision": decision,
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
        if approval_groups is not None:
            self._values["approval_groups"] = approval_groups
        if approval_required is not None:
            self._values["approval_required"] = approval_required
        if exclude is not None:
            self._values["exclude"] = exclude
        if include is not None:
            self._values["include"] = include
        if isolation_required is not None:
            self._values["isolation_required"] = isolation_required
        if purpose_justification_prompt is not None:
            self._values["purpose_justification_prompt"] = purpose_justification_prompt
        if purpose_justification_required is not None:
            self._values["purpose_justification_required"] = purpose_justification_required
        if require is not None:
            self._values["require"] = require
        if session_duration is not None:
            self._values["session_duration"] = session_duration

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#account_id ZeroTrustAccessPolicy#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def decision(self) -> builtins.str:
        '''The action Access will take if a user matches this policy.

        Infrastructure application policies can only use the Allow action.
        Available values: "allow", "deny", "non_identity", "bypass".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#decision ZeroTrustAccessPolicy#decision}
        '''
        result = self._values.get("decision")
        assert result is not None, "Required property 'decision' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the Access policy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#name ZeroTrustAccessPolicy#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def approval_groups(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessPolicyApprovalGroups]]]:
        '''Administrators who can approve a temporary authentication request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#approval_groups ZeroTrustAccessPolicy#approval_groups}
        '''
        result = self._values.get("approval_groups")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessPolicyApprovalGroups]]], result)

    @builtins.property
    def approval_required(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Requires the user to request access from an administrator at the start of each session.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#approval_required ZeroTrustAccessPolicy#approval_required}
        '''
        result = self._values.get("approval_required")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def exclude(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessPolicyExclude"]]]:
        '''Rules evaluated with a NOT logical operator.

        To match the policy, a user cannot meet any of the Exclude rules.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#exclude ZeroTrustAccessPolicy#exclude}
        '''
        result = self._values.get("exclude")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessPolicyExclude"]]], result)

    @builtins.property
    def include(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessPolicyInclude"]]]:
        '''Rules evaluated with an OR logical operator. A user needs to meet only one of the Include rules.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#include ZeroTrustAccessPolicy#include}
        '''
        result = self._values.get("include")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessPolicyInclude"]]], result)

    @builtins.property
    def isolation_required(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Require this application to be served in an isolated browser for users matching this policy.

        'Client Web Isolation' must be on for the account in order to use this feature.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#isolation_required ZeroTrustAccessPolicy#isolation_required}
        '''
        result = self._values.get("isolation_required")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def purpose_justification_prompt(self) -> typing.Optional[builtins.str]:
        '''A custom message that will appear on the purpose justification screen.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#purpose_justification_prompt ZeroTrustAccessPolicy#purpose_justification_prompt}
        '''
        result = self._values.get("purpose_justification_prompt")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def purpose_justification_required(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Require users to enter a justification when they log in to the application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#purpose_justification_required ZeroTrustAccessPolicy#purpose_justification_required}
        '''
        result = self._values.get("purpose_justification_required")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def require(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessPolicyRequire"]]]:
        '''Rules evaluated with an AND logical operator.

        To match the policy, a user must meet all of the Require rules.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#require ZeroTrustAccessPolicy#require}
        '''
        result = self._values.get("require")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustAccessPolicyRequire"]]], result)

    @builtins.property
    def session_duration(self) -> typing.Optional[builtins.str]:
        '''The amount of time that tokens issued for the application will be valid.

        Must be in the format ``300ms`` or ``2h45m``. Valid time units are: ns, us (or µs), ms, s, m, h.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#session_duration ZeroTrustAccessPolicy#session_duration}
        '''
        result = self._values.get("session_duration")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExclude",
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
class ZeroTrustAccessPolicyExclude:
    def __init__(
        self,
        *,
        any_valid_service_token: typing.Optional[typing.Union["ZeroTrustAccessPolicyExcludeAnyValidServiceToken", typing.Dict[builtins.str, typing.Any]]] = None,
        auth_context: typing.Optional[typing.Union["ZeroTrustAccessPolicyExcludeAuthContext", typing.Dict[builtins.str, typing.Any]]] = None,
        auth_method: typing.Optional[typing.Union["ZeroTrustAccessPolicyExcludeAuthMethod", typing.Dict[builtins.str, typing.Any]]] = None,
        azure_ad: typing.Optional[typing.Union["ZeroTrustAccessPolicyExcludeAzureAd", typing.Dict[builtins.str, typing.Any]]] = None,
        certificate: typing.Optional[typing.Union["ZeroTrustAccessPolicyExcludeCertificate", typing.Dict[builtins.str, typing.Any]]] = None,
        common_name: typing.Optional[typing.Union["ZeroTrustAccessPolicyExcludeCommonName", typing.Dict[builtins.str, typing.Any]]] = None,
        device_posture: typing.Optional[typing.Union["ZeroTrustAccessPolicyExcludeDevicePosture", typing.Dict[builtins.str, typing.Any]]] = None,
        email: typing.Optional[typing.Union["ZeroTrustAccessPolicyExcludeEmail", typing.Dict[builtins.str, typing.Any]]] = None,
        email_domain: typing.Optional[typing.Union["ZeroTrustAccessPolicyExcludeEmailDomain", typing.Dict[builtins.str, typing.Any]]] = None,
        email_list: typing.Optional[typing.Union["ZeroTrustAccessPolicyExcludeEmailListStruct", typing.Dict[builtins.str, typing.Any]]] = None,
        everyone: typing.Optional[typing.Union["ZeroTrustAccessPolicyExcludeEveryone", typing.Dict[builtins.str, typing.Any]]] = None,
        external_evaluation: typing.Optional[typing.Union["ZeroTrustAccessPolicyExcludeExternalEvaluation", typing.Dict[builtins.str, typing.Any]]] = None,
        geo: typing.Optional[typing.Union["ZeroTrustAccessPolicyExcludeGeo", typing.Dict[builtins.str, typing.Any]]] = None,
        github_organization: typing.Optional[typing.Union["ZeroTrustAccessPolicyExcludeGithubOrganization", typing.Dict[builtins.str, typing.Any]]] = None,
        group: typing.Optional[typing.Union["ZeroTrustAccessPolicyExcludeGroup", typing.Dict[builtins.str, typing.Any]]] = None,
        gsuite: typing.Optional[typing.Union["ZeroTrustAccessPolicyExcludeGsuite", typing.Dict[builtins.str, typing.Any]]] = None,
        ip: typing.Optional[typing.Union["ZeroTrustAccessPolicyExcludeIp", typing.Dict[builtins.str, typing.Any]]] = None,
        ip_list: typing.Optional[typing.Union["ZeroTrustAccessPolicyExcludeIpListStruct", typing.Dict[builtins.str, typing.Any]]] = None,
        linked_app_token: typing.Optional[typing.Union["ZeroTrustAccessPolicyExcludeLinkedAppToken", typing.Dict[builtins.str, typing.Any]]] = None,
        login_method: typing.Optional[typing.Union["ZeroTrustAccessPolicyExcludeLoginMethod", typing.Dict[builtins.str, typing.Any]]] = None,
        oidc: typing.Optional[typing.Union["ZeroTrustAccessPolicyExcludeOidc", typing.Dict[builtins.str, typing.Any]]] = None,
        okta: typing.Optional[typing.Union["ZeroTrustAccessPolicyExcludeOkta", typing.Dict[builtins.str, typing.Any]]] = None,
        saml: typing.Optional[typing.Union["ZeroTrustAccessPolicyExcludeSaml", typing.Dict[builtins.str, typing.Any]]] = None,
        service_token: typing.Optional[typing.Union["ZeroTrustAccessPolicyExcludeServiceToken", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param any_valid_service_token: An empty object which matches on all service tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#any_valid_service_token ZeroTrustAccessPolicy#any_valid_service_token}
        :param auth_context: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#auth_context ZeroTrustAccessPolicy#auth_context}.
        :param auth_method: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#auth_method ZeroTrustAccessPolicy#auth_method}.
        :param azure_ad: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#azure_ad ZeroTrustAccessPolicy#azure_ad}.
        :param certificate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#certificate ZeroTrustAccessPolicy#certificate}.
        :param common_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#common_name ZeroTrustAccessPolicy#common_name}.
        :param device_posture: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#device_posture ZeroTrustAccessPolicy#device_posture}.
        :param email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email ZeroTrustAccessPolicy#email}.
        :param email_domain: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email_domain ZeroTrustAccessPolicy#email_domain}.
        :param email_list: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email_list ZeroTrustAccessPolicy#email_list}.
        :param everyone: An empty object which matches on all users. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#everyone ZeroTrustAccessPolicy#everyone}
        :param external_evaluation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#external_evaluation ZeroTrustAccessPolicy#external_evaluation}.
        :param geo: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#geo ZeroTrustAccessPolicy#geo}.
        :param github_organization: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#github_organization ZeroTrustAccessPolicy#github_organization}.
        :param group: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#group ZeroTrustAccessPolicy#group}.
        :param gsuite: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#gsuite ZeroTrustAccessPolicy#gsuite}.
        :param ip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ip ZeroTrustAccessPolicy#ip}.
        :param ip_list: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ip_list ZeroTrustAccessPolicy#ip_list}.
        :param linked_app_token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#linked_app_token ZeroTrustAccessPolicy#linked_app_token}.
        :param login_method: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#login_method ZeroTrustAccessPolicy#login_method}.
        :param oidc: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#oidc ZeroTrustAccessPolicy#oidc}.
        :param okta: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#okta ZeroTrustAccessPolicy#okta}.
        :param saml: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#saml ZeroTrustAccessPolicy#saml}.
        :param service_token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#service_token ZeroTrustAccessPolicy#service_token}.
        '''
        if isinstance(any_valid_service_token, dict):
            any_valid_service_token = ZeroTrustAccessPolicyExcludeAnyValidServiceToken(**any_valid_service_token)
        if isinstance(auth_context, dict):
            auth_context = ZeroTrustAccessPolicyExcludeAuthContext(**auth_context)
        if isinstance(auth_method, dict):
            auth_method = ZeroTrustAccessPolicyExcludeAuthMethod(**auth_method)
        if isinstance(azure_ad, dict):
            azure_ad = ZeroTrustAccessPolicyExcludeAzureAd(**azure_ad)
        if isinstance(certificate, dict):
            certificate = ZeroTrustAccessPolicyExcludeCertificate(**certificate)
        if isinstance(common_name, dict):
            common_name = ZeroTrustAccessPolicyExcludeCommonName(**common_name)
        if isinstance(device_posture, dict):
            device_posture = ZeroTrustAccessPolicyExcludeDevicePosture(**device_posture)
        if isinstance(email, dict):
            email = ZeroTrustAccessPolicyExcludeEmail(**email)
        if isinstance(email_domain, dict):
            email_domain = ZeroTrustAccessPolicyExcludeEmailDomain(**email_domain)
        if isinstance(email_list, dict):
            email_list = ZeroTrustAccessPolicyExcludeEmailListStruct(**email_list)
        if isinstance(everyone, dict):
            everyone = ZeroTrustAccessPolicyExcludeEveryone(**everyone)
        if isinstance(external_evaluation, dict):
            external_evaluation = ZeroTrustAccessPolicyExcludeExternalEvaluation(**external_evaluation)
        if isinstance(geo, dict):
            geo = ZeroTrustAccessPolicyExcludeGeo(**geo)
        if isinstance(github_organization, dict):
            github_organization = ZeroTrustAccessPolicyExcludeGithubOrganization(**github_organization)
        if isinstance(group, dict):
            group = ZeroTrustAccessPolicyExcludeGroup(**group)
        if isinstance(gsuite, dict):
            gsuite = ZeroTrustAccessPolicyExcludeGsuite(**gsuite)
        if isinstance(ip, dict):
            ip = ZeroTrustAccessPolicyExcludeIp(**ip)
        if isinstance(ip_list, dict):
            ip_list = ZeroTrustAccessPolicyExcludeIpListStruct(**ip_list)
        if isinstance(linked_app_token, dict):
            linked_app_token = ZeroTrustAccessPolicyExcludeLinkedAppToken(**linked_app_token)
        if isinstance(login_method, dict):
            login_method = ZeroTrustAccessPolicyExcludeLoginMethod(**login_method)
        if isinstance(oidc, dict):
            oidc = ZeroTrustAccessPolicyExcludeOidc(**oidc)
        if isinstance(okta, dict):
            okta = ZeroTrustAccessPolicyExcludeOkta(**okta)
        if isinstance(saml, dict):
            saml = ZeroTrustAccessPolicyExcludeSaml(**saml)
        if isinstance(service_token, dict):
            service_token = ZeroTrustAccessPolicyExcludeServiceToken(**service_token)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7508458f688150ef57942b9bdf3e932d66343852d59e86215a2106a376732e4)
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
    ) -> typing.Optional["ZeroTrustAccessPolicyExcludeAnyValidServiceToken"]:
        '''An empty object which matches on all service tokens.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#any_valid_service_token ZeroTrustAccessPolicy#any_valid_service_token}
        '''
        result = self._values.get("any_valid_service_token")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyExcludeAnyValidServiceToken"], result)

    @builtins.property
    def auth_context(
        self,
    ) -> typing.Optional["ZeroTrustAccessPolicyExcludeAuthContext"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#auth_context ZeroTrustAccessPolicy#auth_context}.'''
        result = self._values.get("auth_context")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyExcludeAuthContext"], result)

    @builtins.property
    def auth_method(self) -> typing.Optional["ZeroTrustAccessPolicyExcludeAuthMethod"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#auth_method ZeroTrustAccessPolicy#auth_method}.'''
        result = self._values.get("auth_method")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyExcludeAuthMethod"], result)

    @builtins.property
    def azure_ad(self) -> typing.Optional["ZeroTrustAccessPolicyExcludeAzureAd"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#azure_ad ZeroTrustAccessPolicy#azure_ad}.'''
        result = self._values.get("azure_ad")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyExcludeAzureAd"], result)

    @builtins.property
    def certificate(self) -> typing.Optional["ZeroTrustAccessPolicyExcludeCertificate"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#certificate ZeroTrustAccessPolicy#certificate}.'''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyExcludeCertificate"], result)

    @builtins.property
    def common_name(self) -> typing.Optional["ZeroTrustAccessPolicyExcludeCommonName"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#common_name ZeroTrustAccessPolicy#common_name}.'''
        result = self._values.get("common_name")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyExcludeCommonName"], result)

    @builtins.property
    def device_posture(
        self,
    ) -> typing.Optional["ZeroTrustAccessPolicyExcludeDevicePosture"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#device_posture ZeroTrustAccessPolicy#device_posture}.'''
        result = self._values.get("device_posture")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyExcludeDevicePosture"], result)

    @builtins.property
    def email(self) -> typing.Optional["ZeroTrustAccessPolicyExcludeEmail"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email ZeroTrustAccessPolicy#email}.'''
        result = self._values.get("email")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyExcludeEmail"], result)

    @builtins.property
    def email_domain(
        self,
    ) -> typing.Optional["ZeroTrustAccessPolicyExcludeEmailDomain"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email_domain ZeroTrustAccessPolicy#email_domain}.'''
        result = self._values.get("email_domain")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyExcludeEmailDomain"], result)

    @builtins.property
    def email_list(
        self,
    ) -> typing.Optional["ZeroTrustAccessPolicyExcludeEmailListStruct"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email_list ZeroTrustAccessPolicy#email_list}.'''
        result = self._values.get("email_list")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyExcludeEmailListStruct"], result)

    @builtins.property
    def everyone(self) -> typing.Optional["ZeroTrustAccessPolicyExcludeEveryone"]:
        '''An empty object which matches on all users.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#everyone ZeroTrustAccessPolicy#everyone}
        '''
        result = self._values.get("everyone")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyExcludeEveryone"], result)

    @builtins.property
    def external_evaluation(
        self,
    ) -> typing.Optional["ZeroTrustAccessPolicyExcludeExternalEvaluation"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#external_evaluation ZeroTrustAccessPolicy#external_evaluation}.'''
        result = self._values.get("external_evaluation")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyExcludeExternalEvaluation"], result)

    @builtins.property
    def geo(self) -> typing.Optional["ZeroTrustAccessPolicyExcludeGeo"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#geo ZeroTrustAccessPolicy#geo}.'''
        result = self._values.get("geo")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyExcludeGeo"], result)

    @builtins.property
    def github_organization(
        self,
    ) -> typing.Optional["ZeroTrustAccessPolicyExcludeGithubOrganization"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#github_organization ZeroTrustAccessPolicy#github_organization}.'''
        result = self._values.get("github_organization")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyExcludeGithubOrganization"], result)

    @builtins.property
    def group(self) -> typing.Optional["ZeroTrustAccessPolicyExcludeGroup"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#group ZeroTrustAccessPolicy#group}.'''
        result = self._values.get("group")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyExcludeGroup"], result)

    @builtins.property
    def gsuite(self) -> typing.Optional["ZeroTrustAccessPolicyExcludeGsuite"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#gsuite ZeroTrustAccessPolicy#gsuite}.'''
        result = self._values.get("gsuite")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyExcludeGsuite"], result)

    @builtins.property
    def ip(self) -> typing.Optional["ZeroTrustAccessPolicyExcludeIp"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ip ZeroTrustAccessPolicy#ip}.'''
        result = self._values.get("ip")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyExcludeIp"], result)

    @builtins.property
    def ip_list(self) -> typing.Optional["ZeroTrustAccessPolicyExcludeIpListStruct"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ip_list ZeroTrustAccessPolicy#ip_list}.'''
        result = self._values.get("ip_list")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyExcludeIpListStruct"], result)

    @builtins.property
    def linked_app_token(
        self,
    ) -> typing.Optional["ZeroTrustAccessPolicyExcludeLinkedAppToken"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#linked_app_token ZeroTrustAccessPolicy#linked_app_token}.'''
        result = self._values.get("linked_app_token")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyExcludeLinkedAppToken"], result)

    @builtins.property
    def login_method(
        self,
    ) -> typing.Optional["ZeroTrustAccessPolicyExcludeLoginMethod"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#login_method ZeroTrustAccessPolicy#login_method}.'''
        result = self._values.get("login_method")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyExcludeLoginMethod"], result)

    @builtins.property
    def oidc(self) -> typing.Optional["ZeroTrustAccessPolicyExcludeOidc"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#oidc ZeroTrustAccessPolicy#oidc}.'''
        result = self._values.get("oidc")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyExcludeOidc"], result)

    @builtins.property
    def okta(self) -> typing.Optional["ZeroTrustAccessPolicyExcludeOkta"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#okta ZeroTrustAccessPolicy#okta}.'''
        result = self._values.get("okta")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyExcludeOkta"], result)

    @builtins.property
    def saml(self) -> typing.Optional["ZeroTrustAccessPolicyExcludeSaml"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#saml ZeroTrustAccessPolicy#saml}.'''
        result = self._values.get("saml")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyExcludeSaml"], result)

    @builtins.property
    def service_token(
        self,
    ) -> typing.Optional["ZeroTrustAccessPolicyExcludeServiceToken"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#service_token ZeroTrustAccessPolicy#service_token}.'''
        result = self._values.get("service_token")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyExcludeServiceToken"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyExclude(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeAnyValidServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class ZeroTrustAccessPolicyExcludeAnyValidServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyExcludeAnyValidServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyExcludeAnyValidServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeAnyValidServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8cb34d6a70c6226b68c12582f6b83e26f9b899edc7e848716e839f2d4e15cc39)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeAnyValidServiceToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeAnyValidServiceToken]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeAnyValidServiceToken]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b948d6039f18a9a386b5d7c895a1e9e9e0339b2af9a362ae0423bbeded638c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeAuthContext",
    jsii_struct_bases=[],
    name_mapping={
        "ac_id": "acId",
        "id": "id",
        "identity_provider_id": "identityProviderId",
    },
)
class ZeroTrustAccessPolicyExcludeAuthContext:
    def __init__(
        self,
        *,
        ac_id: builtins.str,
        id: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param ac_id: The ACID of an Authentication context. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ac_id ZeroTrustAccessPolicy#ac_id}
        :param id: The ID of an Authentication context. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider_id: The ID of your Azure identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0dacad059df343a10cda69136eb22af18fd8bbfffe0b24c1e65092345a490fc4)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ac_id ZeroTrustAccessPolicy#ac_id}
        '''
        result = self._values.get("ac_id")
        assert result is not None, "Required property 'ac_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of an Authentication context.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your Azure identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyExcludeAuthContext(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyExcludeAuthContextOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeAuthContextOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ebcdeac36c8a8c9812c4dfa87190c88c82b11d1731e47fd78982b2f066f5e46f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f0f027f9c8cbbccebc37207f8ee0af4ffc0624a5599948dbc42d5b19791208ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "acId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__028fa0652cc0df99f8c893b6a246d1b79f3fa72f248b849c6e6c76f2bfc5aba4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__622ff023b5e3098ca3b6b4ef69cd2eca0f1d13a82ec338a40c84bafdb1d6c0c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeAuthContext]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeAuthContext]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeAuthContext]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__726b84022b0a708d56e19bb04928f9ff7fbe900dbec6ce41dbb9de0992642d03)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeAuthMethod",
    jsii_struct_bases=[],
    name_mapping={"auth_method": "authMethod"},
)
class ZeroTrustAccessPolicyExcludeAuthMethod:
    def __init__(self, *, auth_method: builtins.str) -> None:
        '''
        :param auth_method: The type of authentication method https://datatracker.ietf.org/doc/html/rfc8176#section-2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#auth_method ZeroTrustAccessPolicy#auth_method}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56e3ff2aa11ec337a255a85e00420ff43733d9a9a26d4c9b6e4f690e4c9abf32)
            check_type(argname="argument auth_method", value=auth_method, expected_type=type_hints["auth_method"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "auth_method": auth_method,
        }

    @builtins.property
    def auth_method(self) -> builtins.str:
        '''The type of authentication method https://datatracker.ietf.org/doc/html/rfc8176#section-2.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#auth_method ZeroTrustAccessPolicy#auth_method}
        '''
        result = self._values.get("auth_method")
        assert result is not None, "Required property 'auth_method' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyExcludeAuthMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyExcludeAuthMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeAuthMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5f426211310c49a3773a61c69af2d5fe33ac1ce19d30fe64b6f4f34f3c178d03)
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
            type_hints = typing.get_type_hints(_typecheckingstub__173e503b2e205b076b61a77efde67cf8ece0835a84adf84eb5055bc283adcb75)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authMethod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeAuthMethod]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeAuthMethod]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeAuthMethod]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e294b103aca90cfa62a02e1970f60689d4693c58f281d4d3cbc72c5e688e180)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeAzureAd",
    jsii_struct_bases=[],
    name_mapping={"id": "id", "identity_provider_id": "identityProviderId"},
)
class ZeroTrustAccessPolicyExcludeAzureAd:
    def __init__(self, *, id: builtins.str, identity_provider_id: builtins.str) -> None:
        '''
        :param id: The ID of an Azure group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider_id: The ID of your Azure identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9320fea2d0fa1c6697fcc1ddeaee4856c5398d75f0665cef303e8381512354f)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
            "identity_provider_id": identity_provider_id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of an Azure group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your Azure identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyExcludeAzureAd(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyExcludeAzureAdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeAzureAdOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__19bf89c73f3df57fe2480f163705d19ae4e1d965ffd50b9c9cd815b07b081d8a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c49f999c452938c35db7b23e7b4b4b02a189b662b304af68ee75111adb42781a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7a42dc45bed66a41429119f0854dd83d03543500a562cc18af41a29320806d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeAzureAd]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeAzureAd]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeAzureAd]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0da7d591e8917f96f2115162a410c968f5150d294be5815675afc39055e2aee3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeCertificate",
    jsii_struct_bases=[],
    name_mapping={},
)
class ZeroTrustAccessPolicyExcludeCertificate:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyExcludeCertificate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyExcludeCertificateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeCertificateOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d88671d34532f3b4cd190f76af7489bff274096cac9afa304b561b45fc464519)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeCertificate]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeCertificate]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeCertificate]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16734a5936189cbfb6618705986417ed2b438255680d6570b08dcb733f17a522)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeCommonName",
    jsii_struct_bases=[],
    name_mapping={"common_name": "commonName"},
)
class ZeroTrustAccessPolicyExcludeCommonName:
    def __init__(self, *, common_name: builtins.str) -> None:
        '''
        :param common_name: The common name to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#common_name ZeroTrustAccessPolicy#common_name}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee37b824162e2238eab6230521f385cdf4c6797ab0da12cf8bd4432589421dc9)
            check_type(argname="argument common_name", value=common_name, expected_type=type_hints["common_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "common_name": common_name,
        }

    @builtins.property
    def common_name(self) -> builtins.str:
        '''The common name to match.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#common_name ZeroTrustAccessPolicy#common_name}
        '''
        result = self._values.get("common_name")
        assert result is not None, "Required property 'common_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyExcludeCommonName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyExcludeCommonNameOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeCommonNameOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4738c6c99a2333c45e2251526de934be1962aec9f1682efdd17609e6a6531953)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a0cb9692cd3f75ad1b1e64e561d549e7e41e81150b06c57c383c476e9543f511)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "commonName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeCommonName]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeCommonName]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeCommonName]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cd1fce646d42f26da177378c209b61ac7340daf06c77829bc0e8b82a9bdb191)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeDevicePosture",
    jsii_struct_bases=[],
    name_mapping={"integration_uid": "integrationUid"},
)
class ZeroTrustAccessPolicyExcludeDevicePosture:
    def __init__(self, *, integration_uid: builtins.str) -> None:
        '''
        :param integration_uid: The ID of a device posture integration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#integration_uid ZeroTrustAccessPolicy#integration_uid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc2985e06108cb9bcbe238824ef4744fe3e925dc50a8985663a090496b4dd4b1)
            check_type(argname="argument integration_uid", value=integration_uid, expected_type=type_hints["integration_uid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "integration_uid": integration_uid,
        }

    @builtins.property
    def integration_uid(self) -> builtins.str:
        '''The ID of a device posture integration.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#integration_uid ZeroTrustAccessPolicy#integration_uid}
        '''
        result = self._values.get("integration_uid")
        assert result is not None, "Required property 'integration_uid' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyExcludeDevicePosture(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyExcludeDevicePostureOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeDevicePostureOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ad58b58dbc74ba7371cf63982cff349f73f9fdb07f3a092be850c1765135665e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0e96cf19320d20c0a6e724243cd55475d95f75bf46c4349930a871df4c8c72b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "integrationUid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeDevicePosture]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeDevicePosture]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeDevicePosture]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddb036770ba06c19719ca0074b6b8ab49d6f0c1d8a6728add5a64e6d55f0b400)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeEmail",
    jsii_struct_bases=[],
    name_mapping={"email": "email"},
)
class ZeroTrustAccessPolicyExcludeEmail:
    def __init__(self, *, email: builtins.str) -> None:
        '''
        :param email: The email of the user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email ZeroTrustAccessPolicy#email}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a574f86f0e601ec8e012a1efe8dafa72664ee20f2d8c0c5c8a9badedf03b27b5)
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "email": email,
        }

    @builtins.property
    def email(self) -> builtins.str:
        '''The email of the user.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email ZeroTrustAccessPolicy#email}
        '''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyExcludeEmail(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeEmailDomain",
    jsii_struct_bases=[],
    name_mapping={"domain": "domain"},
)
class ZeroTrustAccessPolicyExcludeEmailDomain:
    def __init__(self, *, domain: builtins.str) -> None:
        '''
        :param domain: The email domain to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#domain ZeroTrustAccessPolicy#domain}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38b1e29d8836291b31351d8c7ba7f40b7d36534d7cea3c9421cbf66b368ef9b2)
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain": domain,
        }

    @builtins.property
    def domain(self) -> builtins.str:
        '''The email domain to match.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#domain ZeroTrustAccessPolicy#domain}
        '''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyExcludeEmailDomain(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyExcludeEmailDomainOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeEmailDomainOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__00f819cc2a0832bdf8ebb6b09d95f865873e8351d2f1672f40e7e4006bf823eb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__eaf5e40263345a5ed34f20b55df6543acb62a78c9c758f9ccfccb79a8a3eb348)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "domain", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeEmailDomain]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeEmailDomain]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeEmailDomain]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2946389addd90eb25bf5a0f47ede1e88f496cf80592daebdb95dd149b123edc0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeEmailListStruct",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class ZeroTrustAccessPolicyExcludeEmailListStruct:
    def __init__(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created email list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf14ab1f7bee9439e7428a1987e0fe20d607878e406ad0328de4630ca1aa50e4)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of a previously created email list.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id}

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
        return "ZeroTrustAccessPolicyExcludeEmailListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyExcludeEmailListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeEmailListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__eb03908e37c83274ccc08f09d43879d5d4f042c9b922818f41d6b567a9cba09e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3cd8f7d400d6424c8dd1dbdfc10840d43f2665453afc552628ea304c020b63a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeEmailListStruct]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeEmailListStruct]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeEmailListStruct]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33772317cf2d51bd85a2abe8ed95d99d2b9745cfee933db4a0fedefa4c823722)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustAccessPolicyExcludeEmailOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeEmailOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5879e78a55cee273b470d34044b2befcf263896752f48623b72388673c00d853)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e8b57935203d7a43cab5ec1e2564a902bb08f0e2cd862a48843f66ecacda120e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "email", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeEmail]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeEmail]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeEmail]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ca1c3448b9bd8158516156c2270786028415739b00f370f1e2f01b5a7ce4545)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeEveryone",
    jsii_struct_bases=[],
    name_mapping={},
)
class ZeroTrustAccessPolicyExcludeEveryone:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyExcludeEveryone(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyExcludeEveryoneOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeEveryoneOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__975fa9f24e0737ee4e7e7edc9e00d86a28fbe89a4a36f14578b44bb6e1d244b5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeEveryone]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeEveryone]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeEveryone]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2fa4293c975064196b3b68ac073e4272ba99ef1619a74f4811a559a921bf242)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeExternalEvaluation",
    jsii_struct_bases=[],
    name_mapping={"evaluate_url": "evaluateUrl", "keys_url": "keysUrl"},
)
class ZeroTrustAccessPolicyExcludeExternalEvaluation:
    def __init__(self, *, evaluate_url: builtins.str, keys_url: builtins.str) -> None:
        '''
        :param evaluate_url: The API endpoint containing your business logic. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#evaluate_url ZeroTrustAccessPolicy#evaluate_url}
        :param keys_url: The API endpoint containing the key that Access uses to verify that the response came from your API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#keys_url ZeroTrustAccessPolicy#keys_url}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c0776a92d3a7c1dbf524e002e4b6086a83724b86a998e2c74f783da4e74a0f5)
            check_type(argname="argument evaluate_url", value=evaluate_url, expected_type=type_hints["evaluate_url"])
            check_type(argname="argument keys_url", value=keys_url, expected_type=type_hints["keys_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "evaluate_url": evaluate_url,
            "keys_url": keys_url,
        }

    @builtins.property
    def evaluate_url(self) -> builtins.str:
        '''The API endpoint containing your business logic.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#evaluate_url ZeroTrustAccessPolicy#evaluate_url}
        '''
        result = self._values.get("evaluate_url")
        assert result is not None, "Required property 'evaluate_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def keys_url(self) -> builtins.str:
        '''The API endpoint containing the key that Access uses to verify that the response came from your API.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#keys_url ZeroTrustAccessPolicy#keys_url}
        '''
        result = self._values.get("keys_url")
        assert result is not None, "Required property 'keys_url' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyExcludeExternalEvaluation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyExcludeExternalEvaluationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeExternalEvaluationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1873a072afe0860d06990a8d94a00fe835d92d548c26ceb357fbf7cafbeec1bf)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4ce5057eb101b172983146768578f83e01804f6803214e1ccf10a1f177814114)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "evaluateUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keysUrl")
    def keys_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keysUrl"))

    @keys_url.setter
    def keys_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7885370a8efd2f2cc2136d26ef98fd4d499b5e9df948fe11a6b0379171f2e5a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keysUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeExternalEvaluation]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeExternalEvaluation]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeExternalEvaluation]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09579fbe45d9f0dd978351451135fe98a55b27ba8448d6346cf5022b84fdea5d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeGeo",
    jsii_struct_bases=[],
    name_mapping={"country_code": "countryCode"},
)
class ZeroTrustAccessPolicyExcludeGeo:
    def __init__(self, *, country_code: builtins.str) -> None:
        '''
        :param country_code: The country code that should be matched. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#country_code ZeroTrustAccessPolicy#country_code}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9eb1e64668fd978732e947bb80254dfc18ce7af234111d3327c0f25128dc87b6)
            check_type(argname="argument country_code", value=country_code, expected_type=type_hints["country_code"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "country_code": country_code,
        }

    @builtins.property
    def country_code(self) -> builtins.str:
        '''The country code that should be matched.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#country_code ZeroTrustAccessPolicy#country_code}
        '''
        result = self._values.get("country_code")
        assert result is not None, "Required property 'country_code' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyExcludeGeo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyExcludeGeoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeGeoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b0029cfcb2997a8ad304bed9e77acc41e95ac9099b338b737663c0f3a96a09d4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fa87d229a575115fa88238a22adfba2ce4f0745ebdbd0ed849ae913d2b52409a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "countryCode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeGeo]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeGeo]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeGeo]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4aadfc71855fe159e72e59fa2f5188ccd38ac5a23ae5e7a76c29ca06cbbcc5a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeGithubOrganization",
    jsii_struct_bases=[],
    name_mapping={
        "identity_provider_id": "identityProviderId",
        "name": "name",
        "team": "team",
    },
)
class ZeroTrustAccessPolicyExcludeGithubOrganization:
    def __init__(
        self,
        *,
        identity_provider_id: builtins.str,
        name: builtins.str,
        team: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param identity_provider_id: The ID of your Github identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        :param name: The name of the organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#name ZeroTrustAccessPolicy#name}
        :param team: The name of the team. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#team ZeroTrustAccessPolicy#team}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06e528aa23d87f4c8ebd5aa22d57c5f250d5ea72e6c5dfed24be71e4023f4667)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the organization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#name ZeroTrustAccessPolicy#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def team(self) -> typing.Optional[builtins.str]:
        '''The name of the team.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#team ZeroTrustAccessPolicy#team}
        '''
        result = self._values.get("team")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyExcludeGithubOrganization(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyExcludeGithubOrganizationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeGithubOrganizationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ac3eb3c015c0c2e49e4bbe6f8ab0a6d48cf2fcbcfd5e6be741564c3cff6aef79)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ab0fb55852d2d18694d4a35db4b097116d1b9ef46d53632dc4b382e254fe0829)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c79ec67cba0ae9ce4770946a13431f6409af0133b6c3cb9b91c325541ccbc3bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="team")
    def team(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "team"))

    @team.setter
    def team(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0498c7c4e4b4b5d0fee036b0c980f7aa91b08d44edd840e4348f5ba55507f470)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "team", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeGithubOrganization]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeGithubOrganization]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeGithubOrganization]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b608e702ac5ad7c630e8cf5a3baa29028c261d451c11edaba160601b652f232)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeGroup",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class ZeroTrustAccessPolicyExcludeGroup:
    def __init__(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created Access group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ad1b65c7a33817a57383730dd0ddfec3cb8097822f4fb2b0e1a8480c08e5f82)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of a previously created Access group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id}

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
        return "ZeroTrustAccessPolicyExcludeGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyExcludeGroupOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeGroupOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__15418770441dc3aab6b572358a8ded9e21ca2e2cd7522f7ece9b7b9b8c93fb2c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__860ca9233196caa3524704fa736f3bcadd46f257aa2c360ca8ba95555489ff88)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeGroup]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeGroup]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeGroup]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd062bdad12346e212437c353f17f3eac93202c1180637d8e1e64cd3ccd2b32b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeGsuite",
    jsii_struct_bases=[],
    name_mapping={"email": "email", "identity_provider_id": "identityProviderId"},
)
class ZeroTrustAccessPolicyExcludeGsuite:
    def __init__(
        self,
        *,
        email: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param email: The email of the Google Workspace group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email ZeroTrustAccessPolicy#email}
        :param identity_provider_id: The ID of your Google Workspace identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae88135e7743a6d5cc430ff8df3e789449c27a9af7b7e2a03780b59ff4d5f3e1)
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "email": email,
            "identity_provider_id": identity_provider_id,
        }

    @builtins.property
    def email(self) -> builtins.str:
        '''The email of the Google Workspace group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email ZeroTrustAccessPolicy#email}
        '''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your Google Workspace identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyExcludeGsuite(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyExcludeGsuiteOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeGsuiteOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3fd333799c47b9dce616929ee96f8998a4336103b0d1a45a96a02adfc61edecd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e57df1cecda0357c48012da703040230da0fd769521e8a326879664a36177588)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "email", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f36004d6d5bf4295571a65c0cd25bd9153f0aff89e42fedf77db23479226e93)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeGsuite]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeGsuite]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeGsuite]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d849a0df75d20d8c280b63bd813688b106a179241a21e575ac95d0121bef9758)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeIp",
    jsii_struct_bases=[],
    name_mapping={"ip": "ip"},
)
class ZeroTrustAccessPolicyExcludeIp:
    def __init__(self, *, ip: builtins.str) -> None:
        '''
        :param ip: An IPv4 or IPv6 CIDR block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ip ZeroTrustAccessPolicy#ip}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cdf9967615da5efec5d12165b3fa23a660ab9bbff60bb4b1ab705cd31d8b21c6)
            check_type(argname="argument ip", value=ip, expected_type=type_hints["ip"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "ip": ip,
        }

    @builtins.property
    def ip(self) -> builtins.str:
        '''An IPv4 or IPv6 CIDR block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ip ZeroTrustAccessPolicy#ip}
        '''
        result = self._values.get("ip")
        assert result is not None, "Required property 'ip' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyExcludeIp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeIpListStruct",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class ZeroTrustAccessPolicyExcludeIpListStruct:
    def __init__(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created IP list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a0b93e3ffbbeceb13355b44b0e821047e57cbe015dd51be43aa2cd4b7ba3295)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of a previously created IP list.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id}

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
        return "ZeroTrustAccessPolicyExcludeIpListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyExcludeIpListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeIpListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a85b9707ef5b31015398785c069af8e73603f5413592196c6a295b40e32eab95)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a5614d7c60b0115ffa9f81075341b89d91611ba5c5f8685daf62f26d97098c6b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeIpListStruct]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeIpListStruct]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeIpListStruct]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d85365ab40376e2720c16ef16a434550e5ebfa70ff50809a557962dc47cf4ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustAccessPolicyExcludeIpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeIpOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__05acbb1658848675ca93d1474f74e470e14e4239c08fd64187d3e5f11db14b82)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4dd1877f4693402991ef9fc98c6f88e0ef2fb9eb3530d571c88bc3fa1b80a43c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ip", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeIp]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeIp]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeIp]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e4f6b2c602f334f2362726677797c489791308ecb328c11972ecfe7d6faf65a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeLinkedAppToken",
    jsii_struct_bases=[],
    name_mapping={"app_uid": "appUid"},
)
class ZeroTrustAccessPolicyExcludeLinkedAppToken:
    def __init__(self, *, app_uid: builtins.str) -> None:
        '''
        :param app_uid: The ID of an Access OIDC SaaS application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#app_uid ZeroTrustAccessPolicy#app_uid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61993aac9bc58675fc6713527b38583284b4374ce7f551e2f493cef7225678c7)
            check_type(argname="argument app_uid", value=app_uid, expected_type=type_hints["app_uid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "app_uid": app_uid,
        }

    @builtins.property
    def app_uid(self) -> builtins.str:
        '''The ID of an Access OIDC SaaS application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#app_uid ZeroTrustAccessPolicy#app_uid}
        '''
        result = self._values.get("app_uid")
        assert result is not None, "Required property 'app_uid' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyExcludeLinkedAppToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyExcludeLinkedAppTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeLinkedAppTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__be19960dd02299957836d6042f997444c94877c29c06951584283eaed5f23150)
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
            type_hints = typing.get_type_hints(_typecheckingstub__295e02c096e4bb6d28b2fd9b09953924d440755fd28bb1a3e7882fa64d73b35f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "appUid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeLinkedAppToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeLinkedAppToken]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeLinkedAppToken]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82673c7add004666c8fa42fb0f66f50dd4677050545a86bec793412155697baf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustAccessPolicyExcludeList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1c949b5315ea902e02ed42f7388761c09bccf29fc6a701595ba837c86fc727e4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ZeroTrustAccessPolicyExcludeOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73cc7f174bc19ba7b5b1f1e3d4e667f8b7c6733e2b4170ce99071f005eae4a5e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ZeroTrustAccessPolicyExcludeOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d146552daf613c26093e93d326d5ca4a23e70e5d101daefa7afff984a62cfd6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6fd8dff35a8d7824117610f18ae69615bde67725a97ca47b2e25e978e9a5e1b3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__eed49251d5c1ba8dc124f17cfd8d235d28fc020149295255b030de2c25940aec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessPolicyExclude]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessPolicyExclude]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessPolicyExclude]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20d51cdc6cd78c1159638b332825e6a87caca9facad3353f735d9d934a316c76)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeLoginMethod",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class ZeroTrustAccessPolicyExcludeLoginMethod:
    def __init__(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of an identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5835fb3e9669cf4b70c66855f7952dd56edf363b1b72615c76952bf5c4b82fd1)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of an identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id}

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
        return "ZeroTrustAccessPolicyExcludeLoginMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyExcludeLoginMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeLoginMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9b3b4ebf2eb931392c7e038897e9fb45da0afd1261152a4901432dfd3068d677)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a9a81dd30fcac8beccf25945923f7c5170a24fdcec0d8b26e54902781dd4a6a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeLoginMethod]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeLoginMethod]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeLoginMethod]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b135cd3f564560c8e3928bbd261e81adc099df7df1a1e1de1240608c07aca46c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeOidc",
    jsii_struct_bases=[],
    name_mapping={
        "claim_name": "claimName",
        "claim_value": "claimValue",
        "identity_provider_id": "identityProviderId",
    },
)
class ZeroTrustAccessPolicyExcludeOidc:
    def __init__(
        self,
        *,
        claim_name: builtins.str,
        claim_value: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param claim_name: The name of the OIDC claim. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#claim_name ZeroTrustAccessPolicy#claim_name}
        :param claim_value: The OIDC claim value to look for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#claim_value ZeroTrustAccessPolicy#claim_value}
        :param identity_provider_id: The ID of your OIDC identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cdb26f6763584c3acdc388dbfa712e99f8a47db4f04ce5341f0a246af6e3329)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#claim_name ZeroTrustAccessPolicy#claim_name}
        '''
        result = self._values.get("claim_name")
        assert result is not None, "Required property 'claim_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def claim_value(self) -> builtins.str:
        '''The OIDC claim value to look for.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#claim_value ZeroTrustAccessPolicy#claim_value}
        '''
        result = self._values.get("claim_value")
        assert result is not None, "Required property 'claim_value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your OIDC identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyExcludeOidc(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyExcludeOidcOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeOidcOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6645fa80bfe767fc22742d8e64fdd385321b4e37c7932b8b8d93734a6d02a530)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ba351b029a9ca5a6ee95dfdca5699613abcc71ce98b66a22c2f7f8118584d54e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "claimName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="claimValue")
    def claim_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "claimValue"))

    @claim_value.setter
    def claim_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4942c754554959c1ae9e643b9031e373f1015394c8ef53a382ee80e03755002)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "claimValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dabbfe1766a482c13c340dc2535650d67f3be7ceb11f312acedee221c20b054c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeOidc]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeOidc]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeOidc]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__770bf964315dade2ed36ff8d7c122d6fe425bf117572cc119c6654a6a05f1244)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeOkta",
    jsii_struct_bases=[],
    name_mapping={"identity_provider_id": "identityProviderId", "name": "name"},
)
class ZeroTrustAccessPolicyExcludeOkta:
    def __init__(
        self,
        *,
        identity_provider_id: builtins.str,
        name: builtins.str,
    ) -> None:
        '''
        :param identity_provider_id: The ID of your Okta identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        :param name: The name of the Okta group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#name ZeroTrustAccessPolicy#name}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07896720c8fa6082159a98cb5b8d54e7dca4aed7a8dde4c6b4afa3f7d15d03e1)
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "identity_provider_id": identity_provider_id,
            "name": name,
        }

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your Okta identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the Okta group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#name ZeroTrustAccessPolicy#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyExcludeOkta(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyExcludeOktaOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeOktaOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0c854664e8a1d2e009a4ae565f1da4a61c9d1bce15eae8aeda08f3a89a0295fd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f8e789429d70edd5d742d268bcda49c4613565d121a3a69ebd908342f2714e35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8dd3268aa560da2f66bda79e8a2bcc151f6d8a821d7063bd83638f24ad46282c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeOkta]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeOkta]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeOkta]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c94bdb250488478d1ce69cabc4cf8c9d53e4fabca2d68bdcb734f2360871b5d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustAccessPolicyExcludeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4148a0041ccd848539f9e0c787f79bfb5904adab391cf82d680f8c3540189522)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putAnyValidServiceToken")
    def put_any_valid_service_token(self) -> None:
        value = ZeroTrustAccessPolicyExcludeAnyValidServiceToken()

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
        :param ac_id: The ACID of an Authentication context. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ac_id ZeroTrustAccessPolicy#ac_id}
        :param id: The ID of an Authentication context. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider_id: The ID of your Azure identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        value = ZeroTrustAccessPolicyExcludeAuthContext(
            ac_id=ac_id, id=id, identity_provider_id=identity_provider_id
        )

        return typing.cast(None, jsii.invoke(self, "putAuthContext", [value]))

    @jsii.member(jsii_name="putAuthMethod")
    def put_auth_method(self, *, auth_method: builtins.str) -> None:
        '''
        :param auth_method: The type of authentication method https://datatracker.ietf.org/doc/html/rfc8176#section-2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#auth_method ZeroTrustAccessPolicy#auth_method}
        '''
        value = ZeroTrustAccessPolicyExcludeAuthMethod(auth_method=auth_method)

        return typing.cast(None, jsii.invoke(self, "putAuthMethod", [value]))

    @jsii.member(jsii_name="putAzureAd")
    def put_azure_ad(
        self,
        *,
        id: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param id: The ID of an Azure group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider_id: The ID of your Azure identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        value = ZeroTrustAccessPolicyExcludeAzureAd(
            id=id, identity_provider_id=identity_provider_id
        )

        return typing.cast(None, jsii.invoke(self, "putAzureAd", [value]))

    @jsii.member(jsii_name="putCertificate")
    def put_certificate(self) -> None:
        value = ZeroTrustAccessPolicyExcludeCertificate()

        return typing.cast(None, jsii.invoke(self, "putCertificate", [value]))

    @jsii.member(jsii_name="putCommonName")
    def put_common_name(self, *, common_name: builtins.str) -> None:
        '''
        :param common_name: The common name to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#common_name ZeroTrustAccessPolicy#common_name}
        '''
        value = ZeroTrustAccessPolicyExcludeCommonName(common_name=common_name)

        return typing.cast(None, jsii.invoke(self, "putCommonName", [value]))

    @jsii.member(jsii_name="putDevicePosture")
    def put_device_posture(self, *, integration_uid: builtins.str) -> None:
        '''
        :param integration_uid: The ID of a device posture integration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#integration_uid ZeroTrustAccessPolicy#integration_uid}
        '''
        value = ZeroTrustAccessPolicyExcludeDevicePosture(
            integration_uid=integration_uid
        )

        return typing.cast(None, jsii.invoke(self, "putDevicePosture", [value]))

    @jsii.member(jsii_name="putEmail")
    def put_email(self, *, email: builtins.str) -> None:
        '''
        :param email: The email of the user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email ZeroTrustAccessPolicy#email}
        '''
        value = ZeroTrustAccessPolicyExcludeEmail(email=email)

        return typing.cast(None, jsii.invoke(self, "putEmail", [value]))

    @jsii.member(jsii_name="putEmailDomain")
    def put_email_domain(self, *, domain: builtins.str) -> None:
        '''
        :param domain: The email domain to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#domain ZeroTrustAccessPolicy#domain}
        '''
        value = ZeroTrustAccessPolicyExcludeEmailDomain(domain=domain)

        return typing.cast(None, jsii.invoke(self, "putEmailDomain", [value]))

    @jsii.member(jsii_name="putEmailList")
    def put_email_list(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created email list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        value = ZeroTrustAccessPolicyExcludeEmailListStruct(id=id)

        return typing.cast(None, jsii.invoke(self, "putEmailList", [value]))

    @jsii.member(jsii_name="putEveryone")
    def put_everyone(self) -> None:
        value = ZeroTrustAccessPolicyExcludeEveryone()

        return typing.cast(None, jsii.invoke(self, "putEveryone", [value]))

    @jsii.member(jsii_name="putExternalEvaluation")
    def put_external_evaluation(
        self,
        *,
        evaluate_url: builtins.str,
        keys_url: builtins.str,
    ) -> None:
        '''
        :param evaluate_url: The API endpoint containing your business logic. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#evaluate_url ZeroTrustAccessPolicy#evaluate_url}
        :param keys_url: The API endpoint containing the key that Access uses to verify that the response came from your API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#keys_url ZeroTrustAccessPolicy#keys_url}
        '''
        value = ZeroTrustAccessPolicyExcludeExternalEvaluation(
            evaluate_url=evaluate_url, keys_url=keys_url
        )

        return typing.cast(None, jsii.invoke(self, "putExternalEvaluation", [value]))

    @jsii.member(jsii_name="putGeo")
    def put_geo(self, *, country_code: builtins.str) -> None:
        '''
        :param country_code: The country code that should be matched. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#country_code ZeroTrustAccessPolicy#country_code}
        '''
        value = ZeroTrustAccessPolicyExcludeGeo(country_code=country_code)

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
        :param identity_provider_id: The ID of your Github identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        :param name: The name of the organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#name ZeroTrustAccessPolicy#name}
        :param team: The name of the team. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#team ZeroTrustAccessPolicy#team}
        '''
        value = ZeroTrustAccessPolicyExcludeGithubOrganization(
            identity_provider_id=identity_provider_id, name=name, team=team
        )

        return typing.cast(None, jsii.invoke(self, "putGithubOrganization", [value]))

    @jsii.member(jsii_name="putGroup")
    def put_group(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created Access group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        value = ZeroTrustAccessPolicyExcludeGroup(id=id)

        return typing.cast(None, jsii.invoke(self, "putGroup", [value]))

    @jsii.member(jsii_name="putGsuite")
    def put_gsuite(
        self,
        *,
        email: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param email: The email of the Google Workspace group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email ZeroTrustAccessPolicy#email}
        :param identity_provider_id: The ID of your Google Workspace identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        value = ZeroTrustAccessPolicyExcludeGsuite(
            email=email, identity_provider_id=identity_provider_id
        )

        return typing.cast(None, jsii.invoke(self, "putGsuite", [value]))

    @jsii.member(jsii_name="putIp")
    def put_ip(self, *, ip: builtins.str) -> None:
        '''
        :param ip: An IPv4 or IPv6 CIDR block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ip ZeroTrustAccessPolicy#ip}
        '''
        value = ZeroTrustAccessPolicyExcludeIp(ip=ip)

        return typing.cast(None, jsii.invoke(self, "putIp", [value]))

    @jsii.member(jsii_name="putIpList")
    def put_ip_list(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created IP list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        value = ZeroTrustAccessPolicyExcludeIpListStruct(id=id)

        return typing.cast(None, jsii.invoke(self, "putIpList", [value]))

    @jsii.member(jsii_name="putLinkedAppToken")
    def put_linked_app_token(self, *, app_uid: builtins.str) -> None:
        '''
        :param app_uid: The ID of an Access OIDC SaaS application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#app_uid ZeroTrustAccessPolicy#app_uid}
        '''
        value = ZeroTrustAccessPolicyExcludeLinkedAppToken(app_uid=app_uid)

        return typing.cast(None, jsii.invoke(self, "putLinkedAppToken", [value]))

    @jsii.member(jsii_name="putLoginMethod")
    def put_login_method(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of an identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        value = ZeroTrustAccessPolicyExcludeLoginMethod(id=id)

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
        :param claim_name: The name of the OIDC claim. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#claim_name ZeroTrustAccessPolicy#claim_name}
        :param claim_value: The OIDC claim value to look for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#claim_value ZeroTrustAccessPolicy#claim_value}
        :param identity_provider_id: The ID of your OIDC identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        value = ZeroTrustAccessPolicyExcludeOidc(
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
        :param identity_provider_id: The ID of your Okta identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        :param name: The name of the Okta group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#name ZeroTrustAccessPolicy#name}
        '''
        value = ZeroTrustAccessPolicyExcludeOkta(
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
        :param attribute_name: The name of the SAML attribute. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#attribute_name ZeroTrustAccessPolicy#attribute_name}
        :param attribute_value: The SAML attribute value to look for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#attribute_value ZeroTrustAccessPolicy#attribute_value}
        :param identity_provider_id: The ID of your SAML identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        value = ZeroTrustAccessPolicyExcludeSaml(
            attribute_name=attribute_name,
            attribute_value=attribute_value,
            identity_provider_id=identity_provider_id,
        )

        return typing.cast(None, jsii.invoke(self, "putSaml", [value]))

    @jsii.member(jsii_name="putServiceToken")
    def put_service_token(self, *, token_id: builtins.str) -> None:
        '''
        :param token_id: The ID of a Service Token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#token_id ZeroTrustAccessPolicy#token_id}
        '''
        value = ZeroTrustAccessPolicyExcludeServiceToken(token_id=token_id)

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
    ) -> ZeroTrustAccessPolicyExcludeAnyValidServiceTokenOutputReference:
        return typing.cast(ZeroTrustAccessPolicyExcludeAnyValidServiceTokenOutputReference, jsii.get(self, "anyValidServiceToken"))

    @builtins.property
    @jsii.member(jsii_name="authContext")
    def auth_context(self) -> ZeroTrustAccessPolicyExcludeAuthContextOutputReference:
        return typing.cast(ZeroTrustAccessPolicyExcludeAuthContextOutputReference, jsii.get(self, "authContext"))

    @builtins.property
    @jsii.member(jsii_name="authMethod")
    def auth_method(self) -> ZeroTrustAccessPolicyExcludeAuthMethodOutputReference:
        return typing.cast(ZeroTrustAccessPolicyExcludeAuthMethodOutputReference, jsii.get(self, "authMethod"))

    @builtins.property
    @jsii.member(jsii_name="azureAd")
    def azure_ad(self) -> ZeroTrustAccessPolicyExcludeAzureAdOutputReference:
        return typing.cast(ZeroTrustAccessPolicyExcludeAzureAdOutputReference, jsii.get(self, "azureAd"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> ZeroTrustAccessPolicyExcludeCertificateOutputReference:
        return typing.cast(ZeroTrustAccessPolicyExcludeCertificateOutputReference, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(self) -> ZeroTrustAccessPolicyExcludeCommonNameOutputReference:
        return typing.cast(ZeroTrustAccessPolicyExcludeCommonNameOutputReference, jsii.get(self, "commonName"))

    @builtins.property
    @jsii.member(jsii_name="devicePosture")
    def device_posture(
        self,
    ) -> ZeroTrustAccessPolicyExcludeDevicePostureOutputReference:
        return typing.cast(ZeroTrustAccessPolicyExcludeDevicePostureOutputReference, jsii.get(self, "devicePosture"))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(self) -> ZeroTrustAccessPolicyExcludeEmailOutputReference:
        return typing.cast(ZeroTrustAccessPolicyExcludeEmailOutputReference, jsii.get(self, "email"))

    @builtins.property
    @jsii.member(jsii_name="emailDomain")
    def email_domain(self) -> ZeroTrustAccessPolicyExcludeEmailDomainOutputReference:
        return typing.cast(ZeroTrustAccessPolicyExcludeEmailDomainOutputReference, jsii.get(self, "emailDomain"))

    @builtins.property
    @jsii.member(jsii_name="emailList")
    def email_list(self) -> ZeroTrustAccessPolicyExcludeEmailListStructOutputReference:
        return typing.cast(ZeroTrustAccessPolicyExcludeEmailListStructOutputReference, jsii.get(self, "emailList"))

    @builtins.property
    @jsii.member(jsii_name="everyone")
    def everyone(self) -> ZeroTrustAccessPolicyExcludeEveryoneOutputReference:
        return typing.cast(ZeroTrustAccessPolicyExcludeEveryoneOutputReference, jsii.get(self, "everyone"))

    @builtins.property
    @jsii.member(jsii_name="externalEvaluation")
    def external_evaluation(
        self,
    ) -> ZeroTrustAccessPolicyExcludeExternalEvaluationOutputReference:
        return typing.cast(ZeroTrustAccessPolicyExcludeExternalEvaluationOutputReference, jsii.get(self, "externalEvaluation"))

    @builtins.property
    @jsii.member(jsii_name="geo")
    def geo(self) -> ZeroTrustAccessPolicyExcludeGeoOutputReference:
        return typing.cast(ZeroTrustAccessPolicyExcludeGeoOutputReference, jsii.get(self, "geo"))

    @builtins.property
    @jsii.member(jsii_name="githubOrganization")
    def github_organization(
        self,
    ) -> ZeroTrustAccessPolicyExcludeGithubOrganizationOutputReference:
        return typing.cast(ZeroTrustAccessPolicyExcludeGithubOrganizationOutputReference, jsii.get(self, "githubOrganization"))

    @builtins.property
    @jsii.member(jsii_name="group")
    def group(self) -> ZeroTrustAccessPolicyExcludeGroupOutputReference:
        return typing.cast(ZeroTrustAccessPolicyExcludeGroupOutputReference, jsii.get(self, "group"))

    @builtins.property
    @jsii.member(jsii_name="gsuite")
    def gsuite(self) -> ZeroTrustAccessPolicyExcludeGsuiteOutputReference:
        return typing.cast(ZeroTrustAccessPolicyExcludeGsuiteOutputReference, jsii.get(self, "gsuite"))

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> ZeroTrustAccessPolicyExcludeIpOutputReference:
        return typing.cast(ZeroTrustAccessPolicyExcludeIpOutputReference, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="ipList")
    def ip_list(self) -> ZeroTrustAccessPolicyExcludeIpListStructOutputReference:
        return typing.cast(ZeroTrustAccessPolicyExcludeIpListStructOutputReference, jsii.get(self, "ipList"))

    @builtins.property
    @jsii.member(jsii_name="linkedAppToken")
    def linked_app_token(
        self,
    ) -> ZeroTrustAccessPolicyExcludeLinkedAppTokenOutputReference:
        return typing.cast(ZeroTrustAccessPolicyExcludeLinkedAppTokenOutputReference, jsii.get(self, "linkedAppToken"))

    @builtins.property
    @jsii.member(jsii_name="loginMethod")
    def login_method(self) -> ZeroTrustAccessPolicyExcludeLoginMethodOutputReference:
        return typing.cast(ZeroTrustAccessPolicyExcludeLoginMethodOutputReference, jsii.get(self, "loginMethod"))

    @builtins.property
    @jsii.member(jsii_name="oidc")
    def oidc(self) -> ZeroTrustAccessPolicyExcludeOidcOutputReference:
        return typing.cast(ZeroTrustAccessPolicyExcludeOidcOutputReference, jsii.get(self, "oidc"))

    @builtins.property
    @jsii.member(jsii_name="okta")
    def okta(self) -> ZeroTrustAccessPolicyExcludeOktaOutputReference:
        return typing.cast(ZeroTrustAccessPolicyExcludeOktaOutputReference, jsii.get(self, "okta"))

    @builtins.property
    @jsii.member(jsii_name="saml")
    def saml(self) -> "ZeroTrustAccessPolicyExcludeSamlOutputReference":
        return typing.cast("ZeroTrustAccessPolicyExcludeSamlOutputReference", jsii.get(self, "saml"))

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(
        self,
    ) -> "ZeroTrustAccessPolicyExcludeServiceTokenOutputReference":
        return typing.cast("ZeroTrustAccessPolicyExcludeServiceTokenOutputReference", jsii.get(self, "serviceToken"))

    @builtins.property
    @jsii.member(jsii_name="anyValidServiceTokenInput")
    def any_valid_service_token_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeAnyValidServiceToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeAnyValidServiceToken]], jsii.get(self, "anyValidServiceTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="authContextInput")
    def auth_context_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeAuthContext]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeAuthContext]], jsii.get(self, "authContextInput"))

    @builtins.property
    @jsii.member(jsii_name="authMethodInput")
    def auth_method_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeAuthMethod]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeAuthMethod]], jsii.get(self, "authMethodInput"))

    @builtins.property
    @jsii.member(jsii_name="azureAdInput")
    def azure_ad_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeAzureAd]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeAzureAd]], jsii.get(self, "azureAdInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateInput")
    def certificate_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeCertificate]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeCertificate]], jsii.get(self, "certificateInput"))

    @builtins.property
    @jsii.member(jsii_name="commonNameInput")
    def common_name_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeCommonName]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeCommonName]], jsii.get(self, "commonNameInput"))

    @builtins.property
    @jsii.member(jsii_name="devicePostureInput")
    def device_posture_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeDevicePosture]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeDevicePosture]], jsii.get(self, "devicePostureInput"))

    @builtins.property
    @jsii.member(jsii_name="emailDomainInput")
    def email_domain_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeEmailDomain]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeEmailDomain]], jsii.get(self, "emailDomainInput"))

    @builtins.property
    @jsii.member(jsii_name="emailInput")
    def email_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeEmail]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeEmail]], jsii.get(self, "emailInput"))

    @builtins.property
    @jsii.member(jsii_name="emailListInput")
    def email_list_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeEmailListStruct]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeEmailListStruct]], jsii.get(self, "emailListInput"))

    @builtins.property
    @jsii.member(jsii_name="everyoneInput")
    def everyone_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeEveryone]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeEveryone]], jsii.get(self, "everyoneInput"))

    @builtins.property
    @jsii.member(jsii_name="externalEvaluationInput")
    def external_evaluation_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeExternalEvaluation]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeExternalEvaluation]], jsii.get(self, "externalEvaluationInput"))

    @builtins.property
    @jsii.member(jsii_name="geoInput")
    def geo_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeGeo]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeGeo]], jsii.get(self, "geoInput"))

    @builtins.property
    @jsii.member(jsii_name="githubOrganizationInput")
    def github_organization_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeGithubOrganization]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeGithubOrganization]], jsii.get(self, "githubOrganizationInput"))

    @builtins.property
    @jsii.member(jsii_name="groupInput")
    def group_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeGroup]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeGroup]], jsii.get(self, "groupInput"))

    @builtins.property
    @jsii.member(jsii_name="gsuiteInput")
    def gsuite_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeGsuite]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeGsuite]], jsii.get(self, "gsuiteInput"))

    @builtins.property
    @jsii.member(jsii_name="ipInput")
    def ip_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeIp]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeIp]], jsii.get(self, "ipInput"))

    @builtins.property
    @jsii.member(jsii_name="ipListInput")
    def ip_list_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeIpListStruct]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeIpListStruct]], jsii.get(self, "ipListInput"))

    @builtins.property
    @jsii.member(jsii_name="linkedAppTokenInput")
    def linked_app_token_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeLinkedAppToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeLinkedAppToken]], jsii.get(self, "linkedAppTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="loginMethodInput")
    def login_method_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeLoginMethod]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeLoginMethod]], jsii.get(self, "loginMethodInput"))

    @builtins.property
    @jsii.member(jsii_name="oidcInput")
    def oidc_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeOidc]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeOidc]], jsii.get(self, "oidcInput"))

    @builtins.property
    @jsii.member(jsii_name="oktaInput")
    def okta_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeOkta]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeOkta]], jsii.get(self, "oktaInput"))

    @builtins.property
    @jsii.member(jsii_name="samlInput")
    def saml_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustAccessPolicyExcludeSaml"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustAccessPolicyExcludeSaml"]], jsii.get(self, "samlInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceTokenInput")
    def service_token_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustAccessPolicyExcludeServiceToken"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustAccessPolicyExcludeServiceToken"]], jsii.get(self, "serviceTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExclude]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExclude]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExclude]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aeb14724885d1c9f695410983be32b62d5004f77747131fd6def60c05828c592)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeSaml",
    jsii_struct_bases=[],
    name_mapping={
        "attribute_name": "attributeName",
        "attribute_value": "attributeValue",
        "identity_provider_id": "identityProviderId",
    },
)
class ZeroTrustAccessPolicyExcludeSaml:
    def __init__(
        self,
        *,
        attribute_name: builtins.str,
        attribute_value: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param attribute_name: The name of the SAML attribute. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#attribute_name ZeroTrustAccessPolicy#attribute_name}
        :param attribute_value: The SAML attribute value to look for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#attribute_value ZeroTrustAccessPolicy#attribute_value}
        :param identity_provider_id: The ID of your SAML identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__242e44373b7658f0aced88344e8eecd593ff32d89878239016780ed19773f47f)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#attribute_name ZeroTrustAccessPolicy#attribute_name}
        '''
        result = self._values.get("attribute_name")
        assert result is not None, "Required property 'attribute_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attribute_value(self) -> builtins.str:
        '''The SAML attribute value to look for.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#attribute_value ZeroTrustAccessPolicy#attribute_value}
        '''
        result = self._values.get("attribute_value")
        assert result is not None, "Required property 'attribute_value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your SAML identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyExcludeSaml(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyExcludeSamlOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeSamlOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b0ba9a13db53c682e5b22cc04e7fe3bcc4c3d5084621ae9ed74238b102afa8e9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__19229d4243d01f46765a92fb5325daa5da331d86c6a3b13b3c882b4f07f76408)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attributeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="attributeValue")
    def attribute_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "attributeValue"))

    @attribute_value.setter
    def attribute_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__096d237eccd1637b12f01041eabed72fe4a1e3cc3eae29b2018a9575e31fe1f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attributeValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b065cd8145b33e75816a1f959e2aa0f8ffaaee659b2d5bdddf5d656fadfcca97)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeSaml]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeSaml]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeSaml]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89a1fc7ac38fc5b4e59056492b10140cbd8f4752fce19a8b3e0b628de28d30e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeServiceToken",
    jsii_struct_bases=[],
    name_mapping={"token_id": "tokenId"},
)
class ZeroTrustAccessPolicyExcludeServiceToken:
    def __init__(self, *, token_id: builtins.str) -> None:
        '''
        :param token_id: The ID of a Service Token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#token_id ZeroTrustAccessPolicy#token_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49a8b95ac22a21d52f54cf4a96dc81d7afc0269b68291601c919ab8f86d7487f)
            check_type(argname="argument token_id", value=token_id, expected_type=type_hints["token_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "token_id": token_id,
        }

    @builtins.property
    def token_id(self) -> builtins.str:
        '''The ID of a Service Token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#token_id ZeroTrustAccessPolicy#token_id}
        '''
        result = self._values.get("token_id")
        assert result is not None, "Required property 'token_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyExcludeServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyExcludeServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyExcludeServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9c03796f6db00c793bf3cd565c927a5991607a34da90da7c29d0dd04d3777f07)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b1361b3356da9c61e4c4859aeb8fa8729f87b165b5c0c1451a93e84c60d9df6c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeServiceToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeServiceToken]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeServiceToken]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b11384b28df8fc3b6cc5740ed096ef43d0da9b6573100b7c2aa3d16595a44a2f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyInclude",
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
class ZeroTrustAccessPolicyInclude:
    def __init__(
        self,
        *,
        any_valid_service_token: typing.Optional[typing.Union["ZeroTrustAccessPolicyIncludeAnyValidServiceToken", typing.Dict[builtins.str, typing.Any]]] = None,
        auth_context: typing.Optional[typing.Union["ZeroTrustAccessPolicyIncludeAuthContext", typing.Dict[builtins.str, typing.Any]]] = None,
        auth_method: typing.Optional[typing.Union["ZeroTrustAccessPolicyIncludeAuthMethod", typing.Dict[builtins.str, typing.Any]]] = None,
        azure_ad: typing.Optional[typing.Union["ZeroTrustAccessPolicyIncludeAzureAd", typing.Dict[builtins.str, typing.Any]]] = None,
        certificate: typing.Optional[typing.Union["ZeroTrustAccessPolicyIncludeCertificate", typing.Dict[builtins.str, typing.Any]]] = None,
        common_name: typing.Optional[typing.Union["ZeroTrustAccessPolicyIncludeCommonName", typing.Dict[builtins.str, typing.Any]]] = None,
        device_posture: typing.Optional[typing.Union["ZeroTrustAccessPolicyIncludeDevicePosture", typing.Dict[builtins.str, typing.Any]]] = None,
        email: typing.Optional[typing.Union["ZeroTrustAccessPolicyIncludeEmail", typing.Dict[builtins.str, typing.Any]]] = None,
        email_domain: typing.Optional[typing.Union["ZeroTrustAccessPolicyIncludeEmailDomain", typing.Dict[builtins.str, typing.Any]]] = None,
        email_list: typing.Optional[typing.Union["ZeroTrustAccessPolicyIncludeEmailListStruct", typing.Dict[builtins.str, typing.Any]]] = None,
        everyone: typing.Optional[typing.Union["ZeroTrustAccessPolicyIncludeEveryone", typing.Dict[builtins.str, typing.Any]]] = None,
        external_evaluation: typing.Optional[typing.Union["ZeroTrustAccessPolicyIncludeExternalEvaluation", typing.Dict[builtins.str, typing.Any]]] = None,
        geo: typing.Optional[typing.Union["ZeroTrustAccessPolicyIncludeGeo", typing.Dict[builtins.str, typing.Any]]] = None,
        github_organization: typing.Optional[typing.Union["ZeroTrustAccessPolicyIncludeGithubOrganization", typing.Dict[builtins.str, typing.Any]]] = None,
        group: typing.Optional[typing.Union["ZeroTrustAccessPolicyIncludeGroup", typing.Dict[builtins.str, typing.Any]]] = None,
        gsuite: typing.Optional[typing.Union["ZeroTrustAccessPolicyIncludeGsuite", typing.Dict[builtins.str, typing.Any]]] = None,
        ip: typing.Optional[typing.Union["ZeroTrustAccessPolicyIncludeIp", typing.Dict[builtins.str, typing.Any]]] = None,
        ip_list: typing.Optional[typing.Union["ZeroTrustAccessPolicyIncludeIpListStruct", typing.Dict[builtins.str, typing.Any]]] = None,
        linked_app_token: typing.Optional[typing.Union["ZeroTrustAccessPolicyIncludeLinkedAppToken", typing.Dict[builtins.str, typing.Any]]] = None,
        login_method: typing.Optional[typing.Union["ZeroTrustAccessPolicyIncludeLoginMethod", typing.Dict[builtins.str, typing.Any]]] = None,
        oidc: typing.Optional[typing.Union["ZeroTrustAccessPolicyIncludeOidc", typing.Dict[builtins.str, typing.Any]]] = None,
        okta: typing.Optional[typing.Union["ZeroTrustAccessPolicyIncludeOkta", typing.Dict[builtins.str, typing.Any]]] = None,
        saml: typing.Optional[typing.Union["ZeroTrustAccessPolicyIncludeSaml", typing.Dict[builtins.str, typing.Any]]] = None,
        service_token: typing.Optional[typing.Union["ZeroTrustAccessPolicyIncludeServiceToken", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param any_valid_service_token: An empty object which matches on all service tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#any_valid_service_token ZeroTrustAccessPolicy#any_valid_service_token}
        :param auth_context: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#auth_context ZeroTrustAccessPolicy#auth_context}.
        :param auth_method: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#auth_method ZeroTrustAccessPolicy#auth_method}.
        :param azure_ad: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#azure_ad ZeroTrustAccessPolicy#azure_ad}.
        :param certificate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#certificate ZeroTrustAccessPolicy#certificate}.
        :param common_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#common_name ZeroTrustAccessPolicy#common_name}.
        :param device_posture: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#device_posture ZeroTrustAccessPolicy#device_posture}.
        :param email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email ZeroTrustAccessPolicy#email}.
        :param email_domain: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email_domain ZeroTrustAccessPolicy#email_domain}.
        :param email_list: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email_list ZeroTrustAccessPolicy#email_list}.
        :param everyone: An empty object which matches on all users. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#everyone ZeroTrustAccessPolicy#everyone}
        :param external_evaluation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#external_evaluation ZeroTrustAccessPolicy#external_evaluation}.
        :param geo: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#geo ZeroTrustAccessPolicy#geo}.
        :param github_organization: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#github_organization ZeroTrustAccessPolicy#github_organization}.
        :param group: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#group ZeroTrustAccessPolicy#group}.
        :param gsuite: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#gsuite ZeroTrustAccessPolicy#gsuite}.
        :param ip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ip ZeroTrustAccessPolicy#ip}.
        :param ip_list: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ip_list ZeroTrustAccessPolicy#ip_list}.
        :param linked_app_token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#linked_app_token ZeroTrustAccessPolicy#linked_app_token}.
        :param login_method: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#login_method ZeroTrustAccessPolicy#login_method}.
        :param oidc: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#oidc ZeroTrustAccessPolicy#oidc}.
        :param okta: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#okta ZeroTrustAccessPolicy#okta}.
        :param saml: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#saml ZeroTrustAccessPolicy#saml}.
        :param service_token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#service_token ZeroTrustAccessPolicy#service_token}.
        '''
        if isinstance(any_valid_service_token, dict):
            any_valid_service_token = ZeroTrustAccessPolicyIncludeAnyValidServiceToken(**any_valid_service_token)
        if isinstance(auth_context, dict):
            auth_context = ZeroTrustAccessPolicyIncludeAuthContext(**auth_context)
        if isinstance(auth_method, dict):
            auth_method = ZeroTrustAccessPolicyIncludeAuthMethod(**auth_method)
        if isinstance(azure_ad, dict):
            azure_ad = ZeroTrustAccessPolicyIncludeAzureAd(**azure_ad)
        if isinstance(certificate, dict):
            certificate = ZeroTrustAccessPolicyIncludeCertificate(**certificate)
        if isinstance(common_name, dict):
            common_name = ZeroTrustAccessPolicyIncludeCommonName(**common_name)
        if isinstance(device_posture, dict):
            device_posture = ZeroTrustAccessPolicyIncludeDevicePosture(**device_posture)
        if isinstance(email, dict):
            email = ZeroTrustAccessPolicyIncludeEmail(**email)
        if isinstance(email_domain, dict):
            email_domain = ZeroTrustAccessPolicyIncludeEmailDomain(**email_domain)
        if isinstance(email_list, dict):
            email_list = ZeroTrustAccessPolicyIncludeEmailListStruct(**email_list)
        if isinstance(everyone, dict):
            everyone = ZeroTrustAccessPolicyIncludeEveryone(**everyone)
        if isinstance(external_evaluation, dict):
            external_evaluation = ZeroTrustAccessPolicyIncludeExternalEvaluation(**external_evaluation)
        if isinstance(geo, dict):
            geo = ZeroTrustAccessPolicyIncludeGeo(**geo)
        if isinstance(github_organization, dict):
            github_organization = ZeroTrustAccessPolicyIncludeGithubOrganization(**github_organization)
        if isinstance(group, dict):
            group = ZeroTrustAccessPolicyIncludeGroup(**group)
        if isinstance(gsuite, dict):
            gsuite = ZeroTrustAccessPolicyIncludeGsuite(**gsuite)
        if isinstance(ip, dict):
            ip = ZeroTrustAccessPolicyIncludeIp(**ip)
        if isinstance(ip_list, dict):
            ip_list = ZeroTrustAccessPolicyIncludeIpListStruct(**ip_list)
        if isinstance(linked_app_token, dict):
            linked_app_token = ZeroTrustAccessPolicyIncludeLinkedAppToken(**linked_app_token)
        if isinstance(login_method, dict):
            login_method = ZeroTrustAccessPolicyIncludeLoginMethod(**login_method)
        if isinstance(oidc, dict):
            oidc = ZeroTrustAccessPolicyIncludeOidc(**oidc)
        if isinstance(okta, dict):
            okta = ZeroTrustAccessPolicyIncludeOkta(**okta)
        if isinstance(saml, dict):
            saml = ZeroTrustAccessPolicyIncludeSaml(**saml)
        if isinstance(service_token, dict):
            service_token = ZeroTrustAccessPolicyIncludeServiceToken(**service_token)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eba1a19c433cf98c94ebe2094176560fb95a7353c7bcb15ea2c741aa8483bcec)
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
    ) -> typing.Optional["ZeroTrustAccessPolicyIncludeAnyValidServiceToken"]:
        '''An empty object which matches on all service tokens.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#any_valid_service_token ZeroTrustAccessPolicy#any_valid_service_token}
        '''
        result = self._values.get("any_valid_service_token")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyIncludeAnyValidServiceToken"], result)

    @builtins.property
    def auth_context(
        self,
    ) -> typing.Optional["ZeroTrustAccessPolicyIncludeAuthContext"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#auth_context ZeroTrustAccessPolicy#auth_context}.'''
        result = self._values.get("auth_context")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyIncludeAuthContext"], result)

    @builtins.property
    def auth_method(self) -> typing.Optional["ZeroTrustAccessPolicyIncludeAuthMethod"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#auth_method ZeroTrustAccessPolicy#auth_method}.'''
        result = self._values.get("auth_method")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyIncludeAuthMethod"], result)

    @builtins.property
    def azure_ad(self) -> typing.Optional["ZeroTrustAccessPolicyIncludeAzureAd"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#azure_ad ZeroTrustAccessPolicy#azure_ad}.'''
        result = self._values.get("azure_ad")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyIncludeAzureAd"], result)

    @builtins.property
    def certificate(self) -> typing.Optional["ZeroTrustAccessPolicyIncludeCertificate"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#certificate ZeroTrustAccessPolicy#certificate}.'''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyIncludeCertificate"], result)

    @builtins.property
    def common_name(self) -> typing.Optional["ZeroTrustAccessPolicyIncludeCommonName"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#common_name ZeroTrustAccessPolicy#common_name}.'''
        result = self._values.get("common_name")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyIncludeCommonName"], result)

    @builtins.property
    def device_posture(
        self,
    ) -> typing.Optional["ZeroTrustAccessPolicyIncludeDevicePosture"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#device_posture ZeroTrustAccessPolicy#device_posture}.'''
        result = self._values.get("device_posture")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyIncludeDevicePosture"], result)

    @builtins.property
    def email(self) -> typing.Optional["ZeroTrustAccessPolicyIncludeEmail"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email ZeroTrustAccessPolicy#email}.'''
        result = self._values.get("email")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyIncludeEmail"], result)

    @builtins.property
    def email_domain(
        self,
    ) -> typing.Optional["ZeroTrustAccessPolicyIncludeEmailDomain"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email_domain ZeroTrustAccessPolicy#email_domain}.'''
        result = self._values.get("email_domain")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyIncludeEmailDomain"], result)

    @builtins.property
    def email_list(
        self,
    ) -> typing.Optional["ZeroTrustAccessPolicyIncludeEmailListStruct"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email_list ZeroTrustAccessPolicy#email_list}.'''
        result = self._values.get("email_list")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyIncludeEmailListStruct"], result)

    @builtins.property
    def everyone(self) -> typing.Optional["ZeroTrustAccessPolicyIncludeEveryone"]:
        '''An empty object which matches on all users.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#everyone ZeroTrustAccessPolicy#everyone}
        '''
        result = self._values.get("everyone")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyIncludeEveryone"], result)

    @builtins.property
    def external_evaluation(
        self,
    ) -> typing.Optional["ZeroTrustAccessPolicyIncludeExternalEvaluation"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#external_evaluation ZeroTrustAccessPolicy#external_evaluation}.'''
        result = self._values.get("external_evaluation")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyIncludeExternalEvaluation"], result)

    @builtins.property
    def geo(self) -> typing.Optional["ZeroTrustAccessPolicyIncludeGeo"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#geo ZeroTrustAccessPolicy#geo}.'''
        result = self._values.get("geo")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyIncludeGeo"], result)

    @builtins.property
    def github_organization(
        self,
    ) -> typing.Optional["ZeroTrustAccessPolicyIncludeGithubOrganization"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#github_organization ZeroTrustAccessPolicy#github_organization}.'''
        result = self._values.get("github_organization")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyIncludeGithubOrganization"], result)

    @builtins.property
    def group(self) -> typing.Optional["ZeroTrustAccessPolicyIncludeGroup"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#group ZeroTrustAccessPolicy#group}.'''
        result = self._values.get("group")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyIncludeGroup"], result)

    @builtins.property
    def gsuite(self) -> typing.Optional["ZeroTrustAccessPolicyIncludeGsuite"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#gsuite ZeroTrustAccessPolicy#gsuite}.'''
        result = self._values.get("gsuite")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyIncludeGsuite"], result)

    @builtins.property
    def ip(self) -> typing.Optional["ZeroTrustAccessPolicyIncludeIp"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ip ZeroTrustAccessPolicy#ip}.'''
        result = self._values.get("ip")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyIncludeIp"], result)

    @builtins.property
    def ip_list(self) -> typing.Optional["ZeroTrustAccessPolicyIncludeIpListStruct"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ip_list ZeroTrustAccessPolicy#ip_list}.'''
        result = self._values.get("ip_list")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyIncludeIpListStruct"], result)

    @builtins.property
    def linked_app_token(
        self,
    ) -> typing.Optional["ZeroTrustAccessPolicyIncludeLinkedAppToken"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#linked_app_token ZeroTrustAccessPolicy#linked_app_token}.'''
        result = self._values.get("linked_app_token")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyIncludeLinkedAppToken"], result)

    @builtins.property
    def login_method(
        self,
    ) -> typing.Optional["ZeroTrustAccessPolicyIncludeLoginMethod"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#login_method ZeroTrustAccessPolicy#login_method}.'''
        result = self._values.get("login_method")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyIncludeLoginMethod"], result)

    @builtins.property
    def oidc(self) -> typing.Optional["ZeroTrustAccessPolicyIncludeOidc"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#oidc ZeroTrustAccessPolicy#oidc}.'''
        result = self._values.get("oidc")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyIncludeOidc"], result)

    @builtins.property
    def okta(self) -> typing.Optional["ZeroTrustAccessPolicyIncludeOkta"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#okta ZeroTrustAccessPolicy#okta}.'''
        result = self._values.get("okta")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyIncludeOkta"], result)

    @builtins.property
    def saml(self) -> typing.Optional["ZeroTrustAccessPolicyIncludeSaml"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#saml ZeroTrustAccessPolicy#saml}.'''
        result = self._values.get("saml")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyIncludeSaml"], result)

    @builtins.property
    def service_token(
        self,
    ) -> typing.Optional["ZeroTrustAccessPolicyIncludeServiceToken"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#service_token ZeroTrustAccessPolicy#service_token}.'''
        result = self._values.get("service_token")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyIncludeServiceToken"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyInclude(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeAnyValidServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class ZeroTrustAccessPolicyIncludeAnyValidServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyIncludeAnyValidServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyIncludeAnyValidServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeAnyValidServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cd86358aec538bb10e394b6be823e5e6ece505f319bb1b64c4235c6c61ad2401)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeAnyValidServiceToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeAnyValidServiceToken]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeAnyValidServiceToken]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61e76cb06860fbfbada882993aa6c4fda6560193b982a4cb48580b2c6bfebeb6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeAuthContext",
    jsii_struct_bases=[],
    name_mapping={
        "ac_id": "acId",
        "id": "id",
        "identity_provider_id": "identityProviderId",
    },
)
class ZeroTrustAccessPolicyIncludeAuthContext:
    def __init__(
        self,
        *,
        ac_id: builtins.str,
        id: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param ac_id: The ACID of an Authentication context. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ac_id ZeroTrustAccessPolicy#ac_id}
        :param id: The ID of an Authentication context. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider_id: The ID of your Azure identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__781e9053f06d82ec604e4248e23de31214f270847a7df5cce49144ee3c5a15c6)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ac_id ZeroTrustAccessPolicy#ac_id}
        '''
        result = self._values.get("ac_id")
        assert result is not None, "Required property 'ac_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of an Authentication context.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your Azure identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyIncludeAuthContext(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyIncludeAuthContextOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeAuthContextOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5bbfffc801df5041436dc9a457fe8d3fe520d7d8d74db4018c917a5361668553)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c331f7a80c4b9cda857afd4cae2df295df4cbdecc2eb1c35d80d9919d8b94f9c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "acId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__551bef813169c94bf2a71788becb7be8af03b1d301f2b3e9e81fc19a7a676b59)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4a5ebc3557ca0ea2f588a769165827bd4f111ce31bd3f5f18c5f32e7a0d92d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeAuthContext]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeAuthContext]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeAuthContext]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5f4935e195ea5e382584cdc213d3177beb9bfe4cb3bb04e5e274b1a23482a39)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeAuthMethod",
    jsii_struct_bases=[],
    name_mapping={"auth_method": "authMethod"},
)
class ZeroTrustAccessPolicyIncludeAuthMethod:
    def __init__(self, *, auth_method: builtins.str) -> None:
        '''
        :param auth_method: The type of authentication method https://datatracker.ietf.org/doc/html/rfc8176#section-2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#auth_method ZeroTrustAccessPolicy#auth_method}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9270352f597bbcc686d6a9877f8cbb08c4a6a4783d2382e7d6c71ac7ba3929b9)
            check_type(argname="argument auth_method", value=auth_method, expected_type=type_hints["auth_method"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "auth_method": auth_method,
        }

    @builtins.property
    def auth_method(self) -> builtins.str:
        '''The type of authentication method https://datatracker.ietf.org/doc/html/rfc8176#section-2.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#auth_method ZeroTrustAccessPolicy#auth_method}
        '''
        result = self._values.get("auth_method")
        assert result is not None, "Required property 'auth_method' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyIncludeAuthMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyIncludeAuthMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeAuthMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7a1cb51482775867cfb35cdc5c193a15c1b03859b96e61426a8522bf15651a25)
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
            type_hints = typing.get_type_hints(_typecheckingstub__acaa3a67d0aa5269fb136b648954c32e9e80e4f890c3f7aa57e601a27745ce9a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authMethod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeAuthMethod]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeAuthMethod]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeAuthMethod]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da191d71057bd9ef53c26adc126a6fa6127f2dea09989ecd33cf680672009a31)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeAzureAd",
    jsii_struct_bases=[],
    name_mapping={"id": "id", "identity_provider_id": "identityProviderId"},
)
class ZeroTrustAccessPolicyIncludeAzureAd:
    def __init__(self, *, id: builtins.str, identity_provider_id: builtins.str) -> None:
        '''
        :param id: The ID of an Azure group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider_id: The ID of your Azure identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9bd107b6a7f7170f086a6cf6b79e01e1c7919d2e746d729ae10e7a2e499f1025)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
            "identity_provider_id": identity_provider_id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of an Azure group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your Azure identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyIncludeAzureAd(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyIncludeAzureAdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeAzureAdOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5c0d8d387b02f9f6caf3a92ff95488ed3166869cfebf45590b5a1145bcb3ce45)
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
            type_hints = typing.get_type_hints(_typecheckingstub__32bb6c8f792d833cc1e32113999be244b1c319665366080638313ba4ce608b7b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f020128e536badbc6ff3f7f02c5d19225c024dc50851dcdfa4f59207963e3ac9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeAzureAd]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeAzureAd]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeAzureAd]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbf2956abec4edae960965394bd502d1237787b4c6e7d4de826221dd963a58d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeCertificate",
    jsii_struct_bases=[],
    name_mapping={},
)
class ZeroTrustAccessPolicyIncludeCertificate:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyIncludeCertificate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyIncludeCertificateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeCertificateOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f22a761710becc6c1b3a644a73caf05a575748e802915656f4c4db71a02cdcc5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeCertificate]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeCertificate]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeCertificate]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f5c43733f80f99b2ff2f1e8639e0d6e73737f659ac158f39226bd99d3098f48)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeCommonName",
    jsii_struct_bases=[],
    name_mapping={"common_name": "commonName"},
)
class ZeroTrustAccessPolicyIncludeCommonName:
    def __init__(self, *, common_name: builtins.str) -> None:
        '''
        :param common_name: The common name to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#common_name ZeroTrustAccessPolicy#common_name}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5aa9dd6b5e97243767e16727117ec07504704ffc4fc95508009069ab9925429f)
            check_type(argname="argument common_name", value=common_name, expected_type=type_hints["common_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "common_name": common_name,
        }

    @builtins.property
    def common_name(self) -> builtins.str:
        '''The common name to match.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#common_name ZeroTrustAccessPolicy#common_name}
        '''
        result = self._values.get("common_name")
        assert result is not None, "Required property 'common_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyIncludeCommonName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyIncludeCommonNameOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeCommonNameOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7a43acd6445200d53505a8bc528899e7b0244c4a65e24b8e23bdb4f6517ddaeb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a1a8b44081887709d3ba18dc65f88ad6cc33617bb4fa617db4b58cf07afe5bbd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "commonName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeCommonName]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeCommonName]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeCommonName]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e47bbc55b770047d8c96325e0ebb9d9ba01bb127c9a23f27ada317410045b63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeDevicePosture",
    jsii_struct_bases=[],
    name_mapping={"integration_uid": "integrationUid"},
)
class ZeroTrustAccessPolicyIncludeDevicePosture:
    def __init__(self, *, integration_uid: builtins.str) -> None:
        '''
        :param integration_uid: The ID of a device posture integration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#integration_uid ZeroTrustAccessPolicy#integration_uid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52d4172af1a73d3d34e283c4f334e2298ca329aad0e5751595cfc095776a18f9)
            check_type(argname="argument integration_uid", value=integration_uid, expected_type=type_hints["integration_uid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "integration_uid": integration_uid,
        }

    @builtins.property
    def integration_uid(self) -> builtins.str:
        '''The ID of a device posture integration.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#integration_uid ZeroTrustAccessPolicy#integration_uid}
        '''
        result = self._values.get("integration_uid")
        assert result is not None, "Required property 'integration_uid' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyIncludeDevicePosture(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyIncludeDevicePostureOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeDevicePostureOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b77c359b1c1ce923d8399aaacb9228da331c06d16f9f3848af9cd4ac30badea5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3e6bda13a29a5ce536793e27959c8837b3178daa071a22791d8459fd63edd7ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "integrationUid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeDevicePosture]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeDevicePosture]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeDevicePosture]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0bc7980fe105bf86440d6eae6c66ad0ce4e017298dba7ad17b7726cf5a59ba3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeEmail",
    jsii_struct_bases=[],
    name_mapping={"email": "email"},
)
class ZeroTrustAccessPolicyIncludeEmail:
    def __init__(self, *, email: builtins.str) -> None:
        '''
        :param email: The email of the user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email ZeroTrustAccessPolicy#email}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8611e4c3017196b60615760bbb2b357f6c250eb0d2fbacd560e6f6c5755a5835)
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "email": email,
        }

    @builtins.property
    def email(self) -> builtins.str:
        '''The email of the user.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email ZeroTrustAccessPolicy#email}
        '''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyIncludeEmail(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeEmailDomain",
    jsii_struct_bases=[],
    name_mapping={"domain": "domain"},
)
class ZeroTrustAccessPolicyIncludeEmailDomain:
    def __init__(self, *, domain: builtins.str) -> None:
        '''
        :param domain: The email domain to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#domain ZeroTrustAccessPolicy#domain}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e4f33ebbcfb2b294ced7bcaa44220d2546564da6c9fa4a5df5e637a1d45da8d)
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain": domain,
        }

    @builtins.property
    def domain(self) -> builtins.str:
        '''The email domain to match.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#domain ZeroTrustAccessPolicy#domain}
        '''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyIncludeEmailDomain(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyIncludeEmailDomainOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeEmailDomainOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e19ae8402c9544d39056fd0de1a7b252dc632dabaa27c6228cc5961cb2a9e78a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0d1bc5e16f802d517a35b9e42b98e8b216e88c5bc417a9a694af5dcd3be0d0ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "domain", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeEmailDomain]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeEmailDomain]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeEmailDomain]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__933429a68d8a88bd0e47fec8eab9475978679a36d23fdef0e29578df642a2c0f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeEmailListStruct",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class ZeroTrustAccessPolicyIncludeEmailListStruct:
    def __init__(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created email list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__092b82806b61eac4892dfee8a89e3b7acdda74a4525bcf9a2bf62aefc8e48314)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of a previously created email list.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id}

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
        return "ZeroTrustAccessPolicyIncludeEmailListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyIncludeEmailListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeEmailListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5e51a0fdb95eb96116cf5cd3a15b45e6f6baa9e45508b419eac3ca65b0648693)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c77835058d2588dc236a931fa117a36e7839fe9eb0cab8fa9d11f386b5c9a5a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeEmailListStruct]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeEmailListStruct]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeEmailListStruct]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dececbaa454223a4df483b9300af4539a755b57cefc2f8ee51c9398b39d75597)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustAccessPolicyIncludeEmailOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeEmailOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f77caabf1f8b5d617eb4c6cdcca0efb66ca88365360639baa95a0fd526017ddc)
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
            type_hints = typing.get_type_hints(_typecheckingstub__56a17d037349a6a29f4c100c818f7c19529f3fb451f35ff984259d11ac73e017)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "email", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeEmail]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeEmail]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeEmail]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3b011b0ae1db73b21e31f7d3c70db9c2b5639b63dd33eb37d8582d123072616)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeEveryone",
    jsii_struct_bases=[],
    name_mapping={},
)
class ZeroTrustAccessPolicyIncludeEveryone:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyIncludeEveryone(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyIncludeEveryoneOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeEveryoneOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6995d19f84c0477ba6e4346e51e55ba20f95ab00e0e11d98eb712cb646dfe856)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeEveryone]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeEveryone]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeEveryone]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbbf6770b4ebe2215fa4ff8057d84b5a3fd614ec811b56d15538717e40a9ede3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeExternalEvaluation",
    jsii_struct_bases=[],
    name_mapping={"evaluate_url": "evaluateUrl", "keys_url": "keysUrl"},
)
class ZeroTrustAccessPolicyIncludeExternalEvaluation:
    def __init__(self, *, evaluate_url: builtins.str, keys_url: builtins.str) -> None:
        '''
        :param evaluate_url: The API endpoint containing your business logic. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#evaluate_url ZeroTrustAccessPolicy#evaluate_url}
        :param keys_url: The API endpoint containing the key that Access uses to verify that the response came from your API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#keys_url ZeroTrustAccessPolicy#keys_url}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__834fdc2937036d1d34196379875638d3857b05f01fb6392bb029b8c5c95e5f1b)
            check_type(argname="argument evaluate_url", value=evaluate_url, expected_type=type_hints["evaluate_url"])
            check_type(argname="argument keys_url", value=keys_url, expected_type=type_hints["keys_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "evaluate_url": evaluate_url,
            "keys_url": keys_url,
        }

    @builtins.property
    def evaluate_url(self) -> builtins.str:
        '''The API endpoint containing your business logic.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#evaluate_url ZeroTrustAccessPolicy#evaluate_url}
        '''
        result = self._values.get("evaluate_url")
        assert result is not None, "Required property 'evaluate_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def keys_url(self) -> builtins.str:
        '''The API endpoint containing the key that Access uses to verify that the response came from your API.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#keys_url ZeroTrustAccessPolicy#keys_url}
        '''
        result = self._values.get("keys_url")
        assert result is not None, "Required property 'keys_url' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyIncludeExternalEvaluation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyIncludeExternalEvaluationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeExternalEvaluationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a2474259f73939749f6c518c86f96993869dbd012d1d105c453d6d2bf878b6bc)
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
            type_hints = typing.get_type_hints(_typecheckingstub__623e76f372302c9409a3e8e9b623a1df3f0ba6c88b8fb3de4e2378af2626c8ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "evaluateUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keysUrl")
    def keys_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keysUrl"))

    @keys_url.setter
    def keys_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8095dc78ff13e3de511bb08b78c1d79281cacbe409360cf6762d02e1342bb600)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keysUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeExternalEvaluation]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeExternalEvaluation]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeExternalEvaluation]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__996db842431b7909b752892add7ba8e74ba26f7956c5f4354c8a47c7a83fe6dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeGeo",
    jsii_struct_bases=[],
    name_mapping={"country_code": "countryCode"},
)
class ZeroTrustAccessPolicyIncludeGeo:
    def __init__(self, *, country_code: builtins.str) -> None:
        '''
        :param country_code: The country code that should be matched. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#country_code ZeroTrustAccessPolicy#country_code}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f6d70c9a082ad2f8a451a889a7a04299549ae9a8b854bcb9109cdeacf3352de)
            check_type(argname="argument country_code", value=country_code, expected_type=type_hints["country_code"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "country_code": country_code,
        }

    @builtins.property
    def country_code(self) -> builtins.str:
        '''The country code that should be matched.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#country_code ZeroTrustAccessPolicy#country_code}
        '''
        result = self._values.get("country_code")
        assert result is not None, "Required property 'country_code' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyIncludeGeo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyIncludeGeoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeGeoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__74bda68eda7943b0d57912ceacdb57c29b264c29bf55ac7d88aa81c98fa2bfaa)
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
            type_hints = typing.get_type_hints(_typecheckingstub__509cd44692315253b68ff6bf8c6e6d5bbf3c0a01ce697d0379ae09f9cdb6d4d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "countryCode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeGeo]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeGeo]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeGeo]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48396154bc10bc520e86f7872f00ba860ef5da50c7dc4dc736dfeb6e2e4d14ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeGithubOrganization",
    jsii_struct_bases=[],
    name_mapping={
        "identity_provider_id": "identityProviderId",
        "name": "name",
        "team": "team",
    },
)
class ZeroTrustAccessPolicyIncludeGithubOrganization:
    def __init__(
        self,
        *,
        identity_provider_id: builtins.str,
        name: builtins.str,
        team: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param identity_provider_id: The ID of your Github identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        :param name: The name of the organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#name ZeroTrustAccessPolicy#name}
        :param team: The name of the team. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#team ZeroTrustAccessPolicy#team}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55f1d3cc8f727c740db84e1e32fd28c0ab46664d0950f251f25526b5fb5c4c44)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the organization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#name ZeroTrustAccessPolicy#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def team(self) -> typing.Optional[builtins.str]:
        '''The name of the team.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#team ZeroTrustAccessPolicy#team}
        '''
        result = self._values.get("team")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyIncludeGithubOrganization(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyIncludeGithubOrganizationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeGithubOrganizationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__164c4d078acaba1fa9f73c8ea6425e2be8fc1e0a55fad4ea49a5a44e2d14cbd9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__10d9991766622777d94cedf8487a5e407e37dfd9a76a4fd7a7a97684043d43c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e27b2ae9fbbbf5eee5cadc076716d137830510962b70e136cfe106a8cd04341c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="team")
    def team(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "team"))

    @team.setter
    def team(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f901518ec77e37753363ebe6bd54b52fdf78454ed9b34f0930c2b6fd7579795b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "team", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeGithubOrganization]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeGithubOrganization]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeGithubOrganization]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4309feff65deaee3b46b23965cb89915db368538f17cdcafd84ad483e2cd5f2c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeGroup",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class ZeroTrustAccessPolicyIncludeGroup:
    def __init__(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created Access group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0dbaf5609d8c9b03816c986a5a6c21b960ccaa71c3d53a76fdae285cecb8e008)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of a previously created Access group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id}

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
        return "ZeroTrustAccessPolicyIncludeGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyIncludeGroupOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeGroupOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__47514bb6e8e668f5f0bf5c0d34168dbc0b5a9faa9a2c8a71158fb1efd7ae643d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7ea842883f022b6afdfccc36936f1840327be030da60b80f18c20de9521b76ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeGroup]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeGroup]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeGroup]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb40d2fbd7a867e2052d6df519afd09390e8971ccdf5e0618ebfb699875039cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeGsuite",
    jsii_struct_bases=[],
    name_mapping={"email": "email", "identity_provider_id": "identityProviderId"},
)
class ZeroTrustAccessPolicyIncludeGsuite:
    def __init__(
        self,
        *,
        email: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param email: The email of the Google Workspace group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email ZeroTrustAccessPolicy#email}
        :param identity_provider_id: The ID of your Google Workspace identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c92e02eade7181ee80d27b73ff8c93e5abce28f5003140240318bc1f9ebeaa72)
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "email": email,
            "identity_provider_id": identity_provider_id,
        }

    @builtins.property
    def email(self) -> builtins.str:
        '''The email of the Google Workspace group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email ZeroTrustAccessPolicy#email}
        '''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your Google Workspace identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyIncludeGsuite(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyIncludeGsuiteOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeGsuiteOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__073dcd62decb1084eaf33923245b2e90c924f04f85aa1b75501e44fb07c7afa3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5265c081b3159b4567e2fba7b02be9bc8e68f1f50eef361b2799f43360a78201)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "email", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b4d86becdc495f105fb842e8819037de4e9c805817464a882b3daa219fd29d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeGsuite]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeGsuite]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeGsuite]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae2666292c2d540e0cab7d77f151e0ed55cb4e631420dcf275c58e5ebe900ca4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeIp",
    jsii_struct_bases=[],
    name_mapping={"ip": "ip"},
)
class ZeroTrustAccessPolicyIncludeIp:
    def __init__(self, *, ip: builtins.str) -> None:
        '''
        :param ip: An IPv4 or IPv6 CIDR block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ip ZeroTrustAccessPolicy#ip}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d3e2246ec1accde7496d18c665b2646007c70d6f6331ecf8f0784ec62486143)
            check_type(argname="argument ip", value=ip, expected_type=type_hints["ip"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "ip": ip,
        }

    @builtins.property
    def ip(self) -> builtins.str:
        '''An IPv4 or IPv6 CIDR block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ip ZeroTrustAccessPolicy#ip}
        '''
        result = self._values.get("ip")
        assert result is not None, "Required property 'ip' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyIncludeIp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeIpListStruct",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class ZeroTrustAccessPolicyIncludeIpListStruct:
    def __init__(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created IP list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82e68811c744ec9675ca7ee71832fd2f233ab82ef485554d6506264e004d3edc)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of a previously created IP list.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id}

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
        return "ZeroTrustAccessPolicyIncludeIpListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyIncludeIpListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeIpListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b6e80881b460285247018d2959cdde77b26e494c261b014f38862058a862298f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e31a146a12674d179f71f15c2d98f91ec412c4a4a56a6bf4722fec1bf01fe996)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeIpListStruct]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeIpListStruct]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeIpListStruct]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2589db0dff30ecbb74380f7da7630c3bd988f4d13cb3174e6d2ac1b707e518f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustAccessPolicyIncludeIpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeIpOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4f24ae147e37e732b7e3bcf88368c5e4f010d61c086e69307ebd4f68f0582d84)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a26899b1080959ff0d7041ca8bfeb0c1b6d7c6c5045d89e86c73a33f66e99243)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ip", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeIp]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeIp]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeIp]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__506df49184c74d33107b23cee2404d2875f4f78bb9f218afa86e9385159a262e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeLinkedAppToken",
    jsii_struct_bases=[],
    name_mapping={"app_uid": "appUid"},
)
class ZeroTrustAccessPolicyIncludeLinkedAppToken:
    def __init__(self, *, app_uid: builtins.str) -> None:
        '''
        :param app_uid: The ID of an Access OIDC SaaS application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#app_uid ZeroTrustAccessPolicy#app_uid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba40fdacec4dd44d00bd4d43200ed7382ee0688020eaf0d65f601ced38d9c156)
            check_type(argname="argument app_uid", value=app_uid, expected_type=type_hints["app_uid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "app_uid": app_uid,
        }

    @builtins.property
    def app_uid(self) -> builtins.str:
        '''The ID of an Access OIDC SaaS application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#app_uid ZeroTrustAccessPolicy#app_uid}
        '''
        result = self._values.get("app_uid")
        assert result is not None, "Required property 'app_uid' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyIncludeLinkedAppToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyIncludeLinkedAppTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeLinkedAppTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__299452d302911794388a69e6fbaa8da53e7b09751c8dbc669b1edbda14756f25)
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
            type_hints = typing.get_type_hints(_typecheckingstub__aabdff0399bd9866f61d3b99e57617156e8e593f6810b115a777c5d673249d79)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "appUid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeLinkedAppToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeLinkedAppToken]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeLinkedAppToken]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5d412a9132cf8a9f10e6d3f9907ee1d5f33c7fae64e26e630c3901ba3c72c9d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustAccessPolicyIncludeList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dcbfe0f7100a78c79ace647b1ff4352d9308b499a7eb39491c9d722c23a6105a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ZeroTrustAccessPolicyIncludeOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4e713f45f22abe18c5ba8e2e56276024a701fc34673eebfa884b33a8ee48761)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ZeroTrustAccessPolicyIncludeOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f2e293aad229ef751d9ac1f62d9915238936ab67db0723db2babf1d646cd462)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4097638984fe7b1642aae1d74d4ac5e77e79590ea8821ff58098b3fcfe692228)
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
            type_hints = typing.get_type_hints(_typecheckingstub__67ca617d1837b4a7a6ca87201242f98245f9b50fb1f828ef958f380f9410483c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessPolicyInclude]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessPolicyInclude]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessPolicyInclude]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa018ba929260653e91486d503e78806f98ea1dacca34e7b48fdb935d25e8bc6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeLoginMethod",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class ZeroTrustAccessPolicyIncludeLoginMethod:
    def __init__(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of an identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d8dbbfa01bd6a9be398b16f05cb53f8eee1d5de23bcdb82af68bc307d598542)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of an identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id}

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
        return "ZeroTrustAccessPolicyIncludeLoginMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyIncludeLoginMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeLoginMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ca045ff8184f19dd9fd35d90b28d8c5682d5262e716922c1e5e75e0df84758d6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6150d0a0a9048bf5dcf9009181560246daf3b193341d2ac14148afcdd141f28c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeLoginMethod]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeLoginMethod]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeLoginMethod]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53a877d574de2321040473c213e93157c97b03bdb1cd52d2d36023356e4b9027)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeOidc",
    jsii_struct_bases=[],
    name_mapping={
        "claim_name": "claimName",
        "claim_value": "claimValue",
        "identity_provider_id": "identityProviderId",
    },
)
class ZeroTrustAccessPolicyIncludeOidc:
    def __init__(
        self,
        *,
        claim_name: builtins.str,
        claim_value: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param claim_name: The name of the OIDC claim. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#claim_name ZeroTrustAccessPolicy#claim_name}
        :param claim_value: The OIDC claim value to look for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#claim_value ZeroTrustAccessPolicy#claim_value}
        :param identity_provider_id: The ID of your OIDC identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dce6ae9d2d8043d02a0b4bb1b9f01f58a184d9efdb86592a32b57956c4aec6f8)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#claim_name ZeroTrustAccessPolicy#claim_name}
        '''
        result = self._values.get("claim_name")
        assert result is not None, "Required property 'claim_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def claim_value(self) -> builtins.str:
        '''The OIDC claim value to look for.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#claim_value ZeroTrustAccessPolicy#claim_value}
        '''
        result = self._values.get("claim_value")
        assert result is not None, "Required property 'claim_value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your OIDC identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyIncludeOidc(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyIncludeOidcOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeOidcOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__282b245c282b3fee52107b977b3841e3334ce8a87f70d5b5d4f54e9e98d55e64)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e609963f4c8bb8ae3a030e307b279211c09611643f09a45321c76ae0dfe9f571)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "claimName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="claimValue")
    def claim_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "claimValue"))

    @claim_value.setter
    def claim_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cef078c1c371540b54448492d732c3823b2b33d14ac9a797c06a19b99558caa3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "claimValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d726f4aa5aac10fba4f11c936e12c431e76bce42245c0453429e6b22f9515339)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeOidc]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeOidc]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeOidc]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3ad2271a6f420e201a8adcc91de2223142fbb33db9694adbd892bdfdaad1eb0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeOkta",
    jsii_struct_bases=[],
    name_mapping={"identity_provider_id": "identityProviderId", "name": "name"},
)
class ZeroTrustAccessPolicyIncludeOkta:
    def __init__(
        self,
        *,
        identity_provider_id: builtins.str,
        name: builtins.str,
    ) -> None:
        '''
        :param identity_provider_id: The ID of your Okta identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        :param name: The name of the Okta group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#name ZeroTrustAccessPolicy#name}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85ecd512ac738602091d80049ebaee14f828df63a8c54d8e1924f45fa8023872)
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "identity_provider_id": identity_provider_id,
            "name": name,
        }

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your Okta identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the Okta group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#name ZeroTrustAccessPolicy#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyIncludeOkta(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyIncludeOktaOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeOktaOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fa26e2ad5ceab0f3a9dbc02b3e943a0bb9a843dab5c584323b8fba6f512a4a9b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__73d6d12c72bb67226d7d0758bfce0e9b8f44f4c9baa61793e22b256581008feb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96504b4c72c9011a0b83db3816cc5232269a16656e055ef4124b8ce40928e996)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeOkta]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeOkta]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeOkta]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__128ad5f532dab3561fd1663d19cf2f1f6d64830f1361f709dd552c525a8ea472)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustAccessPolicyIncludeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f5e8e7142ffbfddda1dbca8a8320ab3296da6905ef82749c54cc2cb68cff145a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putAnyValidServiceToken")
    def put_any_valid_service_token(self) -> None:
        value = ZeroTrustAccessPolicyIncludeAnyValidServiceToken()

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
        :param ac_id: The ACID of an Authentication context. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ac_id ZeroTrustAccessPolicy#ac_id}
        :param id: The ID of an Authentication context. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider_id: The ID of your Azure identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        value = ZeroTrustAccessPolicyIncludeAuthContext(
            ac_id=ac_id, id=id, identity_provider_id=identity_provider_id
        )

        return typing.cast(None, jsii.invoke(self, "putAuthContext", [value]))

    @jsii.member(jsii_name="putAuthMethod")
    def put_auth_method(self, *, auth_method: builtins.str) -> None:
        '''
        :param auth_method: The type of authentication method https://datatracker.ietf.org/doc/html/rfc8176#section-2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#auth_method ZeroTrustAccessPolicy#auth_method}
        '''
        value = ZeroTrustAccessPolicyIncludeAuthMethod(auth_method=auth_method)

        return typing.cast(None, jsii.invoke(self, "putAuthMethod", [value]))

    @jsii.member(jsii_name="putAzureAd")
    def put_azure_ad(
        self,
        *,
        id: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param id: The ID of an Azure group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider_id: The ID of your Azure identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        value = ZeroTrustAccessPolicyIncludeAzureAd(
            id=id, identity_provider_id=identity_provider_id
        )

        return typing.cast(None, jsii.invoke(self, "putAzureAd", [value]))

    @jsii.member(jsii_name="putCertificate")
    def put_certificate(self) -> None:
        value = ZeroTrustAccessPolicyIncludeCertificate()

        return typing.cast(None, jsii.invoke(self, "putCertificate", [value]))

    @jsii.member(jsii_name="putCommonName")
    def put_common_name(self, *, common_name: builtins.str) -> None:
        '''
        :param common_name: The common name to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#common_name ZeroTrustAccessPolicy#common_name}
        '''
        value = ZeroTrustAccessPolicyIncludeCommonName(common_name=common_name)

        return typing.cast(None, jsii.invoke(self, "putCommonName", [value]))

    @jsii.member(jsii_name="putDevicePosture")
    def put_device_posture(self, *, integration_uid: builtins.str) -> None:
        '''
        :param integration_uid: The ID of a device posture integration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#integration_uid ZeroTrustAccessPolicy#integration_uid}
        '''
        value = ZeroTrustAccessPolicyIncludeDevicePosture(
            integration_uid=integration_uid
        )

        return typing.cast(None, jsii.invoke(self, "putDevicePosture", [value]))

    @jsii.member(jsii_name="putEmail")
    def put_email(self, *, email: builtins.str) -> None:
        '''
        :param email: The email of the user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email ZeroTrustAccessPolicy#email}
        '''
        value = ZeroTrustAccessPolicyIncludeEmail(email=email)

        return typing.cast(None, jsii.invoke(self, "putEmail", [value]))

    @jsii.member(jsii_name="putEmailDomain")
    def put_email_domain(self, *, domain: builtins.str) -> None:
        '''
        :param domain: The email domain to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#domain ZeroTrustAccessPolicy#domain}
        '''
        value = ZeroTrustAccessPolicyIncludeEmailDomain(domain=domain)

        return typing.cast(None, jsii.invoke(self, "putEmailDomain", [value]))

    @jsii.member(jsii_name="putEmailList")
    def put_email_list(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created email list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        value = ZeroTrustAccessPolicyIncludeEmailListStruct(id=id)

        return typing.cast(None, jsii.invoke(self, "putEmailList", [value]))

    @jsii.member(jsii_name="putEveryone")
    def put_everyone(self) -> None:
        value = ZeroTrustAccessPolicyIncludeEveryone()

        return typing.cast(None, jsii.invoke(self, "putEveryone", [value]))

    @jsii.member(jsii_name="putExternalEvaluation")
    def put_external_evaluation(
        self,
        *,
        evaluate_url: builtins.str,
        keys_url: builtins.str,
    ) -> None:
        '''
        :param evaluate_url: The API endpoint containing your business logic. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#evaluate_url ZeroTrustAccessPolicy#evaluate_url}
        :param keys_url: The API endpoint containing the key that Access uses to verify that the response came from your API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#keys_url ZeroTrustAccessPolicy#keys_url}
        '''
        value = ZeroTrustAccessPolicyIncludeExternalEvaluation(
            evaluate_url=evaluate_url, keys_url=keys_url
        )

        return typing.cast(None, jsii.invoke(self, "putExternalEvaluation", [value]))

    @jsii.member(jsii_name="putGeo")
    def put_geo(self, *, country_code: builtins.str) -> None:
        '''
        :param country_code: The country code that should be matched. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#country_code ZeroTrustAccessPolicy#country_code}
        '''
        value = ZeroTrustAccessPolicyIncludeGeo(country_code=country_code)

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
        :param identity_provider_id: The ID of your Github identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        :param name: The name of the organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#name ZeroTrustAccessPolicy#name}
        :param team: The name of the team. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#team ZeroTrustAccessPolicy#team}
        '''
        value = ZeroTrustAccessPolicyIncludeGithubOrganization(
            identity_provider_id=identity_provider_id, name=name, team=team
        )

        return typing.cast(None, jsii.invoke(self, "putGithubOrganization", [value]))

    @jsii.member(jsii_name="putGroup")
    def put_group(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created Access group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        value = ZeroTrustAccessPolicyIncludeGroup(id=id)

        return typing.cast(None, jsii.invoke(self, "putGroup", [value]))

    @jsii.member(jsii_name="putGsuite")
    def put_gsuite(
        self,
        *,
        email: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param email: The email of the Google Workspace group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email ZeroTrustAccessPolicy#email}
        :param identity_provider_id: The ID of your Google Workspace identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        value = ZeroTrustAccessPolicyIncludeGsuite(
            email=email, identity_provider_id=identity_provider_id
        )

        return typing.cast(None, jsii.invoke(self, "putGsuite", [value]))

    @jsii.member(jsii_name="putIp")
    def put_ip(self, *, ip: builtins.str) -> None:
        '''
        :param ip: An IPv4 or IPv6 CIDR block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ip ZeroTrustAccessPolicy#ip}
        '''
        value = ZeroTrustAccessPolicyIncludeIp(ip=ip)

        return typing.cast(None, jsii.invoke(self, "putIp", [value]))

    @jsii.member(jsii_name="putIpList")
    def put_ip_list(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created IP list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        value = ZeroTrustAccessPolicyIncludeIpListStruct(id=id)

        return typing.cast(None, jsii.invoke(self, "putIpList", [value]))

    @jsii.member(jsii_name="putLinkedAppToken")
    def put_linked_app_token(self, *, app_uid: builtins.str) -> None:
        '''
        :param app_uid: The ID of an Access OIDC SaaS application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#app_uid ZeroTrustAccessPolicy#app_uid}
        '''
        value = ZeroTrustAccessPolicyIncludeLinkedAppToken(app_uid=app_uid)

        return typing.cast(None, jsii.invoke(self, "putLinkedAppToken", [value]))

    @jsii.member(jsii_name="putLoginMethod")
    def put_login_method(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of an identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        value = ZeroTrustAccessPolicyIncludeLoginMethod(id=id)

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
        :param claim_name: The name of the OIDC claim. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#claim_name ZeroTrustAccessPolicy#claim_name}
        :param claim_value: The OIDC claim value to look for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#claim_value ZeroTrustAccessPolicy#claim_value}
        :param identity_provider_id: The ID of your OIDC identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        value = ZeroTrustAccessPolicyIncludeOidc(
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
        :param identity_provider_id: The ID of your Okta identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        :param name: The name of the Okta group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#name ZeroTrustAccessPolicy#name}
        '''
        value = ZeroTrustAccessPolicyIncludeOkta(
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
        :param attribute_name: The name of the SAML attribute. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#attribute_name ZeroTrustAccessPolicy#attribute_name}
        :param attribute_value: The SAML attribute value to look for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#attribute_value ZeroTrustAccessPolicy#attribute_value}
        :param identity_provider_id: The ID of your SAML identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        value = ZeroTrustAccessPolicyIncludeSaml(
            attribute_name=attribute_name,
            attribute_value=attribute_value,
            identity_provider_id=identity_provider_id,
        )

        return typing.cast(None, jsii.invoke(self, "putSaml", [value]))

    @jsii.member(jsii_name="putServiceToken")
    def put_service_token(self, *, token_id: builtins.str) -> None:
        '''
        :param token_id: The ID of a Service Token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#token_id ZeroTrustAccessPolicy#token_id}
        '''
        value = ZeroTrustAccessPolicyIncludeServiceToken(token_id=token_id)

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
    ) -> ZeroTrustAccessPolicyIncludeAnyValidServiceTokenOutputReference:
        return typing.cast(ZeroTrustAccessPolicyIncludeAnyValidServiceTokenOutputReference, jsii.get(self, "anyValidServiceToken"))

    @builtins.property
    @jsii.member(jsii_name="authContext")
    def auth_context(self) -> ZeroTrustAccessPolicyIncludeAuthContextOutputReference:
        return typing.cast(ZeroTrustAccessPolicyIncludeAuthContextOutputReference, jsii.get(self, "authContext"))

    @builtins.property
    @jsii.member(jsii_name="authMethod")
    def auth_method(self) -> ZeroTrustAccessPolicyIncludeAuthMethodOutputReference:
        return typing.cast(ZeroTrustAccessPolicyIncludeAuthMethodOutputReference, jsii.get(self, "authMethod"))

    @builtins.property
    @jsii.member(jsii_name="azureAd")
    def azure_ad(self) -> ZeroTrustAccessPolicyIncludeAzureAdOutputReference:
        return typing.cast(ZeroTrustAccessPolicyIncludeAzureAdOutputReference, jsii.get(self, "azureAd"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> ZeroTrustAccessPolicyIncludeCertificateOutputReference:
        return typing.cast(ZeroTrustAccessPolicyIncludeCertificateOutputReference, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(self) -> ZeroTrustAccessPolicyIncludeCommonNameOutputReference:
        return typing.cast(ZeroTrustAccessPolicyIncludeCommonNameOutputReference, jsii.get(self, "commonName"))

    @builtins.property
    @jsii.member(jsii_name="devicePosture")
    def device_posture(
        self,
    ) -> ZeroTrustAccessPolicyIncludeDevicePostureOutputReference:
        return typing.cast(ZeroTrustAccessPolicyIncludeDevicePostureOutputReference, jsii.get(self, "devicePosture"))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(self) -> ZeroTrustAccessPolicyIncludeEmailOutputReference:
        return typing.cast(ZeroTrustAccessPolicyIncludeEmailOutputReference, jsii.get(self, "email"))

    @builtins.property
    @jsii.member(jsii_name="emailDomain")
    def email_domain(self) -> ZeroTrustAccessPolicyIncludeEmailDomainOutputReference:
        return typing.cast(ZeroTrustAccessPolicyIncludeEmailDomainOutputReference, jsii.get(self, "emailDomain"))

    @builtins.property
    @jsii.member(jsii_name="emailList")
    def email_list(self) -> ZeroTrustAccessPolicyIncludeEmailListStructOutputReference:
        return typing.cast(ZeroTrustAccessPolicyIncludeEmailListStructOutputReference, jsii.get(self, "emailList"))

    @builtins.property
    @jsii.member(jsii_name="everyone")
    def everyone(self) -> ZeroTrustAccessPolicyIncludeEveryoneOutputReference:
        return typing.cast(ZeroTrustAccessPolicyIncludeEveryoneOutputReference, jsii.get(self, "everyone"))

    @builtins.property
    @jsii.member(jsii_name="externalEvaluation")
    def external_evaluation(
        self,
    ) -> ZeroTrustAccessPolicyIncludeExternalEvaluationOutputReference:
        return typing.cast(ZeroTrustAccessPolicyIncludeExternalEvaluationOutputReference, jsii.get(self, "externalEvaluation"))

    @builtins.property
    @jsii.member(jsii_name="geo")
    def geo(self) -> ZeroTrustAccessPolicyIncludeGeoOutputReference:
        return typing.cast(ZeroTrustAccessPolicyIncludeGeoOutputReference, jsii.get(self, "geo"))

    @builtins.property
    @jsii.member(jsii_name="githubOrganization")
    def github_organization(
        self,
    ) -> ZeroTrustAccessPolicyIncludeGithubOrganizationOutputReference:
        return typing.cast(ZeroTrustAccessPolicyIncludeGithubOrganizationOutputReference, jsii.get(self, "githubOrganization"))

    @builtins.property
    @jsii.member(jsii_name="group")
    def group(self) -> ZeroTrustAccessPolicyIncludeGroupOutputReference:
        return typing.cast(ZeroTrustAccessPolicyIncludeGroupOutputReference, jsii.get(self, "group"))

    @builtins.property
    @jsii.member(jsii_name="gsuite")
    def gsuite(self) -> ZeroTrustAccessPolicyIncludeGsuiteOutputReference:
        return typing.cast(ZeroTrustAccessPolicyIncludeGsuiteOutputReference, jsii.get(self, "gsuite"))

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> ZeroTrustAccessPolicyIncludeIpOutputReference:
        return typing.cast(ZeroTrustAccessPolicyIncludeIpOutputReference, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="ipList")
    def ip_list(self) -> ZeroTrustAccessPolicyIncludeIpListStructOutputReference:
        return typing.cast(ZeroTrustAccessPolicyIncludeIpListStructOutputReference, jsii.get(self, "ipList"))

    @builtins.property
    @jsii.member(jsii_name="linkedAppToken")
    def linked_app_token(
        self,
    ) -> ZeroTrustAccessPolicyIncludeLinkedAppTokenOutputReference:
        return typing.cast(ZeroTrustAccessPolicyIncludeLinkedAppTokenOutputReference, jsii.get(self, "linkedAppToken"))

    @builtins.property
    @jsii.member(jsii_name="loginMethod")
    def login_method(self) -> ZeroTrustAccessPolicyIncludeLoginMethodOutputReference:
        return typing.cast(ZeroTrustAccessPolicyIncludeLoginMethodOutputReference, jsii.get(self, "loginMethod"))

    @builtins.property
    @jsii.member(jsii_name="oidc")
    def oidc(self) -> ZeroTrustAccessPolicyIncludeOidcOutputReference:
        return typing.cast(ZeroTrustAccessPolicyIncludeOidcOutputReference, jsii.get(self, "oidc"))

    @builtins.property
    @jsii.member(jsii_name="okta")
    def okta(self) -> ZeroTrustAccessPolicyIncludeOktaOutputReference:
        return typing.cast(ZeroTrustAccessPolicyIncludeOktaOutputReference, jsii.get(self, "okta"))

    @builtins.property
    @jsii.member(jsii_name="saml")
    def saml(self) -> "ZeroTrustAccessPolicyIncludeSamlOutputReference":
        return typing.cast("ZeroTrustAccessPolicyIncludeSamlOutputReference", jsii.get(self, "saml"))

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(
        self,
    ) -> "ZeroTrustAccessPolicyIncludeServiceTokenOutputReference":
        return typing.cast("ZeroTrustAccessPolicyIncludeServiceTokenOutputReference", jsii.get(self, "serviceToken"))

    @builtins.property
    @jsii.member(jsii_name="anyValidServiceTokenInput")
    def any_valid_service_token_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeAnyValidServiceToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeAnyValidServiceToken]], jsii.get(self, "anyValidServiceTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="authContextInput")
    def auth_context_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeAuthContext]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeAuthContext]], jsii.get(self, "authContextInput"))

    @builtins.property
    @jsii.member(jsii_name="authMethodInput")
    def auth_method_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeAuthMethod]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeAuthMethod]], jsii.get(self, "authMethodInput"))

    @builtins.property
    @jsii.member(jsii_name="azureAdInput")
    def azure_ad_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeAzureAd]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeAzureAd]], jsii.get(self, "azureAdInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateInput")
    def certificate_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeCertificate]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeCertificate]], jsii.get(self, "certificateInput"))

    @builtins.property
    @jsii.member(jsii_name="commonNameInput")
    def common_name_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeCommonName]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeCommonName]], jsii.get(self, "commonNameInput"))

    @builtins.property
    @jsii.member(jsii_name="devicePostureInput")
    def device_posture_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeDevicePosture]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeDevicePosture]], jsii.get(self, "devicePostureInput"))

    @builtins.property
    @jsii.member(jsii_name="emailDomainInput")
    def email_domain_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeEmailDomain]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeEmailDomain]], jsii.get(self, "emailDomainInput"))

    @builtins.property
    @jsii.member(jsii_name="emailInput")
    def email_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeEmail]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeEmail]], jsii.get(self, "emailInput"))

    @builtins.property
    @jsii.member(jsii_name="emailListInput")
    def email_list_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeEmailListStruct]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeEmailListStruct]], jsii.get(self, "emailListInput"))

    @builtins.property
    @jsii.member(jsii_name="everyoneInput")
    def everyone_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeEveryone]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeEveryone]], jsii.get(self, "everyoneInput"))

    @builtins.property
    @jsii.member(jsii_name="externalEvaluationInput")
    def external_evaluation_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeExternalEvaluation]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeExternalEvaluation]], jsii.get(self, "externalEvaluationInput"))

    @builtins.property
    @jsii.member(jsii_name="geoInput")
    def geo_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeGeo]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeGeo]], jsii.get(self, "geoInput"))

    @builtins.property
    @jsii.member(jsii_name="githubOrganizationInput")
    def github_organization_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeGithubOrganization]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeGithubOrganization]], jsii.get(self, "githubOrganizationInput"))

    @builtins.property
    @jsii.member(jsii_name="groupInput")
    def group_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeGroup]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeGroup]], jsii.get(self, "groupInput"))

    @builtins.property
    @jsii.member(jsii_name="gsuiteInput")
    def gsuite_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeGsuite]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeGsuite]], jsii.get(self, "gsuiteInput"))

    @builtins.property
    @jsii.member(jsii_name="ipInput")
    def ip_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeIp]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeIp]], jsii.get(self, "ipInput"))

    @builtins.property
    @jsii.member(jsii_name="ipListInput")
    def ip_list_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeIpListStruct]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeIpListStruct]], jsii.get(self, "ipListInput"))

    @builtins.property
    @jsii.member(jsii_name="linkedAppTokenInput")
    def linked_app_token_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeLinkedAppToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeLinkedAppToken]], jsii.get(self, "linkedAppTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="loginMethodInput")
    def login_method_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeLoginMethod]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeLoginMethod]], jsii.get(self, "loginMethodInput"))

    @builtins.property
    @jsii.member(jsii_name="oidcInput")
    def oidc_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeOidc]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeOidc]], jsii.get(self, "oidcInput"))

    @builtins.property
    @jsii.member(jsii_name="oktaInput")
    def okta_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeOkta]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeOkta]], jsii.get(self, "oktaInput"))

    @builtins.property
    @jsii.member(jsii_name="samlInput")
    def saml_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustAccessPolicyIncludeSaml"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustAccessPolicyIncludeSaml"]], jsii.get(self, "samlInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceTokenInput")
    def service_token_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustAccessPolicyIncludeServiceToken"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustAccessPolicyIncludeServiceToken"]], jsii.get(self, "serviceTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyInclude]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyInclude]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyInclude]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a5de837a78ad9109022b4feec750fe1f1c93f15069890759bc165b48112d7e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeSaml",
    jsii_struct_bases=[],
    name_mapping={
        "attribute_name": "attributeName",
        "attribute_value": "attributeValue",
        "identity_provider_id": "identityProviderId",
    },
)
class ZeroTrustAccessPolicyIncludeSaml:
    def __init__(
        self,
        *,
        attribute_name: builtins.str,
        attribute_value: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param attribute_name: The name of the SAML attribute. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#attribute_name ZeroTrustAccessPolicy#attribute_name}
        :param attribute_value: The SAML attribute value to look for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#attribute_value ZeroTrustAccessPolicy#attribute_value}
        :param identity_provider_id: The ID of your SAML identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2cfbb42f861777f7b70640ef307bf6e10ff48843c019815300af6cf6fd84285)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#attribute_name ZeroTrustAccessPolicy#attribute_name}
        '''
        result = self._values.get("attribute_name")
        assert result is not None, "Required property 'attribute_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attribute_value(self) -> builtins.str:
        '''The SAML attribute value to look for.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#attribute_value ZeroTrustAccessPolicy#attribute_value}
        '''
        result = self._values.get("attribute_value")
        assert result is not None, "Required property 'attribute_value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your SAML identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyIncludeSaml(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyIncludeSamlOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeSamlOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8d4d834aca93052ab47db4a2d54bbeb5a6dc6411e11c53c7701e881ced50ad34)
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
            type_hints = typing.get_type_hints(_typecheckingstub__151696e5824ee390fdcb4f23eabf8598f7dfd323e645ef86f5d0c2abd1e238e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attributeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="attributeValue")
    def attribute_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "attributeValue"))

    @attribute_value.setter
    def attribute_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d0a9f55b1e45b8e70507bef6728f94417b16d018cdc22ed4d666233172fa265)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attributeValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b0dcc6b0a719a2974c96478ecbe10f80530ca042a67ebce71a5f97080385667)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeSaml]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeSaml]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeSaml]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91f5ec3b9d8ca36fb847c34afd7e138d092e675a3e554428837ed0f06ccd5750)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeServiceToken",
    jsii_struct_bases=[],
    name_mapping={"token_id": "tokenId"},
)
class ZeroTrustAccessPolicyIncludeServiceToken:
    def __init__(self, *, token_id: builtins.str) -> None:
        '''
        :param token_id: The ID of a Service Token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#token_id ZeroTrustAccessPolicy#token_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a477d5833b4bf9c40e3aa4e1f37e260270a2cdca03944d5d53892b382ffa53e5)
            check_type(argname="argument token_id", value=token_id, expected_type=type_hints["token_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "token_id": token_id,
        }

    @builtins.property
    def token_id(self) -> builtins.str:
        '''The ID of a Service Token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#token_id ZeroTrustAccessPolicy#token_id}
        '''
        result = self._values.get("token_id")
        assert result is not None, "Required property 'token_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyIncludeServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyIncludeServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyIncludeServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d1e22f9c6d2ef171eb4bab405fd9db42cbabda6bf7148e0fe87fc78b40e8f9f2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5b0e85d36b21a3860fe6d4c23db21e2c587396c6cbfd5e9ee9ff7858435d77ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeServiceToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeServiceToken]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeServiceToken]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b8cc9cfb300a458588a7da5cd44849a18180e6da5a7b82cf149de9245a64f87)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequire",
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
class ZeroTrustAccessPolicyRequire:
    def __init__(
        self,
        *,
        any_valid_service_token: typing.Optional[typing.Union["ZeroTrustAccessPolicyRequireAnyValidServiceToken", typing.Dict[builtins.str, typing.Any]]] = None,
        auth_context: typing.Optional[typing.Union["ZeroTrustAccessPolicyRequireAuthContext", typing.Dict[builtins.str, typing.Any]]] = None,
        auth_method: typing.Optional[typing.Union["ZeroTrustAccessPolicyRequireAuthMethod", typing.Dict[builtins.str, typing.Any]]] = None,
        azure_ad: typing.Optional[typing.Union["ZeroTrustAccessPolicyRequireAzureAd", typing.Dict[builtins.str, typing.Any]]] = None,
        certificate: typing.Optional[typing.Union["ZeroTrustAccessPolicyRequireCertificate", typing.Dict[builtins.str, typing.Any]]] = None,
        common_name: typing.Optional[typing.Union["ZeroTrustAccessPolicyRequireCommonName", typing.Dict[builtins.str, typing.Any]]] = None,
        device_posture: typing.Optional[typing.Union["ZeroTrustAccessPolicyRequireDevicePosture", typing.Dict[builtins.str, typing.Any]]] = None,
        email: typing.Optional[typing.Union["ZeroTrustAccessPolicyRequireEmail", typing.Dict[builtins.str, typing.Any]]] = None,
        email_domain: typing.Optional[typing.Union["ZeroTrustAccessPolicyRequireEmailDomain", typing.Dict[builtins.str, typing.Any]]] = None,
        email_list: typing.Optional[typing.Union["ZeroTrustAccessPolicyRequireEmailListStruct", typing.Dict[builtins.str, typing.Any]]] = None,
        everyone: typing.Optional[typing.Union["ZeroTrustAccessPolicyRequireEveryone", typing.Dict[builtins.str, typing.Any]]] = None,
        external_evaluation: typing.Optional[typing.Union["ZeroTrustAccessPolicyRequireExternalEvaluation", typing.Dict[builtins.str, typing.Any]]] = None,
        geo: typing.Optional[typing.Union["ZeroTrustAccessPolicyRequireGeo", typing.Dict[builtins.str, typing.Any]]] = None,
        github_organization: typing.Optional[typing.Union["ZeroTrustAccessPolicyRequireGithubOrganization", typing.Dict[builtins.str, typing.Any]]] = None,
        group: typing.Optional[typing.Union["ZeroTrustAccessPolicyRequireGroup", typing.Dict[builtins.str, typing.Any]]] = None,
        gsuite: typing.Optional[typing.Union["ZeroTrustAccessPolicyRequireGsuite", typing.Dict[builtins.str, typing.Any]]] = None,
        ip: typing.Optional[typing.Union["ZeroTrustAccessPolicyRequireIp", typing.Dict[builtins.str, typing.Any]]] = None,
        ip_list: typing.Optional[typing.Union["ZeroTrustAccessPolicyRequireIpListStruct", typing.Dict[builtins.str, typing.Any]]] = None,
        linked_app_token: typing.Optional[typing.Union["ZeroTrustAccessPolicyRequireLinkedAppToken", typing.Dict[builtins.str, typing.Any]]] = None,
        login_method: typing.Optional[typing.Union["ZeroTrustAccessPolicyRequireLoginMethod", typing.Dict[builtins.str, typing.Any]]] = None,
        oidc: typing.Optional[typing.Union["ZeroTrustAccessPolicyRequireOidc", typing.Dict[builtins.str, typing.Any]]] = None,
        okta: typing.Optional[typing.Union["ZeroTrustAccessPolicyRequireOkta", typing.Dict[builtins.str, typing.Any]]] = None,
        saml: typing.Optional[typing.Union["ZeroTrustAccessPolicyRequireSaml", typing.Dict[builtins.str, typing.Any]]] = None,
        service_token: typing.Optional[typing.Union["ZeroTrustAccessPolicyRequireServiceToken", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param any_valid_service_token: An empty object which matches on all service tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#any_valid_service_token ZeroTrustAccessPolicy#any_valid_service_token}
        :param auth_context: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#auth_context ZeroTrustAccessPolicy#auth_context}.
        :param auth_method: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#auth_method ZeroTrustAccessPolicy#auth_method}.
        :param azure_ad: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#azure_ad ZeroTrustAccessPolicy#azure_ad}.
        :param certificate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#certificate ZeroTrustAccessPolicy#certificate}.
        :param common_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#common_name ZeroTrustAccessPolicy#common_name}.
        :param device_posture: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#device_posture ZeroTrustAccessPolicy#device_posture}.
        :param email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email ZeroTrustAccessPolicy#email}.
        :param email_domain: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email_domain ZeroTrustAccessPolicy#email_domain}.
        :param email_list: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email_list ZeroTrustAccessPolicy#email_list}.
        :param everyone: An empty object which matches on all users. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#everyone ZeroTrustAccessPolicy#everyone}
        :param external_evaluation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#external_evaluation ZeroTrustAccessPolicy#external_evaluation}.
        :param geo: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#geo ZeroTrustAccessPolicy#geo}.
        :param github_organization: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#github_organization ZeroTrustAccessPolicy#github_organization}.
        :param group: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#group ZeroTrustAccessPolicy#group}.
        :param gsuite: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#gsuite ZeroTrustAccessPolicy#gsuite}.
        :param ip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ip ZeroTrustAccessPolicy#ip}.
        :param ip_list: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ip_list ZeroTrustAccessPolicy#ip_list}.
        :param linked_app_token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#linked_app_token ZeroTrustAccessPolicy#linked_app_token}.
        :param login_method: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#login_method ZeroTrustAccessPolicy#login_method}.
        :param oidc: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#oidc ZeroTrustAccessPolicy#oidc}.
        :param okta: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#okta ZeroTrustAccessPolicy#okta}.
        :param saml: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#saml ZeroTrustAccessPolicy#saml}.
        :param service_token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#service_token ZeroTrustAccessPolicy#service_token}.
        '''
        if isinstance(any_valid_service_token, dict):
            any_valid_service_token = ZeroTrustAccessPolicyRequireAnyValidServiceToken(**any_valid_service_token)
        if isinstance(auth_context, dict):
            auth_context = ZeroTrustAccessPolicyRequireAuthContext(**auth_context)
        if isinstance(auth_method, dict):
            auth_method = ZeroTrustAccessPolicyRequireAuthMethod(**auth_method)
        if isinstance(azure_ad, dict):
            azure_ad = ZeroTrustAccessPolicyRequireAzureAd(**azure_ad)
        if isinstance(certificate, dict):
            certificate = ZeroTrustAccessPolicyRequireCertificate(**certificate)
        if isinstance(common_name, dict):
            common_name = ZeroTrustAccessPolicyRequireCommonName(**common_name)
        if isinstance(device_posture, dict):
            device_posture = ZeroTrustAccessPolicyRequireDevicePosture(**device_posture)
        if isinstance(email, dict):
            email = ZeroTrustAccessPolicyRequireEmail(**email)
        if isinstance(email_domain, dict):
            email_domain = ZeroTrustAccessPolicyRequireEmailDomain(**email_domain)
        if isinstance(email_list, dict):
            email_list = ZeroTrustAccessPolicyRequireEmailListStruct(**email_list)
        if isinstance(everyone, dict):
            everyone = ZeroTrustAccessPolicyRequireEveryone(**everyone)
        if isinstance(external_evaluation, dict):
            external_evaluation = ZeroTrustAccessPolicyRequireExternalEvaluation(**external_evaluation)
        if isinstance(geo, dict):
            geo = ZeroTrustAccessPolicyRequireGeo(**geo)
        if isinstance(github_organization, dict):
            github_organization = ZeroTrustAccessPolicyRequireGithubOrganization(**github_organization)
        if isinstance(group, dict):
            group = ZeroTrustAccessPolicyRequireGroup(**group)
        if isinstance(gsuite, dict):
            gsuite = ZeroTrustAccessPolicyRequireGsuite(**gsuite)
        if isinstance(ip, dict):
            ip = ZeroTrustAccessPolicyRequireIp(**ip)
        if isinstance(ip_list, dict):
            ip_list = ZeroTrustAccessPolicyRequireIpListStruct(**ip_list)
        if isinstance(linked_app_token, dict):
            linked_app_token = ZeroTrustAccessPolicyRequireLinkedAppToken(**linked_app_token)
        if isinstance(login_method, dict):
            login_method = ZeroTrustAccessPolicyRequireLoginMethod(**login_method)
        if isinstance(oidc, dict):
            oidc = ZeroTrustAccessPolicyRequireOidc(**oidc)
        if isinstance(okta, dict):
            okta = ZeroTrustAccessPolicyRequireOkta(**okta)
        if isinstance(saml, dict):
            saml = ZeroTrustAccessPolicyRequireSaml(**saml)
        if isinstance(service_token, dict):
            service_token = ZeroTrustAccessPolicyRequireServiceToken(**service_token)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58976fcac7d8164c4ed31294320307b3fff1b949a56e45312971fcebaf316e9d)
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
    ) -> typing.Optional["ZeroTrustAccessPolicyRequireAnyValidServiceToken"]:
        '''An empty object which matches on all service tokens.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#any_valid_service_token ZeroTrustAccessPolicy#any_valid_service_token}
        '''
        result = self._values.get("any_valid_service_token")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyRequireAnyValidServiceToken"], result)

    @builtins.property
    def auth_context(
        self,
    ) -> typing.Optional["ZeroTrustAccessPolicyRequireAuthContext"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#auth_context ZeroTrustAccessPolicy#auth_context}.'''
        result = self._values.get("auth_context")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyRequireAuthContext"], result)

    @builtins.property
    def auth_method(self) -> typing.Optional["ZeroTrustAccessPolicyRequireAuthMethod"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#auth_method ZeroTrustAccessPolicy#auth_method}.'''
        result = self._values.get("auth_method")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyRequireAuthMethod"], result)

    @builtins.property
    def azure_ad(self) -> typing.Optional["ZeroTrustAccessPolicyRequireAzureAd"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#azure_ad ZeroTrustAccessPolicy#azure_ad}.'''
        result = self._values.get("azure_ad")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyRequireAzureAd"], result)

    @builtins.property
    def certificate(self) -> typing.Optional["ZeroTrustAccessPolicyRequireCertificate"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#certificate ZeroTrustAccessPolicy#certificate}.'''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyRequireCertificate"], result)

    @builtins.property
    def common_name(self) -> typing.Optional["ZeroTrustAccessPolicyRequireCommonName"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#common_name ZeroTrustAccessPolicy#common_name}.'''
        result = self._values.get("common_name")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyRequireCommonName"], result)

    @builtins.property
    def device_posture(
        self,
    ) -> typing.Optional["ZeroTrustAccessPolicyRequireDevicePosture"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#device_posture ZeroTrustAccessPolicy#device_posture}.'''
        result = self._values.get("device_posture")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyRequireDevicePosture"], result)

    @builtins.property
    def email(self) -> typing.Optional["ZeroTrustAccessPolicyRequireEmail"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email ZeroTrustAccessPolicy#email}.'''
        result = self._values.get("email")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyRequireEmail"], result)

    @builtins.property
    def email_domain(
        self,
    ) -> typing.Optional["ZeroTrustAccessPolicyRequireEmailDomain"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email_domain ZeroTrustAccessPolicy#email_domain}.'''
        result = self._values.get("email_domain")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyRequireEmailDomain"], result)

    @builtins.property
    def email_list(
        self,
    ) -> typing.Optional["ZeroTrustAccessPolicyRequireEmailListStruct"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email_list ZeroTrustAccessPolicy#email_list}.'''
        result = self._values.get("email_list")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyRequireEmailListStruct"], result)

    @builtins.property
    def everyone(self) -> typing.Optional["ZeroTrustAccessPolicyRequireEveryone"]:
        '''An empty object which matches on all users.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#everyone ZeroTrustAccessPolicy#everyone}
        '''
        result = self._values.get("everyone")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyRequireEveryone"], result)

    @builtins.property
    def external_evaluation(
        self,
    ) -> typing.Optional["ZeroTrustAccessPolicyRequireExternalEvaluation"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#external_evaluation ZeroTrustAccessPolicy#external_evaluation}.'''
        result = self._values.get("external_evaluation")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyRequireExternalEvaluation"], result)

    @builtins.property
    def geo(self) -> typing.Optional["ZeroTrustAccessPolicyRequireGeo"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#geo ZeroTrustAccessPolicy#geo}.'''
        result = self._values.get("geo")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyRequireGeo"], result)

    @builtins.property
    def github_organization(
        self,
    ) -> typing.Optional["ZeroTrustAccessPolicyRequireGithubOrganization"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#github_organization ZeroTrustAccessPolicy#github_organization}.'''
        result = self._values.get("github_organization")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyRequireGithubOrganization"], result)

    @builtins.property
    def group(self) -> typing.Optional["ZeroTrustAccessPolicyRequireGroup"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#group ZeroTrustAccessPolicy#group}.'''
        result = self._values.get("group")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyRequireGroup"], result)

    @builtins.property
    def gsuite(self) -> typing.Optional["ZeroTrustAccessPolicyRequireGsuite"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#gsuite ZeroTrustAccessPolicy#gsuite}.'''
        result = self._values.get("gsuite")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyRequireGsuite"], result)

    @builtins.property
    def ip(self) -> typing.Optional["ZeroTrustAccessPolicyRequireIp"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ip ZeroTrustAccessPolicy#ip}.'''
        result = self._values.get("ip")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyRequireIp"], result)

    @builtins.property
    def ip_list(self) -> typing.Optional["ZeroTrustAccessPolicyRequireIpListStruct"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ip_list ZeroTrustAccessPolicy#ip_list}.'''
        result = self._values.get("ip_list")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyRequireIpListStruct"], result)

    @builtins.property
    def linked_app_token(
        self,
    ) -> typing.Optional["ZeroTrustAccessPolicyRequireLinkedAppToken"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#linked_app_token ZeroTrustAccessPolicy#linked_app_token}.'''
        result = self._values.get("linked_app_token")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyRequireLinkedAppToken"], result)

    @builtins.property
    def login_method(
        self,
    ) -> typing.Optional["ZeroTrustAccessPolicyRequireLoginMethod"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#login_method ZeroTrustAccessPolicy#login_method}.'''
        result = self._values.get("login_method")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyRequireLoginMethod"], result)

    @builtins.property
    def oidc(self) -> typing.Optional["ZeroTrustAccessPolicyRequireOidc"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#oidc ZeroTrustAccessPolicy#oidc}.'''
        result = self._values.get("oidc")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyRequireOidc"], result)

    @builtins.property
    def okta(self) -> typing.Optional["ZeroTrustAccessPolicyRequireOkta"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#okta ZeroTrustAccessPolicy#okta}.'''
        result = self._values.get("okta")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyRequireOkta"], result)

    @builtins.property
    def saml(self) -> typing.Optional["ZeroTrustAccessPolicyRequireSaml"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#saml ZeroTrustAccessPolicy#saml}.'''
        result = self._values.get("saml")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyRequireSaml"], result)

    @builtins.property
    def service_token(
        self,
    ) -> typing.Optional["ZeroTrustAccessPolicyRequireServiceToken"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#service_token ZeroTrustAccessPolicy#service_token}.'''
        result = self._values.get("service_token")
        return typing.cast(typing.Optional["ZeroTrustAccessPolicyRequireServiceToken"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyRequire(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireAnyValidServiceToken",
    jsii_struct_bases=[],
    name_mapping={},
)
class ZeroTrustAccessPolicyRequireAnyValidServiceToken:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyRequireAnyValidServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyRequireAnyValidServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireAnyValidServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1131041e506ba91bc7a2f4787797d49cb19bbe0dfab3724e1e18d18f67cba6ee)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireAnyValidServiceToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireAnyValidServiceToken]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireAnyValidServiceToken]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1b28565387ffdf20e09da911bb7f80d11dc9151db98b0a5dbc7332c77012ddc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireAuthContext",
    jsii_struct_bases=[],
    name_mapping={
        "ac_id": "acId",
        "id": "id",
        "identity_provider_id": "identityProviderId",
    },
)
class ZeroTrustAccessPolicyRequireAuthContext:
    def __init__(
        self,
        *,
        ac_id: builtins.str,
        id: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param ac_id: The ACID of an Authentication context. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ac_id ZeroTrustAccessPolicy#ac_id}
        :param id: The ID of an Authentication context. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider_id: The ID of your Azure identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f9e2bf589c96f50c300e14cb1022250d685a2e4266403c6b00b7670e11b5375)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ac_id ZeroTrustAccessPolicy#ac_id}
        '''
        result = self._values.get("ac_id")
        assert result is not None, "Required property 'ac_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of an Authentication context.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your Azure identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyRequireAuthContext(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyRequireAuthContextOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireAuthContextOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__890f96ded9d41fc3bb5835a05958eebde4321d241c78eaac24f85e0b0f4805ec)
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
            type_hints = typing.get_type_hints(_typecheckingstub__69602fe74fc46551e5ee3c97a0fbdacb97303e560537f55dd4efd167f619580e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "acId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__161cb4cd3c7170de61f48bdd5a691061cf2461894d8460cb97ed6aac75cb3468)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfd02a0aceb9ba37258894ca35fac9f29c6539845c1bcfcd7c41de8c3f38bf8c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireAuthContext]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireAuthContext]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireAuthContext]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3881b3ecc14d9098a6a753d8ef9d3460e034cef9dd5f63cbbe3816a23fd0b5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireAuthMethod",
    jsii_struct_bases=[],
    name_mapping={"auth_method": "authMethod"},
)
class ZeroTrustAccessPolicyRequireAuthMethod:
    def __init__(self, *, auth_method: builtins.str) -> None:
        '''
        :param auth_method: The type of authentication method https://datatracker.ietf.org/doc/html/rfc8176#section-2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#auth_method ZeroTrustAccessPolicy#auth_method}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6180c715a0bd35181fbcd823425c718be3d526c287bd9414c30cd0affa11c5d)
            check_type(argname="argument auth_method", value=auth_method, expected_type=type_hints["auth_method"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "auth_method": auth_method,
        }

    @builtins.property
    def auth_method(self) -> builtins.str:
        '''The type of authentication method https://datatracker.ietf.org/doc/html/rfc8176#section-2.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#auth_method ZeroTrustAccessPolicy#auth_method}
        '''
        result = self._values.get("auth_method")
        assert result is not None, "Required property 'auth_method' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyRequireAuthMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyRequireAuthMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireAuthMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c4f1c25764057793364f8294a23f6e702e8e2122b95003e755f04c8703e1d2de)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4fc94e6545c58b99606f93e02c346ce0bb64c6e6777d93378f10e387d827a6c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authMethod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireAuthMethod]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireAuthMethod]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireAuthMethod]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4f421b665b43b234c9a91f03cd7c1544e8d85871df1145fd2bdb44cf1947f3b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireAzureAd",
    jsii_struct_bases=[],
    name_mapping={"id": "id", "identity_provider_id": "identityProviderId"},
)
class ZeroTrustAccessPolicyRequireAzureAd:
    def __init__(self, *, id: builtins.str, identity_provider_id: builtins.str) -> None:
        '''
        :param id: The ID of an Azure group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider_id: The ID of your Azure identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02b0f9933d5cb10f1552baf20f69b6fa1e1b829bf9457ed8e9cd30def2d47ae2)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
            "identity_provider_id": identity_provider_id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of an Azure group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your Azure identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyRequireAzureAd(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyRequireAzureAdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireAzureAdOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__70734c49ace01c4a72cb92b2bddc6142e4b5fc4cebde91ab40671ca17b6f35e2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6b0a9a873ed0f78cd22f347e2f4d939697e49be4e414b96ba093dff16a3eac1a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a718d94c2f11a8b27d5fb92eceb7bbd1ca6b231a91a18321e9f7105723552d14)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireAzureAd]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireAzureAd]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireAzureAd]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3160ec7cadac71220b82bdcec5934e0a6b87f8a4394c88ba3221c02a05538371)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireCertificate",
    jsii_struct_bases=[],
    name_mapping={},
)
class ZeroTrustAccessPolicyRequireCertificate:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyRequireCertificate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyRequireCertificateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireCertificateOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__822eb05e398c48b5908254c612f34213e26fe40739b12ead04ecb9f3f98ae794)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireCertificate]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireCertificate]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireCertificate]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2814c7faeb30667af2e690a65138fe47bb1fad91ee0752d7872bcce951287c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireCommonName",
    jsii_struct_bases=[],
    name_mapping={"common_name": "commonName"},
)
class ZeroTrustAccessPolicyRequireCommonName:
    def __init__(self, *, common_name: builtins.str) -> None:
        '''
        :param common_name: The common name to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#common_name ZeroTrustAccessPolicy#common_name}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c8253f767a8e03811f3bcfbc509a656d67d488c3714d48f0973ea0029fb35f4)
            check_type(argname="argument common_name", value=common_name, expected_type=type_hints["common_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "common_name": common_name,
        }

    @builtins.property
    def common_name(self) -> builtins.str:
        '''The common name to match.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#common_name ZeroTrustAccessPolicy#common_name}
        '''
        result = self._values.get("common_name")
        assert result is not None, "Required property 'common_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyRequireCommonName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyRequireCommonNameOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireCommonNameOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b3346151543bc880e07fb5ea4711f4e2b43515cdc4f0a9f042705c86bc109319)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fbd59fd81aa7dc6b3fc3eedccfb4781c51e221e04dba2fcf908e973eaed9b19c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "commonName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireCommonName]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireCommonName]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireCommonName]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4cb4e66f97c0ad33dbdf62ca033d1e62dcf6f8b6f0c19391e855e11fa8843275)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireDevicePosture",
    jsii_struct_bases=[],
    name_mapping={"integration_uid": "integrationUid"},
)
class ZeroTrustAccessPolicyRequireDevicePosture:
    def __init__(self, *, integration_uid: builtins.str) -> None:
        '''
        :param integration_uid: The ID of a device posture integration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#integration_uid ZeroTrustAccessPolicy#integration_uid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61ba650eb1c758c108abbf32356c62101f0561f8bc3ad2e1cfe6e6c05c984ce0)
            check_type(argname="argument integration_uid", value=integration_uid, expected_type=type_hints["integration_uid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "integration_uid": integration_uid,
        }

    @builtins.property
    def integration_uid(self) -> builtins.str:
        '''The ID of a device posture integration.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#integration_uid ZeroTrustAccessPolicy#integration_uid}
        '''
        result = self._values.get("integration_uid")
        assert result is not None, "Required property 'integration_uid' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyRequireDevicePosture(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyRequireDevicePostureOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireDevicePostureOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3d03f83b87b352f8aacd3b38779057a3164f0d4453403e71aba31ad8eca58af1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7cfdbd1fec8d5120d383d3522706f2487d9a5bedda05071cf86e008e3ec6aec8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "integrationUid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireDevicePosture]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireDevicePosture]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireDevicePosture]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5adf2391d8ab7851a42c324e650c7d834f8c60caa335dc4699c208ac1538e6ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireEmail",
    jsii_struct_bases=[],
    name_mapping={"email": "email"},
)
class ZeroTrustAccessPolicyRequireEmail:
    def __init__(self, *, email: builtins.str) -> None:
        '''
        :param email: The email of the user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email ZeroTrustAccessPolicy#email}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0d6b344a6789e0f3b57acdbe17de58d4d79101c792fb93caf4e1d06a01eb4c8)
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "email": email,
        }

    @builtins.property
    def email(self) -> builtins.str:
        '''The email of the user.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email ZeroTrustAccessPolicy#email}
        '''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyRequireEmail(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireEmailDomain",
    jsii_struct_bases=[],
    name_mapping={"domain": "domain"},
)
class ZeroTrustAccessPolicyRequireEmailDomain:
    def __init__(self, *, domain: builtins.str) -> None:
        '''
        :param domain: The email domain to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#domain ZeroTrustAccessPolicy#domain}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e83296ac4ec0e844e09253cb9c403bad993ea920c6421c65d6b1fa5a4b986677)
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain": domain,
        }

    @builtins.property
    def domain(self) -> builtins.str:
        '''The email domain to match.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#domain ZeroTrustAccessPolicy#domain}
        '''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyRequireEmailDomain(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyRequireEmailDomainOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireEmailDomainOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e693cac2ce604c4d9139d367d0873685103a36afeaea7ceb387e0dde7b12de82)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d1f705bfe1a7e6b18f869c07d5d933d1caf7a74ac998cc2239acecb358695ff6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "domain", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireEmailDomain]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireEmailDomain]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireEmailDomain]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1fc4f38c377842236815fefae64852e648b3f9620ca359a89062fa794437bae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireEmailListStruct",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class ZeroTrustAccessPolicyRequireEmailListStruct:
    def __init__(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created email list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3c012a4dd616da3731d45965bf9cb44f1cea8e3c8f5d1c162e1d23712faad3d)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of a previously created email list.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id}

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
        return "ZeroTrustAccessPolicyRequireEmailListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyRequireEmailListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireEmailListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fd02fedb59332fad528d6b7812deb2f4c3fb72130c94d4f4b310b57642181e91)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3f6b87640a27662869d926968c18b8ccac355eb71e7c9321e45ef176915f24f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireEmailListStruct]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireEmailListStruct]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireEmailListStruct]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac6f322aeae6998c1d5f0080a7b803a71ff9822e283d42495f00b9b4f366eac5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustAccessPolicyRequireEmailOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireEmailOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c51d9b1fb4d733abb39d64b3194cfd2758a80ae4eb40a14268122473d76ad1fb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b0989635a7502d57e7de5d4bc13c95cab05147edc907d1f02f0de6c11644c535)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "email", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireEmail]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireEmail]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireEmail]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24f4700bbaaef32a483d4d7ea9bf311b0f4ee63de430e2392d9d6e9770f53666)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireEveryone",
    jsii_struct_bases=[],
    name_mapping={},
)
class ZeroTrustAccessPolicyRequireEveryone:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyRequireEveryone(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyRequireEveryoneOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireEveryoneOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ac6d527399aabb5fe73a2613991c064c63a8a1f8c18a062b09844b2d880aea0d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireEveryone]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireEveryone]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireEveryone]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9846f128cca04be3d543ab91aabcfbaa9d9c2b95d20552f3726570f50df55fa9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireExternalEvaluation",
    jsii_struct_bases=[],
    name_mapping={"evaluate_url": "evaluateUrl", "keys_url": "keysUrl"},
)
class ZeroTrustAccessPolicyRequireExternalEvaluation:
    def __init__(self, *, evaluate_url: builtins.str, keys_url: builtins.str) -> None:
        '''
        :param evaluate_url: The API endpoint containing your business logic. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#evaluate_url ZeroTrustAccessPolicy#evaluate_url}
        :param keys_url: The API endpoint containing the key that Access uses to verify that the response came from your API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#keys_url ZeroTrustAccessPolicy#keys_url}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca489b5c8d70b7fd12691784b5e28c5ee9ffdfbec65768ed578bdfdcda7459c8)
            check_type(argname="argument evaluate_url", value=evaluate_url, expected_type=type_hints["evaluate_url"])
            check_type(argname="argument keys_url", value=keys_url, expected_type=type_hints["keys_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "evaluate_url": evaluate_url,
            "keys_url": keys_url,
        }

    @builtins.property
    def evaluate_url(self) -> builtins.str:
        '''The API endpoint containing your business logic.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#evaluate_url ZeroTrustAccessPolicy#evaluate_url}
        '''
        result = self._values.get("evaluate_url")
        assert result is not None, "Required property 'evaluate_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def keys_url(self) -> builtins.str:
        '''The API endpoint containing the key that Access uses to verify that the response came from your API.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#keys_url ZeroTrustAccessPolicy#keys_url}
        '''
        result = self._values.get("keys_url")
        assert result is not None, "Required property 'keys_url' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyRequireExternalEvaluation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyRequireExternalEvaluationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireExternalEvaluationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__92ddf25f04fb09aa2782e036dcc0f6affa237e0db425c41b8b92a8164bbdca39)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d0741f8074543787f8c4bf90211bb988efe81ea1500baa6f1fd85006d61f5ebe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "evaluateUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keysUrl")
    def keys_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keysUrl"))

    @keys_url.setter
    def keys_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72a8ab5caa5fc91bd96da810518ffe482225716321c8da3f9558f538a169cf5a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keysUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireExternalEvaluation]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireExternalEvaluation]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireExternalEvaluation]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2be2364117b00f01b16bd5e10098c971b83fb8e81c72eba10bc2e8d1ef5780d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireGeo",
    jsii_struct_bases=[],
    name_mapping={"country_code": "countryCode"},
)
class ZeroTrustAccessPolicyRequireGeo:
    def __init__(self, *, country_code: builtins.str) -> None:
        '''
        :param country_code: The country code that should be matched. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#country_code ZeroTrustAccessPolicy#country_code}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06fb394044a3d18803c0ab114b1e817b93edd9d905adaa0f25f621990e22d5b9)
            check_type(argname="argument country_code", value=country_code, expected_type=type_hints["country_code"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "country_code": country_code,
        }

    @builtins.property
    def country_code(self) -> builtins.str:
        '''The country code that should be matched.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#country_code ZeroTrustAccessPolicy#country_code}
        '''
        result = self._values.get("country_code")
        assert result is not None, "Required property 'country_code' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyRequireGeo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyRequireGeoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireGeoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__eceb9f194e4034e29acf4a14c242b772995b5b928d027766de135fd5fd4e20be)
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
            type_hints = typing.get_type_hints(_typecheckingstub__44e435831024a1a82abd4fd23e041d4244221f0134285ce3f27cf164d027071e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "countryCode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireGeo]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireGeo]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireGeo]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__037ed65890808d9032a6772b579ca7dea7e553d6372a18391576c0bdcd0e86d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireGithubOrganization",
    jsii_struct_bases=[],
    name_mapping={
        "identity_provider_id": "identityProviderId",
        "name": "name",
        "team": "team",
    },
)
class ZeroTrustAccessPolicyRequireGithubOrganization:
    def __init__(
        self,
        *,
        identity_provider_id: builtins.str,
        name: builtins.str,
        team: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param identity_provider_id: The ID of your Github identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        :param name: The name of the organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#name ZeroTrustAccessPolicy#name}
        :param team: The name of the team. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#team ZeroTrustAccessPolicy#team}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ce3812a2103dda2a17ecdb274fb89dc52741c301b03071903cf123cc33d3401)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the organization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#name ZeroTrustAccessPolicy#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def team(self) -> typing.Optional[builtins.str]:
        '''The name of the team.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#team ZeroTrustAccessPolicy#team}
        '''
        result = self._values.get("team")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyRequireGithubOrganization(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyRequireGithubOrganizationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireGithubOrganizationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0c83c6be35ae10eb0a77b61831298810c6b42d148d5a302533f3b0221565bec8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8677266858d0d1c0ae0e6886710fb476dac8a37ce934bcc0b9924624260da0d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5126c0b6e8ea67d283b61e77fe18e89ba86fba657a24ebc72a06018265966ec8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="team")
    def team(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "team"))

    @team.setter
    def team(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fae1c3f771e2978086226a1853fdfdd318b0e4d015148f3fe96474fc8fc71032)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "team", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireGithubOrganization]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireGithubOrganization]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireGithubOrganization]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__606dda372431751075e6156fdcfc73f24b5986b74b4b82eb3fc6e698905fb8b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireGroup",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class ZeroTrustAccessPolicyRequireGroup:
    def __init__(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created Access group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c98c2ee705b69842ad1b534dd50413eba4cb27f9e8bc0f5f7f340a6b1ced909)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of a previously created Access group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id}

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
        return "ZeroTrustAccessPolicyRequireGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyRequireGroupOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireGroupOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a67be8266a74ef6676211ce234cb926a4e6537a067bb4f59aa0d53e0f9324c50)
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
            type_hints = typing.get_type_hints(_typecheckingstub__38d972eea7a94abc9a07709179466dd2cd958f4ecb4fbe0bb4888d73cb000443)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireGroup]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireGroup]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireGroup]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__060dd7024d2c4a3d44267f3f300b123fc419c9819acacacd44956165e0aeab18)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireGsuite",
    jsii_struct_bases=[],
    name_mapping={"email": "email", "identity_provider_id": "identityProviderId"},
)
class ZeroTrustAccessPolicyRequireGsuite:
    def __init__(
        self,
        *,
        email: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param email: The email of the Google Workspace group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email ZeroTrustAccessPolicy#email}
        :param identity_provider_id: The ID of your Google Workspace identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c58c38961e51cade309e3fe236f38fdb39c8c164f86a95924c6a5f88977918d)
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "email": email,
            "identity_provider_id": identity_provider_id,
        }

    @builtins.property
    def email(self) -> builtins.str:
        '''The email of the Google Workspace group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email ZeroTrustAccessPolicy#email}
        '''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your Google Workspace identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyRequireGsuite(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyRequireGsuiteOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireGsuiteOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__52aec0d2fcdd571aab4739868687fd4278584bbff5403ef7b4805b2ee027628b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ac982b65e149f4f83538ef449f09ba4e9ace61f7bf644dd1198a1241c496c015)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "email", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcf2e49c55892f0985c278dc18afb87ce855bcf73e6f203992607a272d65fef9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireGsuite]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireGsuite]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireGsuite]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4b275d348e9b7d5cefc997a6bec0d4af0208d652e15bd654bbad37bad5455cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireIp",
    jsii_struct_bases=[],
    name_mapping={"ip": "ip"},
)
class ZeroTrustAccessPolicyRequireIp:
    def __init__(self, *, ip: builtins.str) -> None:
        '''
        :param ip: An IPv4 or IPv6 CIDR block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ip ZeroTrustAccessPolicy#ip}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f7c41a9800db9238ed5f8ffb6270965c984251826fb8ab1bf062fe3431b392f)
            check_type(argname="argument ip", value=ip, expected_type=type_hints["ip"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "ip": ip,
        }

    @builtins.property
    def ip(self) -> builtins.str:
        '''An IPv4 or IPv6 CIDR block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ip ZeroTrustAccessPolicy#ip}
        '''
        result = self._values.get("ip")
        assert result is not None, "Required property 'ip' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyRequireIp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireIpListStruct",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class ZeroTrustAccessPolicyRequireIpListStruct:
    def __init__(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created IP list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18ffab0455ad9edb7e78d589106cbdfce756a8b98b86a64f7a14fa9a124578fe)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of a previously created IP list.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id}

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
        return "ZeroTrustAccessPolicyRequireIpListStruct(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyRequireIpListStructOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireIpListStructOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c54c4c69500fea1067e0ac048a3fa1f6cf39674ca35ee951b58c503a18daa28b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3c8521fb9b6f8cb33050ab98ff155d04b917136749b423e96d201592ce86f934)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireIpListStruct]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireIpListStruct]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireIpListStruct]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45c465f2f6cde8b100a054dfe98590e05a7b38b77b09d6582c26191a9e8ab119)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustAccessPolicyRequireIpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireIpOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b0323bfda274ec9a0b8687bb5abf349d9a6f8dd1fc98d7779fd771e4f94000a0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4cc8f696ad76e45b8802dcbffbaa20285d4af313d3d745cbe727ea71eed11c5a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ip", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireIp]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireIp]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireIp]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ae1d590703c62c832f4ede7faf891c5f61d8068f20156c8b78079d1c14ac96b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireLinkedAppToken",
    jsii_struct_bases=[],
    name_mapping={"app_uid": "appUid"},
)
class ZeroTrustAccessPolicyRequireLinkedAppToken:
    def __init__(self, *, app_uid: builtins.str) -> None:
        '''
        :param app_uid: The ID of an Access OIDC SaaS application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#app_uid ZeroTrustAccessPolicy#app_uid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__281194b75cc233f93830508df7e4e21a514ea8608c687df520a700732a2fee18)
            check_type(argname="argument app_uid", value=app_uid, expected_type=type_hints["app_uid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "app_uid": app_uid,
        }

    @builtins.property
    def app_uid(self) -> builtins.str:
        '''The ID of an Access OIDC SaaS application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#app_uid ZeroTrustAccessPolicy#app_uid}
        '''
        result = self._values.get("app_uid")
        assert result is not None, "Required property 'app_uid' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyRequireLinkedAppToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyRequireLinkedAppTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireLinkedAppTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d7100e99eb6f7c3a7ee74d22341b7c4691b6c138fcf781a37483dc9c50394598)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f1d1b96e6d1725fd36506357f8f28b7d85e5e6eaa092755fd0036392ca47d8e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "appUid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireLinkedAppToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireLinkedAppToken]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireLinkedAppToken]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b32f3b9505deb6945a9960993b6b30b0d0b5bca6dbe285730b89ddf4d371b67)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustAccessPolicyRequireList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__add2c7af1d343f4bb0d7e7826dc1c4d07cf9b7922f6853d2886980355e4bbed0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ZeroTrustAccessPolicyRequireOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dea9d011fb25866c8d091d1f981dc77d2560cf5f6b8be6c95b436310854a966f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ZeroTrustAccessPolicyRequireOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a785377db35a8e537d2e142590ce3c767ead4d19ab9593253c33c48a9b6d58cc)
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
            type_hints = typing.get_type_hints(_typecheckingstub__96cc2b3540d204af3049bdb4ade0e917d3d7d91d38d4e78a55285c2035ea9abe)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0423166074d99c0e14f7fb2ab445464b862665ac4a1a8cbabd44715b1e5f2716)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessPolicyRequire]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessPolicyRequire]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessPolicyRequire]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a75698e757a4907432c891aaac58e82d1d29bd76488d269bab88b8c70f119b4c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireLoginMethod",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class ZeroTrustAccessPolicyRequireLoginMethod:
    def __init__(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of an identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c47b2e427ff7e5acfe0a387d54747d064fbd7593a380c559b9201ac2b9262603)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The ID of an identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id}

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
        return "ZeroTrustAccessPolicyRequireLoginMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyRequireLoginMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireLoginMethodOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__28e2211b8fdb46d8fd9af761fa72435aae42b7f191fd43fabab5db8f763e4cdd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__682ed63835b3c18f999e06cda4e38acfba0bede92b51a0ffc03750409768cd8b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireLoginMethod]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireLoginMethod]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireLoginMethod]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b8dfce0bf66e507d7098ec4661cb2d2e191096db41ef8a2395ba8f0cb8bd84d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireOidc",
    jsii_struct_bases=[],
    name_mapping={
        "claim_name": "claimName",
        "claim_value": "claimValue",
        "identity_provider_id": "identityProviderId",
    },
)
class ZeroTrustAccessPolicyRequireOidc:
    def __init__(
        self,
        *,
        claim_name: builtins.str,
        claim_value: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param claim_name: The name of the OIDC claim. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#claim_name ZeroTrustAccessPolicy#claim_name}
        :param claim_value: The OIDC claim value to look for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#claim_value ZeroTrustAccessPolicy#claim_value}
        :param identity_provider_id: The ID of your OIDC identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed7e7f2d9301b685201cad3063deec64b5490ecbd85ea0d9a78b615fb2ddb382)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#claim_name ZeroTrustAccessPolicy#claim_name}
        '''
        result = self._values.get("claim_name")
        assert result is not None, "Required property 'claim_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def claim_value(self) -> builtins.str:
        '''The OIDC claim value to look for.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#claim_value ZeroTrustAccessPolicy#claim_value}
        '''
        result = self._values.get("claim_value")
        assert result is not None, "Required property 'claim_value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your OIDC identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyRequireOidc(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyRequireOidcOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireOidcOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e427edf6e1c43e71fbb5311f22fc2ba0745f552357a7e194316f30a80232e607)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4e2e93ef81d78c2500fb4a13109e0f7d7f36c304465e4182d893df5e86c3332c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "claimName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="claimValue")
    def claim_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "claimValue"))

    @claim_value.setter
    def claim_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9863f3f22d8bd1c7a2894a05963b0388f7b1ac0c0be142cbd01c1eadd6d0b98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "claimValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d047d0ccd9f4a29f7a724542ebc70ba46f99bcb93a62d1527de7219549b8e55d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireOidc]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireOidc]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireOidc]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__887e837ad181c7bbd27008729b523eb65bbae7f3e5e6ae61cedd74f35517f9de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireOkta",
    jsii_struct_bases=[],
    name_mapping={"identity_provider_id": "identityProviderId", "name": "name"},
)
class ZeroTrustAccessPolicyRequireOkta:
    def __init__(
        self,
        *,
        identity_provider_id: builtins.str,
        name: builtins.str,
    ) -> None:
        '''
        :param identity_provider_id: The ID of your Okta identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        :param name: The name of the Okta group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#name ZeroTrustAccessPolicy#name}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__128fd5d7175c44c806d147df2b6e441ed3f710d378daac7e14a21769c24a2d9d)
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "identity_provider_id": identity_provider_id,
            "name": name,
        }

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your Okta identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the Okta group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#name ZeroTrustAccessPolicy#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyRequireOkta(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyRequireOktaOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireOktaOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__adb3fefe84888c4a7b05466853ba44f87f5315f86ce8ff82ffaf5a99961fe741)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4d53d5ea1af4f0422debeabe7ac07819876a1b49b058038cace3f96249e2020b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3aa7fbf983d5228dd8caf31da7d602e0e9d83a3feb30dfdda417fd8adfc0d1af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireOkta]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireOkta]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireOkta]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8f232d26d2df3dd36231d316664242b52a2f8854ca1bcc4dca3665d4a26226f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustAccessPolicyRequireOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5a94eaa9a70d6382843d0af7d52f60784ff6f6a1e9b7dd9000bd7a1d8c179e16)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putAnyValidServiceToken")
    def put_any_valid_service_token(self) -> None:
        value = ZeroTrustAccessPolicyRequireAnyValidServiceToken()

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
        :param ac_id: The ACID of an Authentication context. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ac_id ZeroTrustAccessPolicy#ac_id}
        :param id: The ID of an Authentication context. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider_id: The ID of your Azure identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        value = ZeroTrustAccessPolicyRequireAuthContext(
            ac_id=ac_id, id=id, identity_provider_id=identity_provider_id
        )

        return typing.cast(None, jsii.invoke(self, "putAuthContext", [value]))

    @jsii.member(jsii_name="putAuthMethod")
    def put_auth_method(self, *, auth_method: builtins.str) -> None:
        '''
        :param auth_method: The type of authentication method https://datatracker.ietf.org/doc/html/rfc8176#section-2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#auth_method ZeroTrustAccessPolicy#auth_method}
        '''
        value = ZeroTrustAccessPolicyRequireAuthMethod(auth_method=auth_method)

        return typing.cast(None, jsii.invoke(self, "putAuthMethod", [value]))

    @jsii.member(jsii_name="putAzureAd")
    def put_azure_ad(
        self,
        *,
        id: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param id: The ID of an Azure group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider_id: The ID of your Azure identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        value = ZeroTrustAccessPolicyRequireAzureAd(
            id=id, identity_provider_id=identity_provider_id
        )

        return typing.cast(None, jsii.invoke(self, "putAzureAd", [value]))

    @jsii.member(jsii_name="putCertificate")
    def put_certificate(self) -> None:
        value = ZeroTrustAccessPolicyRequireCertificate()

        return typing.cast(None, jsii.invoke(self, "putCertificate", [value]))

    @jsii.member(jsii_name="putCommonName")
    def put_common_name(self, *, common_name: builtins.str) -> None:
        '''
        :param common_name: The common name to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#common_name ZeroTrustAccessPolicy#common_name}
        '''
        value = ZeroTrustAccessPolicyRequireCommonName(common_name=common_name)

        return typing.cast(None, jsii.invoke(self, "putCommonName", [value]))

    @jsii.member(jsii_name="putDevicePosture")
    def put_device_posture(self, *, integration_uid: builtins.str) -> None:
        '''
        :param integration_uid: The ID of a device posture integration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#integration_uid ZeroTrustAccessPolicy#integration_uid}
        '''
        value = ZeroTrustAccessPolicyRequireDevicePosture(
            integration_uid=integration_uid
        )

        return typing.cast(None, jsii.invoke(self, "putDevicePosture", [value]))

    @jsii.member(jsii_name="putEmail")
    def put_email(self, *, email: builtins.str) -> None:
        '''
        :param email: The email of the user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email ZeroTrustAccessPolicy#email}
        '''
        value = ZeroTrustAccessPolicyRequireEmail(email=email)

        return typing.cast(None, jsii.invoke(self, "putEmail", [value]))

    @jsii.member(jsii_name="putEmailDomain")
    def put_email_domain(self, *, domain: builtins.str) -> None:
        '''
        :param domain: The email domain to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#domain ZeroTrustAccessPolicy#domain}
        '''
        value = ZeroTrustAccessPolicyRequireEmailDomain(domain=domain)

        return typing.cast(None, jsii.invoke(self, "putEmailDomain", [value]))

    @jsii.member(jsii_name="putEmailList")
    def put_email_list(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created email list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        value = ZeroTrustAccessPolicyRequireEmailListStruct(id=id)

        return typing.cast(None, jsii.invoke(self, "putEmailList", [value]))

    @jsii.member(jsii_name="putEveryone")
    def put_everyone(self) -> None:
        value = ZeroTrustAccessPolicyRequireEveryone()

        return typing.cast(None, jsii.invoke(self, "putEveryone", [value]))

    @jsii.member(jsii_name="putExternalEvaluation")
    def put_external_evaluation(
        self,
        *,
        evaluate_url: builtins.str,
        keys_url: builtins.str,
    ) -> None:
        '''
        :param evaluate_url: The API endpoint containing your business logic. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#evaluate_url ZeroTrustAccessPolicy#evaluate_url}
        :param keys_url: The API endpoint containing the key that Access uses to verify that the response came from your API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#keys_url ZeroTrustAccessPolicy#keys_url}
        '''
        value = ZeroTrustAccessPolicyRequireExternalEvaluation(
            evaluate_url=evaluate_url, keys_url=keys_url
        )

        return typing.cast(None, jsii.invoke(self, "putExternalEvaluation", [value]))

    @jsii.member(jsii_name="putGeo")
    def put_geo(self, *, country_code: builtins.str) -> None:
        '''
        :param country_code: The country code that should be matched. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#country_code ZeroTrustAccessPolicy#country_code}
        '''
        value = ZeroTrustAccessPolicyRequireGeo(country_code=country_code)

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
        :param identity_provider_id: The ID of your Github identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        :param name: The name of the organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#name ZeroTrustAccessPolicy#name}
        :param team: The name of the team. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#team ZeroTrustAccessPolicy#team}
        '''
        value = ZeroTrustAccessPolicyRequireGithubOrganization(
            identity_provider_id=identity_provider_id, name=name, team=team
        )

        return typing.cast(None, jsii.invoke(self, "putGithubOrganization", [value]))

    @jsii.member(jsii_name="putGroup")
    def put_group(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created Access group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        value = ZeroTrustAccessPolicyRequireGroup(id=id)

        return typing.cast(None, jsii.invoke(self, "putGroup", [value]))

    @jsii.member(jsii_name="putGsuite")
    def put_gsuite(
        self,
        *,
        email: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param email: The email of the Google Workspace group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#email ZeroTrustAccessPolicy#email}
        :param identity_provider_id: The ID of your Google Workspace identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        value = ZeroTrustAccessPolicyRequireGsuite(
            email=email, identity_provider_id=identity_provider_id
        )

        return typing.cast(None, jsii.invoke(self, "putGsuite", [value]))

    @jsii.member(jsii_name="putIp")
    def put_ip(self, *, ip: builtins.str) -> None:
        '''
        :param ip: An IPv4 or IPv6 CIDR block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#ip ZeroTrustAccessPolicy#ip}
        '''
        value = ZeroTrustAccessPolicyRequireIp(ip=ip)

        return typing.cast(None, jsii.invoke(self, "putIp", [value]))

    @jsii.member(jsii_name="putIpList")
    def put_ip_list(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of a previously created IP list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        value = ZeroTrustAccessPolicyRequireIpListStruct(id=id)

        return typing.cast(None, jsii.invoke(self, "putIpList", [value]))

    @jsii.member(jsii_name="putLinkedAppToken")
    def put_linked_app_token(self, *, app_uid: builtins.str) -> None:
        '''
        :param app_uid: The ID of an Access OIDC SaaS application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#app_uid ZeroTrustAccessPolicy#app_uid}
        '''
        value = ZeroTrustAccessPolicyRequireLinkedAppToken(app_uid=app_uid)

        return typing.cast(None, jsii.invoke(self, "putLinkedAppToken", [value]))

    @jsii.member(jsii_name="putLoginMethod")
    def put_login_method(self, *, id: builtins.str) -> None:
        '''
        :param id: The ID of an identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#id ZeroTrustAccessPolicy#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        value = ZeroTrustAccessPolicyRequireLoginMethod(id=id)

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
        :param claim_name: The name of the OIDC claim. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#claim_name ZeroTrustAccessPolicy#claim_name}
        :param claim_value: The OIDC claim value to look for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#claim_value ZeroTrustAccessPolicy#claim_value}
        :param identity_provider_id: The ID of your OIDC identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        value = ZeroTrustAccessPolicyRequireOidc(
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
        :param identity_provider_id: The ID of your Okta identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        :param name: The name of the Okta group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#name ZeroTrustAccessPolicy#name}
        '''
        value = ZeroTrustAccessPolicyRequireOkta(
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
        :param attribute_name: The name of the SAML attribute. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#attribute_name ZeroTrustAccessPolicy#attribute_name}
        :param attribute_value: The SAML attribute value to look for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#attribute_value ZeroTrustAccessPolicy#attribute_value}
        :param identity_provider_id: The ID of your SAML identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        value = ZeroTrustAccessPolicyRequireSaml(
            attribute_name=attribute_name,
            attribute_value=attribute_value,
            identity_provider_id=identity_provider_id,
        )

        return typing.cast(None, jsii.invoke(self, "putSaml", [value]))

    @jsii.member(jsii_name="putServiceToken")
    def put_service_token(self, *, token_id: builtins.str) -> None:
        '''
        :param token_id: The ID of a Service Token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#token_id ZeroTrustAccessPolicy#token_id}
        '''
        value = ZeroTrustAccessPolicyRequireServiceToken(token_id=token_id)

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
    ) -> ZeroTrustAccessPolicyRequireAnyValidServiceTokenOutputReference:
        return typing.cast(ZeroTrustAccessPolicyRequireAnyValidServiceTokenOutputReference, jsii.get(self, "anyValidServiceToken"))

    @builtins.property
    @jsii.member(jsii_name="authContext")
    def auth_context(self) -> ZeroTrustAccessPolicyRequireAuthContextOutputReference:
        return typing.cast(ZeroTrustAccessPolicyRequireAuthContextOutputReference, jsii.get(self, "authContext"))

    @builtins.property
    @jsii.member(jsii_name="authMethod")
    def auth_method(self) -> ZeroTrustAccessPolicyRequireAuthMethodOutputReference:
        return typing.cast(ZeroTrustAccessPolicyRequireAuthMethodOutputReference, jsii.get(self, "authMethod"))

    @builtins.property
    @jsii.member(jsii_name="azureAd")
    def azure_ad(self) -> ZeroTrustAccessPolicyRequireAzureAdOutputReference:
        return typing.cast(ZeroTrustAccessPolicyRequireAzureAdOutputReference, jsii.get(self, "azureAd"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> ZeroTrustAccessPolicyRequireCertificateOutputReference:
        return typing.cast(ZeroTrustAccessPolicyRequireCertificateOutputReference, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(self) -> ZeroTrustAccessPolicyRequireCommonNameOutputReference:
        return typing.cast(ZeroTrustAccessPolicyRequireCommonNameOutputReference, jsii.get(self, "commonName"))

    @builtins.property
    @jsii.member(jsii_name="devicePosture")
    def device_posture(
        self,
    ) -> ZeroTrustAccessPolicyRequireDevicePostureOutputReference:
        return typing.cast(ZeroTrustAccessPolicyRequireDevicePostureOutputReference, jsii.get(self, "devicePosture"))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(self) -> ZeroTrustAccessPolicyRequireEmailOutputReference:
        return typing.cast(ZeroTrustAccessPolicyRequireEmailOutputReference, jsii.get(self, "email"))

    @builtins.property
    @jsii.member(jsii_name="emailDomain")
    def email_domain(self) -> ZeroTrustAccessPolicyRequireEmailDomainOutputReference:
        return typing.cast(ZeroTrustAccessPolicyRequireEmailDomainOutputReference, jsii.get(self, "emailDomain"))

    @builtins.property
    @jsii.member(jsii_name="emailList")
    def email_list(self) -> ZeroTrustAccessPolicyRequireEmailListStructOutputReference:
        return typing.cast(ZeroTrustAccessPolicyRequireEmailListStructOutputReference, jsii.get(self, "emailList"))

    @builtins.property
    @jsii.member(jsii_name="everyone")
    def everyone(self) -> ZeroTrustAccessPolicyRequireEveryoneOutputReference:
        return typing.cast(ZeroTrustAccessPolicyRequireEveryoneOutputReference, jsii.get(self, "everyone"))

    @builtins.property
    @jsii.member(jsii_name="externalEvaluation")
    def external_evaluation(
        self,
    ) -> ZeroTrustAccessPolicyRequireExternalEvaluationOutputReference:
        return typing.cast(ZeroTrustAccessPolicyRequireExternalEvaluationOutputReference, jsii.get(self, "externalEvaluation"))

    @builtins.property
    @jsii.member(jsii_name="geo")
    def geo(self) -> ZeroTrustAccessPolicyRequireGeoOutputReference:
        return typing.cast(ZeroTrustAccessPolicyRequireGeoOutputReference, jsii.get(self, "geo"))

    @builtins.property
    @jsii.member(jsii_name="githubOrganization")
    def github_organization(
        self,
    ) -> ZeroTrustAccessPolicyRequireGithubOrganizationOutputReference:
        return typing.cast(ZeroTrustAccessPolicyRequireGithubOrganizationOutputReference, jsii.get(self, "githubOrganization"))

    @builtins.property
    @jsii.member(jsii_name="group")
    def group(self) -> ZeroTrustAccessPolicyRequireGroupOutputReference:
        return typing.cast(ZeroTrustAccessPolicyRequireGroupOutputReference, jsii.get(self, "group"))

    @builtins.property
    @jsii.member(jsii_name="gsuite")
    def gsuite(self) -> ZeroTrustAccessPolicyRequireGsuiteOutputReference:
        return typing.cast(ZeroTrustAccessPolicyRequireGsuiteOutputReference, jsii.get(self, "gsuite"))

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> ZeroTrustAccessPolicyRequireIpOutputReference:
        return typing.cast(ZeroTrustAccessPolicyRequireIpOutputReference, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="ipList")
    def ip_list(self) -> ZeroTrustAccessPolicyRequireIpListStructOutputReference:
        return typing.cast(ZeroTrustAccessPolicyRequireIpListStructOutputReference, jsii.get(self, "ipList"))

    @builtins.property
    @jsii.member(jsii_name="linkedAppToken")
    def linked_app_token(
        self,
    ) -> ZeroTrustAccessPolicyRequireLinkedAppTokenOutputReference:
        return typing.cast(ZeroTrustAccessPolicyRequireLinkedAppTokenOutputReference, jsii.get(self, "linkedAppToken"))

    @builtins.property
    @jsii.member(jsii_name="loginMethod")
    def login_method(self) -> ZeroTrustAccessPolicyRequireLoginMethodOutputReference:
        return typing.cast(ZeroTrustAccessPolicyRequireLoginMethodOutputReference, jsii.get(self, "loginMethod"))

    @builtins.property
    @jsii.member(jsii_name="oidc")
    def oidc(self) -> ZeroTrustAccessPolicyRequireOidcOutputReference:
        return typing.cast(ZeroTrustAccessPolicyRequireOidcOutputReference, jsii.get(self, "oidc"))

    @builtins.property
    @jsii.member(jsii_name="okta")
    def okta(self) -> ZeroTrustAccessPolicyRequireOktaOutputReference:
        return typing.cast(ZeroTrustAccessPolicyRequireOktaOutputReference, jsii.get(self, "okta"))

    @builtins.property
    @jsii.member(jsii_name="saml")
    def saml(self) -> "ZeroTrustAccessPolicyRequireSamlOutputReference":
        return typing.cast("ZeroTrustAccessPolicyRequireSamlOutputReference", jsii.get(self, "saml"))

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(
        self,
    ) -> "ZeroTrustAccessPolicyRequireServiceTokenOutputReference":
        return typing.cast("ZeroTrustAccessPolicyRequireServiceTokenOutputReference", jsii.get(self, "serviceToken"))

    @builtins.property
    @jsii.member(jsii_name="anyValidServiceTokenInput")
    def any_valid_service_token_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireAnyValidServiceToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireAnyValidServiceToken]], jsii.get(self, "anyValidServiceTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="authContextInput")
    def auth_context_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireAuthContext]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireAuthContext]], jsii.get(self, "authContextInput"))

    @builtins.property
    @jsii.member(jsii_name="authMethodInput")
    def auth_method_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireAuthMethod]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireAuthMethod]], jsii.get(self, "authMethodInput"))

    @builtins.property
    @jsii.member(jsii_name="azureAdInput")
    def azure_ad_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireAzureAd]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireAzureAd]], jsii.get(self, "azureAdInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateInput")
    def certificate_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireCertificate]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireCertificate]], jsii.get(self, "certificateInput"))

    @builtins.property
    @jsii.member(jsii_name="commonNameInput")
    def common_name_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireCommonName]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireCommonName]], jsii.get(self, "commonNameInput"))

    @builtins.property
    @jsii.member(jsii_name="devicePostureInput")
    def device_posture_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireDevicePosture]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireDevicePosture]], jsii.get(self, "devicePostureInput"))

    @builtins.property
    @jsii.member(jsii_name="emailDomainInput")
    def email_domain_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireEmailDomain]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireEmailDomain]], jsii.get(self, "emailDomainInput"))

    @builtins.property
    @jsii.member(jsii_name="emailInput")
    def email_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireEmail]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireEmail]], jsii.get(self, "emailInput"))

    @builtins.property
    @jsii.member(jsii_name="emailListInput")
    def email_list_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireEmailListStruct]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireEmailListStruct]], jsii.get(self, "emailListInput"))

    @builtins.property
    @jsii.member(jsii_name="everyoneInput")
    def everyone_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireEveryone]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireEveryone]], jsii.get(self, "everyoneInput"))

    @builtins.property
    @jsii.member(jsii_name="externalEvaluationInput")
    def external_evaluation_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireExternalEvaluation]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireExternalEvaluation]], jsii.get(self, "externalEvaluationInput"))

    @builtins.property
    @jsii.member(jsii_name="geoInput")
    def geo_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireGeo]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireGeo]], jsii.get(self, "geoInput"))

    @builtins.property
    @jsii.member(jsii_name="githubOrganizationInput")
    def github_organization_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireGithubOrganization]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireGithubOrganization]], jsii.get(self, "githubOrganizationInput"))

    @builtins.property
    @jsii.member(jsii_name="groupInput")
    def group_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireGroup]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireGroup]], jsii.get(self, "groupInput"))

    @builtins.property
    @jsii.member(jsii_name="gsuiteInput")
    def gsuite_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireGsuite]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireGsuite]], jsii.get(self, "gsuiteInput"))

    @builtins.property
    @jsii.member(jsii_name="ipInput")
    def ip_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireIp]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireIp]], jsii.get(self, "ipInput"))

    @builtins.property
    @jsii.member(jsii_name="ipListInput")
    def ip_list_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireIpListStruct]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireIpListStruct]], jsii.get(self, "ipListInput"))

    @builtins.property
    @jsii.member(jsii_name="linkedAppTokenInput")
    def linked_app_token_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireLinkedAppToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireLinkedAppToken]], jsii.get(self, "linkedAppTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="loginMethodInput")
    def login_method_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireLoginMethod]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireLoginMethod]], jsii.get(self, "loginMethodInput"))

    @builtins.property
    @jsii.member(jsii_name="oidcInput")
    def oidc_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireOidc]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireOidc]], jsii.get(self, "oidcInput"))

    @builtins.property
    @jsii.member(jsii_name="oktaInput")
    def okta_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireOkta]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireOkta]], jsii.get(self, "oktaInput"))

    @builtins.property
    @jsii.member(jsii_name="samlInput")
    def saml_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustAccessPolicyRequireSaml"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustAccessPolicyRequireSaml"]], jsii.get(self, "samlInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceTokenInput")
    def service_token_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustAccessPolicyRequireServiceToken"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustAccessPolicyRequireServiceToken"]], jsii.get(self, "serviceTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequire]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequire]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequire]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6edfd3e851fb78c0fdfba079e5a79bc22ac6e3f2849664f72ed7a32858fda6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireSaml",
    jsii_struct_bases=[],
    name_mapping={
        "attribute_name": "attributeName",
        "attribute_value": "attributeValue",
        "identity_provider_id": "identityProviderId",
    },
)
class ZeroTrustAccessPolicyRequireSaml:
    def __init__(
        self,
        *,
        attribute_name: builtins.str,
        attribute_value: builtins.str,
        identity_provider_id: builtins.str,
    ) -> None:
        '''
        :param attribute_name: The name of the SAML attribute. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#attribute_name ZeroTrustAccessPolicy#attribute_name}
        :param attribute_value: The SAML attribute value to look for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#attribute_value ZeroTrustAccessPolicy#attribute_value}
        :param identity_provider_id: The ID of your SAML identity provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__586e7633636de91fde0dacc286d80ba7f992d77dc5e953fa7149a7b340a71a41)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#attribute_name ZeroTrustAccessPolicy#attribute_name}
        '''
        result = self._values.get("attribute_name")
        assert result is not None, "Required property 'attribute_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attribute_value(self) -> builtins.str:
        '''The SAML attribute value to look for.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#attribute_value ZeroTrustAccessPolicy#attribute_value}
        '''
        result = self._values.get("attribute_value")
        assert result is not None, "Required property 'attribute_value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_id(self) -> builtins.str:
        '''The ID of your SAML identity provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#identity_provider_id ZeroTrustAccessPolicy#identity_provider_id}
        '''
        result = self._values.get("identity_provider_id")
        assert result is not None, "Required property 'identity_provider_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyRequireSaml(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyRequireSamlOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireSamlOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0f8344e714937527b22ce6cf4165b4bc11f9aea89162d784b3c8b5d0b03d3d12)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c33e2cc6dd0599c1c816031bdb76f171a26169a1b40fbd041207f68d5b0a3d26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attributeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="attributeValue")
    def attribute_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "attributeValue"))

    @attribute_value.setter
    def attribute_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb46e9878eb3b195fd89f32076c4439dc9a45ca5ca07598703066216ef1d029a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attributeValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74cb70b0cf4c81fe78bbeb3b35ba812f5e09ff675115c5f3c9a90c2b6d5a1491)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireSaml]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireSaml]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireSaml]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ec61bc245153747e1e0fa1f004d9190d56a519e68a9bd8a0d8f5fa0f3cf22e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireServiceToken",
    jsii_struct_bases=[],
    name_mapping={"token_id": "tokenId"},
)
class ZeroTrustAccessPolicyRequireServiceToken:
    def __init__(self, *, token_id: builtins.str) -> None:
        '''
        :param token_id: The ID of a Service Token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#token_id ZeroTrustAccessPolicy#token_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea70d479a424ec258ff3e9faa00f2be2cd7b4ba97ad9d0579dcc6188f6b4812d)
            check_type(argname="argument token_id", value=token_id, expected_type=type_hints["token_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "token_id": token_id,
        }

    @builtins.property
    def token_id(self) -> builtins.str:
        '''The ID of a Service Token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_access_policy#token_id ZeroTrustAccessPolicy#token_id}
        '''
        result = self._values.get("token_id")
        assert result is not None, "Required property 'token_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustAccessPolicyRequireServiceToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustAccessPolicyRequireServiceTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustAccessPolicy.ZeroTrustAccessPolicyRequireServiceTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__59e8b29a3cd27577d02d208cf27d054aa2ce2c6042cbcaa08bfc07e5b05a21e4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__549a12269d7860ca92ad3250ad82ed8d32409956b6b4201d6f5e81a664902d18)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireServiceToken]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireServiceToken]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireServiceToken]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5df576ea24f19031ae4aa3c0fd788ee761f38cf43c904c793dd26024a895c6d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ZeroTrustAccessPolicy",
    "ZeroTrustAccessPolicyApprovalGroups",
    "ZeroTrustAccessPolicyApprovalGroupsList",
    "ZeroTrustAccessPolicyApprovalGroupsOutputReference",
    "ZeroTrustAccessPolicyConfig",
    "ZeroTrustAccessPolicyExclude",
    "ZeroTrustAccessPolicyExcludeAnyValidServiceToken",
    "ZeroTrustAccessPolicyExcludeAnyValidServiceTokenOutputReference",
    "ZeroTrustAccessPolicyExcludeAuthContext",
    "ZeroTrustAccessPolicyExcludeAuthContextOutputReference",
    "ZeroTrustAccessPolicyExcludeAuthMethod",
    "ZeroTrustAccessPolicyExcludeAuthMethodOutputReference",
    "ZeroTrustAccessPolicyExcludeAzureAd",
    "ZeroTrustAccessPolicyExcludeAzureAdOutputReference",
    "ZeroTrustAccessPolicyExcludeCertificate",
    "ZeroTrustAccessPolicyExcludeCertificateOutputReference",
    "ZeroTrustAccessPolicyExcludeCommonName",
    "ZeroTrustAccessPolicyExcludeCommonNameOutputReference",
    "ZeroTrustAccessPolicyExcludeDevicePosture",
    "ZeroTrustAccessPolicyExcludeDevicePostureOutputReference",
    "ZeroTrustAccessPolicyExcludeEmail",
    "ZeroTrustAccessPolicyExcludeEmailDomain",
    "ZeroTrustAccessPolicyExcludeEmailDomainOutputReference",
    "ZeroTrustAccessPolicyExcludeEmailListStruct",
    "ZeroTrustAccessPolicyExcludeEmailListStructOutputReference",
    "ZeroTrustAccessPolicyExcludeEmailOutputReference",
    "ZeroTrustAccessPolicyExcludeEveryone",
    "ZeroTrustAccessPolicyExcludeEveryoneOutputReference",
    "ZeroTrustAccessPolicyExcludeExternalEvaluation",
    "ZeroTrustAccessPolicyExcludeExternalEvaluationOutputReference",
    "ZeroTrustAccessPolicyExcludeGeo",
    "ZeroTrustAccessPolicyExcludeGeoOutputReference",
    "ZeroTrustAccessPolicyExcludeGithubOrganization",
    "ZeroTrustAccessPolicyExcludeGithubOrganizationOutputReference",
    "ZeroTrustAccessPolicyExcludeGroup",
    "ZeroTrustAccessPolicyExcludeGroupOutputReference",
    "ZeroTrustAccessPolicyExcludeGsuite",
    "ZeroTrustAccessPolicyExcludeGsuiteOutputReference",
    "ZeroTrustAccessPolicyExcludeIp",
    "ZeroTrustAccessPolicyExcludeIpListStruct",
    "ZeroTrustAccessPolicyExcludeIpListStructOutputReference",
    "ZeroTrustAccessPolicyExcludeIpOutputReference",
    "ZeroTrustAccessPolicyExcludeLinkedAppToken",
    "ZeroTrustAccessPolicyExcludeLinkedAppTokenOutputReference",
    "ZeroTrustAccessPolicyExcludeList",
    "ZeroTrustAccessPolicyExcludeLoginMethod",
    "ZeroTrustAccessPolicyExcludeLoginMethodOutputReference",
    "ZeroTrustAccessPolicyExcludeOidc",
    "ZeroTrustAccessPolicyExcludeOidcOutputReference",
    "ZeroTrustAccessPolicyExcludeOkta",
    "ZeroTrustAccessPolicyExcludeOktaOutputReference",
    "ZeroTrustAccessPolicyExcludeOutputReference",
    "ZeroTrustAccessPolicyExcludeSaml",
    "ZeroTrustAccessPolicyExcludeSamlOutputReference",
    "ZeroTrustAccessPolicyExcludeServiceToken",
    "ZeroTrustAccessPolicyExcludeServiceTokenOutputReference",
    "ZeroTrustAccessPolicyInclude",
    "ZeroTrustAccessPolicyIncludeAnyValidServiceToken",
    "ZeroTrustAccessPolicyIncludeAnyValidServiceTokenOutputReference",
    "ZeroTrustAccessPolicyIncludeAuthContext",
    "ZeroTrustAccessPolicyIncludeAuthContextOutputReference",
    "ZeroTrustAccessPolicyIncludeAuthMethod",
    "ZeroTrustAccessPolicyIncludeAuthMethodOutputReference",
    "ZeroTrustAccessPolicyIncludeAzureAd",
    "ZeroTrustAccessPolicyIncludeAzureAdOutputReference",
    "ZeroTrustAccessPolicyIncludeCertificate",
    "ZeroTrustAccessPolicyIncludeCertificateOutputReference",
    "ZeroTrustAccessPolicyIncludeCommonName",
    "ZeroTrustAccessPolicyIncludeCommonNameOutputReference",
    "ZeroTrustAccessPolicyIncludeDevicePosture",
    "ZeroTrustAccessPolicyIncludeDevicePostureOutputReference",
    "ZeroTrustAccessPolicyIncludeEmail",
    "ZeroTrustAccessPolicyIncludeEmailDomain",
    "ZeroTrustAccessPolicyIncludeEmailDomainOutputReference",
    "ZeroTrustAccessPolicyIncludeEmailListStruct",
    "ZeroTrustAccessPolicyIncludeEmailListStructOutputReference",
    "ZeroTrustAccessPolicyIncludeEmailOutputReference",
    "ZeroTrustAccessPolicyIncludeEveryone",
    "ZeroTrustAccessPolicyIncludeEveryoneOutputReference",
    "ZeroTrustAccessPolicyIncludeExternalEvaluation",
    "ZeroTrustAccessPolicyIncludeExternalEvaluationOutputReference",
    "ZeroTrustAccessPolicyIncludeGeo",
    "ZeroTrustAccessPolicyIncludeGeoOutputReference",
    "ZeroTrustAccessPolicyIncludeGithubOrganization",
    "ZeroTrustAccessPolicyIncludeGithubOrganizationOutputReference",
    "ZeroTrustAccessPolicyIncludeGroup",
    "ZeroTrustAccessPolicyIncludeGroupOutputReference",
    "ZeroTrustAccessPolicyIncludeGsuite",
    "ZeroTrustAccessPolicyIncludeGsuiteOutputReference",
    "ZeroTrustAccessPolicyIncludeIp",
    "ZeroTrustAccessPolicyIncludeIpListStruct",
    "ZeroTrustAccessPolicyIncludeIpListStructOutputReference",
    "ZeroTrustAccessPolicyIncludeIpOutputReference",
    "ZeroTrustAccessPolicyIncludeLinkedAppToken",
    "ZeroTrustAccessPolicyIncludeLinkedAppTokenOutputReference",
    "ZeroTrustAccessPolicyIncludeList",
    "ZeroTrustAccessPolicyIncludeLoginMethod",
    "ZeroTrustAccessPolicyIncludeLoginMethodOutputReference",
    "ZeroTrustAccessPolicyIncludeOidc",
    "ZeroTrustAccessPolicyIncludeOidcOutputReference",
    "ZeroTrustAccessPolicyIncludeOkta",
    "ZeroTrustAccessPolicyIncludeOktaOutputReference",
    "ZeroTrustAccessPolicyIncludeOutputReference",
    "ZeroTrustAccessPolicyIncludeSaml",
    "ZeroTrustAccessPolicyIncludeSamlOutputReference",
    "ZeroTrustAccessPolicyIncludeServiceToken",
    "ZeroTrustAccessPolicyIncludeServiceTokenOutputReference",
    "ZeroTrustAccessPolicyRequire",
    "ZeroTrustAccessPolicyRequireAnyValidServiceToken",
    "ZeroTrustAccessPolicyRequireAnyValidServiceTokenOutputReference",
    "ZeroTrustAccessPolicyRequireAuthContext",
    "ZeroTrustAccessPolicyRequireAuthContextOutputReference",
    "ZeroTrustAccessPolicyRequireAuthMethod",
    "ZeroTrustAccessPolicyRequireAuthMethodOutputReference",
    "ZeroTrustAccessPolicyRequireAzureAd",
    "ZeroTrustAccessPolicyRequireAzureAdOutputReference",
    "ZeroTrustAccessPolicyRequireCertificate",
    "ZeroTrustAccessPolicyRequireCertificateOutputReference",
    "ZeroTrustAccessPolicyRequireCommonName",
    "ZeroTrustAccessPolicyRequireCommonNameOutputReference",
    "ZeroTrustAccessPolicyRequireDevicePosture",
    "ZeroTrustAccessPolicyRequireDevicePostureOutputReference",
    "ZeroTrustAccessPolicyRequireEmail",
    "ZeroTrustAccessPolicyRequireEmailDomain",
    "ZeroTrustAccessPolicyRequireEmailDomainOutputReference",
    "ZeroTrustAccessPolicyRequireEmailListStruct",
    "ZeroTrustAccessPolicyRequireEmailListStructOutputReference",
    "ZeroTrustAccessPolicyRequireEmailOutputReference",
    "ZeroTrustAccessPolicyRequireEveryone",
    "ZeroTrustAccessPolicyRequireEveryoneOutputReference",
    "ZeroTrustAccessPolicyRequireExternalEvaluation",
    "ZeroTrustAccessPolicyRequireExternalEvaluationOutputReference",
    "ZeroTrustAccessPolicyRequireGeo",
    "ZeroTrustAccessPolicyRequireGeoOutputReference",
    "ZeroTrustAccessPolicyRequireGithubOrganization",
    "ZeroTrustAccessPolicyRequireGithubOrganizationOutputReference",
    "ZeroTrustAccessPolicyRequireGroup",
    "ZeroTrustAccessPolicyRequireGroupOutputReference",
    "ZeroTrustAccessPolicyRequireGsuite",
    "ZeroTrustAccessPolicyRequireGsuiteOutputReference",
    "ZeroTrustAccessPolicyRequireIp",
    "ZeroTrustAccessPolicyRequireIpListStruct",
    "ZeroTrustAccessPolicyRequireIpListStructOutputReference",
    "ZeroTrustAccessPolicyRequireIpOutputReference",
    "ZeroTrustAccessPolicyRequireLinkedAppToken",
    "ZeroTrustAccessPolicyRequireLinkedAppTokenOutputReference",
    "ZeroTrustAccessPolicyRequireList",
    "ZeroTrustAccessPolicyRequireLoginMethod",
    "ZeroTrustAccessPolicyRequireLoginMethodOutputReference",
    "ZeroTrustAccessPolicyRequireOidc",
    "ZeroTrustAccessPolicyRequireOidcOutputReference",
    "ZeroTrustAccessPolicyRequireOkta",
    "ZeroTrustAccessPolicyRequireOktaOutputReference",
    "ZeroTrustAccessPolicyRequireOutputReference",
    "ZeroTrustAccessPolicyRequireSaml",
    "ZeroTrustAccessPolicyRequireSamlOutputReference",
    "ZeroTrustAccessPolicyRequireServiceToken",
    "ZeroTrustAccessPolicyRequireServiceTokenOutputReference",
]

publication.publish()

def _typecheckingstub__d70830b701fa21bbe3097e3ce85383f1c5172780596ccae55d9e71390a0b5c83(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    decision: builtins.str,
    name: builtins.str,
    approval_groups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustAccessPolicyApprovalGroups, typing.Dict[builtins.str, typing.Any]]]]] = None,
    approval_required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    exclude: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustAccessPolicyExclude, typing.Dict[builtins.str, typing.Any]]]]] = None,
    include: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustAccessPolicyInclude, typing.Dict[builtins.str, typing.Any]]]]] = None,
    isolation_required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    purpose_justification_prompt: typing.Optional[builtins.str] = None,
    purpose_justification_required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    require: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustAccessPolicyRequire, typing.Dict[builtins.str, typing.Any]]]]] = None,
    session_duration: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__103d4924d25381220a059d6856d206bd9ca0af15f9e4ab5371afd16acf97cc2f(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97e5936063f8543a55f835bd59b166e189210684b93e5d7b5dd2da09ffd91343(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustAccessPolicyApprovalGroups, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c42102dd1d8b5019e25d4f8e55ec147664c6162d1586a969cb77f1fd7a6b5b12(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustAccessPolicyExclude, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7eefe6d5ef3b21987cbacb6cfd625d26f7880e61dd069b42a00872eac2c961d8(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustAccessPolicyInclude, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f91846a3e5cfe024f97ba5b88ecb39d6ab64c64418a1cdce2326098d53fe3558(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustAccessPolicyRequire, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e6d8254b5fac529f599e7382dc614282357239e541ba2f429392a8781f7adf7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c72aca090dca014edbce31c869cedbe59d52c721b468e5e329da2f34a9e0325c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4833cac024c32ee344b1b7291f07a5bb3feab51085514c71bd41c4864c326f76(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__711aa0a4df834b4579ec0ab636b699ce0d56fe8642f1a327da3e74ae869f9a8c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9675c9ce6ab73ad2e8d9e890440bb8ced121ec187d2a2e94112b6251003de283(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c770cef1a421a715549246cc86649bbde00ec7553d7664a3922ff2734b51d3e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0e8698c87c24aded5d3110e9e104243e6b5fce2f23bb7aeb58ded25ebd6328c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a6b1ed10b68bddf566328fdd936fd040cf78628c6daf76f0cd5335e26ffa76e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff4f4f1a2a58ee8e9cdde159bfb04f70ef04e438b77b2ffdeeb16f09f231696a(
    *,
    approvals_needed: jsii.Number,
    email_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
    email_list_uuid: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e316f0e0ab35c0bd923e8f1d5dcfb135ac19a8d2a61a70d1251fe3b07188361d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77ff6acba382fb8ac99c314a3bf713a9d972ae20d7cc66564d991d487dd06925(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3b41d610a9c6159e872411e70ed00077819e3b22becf2e81b9e4f5412bda726(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__574c033ebd3cf42f1565d092b5ef513755b3077f208eba2890981d139af0a625(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84ca3ac07d37f53057891ff1a8d1a416bdb4981f327b39d15983399865308337(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9519fd3c2ca362307587a40f0be5eeea3de99d1e40d2f79c208f4be7e4b05f74(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessPolicyApprovalGroups]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3506a0c26fe09cbfdd02d9902a6854e1ccfec5611a1e4e45397b2cb5df189f87(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd4f59379c2124ce0c508ef79810953b9b4139dda309afcde19881a5762d2d66(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7719394293a74ce0926b4c4da9295339a59e1485fdb68b35ee4608ad43ffd922(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3b285206e1087e666dcdf0012079b70e4eebc60b1f60a6fb7ba7bdb0ad423dc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b4a9aab03cda8da1a3b925dc458c3824a3b4a4120419595eab2aca1d2c37f02(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyApprovalGroups]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42bd77d29aedbebe7fe114c3db69a254776c577afb59e10e4296bb00cb90027f(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    decision: builtins.str,
    name: builtins.str,
    approval_groups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustAccessPolicyApprovalGroups, typing.Dict[builtins.str, typing.Any]]]]] = None,
    approval_required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    exclude: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustAccessPolicyExclude, typing.Dict[builtins.str, typing.Any]]]]] = None,
    include: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustAccessPolicyInclude, typing.Dict[builtins.str, typing.Any]]]]] = None,
    isolation_required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    purpose_justification_prompt: typing.Optional[builtins.str] = None,
    purpose_justification_required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    require: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustAccessPolicyRequire, typing.Dict[builtins.str, typing.Any]]]]] = None,
    session_duration: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7508458f688150ef57942b9bdf3e932d66343852d59e86215a2106a376732e4(
    *,
    any_valid_service_token: typing.Optional[typing.Union[ZeroTrustAccessPolicyExcludeAnyValidServiceToken, typing.Dict[builtins.str, typing.Any]]] = None,
    auth_context: typing.Optional[typing.Union[ZeroTrustAccessPolicyExcludeAuthContext, typing.Dict[builtins.str, typing.Any]]] = None,
    auth_method: typing.Optional[typing.Union[ZeroTrustAccessPolicyExcludeAuthMethod, typing.Dict[builtins.str, typing.Any]]] = None,
    azure_ad: typing.Optional[typing.Union[ZeroTrustAccessPolicyExcludeAzureAd, typing.Dict[builtins.str, typing.Any]]] = None,
    certificate: typing.Optional[typing.Union[ZeroTrustAccessPolicyExcludeCertificate, typing.Dict[builtins.str, typing.Any]]] = None,
    common_name: typing.Optional[typing.Union[ZeroTrustAccessPolicyExcludeCommonName, typing.Dict[builtins.str, typing.Any]]] = None,
    device_posture: typing.Optional[typing.Union[ZeroTrustAccessPolicyExcludeDevicePosture, typing.Dict[builtins.str, typing.Any]]] = None,
    email: typing.Optional[typing.Union[ZeroTrustAccessPolicyExcludeEmail, typing.Dict[builtins.str, typing.Any]]] = None,
    email_domain: typing.Optional[typing.Union[ZeroTrustAccessPolicyExcludeEmailDomain, typing.Dict[builtins.str, typing.Any]]] = None,
    email_list: typing.Optional[typing.Union[ZeroTrustAccessPolicyExcludeEmailListStruct, typing.Dict[builtins.str, typing.Any]]] = None,
    everyone: typing.Optional[typing.Union[ZeroTrustAccessPolicyExcludeEveryone, typing.Dict[builtins.str, typing.Any]]] = None,
    external_evaluation: typing.Optional[typing.Union[ZeroTrustAccessPolicyExcludeExternalEvaluation, typing.Dict[builtins.str, typing.Any]]] = None,
    geo: typing.Optional[typing.Union[ZeroTrustAccessPolicyExcludeGeo, typing.Dict[builtins.str, typing.Any]]] = None,
    github_organization: typing.Optional[typing.Union[ZeroTrustAccessPolicyExcludeGithubOrganization, typing.Dict[builtins.str, typing.Any]]] = None,
    group: typing.Optional[typing.Union[ZeroTrustAccessPolicyExcludeGroup, typing.Dict[builtins.str, typing.Any]]] = None,
    gsuite: typing.Optional[typing.Union[ZeroTrustAccessPolicyExcludeGsuite, typing.Dict[builtins.str, typing.Any]]] = None,
    ip: typing.Optional[typing.Union[ZeroTrustAccessPolicyExcludeIp, typing.Dict[builtins.str, typing.Any]]] = None,
    ip_list: typing.Optional[typing.Union[ZeroTrustAccessPolicyExcludeIpListStruct, typing.Dict[builtins.str, typing.Any]]] = None,
    linked_app_token: typing.Optional[typing.Union[ZeroTrustAccessPolicyExcludeLinkedAppToken, typing.Dict[builtins.str, typing.Any]]] = None,
    login_method: typing.Optional[typing.Union[ZeroTrustAccessPolicyExcludeLoginMethod, typing.Dict[builtins.str, typing.Any]]] = None,
    oidc: typing.Optional[typing.Union[ZeroTrustAccessPolicyExcludeOidc, typing.Dict[builtins.str, typing.Any]]] = None,
    okta: typing.Optional[typing.Union[ZeroTrustAccessPolicyExcludeOkta, typing.Dict[builtins.str, typing.Any]]] = None,
    saml: typing.Optional[typing.Union[ZeroTrustAccessPolicyExcludeSaml, typing.Dict[builtins.str, typing.Any]]] = None,
    service_token: typing.Optional[typing.Union[ZeroTrustAccessPolicyExcludeServiceToken, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cb34d6a70c6226b68c12582f6b83e26f9b899edc7e848716e839f2d4e15cc39(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b948d6039f18a9a386b5d7c895a1e9e9e0339b2af9a362ae0423bbeded638c8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeAnyValidServiceToken]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0dacad059df343a10cda69136eb22af18fd8bbfffe0b24c1e65092345a490fc4(
    *,
    ac_id: builtins.str,
    id: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebcdeac36c8a8c9812c4dfa87190c88c82b11d1731e47fd78982b2f066f5e46f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0f027f9c8cbbccebc37207f8ee0af4ffc0624a5599948dbc42d5b19791208ca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__028fa0652cc0df99f8c893b6a246d1b79f3fa72f248b849c6e6c76f2bfc5aba4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__622ff023b5e3098ca3b6b4ef69cd2eca0f1d13a82ec338a40c84bafdb1d6c0c5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__726b84022b0a708d56e19bb04928f9ff7fbe900dbec6ce41dbb9de0992642d03(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeAuthContext]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56e3ff2aa11ec337a255a85e00420ff43733d9a9a26d4c9b6e4f690e4c9abf32(
    *,
    auth_method: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f426211310c49a3773a61c69af2d5fe33ac1ce19d30fe64b6f4f34f3c178d03(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__173e503b2e205b076b61a77efde67cf8ece0835a84adf84eb5055bc283adcb75(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e294b103aca90cfa62a02e1970f60689d4693c58f281d4d3cbc72c5e688e180(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeAuthMethod]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9320fea2d0fa1c6697fcc1ddeaee4856c5398d75f0665cef303e8381512354f(
    *,
    id: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19bf89c73f3df57fe2480f163705d19ae4e1d965ffd50b9c9cd815b07b081d8a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c49f999c452938c35db7b23e7b4b4b02a189b662b304af68ee75111adb42781a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7a42dc45bed66a41429119f0854dd83d03543500a562cc18af41a29320806d6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0da7d591e8917f96f2115162a410c968f5150d294be5815675afc39055e2aee3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeAzureAd]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d88671d34532f3b4cd190f76af7489bff274096cac9afa304b561b45fc464519(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16734a5936189cbfb6618705986417ed2b438255680d6570b08dcb733f17a522(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeCertificate]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee37b824162e2238eab6230521f385cdf4c6797ab0da12cf8bd4432589421dc9(
    *,
    common_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4738c6c99a2333c45e2251526de934be1962aec9f1682efdd17609e6a6531953(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0cb9692cd3f75ad1b1e64e561d549e7e41e81150b06c57c383c476e9543f511(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cd1fce646d42f26da177378c209b61ac7340daf06c77829bc0e8b82a9bdb191(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeCommonName]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc2985e06108cb9bcbe238824ef4744fe3e925dc50a8985663a090496b4dd4b1(
    *,
    integration_uid: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad58b58dbc74ba7371cf63982cff349f73f9fdb07f3a092be850c1765135665e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e96cf19320d20c0a6e724243cd55475d95f75bf46c4349930a871df4c8c72b7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddb036770ba06c19719ca0074b6b8ab49d6f0c1d8a6728add5a64e6d55f0b400(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeDevicePosture]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a574f86f0e601ec8e012a1efe8dafa72664ee20f2d8c0c5c8a9badedf03b27b5(
    *,
    email: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38b1e29d8836291b31351d8c7ba7f40b7d36534d7cea3c9421cbf66b368ef9b2(
    *,
    domain: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00f819cc2a0832bdf8ebb6b09d95f865873e8351d2f1672f40e7e4006bf823eb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eaf5e40263345a5ed34f20b55df6543acb62a78c9c758f9ccfccb79a8a3eb348(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2946389addd90eb25bf5a0f47ede1e88f496cf80592daebdb95dd149b123edc0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeEmailDomain]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf14ab1f7bee9439e7428a1987e0fe20d607878e406ad0328de4630ca1aa50e4(
    *,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb03908e37c83274ccc08f09d43879d5d4f042c9b922818f41d6b567a9cba09e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cd8f7d400d6424c8dd1dbdfc10840d43f2665453afc552628ea304c020b63a4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33772317cf2d51bd85a2abe8ed95d99d2b9745cfee933db4a0fedefa4c823722(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeEmailListStruct]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5879e78a55cee273b470d34044b2befcf263896752f48623b72388673c00d853(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8b57935203d7a43cab5ec1e2564a902bb08f0e2cd862a48843f66ecacda120e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ca1c3448b9bd8158516156c2270786028415739b00f370f1e2f01b5a7ce4545(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeEmail]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__975fa9f24e0737ee4e7e7edc9e00d86a28fbe89a4a36f14578b44bb6e1d244b5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2fa4293c975064196b3b68ac073e4272ba99ef1619a74f4811a559a921bf242(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeEveryone]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c0776a92d3a7c1dbf524e002e4b6086a83724b86a998e2c74f783da4e74a0f5(
    *,
    evaluate_url: builtins.str,
    keys_url: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1873a072afe0860d06990a8d94a00fe835d92d548c26ceb357fbf7cafbeec1bf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ce5057eb101b172983146768578f83e01804f6803214e1ccf10a1f177814114(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7885370a8efd2f2cc2136d26ef98fd4d499b5e9df948fe11a6b0379171f2e5a7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09579fbe45d9f0dd978351451135fe98a55b27ba8448d6346cf5022b84fdea5d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeExternalEvaluation]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9eb1e64668fd978732e947bb80254dfc18ce7af234111d3327c0f25128dc87b6(
    *,
    country_code: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0029cfcb2997a8ad304bed9e77acc41e95ac9099b338b737663c0f3a96a09d4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa87d229a575115fa88238a22adfba2ce4f0745ebdbd0ed849ae913d2b52409a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4aadfc71855fe159e72e59fa2f5188ccd38ac5a23ae5e7a76c29ca06cbbcc5a3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeGeo]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06e528aa23d87f4c8ebd5aa22d57c5f250d5ea72e6c5dfed24be71e4023f4667(
    *,
    identity_provider_id: builtins.str,
    name: builtins.str,
    team: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac3eb3c015c0c2e49e4bbe6f8ab0a6d48cf2fcbcfd5e6be741564c3cff6aef79(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab0fb55852d2d18694d4a35db4b097116d1b9ef46d53632dc4b382e254fe0829(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c79ec67cba0ae9ce4770946a13431f6409af0133b6c3cb9b91c325541ccbc3bc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0498c7c4e4b4b5d0fee036b0c980f7aa91b08d44edd840e4348f5ba55507f470(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b608e702ac5ad7c630e8cf5a3baa29028c261d451c11edaba160601b652f232(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeGithubOrganization]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ad1b65c7a33817a57383730dd0ddfec3cb8097822f4fb2b0e1a8480c08e5f82(
    *,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15418770441dc3aab6b572358a8ded9e21ca2e2cd7522f7ece9b7b9b8c93fb2c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__860ca9233196caa3524704fa736f3bcadd46f257aa2c360ca8ba95555489ff88(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd062bdad12346e212437c353f17f3eac93202c1180637d8e1e64cd3ccd2b32b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeGroup]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae88135e7743a6d5cc430ff8df3e789449c27a9af7b7e2a03780b59ff4d5f3e1(
    *,
    email: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fd333799c47b9dce616929ee96f8998a4336103b0d1a45a96a02adfc61edecd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e57df1cecda0357c48012da703040230da0fd769521e8a326879664a36177588(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f36004d6d5bf4295571a65c0cd25bd9153f0aff89e42fedf77db23479226e93(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d849a0df75d20d8c280b63bd813688b106a179241a21e575ac95d0121bef9758(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeGsuite]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdf9967615da5efec5d12165b3fa23a660ab9bbff60bb4b1ab705cd31d8b21c6(
    *,
    ip: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a0b93e3ffbbeceb13355b44b0e821047e57cbe015dd51be43aa2cd4b7ba3295(
    *,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a85b9707ef5b31015398785c069af8e73603f5413592196c6a295b40e32eab95(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5614d7c60b0115ffa9f81075341b89d91611ba5c5f8685daf62f26d97098c6b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d85365ab40376e2720c16ef16a434550e5ebfa70ff50809a557962dc47cf4ab(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeIpListStruct]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05acbb1658848675ca93d1474f74e470e14e4239c08fd64187d3e5f11db14b82(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4dd1877f4693402991ef9fc98c6f88e0ef2fb9eb3530d571c88bc3fa1b80a43c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e4f6b2c602f334f2362726677797c489791308ecb328c11972ecfe7d6faf65a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeIp]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61993aac9bc58675fc6713527b38583284b4374ce7f551e2f493cef7225678c7(
    *,
    app_uid: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be19960dd02299957836d6042f997444c94877c29c06951584283eaed5f23150(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__295e02c096e4bb6d28b2fd9b09953924d440755fd28bb1a3e7882fa64d73b35f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82673c7add004666c8fa42fb0f66f50dd4677050545a86bec793412155697baf(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeLinkedAppToken]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c949b5315ea902e02ed42f7388761c09bccf29fc6a701595ba837c86fc727e4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73cc7f174bc19ba7b5b1f1e3d4e667f8b7c6733e2b4170ce99071f005eae4a5e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d146552daf613c26093e93d326d5ca4a23e70e5d101daefa7afff984a62cfd6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fd8dff35a8d7824117610f18ae69615bde67725a97ca47b2e25e978e9a5e1b3(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eed49251d5c1ba8dc124f17cfd8d235d28fc020149295255b030de2c25940aec(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20d51cdc6cd78c1159638b332825e6a87caca9facad3353f735d9d934a316c76(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessPolicyExclude]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5835fb3e9669cf4b70c66855f7952dd56edf363b1b72615c76952bf5c4b82fd1(
    *,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b3b4ebf2eb931392c7e038897e9fb45da0afd1261152a4901432dfd3068d677(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9a81dd30fcac8beccf25945923f7c5170a24fdcec0d8b26e54902781dd4a6a1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b135cd3f564560c8e3928bbd261e81adc099df7df1a1e1de1240608c07aca46c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeLoginMethod]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cdb26f6763584c3acdc388dbfa712e99f8a47db4f04ce5341f0a246af6e3329(
    *,
    claim_name: builtins.str,
    claim_value: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6645fa80bfe767fc22742d8e64fdd385321b4e37c7932b8b8d93734a6d02a530(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba351b029a9ca5a6ee95dfdca5699613abcc71ce98b66a22c2f7f8118584d54e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4942c754554959c1ae9e643b9031e373f1015394c8ef53a382ee80e03755002(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dabbfe1766a482c13c340dc2535650d67f3be7ceb11f312acedee221c20b054c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__770bf964315dade2ed36ff8d7c122d6fe425bf117572cc119c6654a6a05f1244(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeOidc]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07896720c8fa6082159a98cb5b8d54e7dca4aed7a8dde4c6b4afa3f7d15d03e1(
    *,
    identity_provider_id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c854664e8a1d2e009a4ae565f1da4a61c9d1bce15eae8aeda08f3a89a0295fd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8e789429d70edd5d742d268bcda49c4613565d121a3a69ebd908342f2714e35(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8dd3268aa560da2f66bda79e8a2bcc151f6d8a821d7063bd83638f24ad46282c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c94bdb250488478d1ce69cabc4cf8c9d53e4fabca2d68bdcb734f2360871b5d0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeOkta]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4148a0041ccd848539f9e0c787f79bfb5904adab391cf82d680f8c3540189522(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aeb14724885d1c9f695410983be32b62d5004f77747131fd6def60c05828c592(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExclude]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__242e44373b7658f0aced88344e8eecd593ff32d89878239016780ed19773f47f(
    *,
    attribute_name: builtins.str,
    attribute_value: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0ba9a13db53c682e5b22cc04e7fe3bcc4c3d5084621ae9ed74238b102afa8e9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19229d4243d01f46765a92fb5325daa5da331d86c6a3b13b3c882b4f07f76408(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__096d237eccd1637b12f01041eabed72fe4a1e3cc3eae29b2018a9575e31fe1f8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b065cd8145b33e75816a1f959e2aa0f8ffaaee659b2d5bdddf5d656fadfcca97(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89a1fc7ac38fc5b4e59056492b10140cbd8f4752fce19a8b3e0b628de28d30e3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeSaml]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49a8b95ac22a21d52f54cf4a96dc81d7afc0269b68291601c919ab8f86d7487f(
    *,
    token_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c03796f6db00c793bf3cd565c927a5991607a34da90da7c29d0dd04d3777f07(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1361b3356da9c61e4c4859aeb8fa8729f87b165b5c0c1451a93e84c60d9df6c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b11384b28df8fc3b6cc5740ed096ef43d0da9b6573100b7c2aa3d16595a44a2f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyExcludeServiceToken]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eba1a19c433cf98c94ebe2094176560fb95a7353c7bcb15ea2c741aa8483bcec(
    *,
    any_valid_service_token: typing.Optional[typing.Union[ZeroTrustAccessPolicyIncludeAnyValidServiceToken, typing.Dict[builtins.str, typing.Any]]] = None,
    auth_context: typing.Optional[typing.Union[ZeroTrustAccessPolicyIncludeAuthContext, typing.Dict[builtins.str, typing.Any]]] = None,
    auth_method: typing.Optional[typing.Union[ZeroTrustAccessPolicyIncludeAuthMethod, typing.Dict[builtins.str, typing.Any]]] = None,
    azure_ad: typing.Optional[typing.Union[ZeroTrustAccessPolicyIncludeAzureAd, typing.Dict[builtins.str, typing.Any]]] = None,
    certificate: typing.Optional[typing.Union[ZeroTrustAccessPolicyIncludeCertificate, typing.Dict[builtins.str, typing.Any]]] = None,
    common_name: typing.Optional[typing.Union[ZeroTrustAccessPolicyIncludeCommonName, typing.Dict[builtins.str, typing.Any]]] = None,
    device_posture: typing.Optional[typing.Union[ZeroTrustAccessPolicyIncludeDevicePosture, typing.Dict[builtins.str, typing.Any]]] = None,
    email: typing.Optional[typing.Union[ZeroTrustAccessPolicyIncludeEmail, typing.Dict[builtins.str, typing.Any]]] = None,
    email_domain: typing.Optional[typing.Union[ZeroTrustAccessPolicyIncludeEmailDomain, typing.Dict[builtins.str, typing.Any]]] = None,
    email_list: typing.Optional[typing.Union[ZeroTrustAccessPolicyIncludeEmailListStruct, typing.Dict[builtins.str, typing.Any]]] = None,
    everyone: typing.Optional[typing.Union[ZeroTrustAccessPolicyIncludeEveryone, typing.Dict[builtins.str, typing.Any]]] = None,
    external_evaluation: typing.Optional[typing.Union[ZeroTrustAccessPolicyIncludeExternalEvaluation, typing.Dict[builtins.str, typing.Any]]] = None,
    geo: typing.Optional[typing.Union[ZeroTrustAccessPolicyIncludeGeo, typing.Dict[builtins.str, typing.Any]]] = None,
    github_organization: typing.Optional[typing.Union[ZeroTrustAccessPolicyIncludeGithubOrganization, typing.Dict[builtins.str, typing.Any]]] = None,
    group: typing.Optional[typing.Union[ZeroTrustAccessPolicyIncludeGroup, typing.Dict[builtins.str, typing.Any]]] = None,
    gsuite: typing.Optional[typing.Union[ZeroTrustAccessPolicyIncludeGsuite, typing.Dict[builtins.str, typing.Any]]] = None,
    ip: typing.Optional[typing.Union[ZeroTrustAccessPolicyIncludeIp, typing.Dict[builtins.str, typing.Any]]] = None,
    ip_list: typing.Optional[typing.Union[ZeroTrustAccessPolicyIncludeIpListStruct, typing.Dict[builtins.str, typing.Any]]] = None,
    linked_app_token: typing.Optional[typing.Union[ZeroTrustAccessPolicyIncludeLinkedAppToken, typing.Dict[builtins.str, typing.Any]]] = None,
    login_method: typing.Optional[typing.Union[ZeroTrustAccessPolicyIncludeLoginMethod, typing.Dict[builtins.str, typing.Any]]] = None,
    oidc: typing.Optional[typing.Union[ZeroTrustAccessPolicyIncludeOidc, typing.Dict[builtins.str, typing.Any]]] = None,
    okta: typing.Optional[typing.Union[ZeroTrustAccessPolicyIncludeOkta, typing.Dict[builtins.str, typing.Any]]] = None,
    saml: typing.Optional[typing.Union[ZeroTrustAccessPolicyIncludeSaml, typing.Dict[builtins.str, typing.Any]]] = None,
    service_token: typing.Optional[typing.Union[ZeroTrustAccessPolicyIncludeServiceToken, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd86358aec538bb10e394b6be823e5e6ece505f319bb1b64c4235c6c61ad2401(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61e76cb06860fbfbada882993aa6c4fda6560193b982a4cb48580b2c6bfebeb6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeAnyValidServiceToken]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__781e9053f06d82ec604e4248e23de31214f270847a7df5cce49144ee3c5a15c6(
    *,
    ac_id: builtins.str,
    id: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bbfffc801df5041436dc9a457fe8d3fe520d7d8d74db4018c917a5361668553(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c331f7a80c4b9cda857afd4cae2df295df4cbdecc2eb1c35d80d9919d8b94f9c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__551bef813169c94bf2a71788becb7be8af03b1d301f2b3e9e81fc19a7a676b59(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4a5ebc3557ca0ea2f588a769165827bd4f111ce31bd3f5f18c5f32e7a0d92d4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5f4935e195ea5e382584cdc213d3177beb9bfe4cb3bb04e5e274b1a23482a39(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeAuthContext]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9270352f597bbcc686d6a9877f8cbb08c4a6a4783d2382e7d6c71ac7ba3929b9(
    *,
    auth_method: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a1cb51482775867cfb35cdc5c193a15c1b03859b96e61426a8522bf15651a25(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acaa3a67d0aa5269fb136b648954c32e9e80e4f890c3f7aa57e601a27745ce9a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da191d71057bd9ef53c26adc126a6fa6127f2dea09989ecd33cf680672009a31(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeAuthMethod]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bd107b6a7f7170f086a6cf6b79e01e1c7919d2e746d729ae10e7a2e499f1025(
    *,
    id: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c0d8d387b02f9f6caf3a92ff95488ed3166869cfebf45590b5a1145bcb3ce45(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32bb6c8f792d833cc1e32113999be244b1c319665366080638313ba4ce608b7b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f020128e536badbc6ff3f7f02c5d19225c024dc50851dcdfa4f59207963e3ac9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbf2956abec4edae960965394bd502d1237787b4c6e7d4de826221dd963a58d6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeAzureAd]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f22a761710becc6c1b3a644a73caf05a575748e802915656f4c4db71a02cdcc5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f5c43733f80f99b2ff2f1e8639e0d6e73737f659ac158f39226bd99d3098f48(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeCertificate]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5aa9dd6b5e97243767e16727117ec07504704ffc4fc95508009069ab9925429f(
    *,
    common_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a43acd6445200d53505a8bc528899e7b0244c4a65e24b8e23bdb4f6517ddaeb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1a8b44081887709d3ba18dc65f88ad6cc33617bb4fa617db4b58cf07afe5bbd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e47bbc55b770047d8c96325e0ebb9d9ba01bb127c9a23f27ada317410045b63(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeCommonName]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52d4172af1a73d3d34e283c4f334e2298ca329aad0e5751595cfc095776a18f9(
    *,
    integration_uid: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b77c359b1c1ce923d8399aaacb9228da331c06d16f9f3848af9cd4ac30badea5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e6bda13a29a5ce536793e27959c8837b3178daa071a22791d8459fd63edd7ab(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0bc7980fe105bf86440d6eae6c66ad0ce4e017298dba7ad17b7726cf5a59ba3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeDevicePosture]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8611e4c3017196b60615760bbb2b357f6c250eb0d2fbacd560e6f6c5755a5835(
    *,
    email: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e4f33ebbcfb2b294ced7bcaa44220d2546564da6c9fa4a5df5e637a1d45da8d(
    *,
    domain: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e19ae8402c9544d39056fd0de1a7b252dc632dabaa27c6228cc5961cb2a9e78a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d1bc5e16f802d517a35b9e42b98e8b216e88c5bc417a9a694af5dcd3be0d0ef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__933429a68d8a88bd0e47fec8eab9475978679a36d23fdef0e29578df642a2c0f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeEmailDomain]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__092b82806b61eac4892dfee8a89e3b7acdda74a4525bcf9a2bf62aefc8e48314(
    *,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e51a0fdb95eb96116cf5cd3a15b45e6f6baa9e45508b419eac3ca65b0648693(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c77835058d2588dc236a931fa117a36e7839fe9eb0cab8fa9d11f386b5c9a5a3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dececbaa454223a4df483b9300af4539a755b57cefc2f8ee51c9398b39d75597(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeEmailListStruct]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f77caabf1f8b5d617eb4c6cdcca0efb66ca88365360639baa95a0fd526017ddc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56a17d037349a6a29f4c100c818f7c19529f3fb451f35ff984259d11ac73e017(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3b011b0ae1db73b21e31f7d3c70db9c2b5639b63dd33eb37d8582d123072616(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeEmail]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6995d19f84c0477ba6e4346e51e55ba20f95ab00e0e11d98eb712cb646dfe856(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbbf6770b4ebe2215fa4ff8057d84b5a3fd614ec811b56d15538717e40a9ede3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeEveryone]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__834fdc2937036d1d34196379875638d3857b05f01fb6392bb029b8c5c95e5f1b(
    *,
    evaluate_url: builtins.str,
    keys_url: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2474259f73939749f6c518c86f96993869dbd012d1d105c453d6d2bf878b6bc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__623e76f372302c9409a3e8e9b623a1df3f0ba6c88b8fb3de4e2378af2626c8ce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8095dc78ff13e3de511bb08b78c1d79281cacbe409360cf6762d02e1342bb600(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__996db842431b7909b752892add7ba8e74ba26f7956c5f4354c8a47c7a83fe6dc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeExternalEvaluation]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f6d70c9a082ad2f8a451a889a7a04299549ae9a8b854bcb9109cdeacf3352de(
    *,
    country_code: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74bda68eda7943b0d57912ceacdb57c29b264c29bf55ac7d88aa81c98fa2bfaa(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__509cd44692315253b68ff6bf8c6e6d5bbf3c0a01ce697d0379ae09f9cdb6d4d9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48396154bc10bc520e86f7872f00ba860ef5da50c7dc4dc736dfeb6e2e4d14ee(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeGeo]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55f1d3cc8f727c740db84e1e32fd28c0ab46664d0950f251f25526b5fb5c4c44(
    *,
    identity_provider_id: builtins.str,
    name: builtins.str,
    team: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__164c4d078acaba1fa9f73c8ea6425e2be8fc1e0a55fad4ea49a5a44e2d14cbd9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10d9991766622777d94cedf8487a5e407e37dfd9a76a4fd7a7a97684043d43c2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e27b2ae9fbbbf5eee5cadc076716d137830510962b70e136cfe106a8cd04341c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f901518ec77e37753363ebe6bd54b52fdf78454ed9b34f0930c2b6fd7579795b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4309feff65deaee3b46b23965cb89915db368538f17cdcafd84ad483e2cd5f2c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeGithubOrganization]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0dbaf5609d8c9b03816c986a5a6c21b960ccaa71c3d53a76fdae285cecb8e008(
    *,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47514bb6e8e668f5f0bf5c0d34168dbc0b5a9faa9a2c8a71158fb1efd7ae643d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ea842883f022b6afdfccc36936f1840327be030da60b80f18c20de9521b76ce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb40d2fbd7a867e2052d6df519afd09390e8971ccdf5e0618ebfb699875039cb(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeGroup]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c92e02eade7181ee80d27b73ff8c93e5abce28f5003140240318bc1f9ebeaa72(
    *,
    email: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__073dcd62decb1084eaf33923245b2e90c924f04f85aa1b75501e44fb07c7afa3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5265c081b3159b4567e2fba7b02be9bc8e68f1f50eef361b2799f43360a78201(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b4d86becdc495f105fb842e8819037de4e9c805817464a882b3daa219fd29d6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae2666292c2d540e0cab7d77f151e0ed55cb4e631420dcf275c58e5ebe900ca4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeGsuite]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d3e2246ec1accde7496d18c665b2646007c70d6f6331ecf8f0784ec62486143(
    *,
    ip: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82e68811c744ec9675ca7ee71832fd2f233ab82ef485554d6506264e004d3edc(
    *,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6e80881b460285247018d2959cdde77b26e494c261b014f38862058a862298f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e31a146a12674d179f71f15c2d98f91ec412c4a4a56a6bf4722fec1bf01fe996(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2589db0dff30ecbb74380f7da7630c3bd988f4d13cb3174e6d2ac1b707e518f6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeIpListStruct]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f24ae147e37e732b7e3bcf88368c5e4f010d61c086e69307ebd4f68f0582d84(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a26899b1080959ff0d7041ca8bfeb0c1b6d7c6c5045d89e86c73a33f66e99243(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__506df49184c74d33107b23cee2404d2875f4f78bb9f218afa86e9385159a262e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeIp]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba40fdacec4dd44d00bd4d43200ed7382ee0688020eaf0d65f601ced38d9c156(
    *,
    app_uid: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__299452d302911794388a69e6fbaa8da53e7b09751c8dbc669b1edbda14756f25(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aabdff0399bd9866f61d3b99e57617156e8e593f6810b115a777c5d673249d79(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5d412a9132cf8a9f10e6d3f9907ee1d5f33c7fae64e26e630c3901ba3c72c9d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeLinkedAppToken]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcbfe0f7100a78c79ace647b1ff4352d9308b499a7eb39491c9d722c23a6105a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4e713f45f22abe18c5ba8e2e56276024a701fc34673eebfa884b33a8ee48761(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f2e293aad229ef751d9ac1f62d9915238936ab67db0723db2babf1d646cd462(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4097638984fe7b1642aae1d74d4ac5e77e79590ea8821ff58098b3fcfe692228(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67ca617d1837b4a7a6ca87201242f98245f9b50fb1f828ef958f380f9410483c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa018ba929260653e91486d503e78806f98ea1dacca34e7b48fdb935d25e8bc6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessPolicyInclude]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d8dbbfa01bd6a9be398b16f05cb53f8eee1d5de23bcdb82af68bc307d598542(
    *,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca045ff8184f19dd9fd35d90b28d8c5682d5262e716922c1e5e75e0df84758d6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6150d0a0a9048bf5dcf9009181560246daf3b193341d2ac14148afcdd141f28c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53a877d574de2321040473c213e93157c97b03bdb1cd52d2d36023356e4b9027(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeLoginMethod]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dce6ae9d2d8043d02a0b4bb1b9f01f58a184d9efdb86592a32b57956c4aec6f8(
    *,
    claim_name: builtins.str,
    claim_value: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__282b245c282b3fee52107b977b3841e3334ce8a87f70d5b5d4f54e9e98d55e64(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e609963f4c8bb8ae3a030e307b279211c09611643f09a45321c76ae0dfe9f571(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cef078c1c371540b54448492d732c3823b2b33d14ac9a797c06a19b99558caa3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d726f4aa5aac10fba4f11c936e12c431e76bce42245c0453429e6b22f9515339(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3ad2271a6f420e201a8adcc91de2223142fbb33db9694adbd892bdfdaad1eb0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeOidc]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85ecd512ac738602091d80049ebaee14f828df63a8c54d8e1924f45fa8023872(
    *,
    identity_provider_id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa26e2ad5ceab0f3a9dbc02b3e943a0bb9a843dab5c584323b8fba6f512a4a9b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73d6d12c72bb67226d7d0758bfce0e9b8f44f4c9baa61793e22b256581008feb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96504b4c72c9011a0b83db3816cc5232269a16656e055ef4124b8ce40928e996(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__128ad5f532dab3561fd1663d19cf2f1f6d64830f1361f709dd552c525a8ea472(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeOkta]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5e8e7142ffbfddda1dbca8a8320ab3296da6905ef82749c54cc2cb68cff145a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a5de837a78ad9109022b4feec750fe1f1c93f15069890759bc165b48112d7e9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyInclude]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2cfbb42f861777f7b70640ef307bf6e10ff48843c019815300af6cf6fd84285(
    *,
    attribute_name: builtins.str,
    attribute_value: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d4d834aca93052ab47db4a2d54bbeb5a6dc6411e11c53c7701e881ced50ad34(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__151696e5824ee390fdcb4f23eabf8598f7dfd323e645ef86f5d0c2abd1e238e1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d0a9f55b1e45b8e70507bef6728f94417b16d018cdc22ed4d666233172fa265(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b0dcc6b0a719a2974c96478ecbe10f80530ca042a67ebce71a5f97080385667(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91f5ec3b9d8ca36fb847c34afd7e138d092e675a3e554428837ed0f06ccd5750(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeSaml]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a477d5833b4bf9c40e3aa4e1f37e260270a2cdca03944d5d53892b382ffa53e5(
    *,
    token_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1e22f9c6d2ef171eb4bab405fd9db42cbabda6bf7148e0fe87fc78b40e8f9f2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b0e85d36b21a3860fe6d4c23db21e2c587396c6cbfd5e9ee9ff7858435d77ba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b8cc9cfb300a458588a7da5cd44849a18180e6da5a7b82cf149de9245a64f87(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyIncludeServiceToken]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58976fcac7d8164c4ed31294320307b3fff1b949a56e45312971fcebaf316e9d(
    *,
    any_valid_service_token: typing.Optional[typing.Union[ZeroTrustAccessPolicyRequireAnyValidServiceToken, typing.Dict[builtins.str, typing.Any]]] = None,
    auth_context: typing.Optional[typing.Union[ZeroTrustAccessPolicyRequireAuthContext, typing.Dict[builtins.str, typing.Any]]] = None,
    auth_method: typing.Optional[typing.Union[ZeroTrustAccessPolicyRequireAuthMethod, typing.Dict[builtins.str, typing.Any]]] = None,
    azure_ad: typing.Optional[typing.Union[ZeroTrustAccessPolicyRequireAzureAd, typing.Dict[builtins.str, typing.Any]]] = None,
    certificate: typing.Optional[typing.Union[ZeroTrustAccessPolicyRequireCertificate, typing.Dict[builtins.str, typing.Any]]] = None,
    common_name: typing.Optional[typing.Union[ZeroTrustAccessPolicyRequireCommonName, typing.Dict[builtins.str, typing.Any]]] = None,
    device_posture: typing.Optional[typing.Union[ZeroTrustAccessPolicyRequireDevicePosture, typing.Dict[builtins.str, typing.Any]]] = None,
    email: typing.Optional[typing.Union[ZeroTrustAccessPolicyRequireEmail, typing.Dict[builtins.str, typing.Any]]] = None,
    email_domain: typing.Optional[typing.Union[ZeroTrustAccessPolicyRequireEmailDomain, typing.Dict[builtins.str, typing.Any]]] = None,
    email_list: typing.Optional[typing.Union[ZeroTrustAccessPolicyRequireEmailListStruct, typing.Dict[builtins.str, typing.Any]]] = None,
    everyone: typing.Optional[typing.Union[ZeroTrustAccessPolicyRequireEveryone, typing.Dict[builtins.str, typing.Any]]] = None,
    external_evaluation: typing.Optional[typing.Union[ZeroTrustAccessPolicyRequireExternalEvaluation, typing.Dict[builtins.str, typing.Any]]] = None,
    geo: typing.Optional[typing.Union[ZeroTrustAccessPolicyRequireGeo, typing.Dict[builtins.str, typing.Any]]] = None,
    github_organization: typing.Optional[typing.Union[ZeroTrustAccessPolicyRequireGithubOrganization, typing.Dict[builtins.str, typing.Any]]] = None,
    group: typing.Optional[typing.Union[ZeroTrustAccessPolicyRequireGroup, typing.Dict[builtins.str, typing.Any]]] = None,
    gsuite: typing.Optional[typing.Union[ZeroTrustAccessPolicyRequireGsuite, typing.Dict[builtins.str, typing.Any]]] = None,
    ip: typing.Optional[typing.Union[ZeroTrustAccessPolicyRequireIp, typing.Dict[builtins.str, typing.Any]]] = None,
    ip_list: typing.Optional[typing.Union[ZeroTrustAccessPolicyRequireIpListStruct, typing.Dict[builtins.str, typing.Any]]] = None,
    linked_app_token: typing.Optional[typing.Union[ZeroTrustAccessPolicyRequireLinkedAppToken, typing.Dict[builtins.str, typing.Any]]] = None,
    login_method: typing.Optional[typing.Union[ZeroTrustAccessPolicyRequireLoginMethod, typing.Dict[builtins.str, typing.Any]]] = None,
    oidc: typing.Optional[typing.Union[ZeroTrustAccessPolicyRequireOidc, typing.Dict[builtins.str, typing.Any]]] = None,
    okta: typing.Optional[typing.Union[ZeroTrustAccessPolicyRequireOkta, typing.Dict[builtins.str, typing.Any]]] = None,
    saml: typing.Optional[typing.Union[ZeroTrustAccessPolicyRequireSaml, typing.Dict[builtins.str, typing.Any]]] = None,
    service_token: typing.Optional[typing.Union[ZeroTrustAccessPolicyRequireServiceToken, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1131041e506ba91bc7a2f4787797d49cb19bbe0dfab3724e1e18d18f67cba6ee(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1b28565387ffdf20e09da911bb7f80d11dc9151db98b0a5dbc7332c77012ddc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireAnyValidServiceToken]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f9e2bf589c96f50c300e14cb1022250d685a2e4266403c6b00b7670e11b5375(
    *,
    ac_id: builtins.str,
    id: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__890f96ded9d41fc3bb5835a05958eebde4321d241c78eaac24f85e0b0f4805ec(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69602fe74fc46551e5ee3c97a0fbdacb97303e560537f55dd4efd167f619580e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__161cb4cd3c7170de61f48bdd5a691061cf2461894d8460cb97ed6aac75cb3468(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfd02a0aceb9ba37258894ca35fac9f29c6539845c1bcfcd7c41de8c3f38bf8c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3881b3ecc14d9098a6a753d8ef9d3460e034cef9dd5f63cbbe3816a23fd0b5f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireAuthContext]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6180c715a0bd35181fbcd823425c718be3d526c287bd9414c30cd0affa11c5d(
    *,
    auth_method: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4f1c25764057793364f8294a23f6e702e8e2122b95003e755f04c8703e1d2de(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fc94e6545c58b99606f93e02c346ce0bb64c6e6777d93378f10e387d827a6c8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4f421b665b43b234c9a91f03cd7c1544e8d85871df1145fd2bdb44cf1947f3b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireAuthMethod]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02b0f9933d5cb10f1552baf20f69b6fa1e1b829bf9457ed8e9cd30def2d47ae2(
    *,
    id: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70734c49ace01c4a72cb92b2bddc6142e4b5fc4cebde91ab40671ca17b6f35e2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b0a9a873ed0f78cd22f347e2f4d939697e49be4e414b96ba093dff16a3eac1a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a718d94c2f11a8b27d5fb92eceb7bbd1ca6b231a91a18321e9f7105723552d14(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3160ec7cadac71220b82bdcec5934e0a6b87f8a4394c88ba3221c02a05538371(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireAzureAd]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__822eb05e398c48b5908254c612f34213e26fe40739b12ead04ecb9f3f98ae794(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2814c7faeb30667af2e690a65138fe47bb1fad91ee0752d7872bcce951287c9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireCertificate]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c8253f767a8e03811f3bcfbc509a656d67d488c3714d48f0973ea0029fb35f4(
    *,
    common_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3346151543bc880e07fb5ea4711f4e2b43515cdc4f0a9f042705c86bc109319(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbd59fd81aa7dc6b3fc3eedccfb4781c51e221e04dba2fcf908e973eaed9b19c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4cb4e66f97c0ad33dbdf62ca033d1e62dcf6f8b6f0c19391e855e11fa8843275(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireCommonName]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61ba650eb1c758c108abbf32356c62101f0561f8bc3ad2e1cfe6e6c05c984ce0(
    *,
    integration_uid: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d03f83b87b352f8aacd3b38779057a3164f0d4453403e71aba31ad8eca58af1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cfdbd1fec8d5120d383d3522706f2487d9a5bedda05071cf86e008e3ec6aec8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5adf2391d8ab7851a42c324e650c7d834f8c60caa335dc4699c208ac1538e6ad(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireDevicePosture]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0d6b344a6789e0f3b57acdbe17de58d4d79101c792fb93caf4e1d06a01eb4c8(
    *,
    email: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e83296ac4ec0e844e09253cb9c403bad993ea920c6421c65d6b1fa5a4b986677(
    *,
    domain: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e693cac2ce604c4d9139d367d0873685103a36afeaea7ceb387e0dde7b12de82(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1f705bfe1a7e6b18f869c07d5d933d1caf7a74ac998cc2239acecb358695ff6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1fc4f38c377842236815fefae64852e648b3f9620ca359a89062fa794437bae(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireEmailDomain]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3c012a4dd616da3731d45965bf9cb44f1cea8e3c8f5d1c162e1d23712faad3d(
    *,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd02fedb59332fad528d6b7812deb2f4c3fb72130c94d4f4b310b57642181e91(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f6b87640a27662869d926968c18b8ccac355eb71e7c9321e45ef176915f24f9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac6f322aeae6998c1d5f0080a7b803a71ff9822e283d42495f00b9b4f366eac5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireEmailListStruct]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c51d9b1fb4d733abb39d64b3194cfd2758a80ae4eb40a14268122473d76ad1fb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0989635a7502d57e7de5d4bc13c95cab05147edc907d1f02f0de6c11644c535(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24f4700bbaaef32a483d4d7ea9bf311b0f4ee63de430e2392d9d6e9770f53666(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireEmail]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac6d527399aabb5fe73a2613991c064c63a8a1f8c18a062b09844b2d880aea0d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9846f128cca04be3d543ab91aabcfbaa9d9c2b95d20552f3726570f50df55fa9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireEveryone]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca489b5c8d70b7fd12691784b5e28c5ee9ffdfbec65768ed578bdfdcda7459c8(
    *,
    evaluate_url: builtins.str,
    keys_url: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92ddf25f04fb09aa2782e036dcc0f6affa237e0db425c41b8b92a8164bbdca39(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0741f8074543787f8c4bf90211bb988efe81ea1500baa6f1fd85006d61f5ebe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72a8ab5caa5fc91bd96da810518ffe482225716321c8da3f9558f538a169cf5a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2be2364117b00f01b16bd5e10098c971b83fb8e81c72eba10bc2e8d1ef5780d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireExternalEvaluation]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06fb394044a3d18803c0ab114b1e817b93edd9d905adaa0f25f621990e22d5b9(
    *,
    country_code: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eceb9f194e4034e29acf4a14c242b772995b5b928d027766de135fd5fd4e20be(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44e435831024a1a82abd4fd23e041d4244221f0134285ce3f27cf164d027071e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__037ed65890808d9032a6772b579ca7dea7e553d6372a18391576c0bdcd0e86d6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireGeo]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ce3812a2103dda2a17ecdb274fb89dc52741c301b03071903cf123cc33d3401(
    *,
    identity_provider_id: builtins.str,
    name: builtins.str,
    team: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c83c6be35ae10eb0a77b61831298810c6b42d148d5a302533f3b0221565bec8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8677266858d0d1c0ae0e6886710fb476dac8a37ce934bcc0b9924624260da0d1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5126c0b6e8ea67d283b61e77fe18e89ba86fba657a24ebc72a06018265966ec8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fae1c3f771e2978086226a1853fdfdd318b0e4d015148f3fe96474fc8fc71032(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__606dda372431751075e6156fdcfc73f24b5986b74b4b82eb3fc6e698905fb8b5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireGithubOrganization]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c98c2ee705b69842ad1b534dd50413eba4cb27f9e8bc0f5f7f340a6b1ced909(
    *,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a67be8266a74ef6676211ce234cb926a4e6537a067bb4f59aa0d53e0f9324c50(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38d972eea7a94abc9a07709179466dd2cd958f4ecb4fbe0bb4888d73cb000443(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__060dd7024d2c4a3d44267f3f300b123fc419c9819acacacd44956165e0aeab18(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireGroup]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c58c38961e51cade309e3fe236f38fdb39c8c164f86a95924c6a5f88977918d(
    *,
    email: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52aec0d2fcdd571aab4739868687fd4278584bbff5403ef7b4805b2ee027628b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac982b65e149f4f83538ef449f09ba4e9ace61f7bf644dd1198a1241c496c015(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcf2e49c55892f0985c278dc18afb87ce855bcf73e6f203992607a272d65fef9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4b275d348e9b7d5cefc997a6bec0d4af0208d652e15bd654bbad37bad5455cd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireGsuite]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f7c41a9800db9238ed5f8ffb6270965c984251826fb8ab1bf062fe3431b392f(
    *,
    ip: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18ffab0455ad9edb7e78d589106cbdfce756a8b98b86a64f7a14fa9a124578fe(
    *,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c54c4c69500fea1067e0ac048a3fa1f6cf39674ca35ee951b58c503a18daa28b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c8521fb9b6f8cb33050ab98ff155d04b917136749b423e96d201592ce86f934(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45c465f2f6cde8b100a054dfe98590e05a7b38b77b09d6582c26191a9e8ab119(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireIpListStruct]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0323bfda274ec9a0b8687bb5abf349d9a6f8dd1fc98d7779fd771e4f94000a0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4cc8f696ad76e45b8802dcbffbaa20285d4af313d3d745cbe727ea71eed11c5a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ae1d590703c62c832f4ede7faf891c5f61d8068f20156c8b78079d1c14ac96b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireIp]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__281194b75cc233f93830508df7e4e21a514ea8608c687df520a700732a2fee18(
    *,
    app_uid: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7100e99eb6f7c3a7ee74d22341b7c4691b6c138fcf781a37483dc9c50394598(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1d1b96e6d1725fd36506357f8f28b7d85e5e6eaa092755fd0036392ca47d8e8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b32f3b9505deb6945a9960993b6b30b0d0b5bca6dbe285730b89ddf4d371b67(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireLinkedAppToken]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__add2c7af1d343f4bb0d7e7826dc1c4d07cf9b7922f6853d2886980355e4bbed0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dea9d011fb25866c8d091d1f981dc77d2560cf5f6b8be6c95b436310854a966f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a785377db35a8e537d2e142590ce3c767ead4d19ab9593253c33c48a9b6d58cc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96cc2b3540d204af3049bdb4ade0e917d3d7d91d38d4e78a55285c2035ea9abe(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0423166074d99c0e14f7fb2ab445464b862665ac4a1a8cbabd44715b1e5f2716(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a75698e757a4907432c891aaac58e82d1d29bd76488d269bab88b8c70f119b4c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustAccessPolicyRequire]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c47b2e427ff7e5acfe0a387d54747d064fbd7593a380c559b9201ac2b9262603(
    *,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28e2211b8fdb46d8fd9af761fa72435aae42b7f191fd43fabab5db8f763e4cdd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__682ed63835b3c18f999e06cda4e38acfba0bede92b51a0ffc03750409768cd8b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b8dfce0bf66e507d7098ec4661cb2d2e191096db41ef8a2395ba8f0cb8bd84d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireLoginMethod]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed7e7f2d9301b685201cad3063deec64b5490ecbd85ea0d9a78b615fb2ddb382(
    *,
    claim_name: builtins.str,
    claim_value: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e427edf6e1c43e71fbb5311f22fc2ba0745f552357a7e194316f30a80232e607(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e2e93ef81d78c2500fb4a13109e0f7d7f36c304465e4182d893df5e86c3332c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9863f3f22d8bd1c7a2894a05963b0388f7b1ac0c0be142cbd01c1eadd6d0b98(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d047d0ccd9f4a29f7a724542ebc70ba46f99bcb93a62d1527de7219549b8e55d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__887e837ad181c7bbd27008729b523eb65bbae7f3e5e6ae61cedd74f35517f9de(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireOidc]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__128fd5d7175c44c806d147df2b6e441ed3f710d378daac7e14a21769c24a2d9d(
    *,
    identity_provider_id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__adb3fefe84888c4a7b05466853ba44f87f5315f86ce8ff82ffaf5a99961fe741(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d53d5ea1af4f0422debeabe7ac07819876a1b49b058038cace3f96249e2020b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3aa7fbf983d5228dd8caf31da7d602e0e9d83a3feb30dfdda417fd8adfc0d1af(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8f232d26d2df3dd36231d316664242b52a2f8854ca1bcc4dca3665d4a26226f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireOkta]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a94eaa9a70d6382843d0af7d52f60784ff6f6a1e9b7dd9000bd7a1d8c179e16(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6edfd3e851fb78c0fdfba079e5a79bc22ac6e3f2849664f72ed7a32858fda6d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequire]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__586e7633636de91fde0dacc286d80ba7f992d77dc5e953fa7149a7b340a71a41(
    *,
    attribute_name: builtins.str,
    attribute_value: builtins.str,
    identity_provider_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f8344e714937527b22ce6cf4165b4bc11f9aea89162d784b3c8b5d0b03d3d12(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c33e2cc6dd0599c1c816031bdb76f171a26169a1b40fbd041207f68d5b0a3d26(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb46e9878eb3b195fd89f32076c4439dc9a45ca5ca07598703066216ef1d029a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74cb70b0cf4c81fe78bbeb3b35ba812f5e09ff675115c5f3c9a90c2b6d5a1491(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ec61bc245153747e1e0fa1f004d9190d56a519e68a9bd8a0d8f5fa0f3cf22e0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireSaml]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea70d479a424ec258ff3e9faa00f2be2cd7b4ba97ad9d0579dcc6188f6b4812d(
    *,
    token_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59e8b29a3cd27577d02d208cf27d054aa2ce2c6042cbcaa08bfc07e5b05a21e4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__549a12269d7860ca92ad3250ad82ed8d32409956b6b4201d6f5e81a664902d18(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5df576ea24f19031ae4aa3c0fd788ee761f38cf43c904c793dd26024a895c6d1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustAccessPolicyRequireServiceToken]],
) -> None:
    """Type checking stubs"""
    pass
