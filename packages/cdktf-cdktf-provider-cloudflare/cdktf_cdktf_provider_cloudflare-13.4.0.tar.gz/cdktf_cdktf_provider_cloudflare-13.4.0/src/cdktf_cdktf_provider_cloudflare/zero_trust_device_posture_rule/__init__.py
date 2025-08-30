r'''
# `cloudflare_zero_trust_device_posture_rule`

Refer to the Terraform Registry for docs: [`cloudflare_zero_trust_device_posture_rule`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule).
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


class ZeroTrustDevicePostureRule(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDevicePostureRule.ZeroTrustDevicePostureRule",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule cloudflare_zero_trust_device_posture_rule}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        name: builtins.str,
        type: builtins.str,
        description: typing.Optional[builtins.str] = None,
        expiration: typing.Optional[builtins.str] = None,
        input: typing.Optional[typing.Union["ZeroTrustDevicePostureRuleInput", typing.Dict[builtins.str, typing.Any]]] = None,
        match: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustDevicePostureRuleMatch", typing.Dict[builtins.str, typing.Any]]]]] = None,
        schedule: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule cloudflare_zero_trust_device_posture_rule} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#account_id ZeroTrustDevicePostureRule#account_id}.
        :param name: The name of the device posture rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#name ZeroTrustDevicePostureRule#name}
        :param type: The type of device posture rule. Available values: "file", "application", "tanium", "gateway", "warp", "disk_encryption", "serial_number", "sentinelone", "carbonblack", "firewall", "os_version", "domain_joined", "client_certificate", "client_certificate_v2", "unique_client_id", "kolide", "tanium_s2s", "crowdstrike_s2s", "intune", "workspace_one", "sentinelone_s2s", "custom_s2s". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#type ZeroTrustDevicePostureRule#type}
        :param description: The description of the device posture rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#description ZeroTrustDevicePostureRule#description}
        :param expiration: Sets the expiration time for a posture check result. If empty, the result remains valid until it is overwritten by new data from the WARP client. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#expiration ZeroTrustDevicePostureRule#expiration}
        :param input: The value to be checked against. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#input ZeroTrustDevicePostureRule#input}
        :param match: The conditions that the client must match to run the rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#match ZeroTrustDevicePostureRule#match}
        :param schedule: Polling frequency for the WARP client posture check. Default: ``5m`` (poll every five minutes). Minimum: ``1m``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#schedule ZeroTrustDevicePostureRule#schedule}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd60b48f6bf9792c09d2f75e75ecfba2938a4d14986bca399156b4cbc246dd4b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = ZeroTrustDevicePostureRuleConfig(
            account_id=account_id,
            name=name,
            type=type,
            description=description,
            expiration=expiration,
            input=input,
            match=match,
            schedule=schedule,
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
        '''Generates CDKTF code for importing a ZeroTrustDevicePostureRule resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ZeroTrustDevicePostureRule to import.
        :param import_from_id: The id of the existing ZeroTrustDevicePostureRule that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ZeroTrustDevicePostureRule to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62e0789401a7db589386f102caa8fce22c7b5c14e94d978f4b67313c95d5bb6b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putInput")
    def put_input(
        self,
        *,
        active_threats: typing.Optional[jsii.Number] = None,
        certificate_id: typing.Optional[builtins.str] = None,
        check_disks: typing.Optional[typing.Sequence[builtins.str]] = None,
        check_private_key: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cn: typing.Optional[builtins.str] = None,
        compliance_status: typing.Optional[builtins.str] = None,
        connection_id: typing.Optional[builtins.str] = None,
        count_operator: typing.Optional[builtins.str] = None,
        domain: typing.Optional[builtins.str] = None,
        eid_last_seen: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        exists: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        extended_key_usage: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        infected: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        is_active: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        issue_count: typing.Optional[builtins.str] = None,
        last_seen: typing.Optional[builtins.str] = None,
        locations: typing.Optional[typing.Union["ZeroTrustDevicePostureRuleInputLocations", typing.Dict[builtins.str, typing.Any]]] = None,
        network_status: typing.Optional[builtins.str] = None,
        operating_system: typing.Optional[builtins.str] = None,
        operational_state: typing.Optional[builtins.str] = None,
        operator: typing.Optional[builtins.str] = None,
        os: typing.Optional[builtins.str] = None,
        os_distro_name: typing.Optional[builtins.str] = None,
        os_distro_revision: typing.Optional[builtins.str] = None,
        os_version_extra: typing.Optional[builtins.str] = None,
        overall: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
        require_all: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        risk_level: typing.Optional[builtins.str] = None,
        score: typing.Optional[jsii.Number] = None,
        score_operator: typing.Optional[builtins.str] = None,
        sensor_config: typing.Optional[builtins.str] = None,
        sha256: typing.Optional[builtins.str] = None,
        state: typing.Optional[builtins.str] = None,
        subject_alternative_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        thumbprint: typing.Optional[builtins.str] = None,
        total_score: typing.Optional[jsii.Number] = None,
        version: typing.Optional[builtins.str] = None,
        version_operator: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param active_threats: The Number of active threats. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#active_threats ZeroTrustDevicePostureRule#active_threats}
        :param certificate_id: UUID of Cloudflare managed certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#certificate_id ZeroTrustDevicePostureRule#certificate_id}
        :param check_disks: List of volume names to be checked for encryption. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#check_disks ZeroTrustDevicePostureRule#check_disks}
        :param check_private_key: Confirm the certificate was not imported from another device. We recommend keeping this enabled unless the certificate was deployed without a private key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#check_private_key ZeroTrustDevicePostureRule#check_private_key}
        :param cn: Common Name that is protected by the certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#cn ZeroTrustDevicePostureRule#cn}
        :param compliance_status: Compliance Status. Available values: "compliant", "noncompliant", "unknown", "notapplicable", "ingraceperiod", "error". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#compliance_status ZeroTrustDevicePostureRule#compliance_status}
        :param connection_id: Posture Integration ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#connection_id ZeroTrustDevicePostureRule#connection_id}
        :param count_operator: Count Operator. Available values: "<", "<=", ">", ">=", "==". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#count_operator ZeroTrustDevicePostureRule#count_operator}
        :param domain: Domain. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#domain ZeroTrustDevicePostureRule#domain}
        :param eid_last_seen: For more details on eid last seen, refer to the Tanium documentation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#eid_last_seen ZeroTrustDevicePostureRule#eid_last_seen}
        :param enabled: Enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#enabled ZeroTrustDevicePostureRule#enabled}
        :param exists: Whether or not file exists. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#exists ZeroTrustDevicePostureRule#exists}
        :param extended_key_usage: List of values indicating purposes for which the certificate public key can be used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#extended_key_usage ZeroTrustDevicePostureRule#extended_key_usage}
        :param id: List ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#id ZeroTrustDevicePostureRule#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param infected: Whether device is infected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#infected ZeroTrustDevicePostureRule#infected}
        :param is_active: Whether device is active. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#is_active ZeroTrustDevicePostureRule#is_active}
        :param issue_count: The Number of Issues. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#issue_count ZeroTrustDevicePostureRule#issue_count}
        :param last_seen: For more details on last seen, please refer to the Crowdstrike documentation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#last_seen ZeroTrustDevicePostureRule#last_seen}
        :param locations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#locations ZeroTrustDevicePostureRule#locations}.
        :param network_status: Network status of device. Available values: "connected", "disconnected", "disconnecting", "connecting". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#network_status ZeroTrustDevicePostureRule#network_status}
        :param operating_system: Operating system. Available values: "windows", "linux", "mac", "android", "ios", "chromeos". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#operating_system ZeroTrustDevicePostureRule#operating_system}
        :param operational_state: Agent operational state. Available values: "na", "partially_disabled", "auto_fully_disabled", "fully_disabled", "auto_partially_disabled", "disabled_error", "db_corruption". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#operational_state ZeroTrustDevicePostureRule#operational_state}
        :param operator: Operator. Available values: "<", "<=", ">", ">=", "==". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#operator ZeroTrustDevicePostureRule#operator}
        :param os: Os Version. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#os ZeroTrustDevicePostureRule#os}
        :param os_distro_name: Operating System Distribution Name (linux only). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#os_distro_name ZeroTrustDevicePostureRule#os_distro_name}
        :param os_distro_revision: Version of OS Distribution (linux only). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#os_distro_revision ZeroTrustDevicePostureRule#os_distro_revision}
        :param os_version_extra: Additional version data. For Mac or iOS, the Product Version Extra. For Linux, the kernel release version. (Mac, iOS, and Linux only). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#os_version_extra ZeroTrustDevicePostureRule#os_version_extra}
        :param overall: Overall. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#overall ZeroTrustDevicePostureRule#overall}
        :param path: File path. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#path ZeroTrustDevicePostureRule#path}
        :param require_all: Whether to check all disks for encryption. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#require_all ZeroTrustDevicePostureRule#require_all}
        :param risk_level: For more details on risk level, refer to the Tanium documentation. Available values: "low", "medium", "high", "critical". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#risk_level ZeroTrustDevicePostureRule#risk_level}
        :param score: A value between 0-100 assigned to devices set by the 3rd party posture provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#score ZeroTrustDevicePostureRule#score}
        :param score_operator: Score Operator. Available values: "<", "<=", ">", ">=", "==". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#score_operator ZeroTrustDevicePostureRule#score_operator}
        :param sensor_config: SensorConfig. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#sensor_config ZeroTrustDevicePostureRule#sensor_config}
        :param sha256: SHA-256. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#sha256 ZeroTrustDevicePostureRule#sha256}
        :param state: For more details on state, please refer to the Crowdstrike documentation. Available values: "online", "offline", "unknown". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#state ZeroTrustDevicePostureRule#state}
        :param subject_alternative_names: List of certificate Subject Alternative Names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#subject_alternative_names ZeroTrustDevicePostureRule#subject_alternative_names}
        :param thumbprint: Signing certificate thumbprint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#thumbprint ZeroTrustDevicePostureRule#thumbprint}
        :param total_score: For more details on total score, refer to the Tanium documentation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#total_score ZeroTrustDevicePostureRule#total_score}
        :param version: Version of OS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#version ZeroTrustDevicePostureRule#version}
        :param version_operator: Version Operator. Available values: "<", "<=", ">", ">=", "==". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#version_operator ZeroTrustDevicePostureRule#version_operator}
        '''
        value = ZeroTrustDevicePostureRuleInput(
            active_threats=active_threats,
            certificate_id=certificate_id,
            check_disks=check_disks,
            check_private_key=check_private_key,
            cn=cn,
            compliance_status=compliance_status,
            connection_id=connection_id,
            count_operator=count_operator,
            domain=domain,
            eid_last_seen=eid_last_seen,
            enabled=enabled,
            exists=exists,
            extended_key_usage=extended_key_usage,
            id=id,
            infected=infected,
            is_active=is_active,
            issue_count=issue_count,
            last_seen=last_seen,
            locations=locations,
            network_status=network_status,
            operating_system=operating_system,
            operational_state=operational_state,
            operator=operator,
            os=os,
            os_distro_name=os_distro_name,
            os_distro_revision=os_distro_revision,
            os_version_extra=os_version_extra,
            overall=overall,
            path=path,
            require_all=require_all,
            risk_level=risk_level,
            score=score,
            score_operator=score_operator,
            sensor_config=sensor_config,
            sha256=sha256,
            state=state,
            subject_alternative_names=subject_alternative_names,
            thumbprint=thumbprint,
            total_score=total_score,
            version=version,
            version_operator=version_operator,
        )

        return typing.cast(None, jsii.invoke(self, "putInput", [value]))

    @jsii.member(jsii_name="putMatch")
    def put_match(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustDevicePostureRuleMatch", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fc17380a3e81f9d5e8c16bcfb7c4cf1e5eb49fdd4a73f414f240b3c45f410ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putMatch", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetExpiration")
    def reset_expiration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExpiration", []))

    @jsii.member(jsii_name="resetInput")
    def reset_input(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInput", []))

    @jsii.member(jsii_name="resetMatch")
    def reset_match(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMatch", []))

    @jsii.member(jsii_name="resetSchedule")
    def reset_schedule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchedule", []))

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
    @jsii.member(jsii_name="input")
    def input(self) -> "ZeroTrustDevicePostureRuleInputOutputReference":
        return typing.cast("ZeroTrustDevicePostureRuleInputOutputReference", jsii.get(self, "input"))

    @builtins.property
    @jsii.member(jsii_name="match")
    def match(self) -> "ZeroTrustDevicePostureRuleMatchList":
        return typing.cast("ZeroTrustDevicePostureRuleMatchList", jsii.get(self, "match"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="expirationInput")
    def expiration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "expirationInput"))

    @builtins.property
    @jsii.member(jsii_name="inputInput")
    def input_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustDevicePostureRuleInput"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZeroTrustDevicePostureRuleInput"]], jsii.get(self, "inputInput"))

    @builtins.property
    @jsii.member(jsii_name="matchInput")
    def match_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDevicePostureRuleMatch"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDevicePostureRuleMatch"]]], jsii.get(self, "matchInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="scheduleInput")
    def schedule_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scheduleInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5032ea93ba752507c67e51361bb4240e9a8c374b606f9faa17d097759528245d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f2537df048390cb809367bd506f1e8f3c12e6a027af5e230080e3bc3399fc07)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="expiration")
    def expiration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "expiration"))

    @expiration.setter
    def expiration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8758a3f0c76bb9261f97e418c99bace38749f2b76a6bc842eabb52f005393126)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "expiration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f05345b945d1a808ccde1cafc3adf60a6a4d6597640c381f19f0522c459f6eca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schedule"))

    @schedule.setter
    def schedule(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d8d9114d9f167670fef321332076433d319a5f2d458e798ff5afb12b77ec3ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "schedule", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c20ba511f64042e6e59f898b0c3df6dc7d5438ba0063c937a3fec3dc4b630fb7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDevicePostureRule.ZeroTrustDevicePostureRuleConfig",
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
        "type": "type",
        "description": "description",
        "expiration": "expiration",
        "input": "input",
        "match": "match",
        "schedule": "schedule",
    },
)
class ZeroTrustDevicePostureRuleConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        type: builtins.str,
        description: typing.Optional[builtins.str] = None,
        expiration: typing.Optional[builtins.str] = None,
        input: typing.Optional[typing.Union["ZeroTrustDevicePostureRuleInput", typing.Dict[builtins.str, typing.Any]]] = None,
        match: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ZeroTrustDevicePostureRuleMatch", typing.Dict[builtins.str, typing.Any]]]]] = None,
        schedule: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#account_id ZeroTrustDevicePostureRule#account_id}.
        :param name: The name of the device posture rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#name ZeroTrustDevicePostureRule#name}
        :param type: The type of device posture rule. Available values: "file", "application", "tanium", "gateway", "warp", "disk_encryption", "serial_number", "sentinelone", "carbonblack", "firewall", "os_version", "domain_joined", "client_certificate", "client_certificate_v2", "unique_client_id", "kolide", "tanium_s2s", "crowdstrike_s2s", "intune", "workspace_one", "sentinelone_s2s", "custom_s2s". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#type ZeroTrustDevicePostureRule#type}
        :param description: The description of the device posture rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#description ZeroTrustDevicePostureRule#description}
        :param expiration: Sets the expiration time for a posture check result. If empty, the result remains valid until it is overwritten by new data from the WARP client. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#expiration ZeroTrustDevicePostureRule#expiration}
        :param input: The value to be checked against. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#input ZeroTrustDevicePostureRule#input}
        :param match: The conditions that the client must match to run the rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#match ZeroTrustDevicePostureRule#match}
        :param schedule: Polling frequency for the WARP client posture check. Default: ``5m`` (poll every five minutes). Minimum: ``1m``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#schedule ZeroTrustDevicePostureRule#schedule}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(input, dict):
            input = ZeroTrustDevicePostureRuleInput(**input)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d71d65986f39d03f15f7ba09af383b7859278d2512ab445f38431e9ee9364c26)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument expiration", value=expiration, expected_type=type_hints["expiration"])
            check_type(argname="argument input", value=input, expected_type=type_hints["input"])
            check_type(argname="argument match", value=match, expected_type=type_hints["match"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
            "name": name,
            "type": type,
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
        if expiration is not None:
            self._values["expiration"] = expiration
        if input is not None:
            self._values["input"] = input
        if match is not None:
            self._values["match"] = match
        if schedule is not None:
            self._values["schedule"] = schedule

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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#account_id ZeroTrustDevicePostureRule#account_id}.'''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the device posture rule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#name ZeroTrustDevicePostureRule#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''The type of device posture rule.

        Available values: "file", "application", "tanium", "gateway", "warp", "disk_encryption", "serial_number", "sentinelone", "carbonblack", "firewall", "os_version", "domain_joined", "client_certificate", "client_certificate_v2", "unique_client_id", "kolide", "tanium_s2s", "crowdstrike_s2s", "intune", "workspace_one", "sentinelone_s2s", "custom_s2s".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#type ZeroTrustDevicePostureRule#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the device posture rule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#description ZeroTrustDevicePostureRule#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def expiration(self) -> typing.Optional[builtins.str]:
        '''Sets the expiration time for a posture check result.

        If empty, the result remains valid until it is overwritten by new data from the WARP client.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#expiration ZeroTrustDevicePostureRule#expiration}
        '''
        result = self._values.get("expiration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def input(self) -> typing.Optional["ZeroTrustDevicePostureRuleInput"]:
        '''The value to be checked against.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#input ZeroTrustDevicePostureRule#input}
        '''
        result = self._values.get("input")
        return typing.cast(typing.Optional["ZeroTrustDevicePostureRuleInput"], result)

    @builtins.property
    def match(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDevicePostureRuleMatch"]]]:
        '''The conditions that the client must match to run the rule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#match ZeroTrustDevicePostureRule#match}
        '''
        result = self._values.get("match")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ZeroTrustDevicePostureRuleMatch"]]], result)

    @builtins.property
    def schedule(self) -> typing.Optional[builtins.str]:
        '''Polling frequency for the WARP client posture check. Default: ``5m`` (poll every five minutes). Minimum: ``1m``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#schedule ZeroTrustDevicePostureRule#schedule}
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustDevicePostureRuleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDevicePostureRule.ZeroTrustDevicePostureRuleInput",
    jsii_struct_bases=[],
    name_mapping={
        "active_threats": "activeThreats",
        "certificate_id": "certificateId",
        "check_disks": "checkDisks",
        "check_private_key": "checkPrivateKey",
        "cn": "cn",
        "compliance_status": "complianceStatus",
        "connection_id": "connectionId",
        "count_operator": "countOperator",
        "domain": "domain",
        "eid_last_seen": "eidLastSeen",
        "enabled": "enabled",
        "exists": "exists",
        "extended_key_usage": "extendedKeyUsage",
        "id": "id",
        "infected": "infected",
        "is_active": "isActive",
        "issue_count": "issueCount",
        "last_seen": "lastSeen",
        "locations": "locations",
        "network_status": "networkStatus",
        "operating_system": "operatingSystem",
        "operational_state": "operationalState",
        "operator": "operator",
        "os": "os",
        "os_distro_name": "osDistroName",
        "os_distro_revision": "osDistroRevision",
        "os_version_extra": "osVersionExtra",
        "overall": "overall",
        "path": "path",
        "require_all": "requireAll",
        "risk_level": "riskLevel",
        "score": "score",
        "score_operator": "scoreOperator",
        "sensor_config": "sensorConfig",
        "sha256": "sha256",
        "state": "state",
        "subject_alternative_names": "subjectAlternativeNames",
        "thumbprint": "thumbprint",
        "total_score": "totalScore",
        "version": "version",
        "version_operator": "versionOperator",
    },
)
class ZeroTrustDevicePostureRuleInput:
    def __init__(
        self,
        *,
        active_threats: typing.Optional[jsii.Number] = None,
        certificate_id: typing.Optional[builtins.str] = None,
        check_disks: typing.Optional[typing.Sequence[builtins.str]] = None,
        check_private_key: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cn: typing.Optional[builtins.str] = None,
        compliance_status: typing.Optional[builtins.str] = None,
        connection_id: typing.Optional[builtins.str] = None,
        count_operator: typing.Optional[builtins.str] = None,
        domain: typing.Optional[builtins.str] = None,
        eid_last_seen: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        exists: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        extended_key_usage: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        infected: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        is_active: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        issue_count: typing.Optional[builtins.str] = None,
        last_seen: typing.Optional[builtins.str] = None,
        locations: typing.Optional[typing.Union["ZeroTrustDevicePostureRuleInputLocations", typing.Dict[builtins.str, typing.Any]]] = None,
        network_status: typing.Optional[builtins.str] = None,
        operating_system: typing.Optional[builtins.str] = None,
        operational_state: typing.Optional[builtins.str] = None,
        operator: typing.Optional[builtins.str] = None,
        os: typing.Optional[builtins.str] = None,
        os_distro_name: typing.Optional[builtins.str] = None,
        os_distro_revision: typing.Optional[builtins.str] = None,
        os_version_extra: typing.Optional[builtins.str] = None,
        overall: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
        require_all: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        risk_level: typing.Optional[builtins.str] = None,
        score: typing.Optional[jsii.Number] = None,
        score_operator: typing.Optional[builtins.str] = None,
        sensor_config: typing.Optional[builtins.str] = None,
        sha256: typing.Optional[builtins.str] = None,
        state: typing.Optional[builtins.str] = None,
        subject_alternative_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        thumbprint: typing.Optional[builtins.str] = None,
        total_score: typing.Optional[jsii.Number] = None,
        version: typing.Optional[builtins.str] = None,
        version_operator: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param active_threats: The Number of active threats. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#active_threats ZeroTrustDevicePostureRule#active_threats}
        :param certificate_id: UUID of Cloudflare managed certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#certificate_id ZeroTrustDevicePostureRule#certificate_id}
        :param check_disks: List of volume names to be checked for encryption. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#check_disks ZeroTrustDevicePostureRule#check_disks}
        :param check_private_key: Confirm the certificate was not imported from another device. We recommend keeping this enabled unless the certificate was deployed without a private key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#check_private_key ZeroTrustDevicePostureRule#check_private_key}
        :param cn: Common Name that is protected by the certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#cn ZeroTrustDevicePostureRule#cn}
        :param compliance_status: Compliance Status. Available values: "compliant", "noncompliant", "unknown", "notapplicable", "ingraceperiod", "error". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#compliance_status ZeroTrustDevicePostureRule#compliance_status}
        :param connection_id: Posture Integration ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#connection_id ZeroTrustDevicePostureRule#connection_id}
        :param count_operator: Count Operator. Available values: "<", "<=", ">", ">=", "==". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#count_operator ZeroTrustDevicePostureRule#count_operator}
        :param domain: Domain. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#domain ZeroTrustDevicePostureRule#domain}
        :param eid_last_seen: For more details on eid last seen, refer to the Tanium documentation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#eid_last_seen ZeroTrustDevicePostureRule#eid_last_seen}
        :param enabled: Enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#enabled ZeroTrustDevicePostureRule#enabled}
        :param exists: Whether or not file exists. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#exists ZeroTrustDevicePostureRule#exists}
        :param extended_key_usage: List of values indicating purposes for which the certificate public key can be used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#extended_key_usage ZeroTrustDevicePostureRule#extended_key_usage}
        :param id: List ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#id ZeroTrustDevicePostureRule#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param infected: Whether device is infected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#infected ZeroTrustDevicePostureRule#infected}
        :param is_active: Whether device is active. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#is_active ZeroTrustDevicePostureRule#is_active}
        :param issue_count: The Number of Issues. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#issue_count ZeroTrustDevicePostureRule#issue_count}
        :param last_seen: For more details on last seen, please refer to the Crowdstrike documentation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#last_seen ZeroTrustDevicePostureRule#last_seen}
        :param locations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#locations ZeroTrustDevicePostureRule#locations}.
        :param network_status: Network status of device. Available values: "connected", "disconnected", "disconnecting", "connecting". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#network_status ZeroTrustDevicePostureRule#network_status}
        :param operating_system: Operating system. Available values: "windows", "linux", "mac", "android", "ios", "chromeos". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#operating_system ZeroTrustDevicePostureRule#operating_system}
        :param operational_state: Agent operational state. Available values: "na", "partially_disabled", "auto_fully_disabled", "fully_disabled", "auto_partially_disabled", "disabled_error", "db_corruption". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#operational_state ZeroTrustDevicePostureRule#operational_state}
        :param operator: Operator. Available values: "<", "<=", ">", ">=", "==". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#operator ZeroTrustDevicePostureRule#operator}
        :param os: Os Version. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#os ZeroTrustDevicePostureRule#os}
        :param os_distro_name: Operating System Distribution Name (linux only). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#os_distro_name ZeroTrustDevicePostureRule#os_distro_name}
        :param os_distro_revision: Version of OS Distribution (linux only). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#os_distro_revision ZeroTrustDevicePostureRule#os_distro_revision}
        :param os_version_extra: Additional version data. For Mac or iOS, the Product Version Extra. For Linux, the kernel release version. (Mac, iOS, and Linux only). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#os_version_extra ZeroTrustDevicePostureRule#os_version_extra}
        :param overall: Overall. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#overall ZeroTrustDevicePostureRule#overall}
        :param path: File path. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#path ZeroTrustDevicePostureRule#path}
        :param require_all: Whether to check all disks for encryption. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#require_all ZeroTrustDevicePostureRule#require_all}
        :param risk_level: For more details on risk level, refer to the Tanium documentation. Available values: "low", "medium", "high", "critical". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#risk_level ZeroTrustDevicePostureRule#risk_level}
        :param score: A value between 0-100 assigned to devices set by the 3rd party posture provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#score ZeroTrustDevicePostureRule#score}
        :param score_operator: Score Operator. Available values: "<", "<=", ">", ">=", "==". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#score_operator ZeroTrustDevicePostureRule#score_operator}
        :param sensor_config: SensorConfig. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#sensor_config ZeroTrustDevicePostureRule#sensor_config}
        :param sha256: SHA-256. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#sha256 ZeroTrustDevicePostureRule#sha256}
        :param state: For more details on state, please refer to the Crowdstrike documentation. Available values: "online", "offline", "unknown". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#state ZeroTrustDevicePostureRule#state}
        :param subject_alternative_names: List of certificate Subject Alternative Names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#subject_alternative_names ZeroTrustDevicePostureRule#subject_alternative_names}
        :param thumbprint: Signing certificate thumbprint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#thumbprint ZeroTrustDevicePostureRule#thumbprint}
        :param total_score: For more details on total score, refer to the Tanium documentation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#total_score ZeroTrustDevicePostureRule#total_score}
        :param version: Version of OS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#version ZeroTrustDevicePostureRule#version}
        :param version_operator: Version Operator. Available values: "<", "<=", ">", ">=", "==". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#version_operator ZeroTrustDevicePostureRule#version_operator}
        '''
        if isinstance(locations, dict):
            locations = ZeroTrustDevicePostureRuleInputLocations(**locations)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__184276d48f899997ed000313023e28073e0f0efa916fa54e07ee62b5dc576740)
            check_type(argname="argument active_threats", value=active_threats, expected_type=type_hints["active_threats"])
            check_type(argname="argument certificate_id", value=certificate_id, expected_type=type_hints["certificate_id"])
            check_type(argname="argument check_disks", value=check_disks, expected_type=type_hints["check_disks"])
            check_type(argname="argument check_private_key", value=check_private_key, expected_type=type_hints["check_private_key"])
            check_type(argname="argument cn", value=cn, expected_type=type_hints["cn"])
            check_type(argname="argument compliance_status", value=compliance_status, expected_type=type_hints["compliance_status"])
            check_type(argname="argument connection_id", value=connection_id, expected_type=type_hints["connection_id"])
            check_type(argname="argument count_operator", value=count_operator, expected_type=type_hints["count_operator"])
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument eid_last_seen", value=eid_last_seen, expected_type=type_hints["eid_last_seen"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument exists", value=exists, expected_type=type_hints["exists"])
            check_type(argname="argument extended_key_usage", value=extended_key_usage, expected_type=type_hints["extended_key_usage"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument infected", value=infected, expected_type=type_hints["infected"])
            check_type(argname="argument is_active", value=is_active, expected_type=type_hints["is_active"])
            check_type(argname="argument issue_count", value=issue_count, expected_type=type_hints["issue_count"])
            check_type(argname="argument last_seen", value=last_seen, expected_type=type_hints["last_seen"])
            check_type(argname="argument locations", value=locations, expected_type=type_hints["locations"])
            check_type(argname="argument network_status", value=network_status, expected_type=type_hints["network_status"])
            check_type(argname="argument operating_system", value=operating_system, expected_type=type_hints["operating_system"])
            check_type(argname="argument operational_state", value=operational_state, expected_type=type_hints["operational_state"])
            check_type(argname="argument operator", value=operator, expected_type=type_hints["operator"])
            check_type(argname="argument os", value=os, expected_type=type_hints["os"])
            check_type(argname="argument os_distro_name", value=os_distro_name, expected_type=type_hints["os_distro_name"])
            check_type(argname="argument os_distro_revision", value=os_distro_revision, expected_type=type_hints["os_distro_revision"])
            check_type(argname="argument os_version_extra", value=os_version_extra, expected_type=type_hints["os_version_extra"])
            check_type(argname="argument overall", value=overall, expected_type=type_hints["overall"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument require_all", value=require_all, expected_type=type_hints["require_all"])
            check_type(argname="argument risk_level", value=risk_level, expected_type=type_hints["risk_level"])
            check_type(argname="argument score", value=score, expected_type=type_hints["score"])
            check_type(argname="argument score_operator", value=score_operator, expected_type=type_hints["score_operator"])
            check_type(argname="argument sensor_config", value=sensor_config, expected_type=type_hints["sensor_config"])
            check_type(argname="argument sha256", value=sha256, expected_type=type_hints["sha256"])
            check_type(argname="argument state", value=state, expected_type=type_hints["state"])
            check_type(argname="argument subject_alternative_names", value=subject_alternative_names, expected_type=type_hints["subject_alternative_names"])
            check_type(argname="argument thumbprint", value=thumbprint, expected_type=type_hints["thumbprint"])
            check_type(argname="argument total_score", value=total_score, expected_type=type_hints["total_score"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            check_type(argname="argument version_operator", value=version_operator, expected_type=type_hints["version_operator"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if active_threats is not None:
            self._values["active_threats"] = active_threats
        if certificate_id is not None:
            self._values["certificate_id"] = certificate_id
        if check_disks is not None:
            self._values["check_disks"] = check_disks
        if check_private_key is not None:
            self._values["check_private_key"] = check_private_key
        if cn is not None:
            self._values["cn"] = cn
        if compliance_status is not None:
            self._values["compliance_status"] = compliance_status
        if connection_id is not None:
            self._values["connection_id"] = connection_id
        if count_operator is not None:
            self._values["count_operator"] = count_operator
        if domain is not None:
            self._values["domain"] = domain
        if eid_last_seen is not None:
            self._values["eid_last_seen"] = eid_last_seen
        if enabled is not None:
            self._values["enabled"] = enabled
        if exists is not None:
            self._values["exists"] = exists
        if extended_key_usage is not None:
            self._values["extended_key_usage"] = extended_key_usage
        if id is not None:
            self._values["id"] = id
        if infected is not None:
            self._values["infected"] = infected
        if is_active is not None:
            self._values["is_active"] = is_active
        if issue_count is not None:
            self._values["issue_count"] = issue_count
        if last_seen is not None:
            self._values["last_seen"] = last_seen
        if locations is not None:
            self._values["locations"] = locations
        if network_status is not None:
            self._values["network_status"] = network_status
        if operating_system is not None:
            self._values["operating_system"] = operating_system
        if operational_state is not None:
            self._values["operational_state"] = operational_state
        if operator is not None:
            self._values["operator"] = operator
        if os is not None:
            self._values["os"] = os
        if os_distro_name is not None:
            self._values["os_distro_name"] = os_distro_name
        if os_distro_revision is not None:
            self._values["os_distro_revision"] = os_distro_revision
        if os_version_extra is not None:
            self._values["os_version_extra"] = os_version_extra
        if overall is not None:
            self._values["overall"] = overall
        if path is not None:
            self._values["path"] = path
        if require_all is not None:
            self._values["require_all"] = require_all
        if risk_level is not None:
            self._values["risk_level"] = risk_level
        if score is not None:
            self._values["score"] = score
        if score_operator is not None:
            self._values["score_operator"] = score_operator
        if sensor_config is not None:
            self._values["sensor_config"] = sensor_config
        if sha256 is not None:
            self._values["sha256"] = sha256
        if state is not None:
            self._values["state"] = state
        if subject_alternative_names is not None:
            self._values["subject_alternative_names"] = subject_alternative_names
        if thumbprint is not None:
            self._values["thumbprint"] = thumbprint
        if total_score is not None:
            self._values["total_score"] = total_score
        if version is not None:
            self._values["version"] = version
        if version_operator is not None:
            self._values["version_operator"] = version_operator

    @builtins.property
    def active_threats(self) -> typing.Optional[jsii.Number]:
        '''The Number of active threats.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#active_threats ZeroTrustDevicePostureRule#active_threats}
        '''
        result = self._values.get("active_threats")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def certificate_id(self) -> typing.Optional[builtins.str]:
        '''UUID of Cloudflare managed certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#certificate_id ZeroTrustDevicePostureRule#certificate_id}
        '''
        result = self._values.get("certificate_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def check_disks(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of volume names to be checked for encryption.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#check_disks ZeroTrustDevicePostureRule#check_disks}
        '''
        result = self._values.get("check_disks")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def check_private_key(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Confirm the certificate was not imported from another device.

        We recommend keeping this enabled unless the certificate was deployed without a private key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#check_private_key ZeroTrustDevicePostureRule#check_private_key}
        '''
        result = self._values.get("check_private_key")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def cn(self) -> typing.Optional[builtins.str]:
        '''Common Name that is protected by the certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#cn ZeroTrustDevicePostureRule#cn}
        '''
        result = self._values.get("cn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compliance_status(self) -> typing.Optional[builtins.str]:
        '''Compliance Status. Available values: "compliant", "noncompliant", "unknown", "notapplicable", "ingraceperiod", "error".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#compliance_status ZeroTrustDevicePostureRule#compliance_status}
        '''
        result = self._values.get("compliance_status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connection_id(self) -> typing.Optional[builtins.str]:
        '''Posture Integration ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#connection_id ZeroTrustDevicePostureRule#connection_id}
        '''
        result = self._values.get("connection_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def count_operator(self) -> typing.Optional[builtins.str]:
        '''Count Operator. Available values: "<", "<=", ">", ">=", "==".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#count_operator ZeroTrustDevicePostureRule#count_operator}
        '''
        result = self._values.get("count_operator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain(self) -> typing.Optional[builtins.str]:
        '''Domain.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#domain ZeroTrustDevicePostureRule#domain}
        '''
        result = self._values.get("domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def eid_last_seen(self) -> typing.Optional[builtins.str]:
        '''For more details on eid last seen, refer to the Tanium documentation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#eid_last_seen ZeroTrustDevicePostureRule#eid_last_seen}
        '''
        result = self._values.get("eid_last_seen")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#enabled ZeroTrustDevicePostureRule#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def exists(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether or not file exists.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#exists ZeroTrustDevicePostureRule#exists}
        '''
        result = self._values.get("exists")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def extended_key_usage(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of values indicating purposes for which the certificate public key can be used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#extended_key_usage ZeroTrustDevicePostureRule#extended_key_usage}
        '''
        result = self._values.get("extended_key_usage")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''List ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#id ZeroTrustDevicePostureRule#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def infected(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether device is infected.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#infected ZeroTrustDevicePostureRule#infected}
        '''
        result = self._values.get("infected")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def is_active(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether device is active.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#is_active ZeroTrustDevicePostureRule#is_active}
        '''
        result = self._values.get("is_active")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def issue_count(self) -> typing.Optional[builtins.str]:
        '''The Number of Issues.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#issue_count ZeroTrustDevicePostureRule#issue_count}
        '''
        result = self._values.get("issue_count")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def last_seen(self) -> typing.Optional[builtins.str]:
        '''For more details on last seen, please refer to the Crowdstrike documentation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#last_seen ZeroTrustDevicePostureRule#last_seen}
        '''
        result = self._values.get("last_seen")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def locations(self) -> typing.Optional["ZeroTrustDevicePostureRuleInputLocations"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#locations ZeroTrustDevicePostureRule#locations}.'''
        result = self._values.get("locations")
        return typing.cast(typing.Optional["ZeroTrustDevicePostureRuleInputLocations"], result)

    @builtins.property
    def network_status(self) -> typing.Optional[builtins.str]:
        '''Network status of device. Available values: "connected", "disconnected", "disconnecting", "connecting".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#network_status ZeroTrustDevicePostureRule#network_status}
        '''
        result = self._values.get("network_status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def operating_system(self) -> typing.Optional[builtins.str]:
        '''Operating system. Available values: "windows", "linux", "mac", "android", "ios", "chromeos".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#operating_system ZeroTrustDevicePostureRule#operating_system}
        '''
        result = self._values.get("operating_system")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def operational_state(self) -> typing.Optional[builtins.str]:
        '''Agent operational state. Available values: "na", "partially_disabled", "auto_fully_disabled", "fully_disabled", "auto_partially_disabled", "disabled_error", "db_corruption".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#operational_state ZeroTrustDevicePostureRule#operational_state}
        '''
        result = self._values.get("operational_state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def operator(self) -> typing.Optional[builtins.str]:
        '''Operator. Available values: "<", "<=", ">", ">=", "==".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#operator ZeroTrustDevicePostureRule#operator}
        '''
        result = self._values.get("operator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def os(self) -> typing.Optional[builtins.str]:
        '''Os Version.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#os ZeroTrustDevicePostureRule#os}
        '''
        result = self._values.get("os")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def os_distro_name(self) -> typing.Optional[builtins.str]:
        '''Operating System Distribution Name (linux only).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#os_distro_name ZeroTrustDevicePostureRule#os_distro_name}
        '''
        result = self._values.get("os_distro_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def os_distro_revision(self) -> typing.Optional[builtins.str]:
        '''Version of OS Distribution (linux only).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#os_distro_revision ZeroTrustDevicePostureRule#os_distro_revision}
        '''
        result = self._values.get("os_distro_revision")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def os_version_extra(self) -> typing.Optional[builtins.str]:
        '''Additional version data.

        For Mac or iOS, the Product Version Extra. For Linux, the kernel release version. (Mac, iOS, and Linux only).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#os_version_extra ZeroTrustDevicePostureRule#os_version_extra}
        '''
        result = self._values.get("os_version_extra")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def overall(self) -> typing.Optional[builtins.str]:
        '''Overall.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#overall ZeroTrustDevicePostureRule#overall}
        '''
        result = self._values.get("overall")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''File path.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#path ZeroTrustDevicePostureRule#path}
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def require_all(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to check all disks for encryption.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#require_all ZeroTrustDevicePostureRule#require_all}
        '''
        result = self._values.get("require_all")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def risk_level(self) -> typing.Optional[builtins.str]:
        '''For more details on risk level, refer to the Tanium documentation. Available values: "low", "medium", "high", "critical".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#risk_level ZeroTrustDevicePostureRule#risk_level}
        '''
        result = self._values.get("risk_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def score(self) -> typing.Optional[jsii.Number]:
        '''A value between 0-100 assigned to devices set by the 3rd party posture provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#score ZeroTrustDevicePostureRule#score}
        '''
        result = self._values.get("score")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def score_operator(self) -> typing.Optional[builtins.str]:
        '''Score Operator. Available values: "<", "<=", ">", ">=", "==".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#score_operator ZeroTrustDevicePostureRule#score_operator}
        '''
        result = self._values.get("score_operator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sensor_config(self) -> typing.Optional[builtins.str]:
        '''SensorConfig.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#sensor_config ZeroTrustDevicePostureRule#sensor_config}
        '''
        result = self._values.get("sensor_config")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sha256(self) -> typing.Optional[builtins.str]:
        '''SHA-256.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#sha256 ZeroTrustDevicePostureRule#sha256}
        '''
        result = self._values.get("sha256")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state(self) -> typing.Optional[builtins.str]:
        '''For more details on state, please refer to the Crowdstrike documentation. Available values: "online", "offline", "unknown".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#state ZeroTrustDevicePostureRule#state}
        '''
        result = self._values.get("state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subject_alternative_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of certificate Subject Alternative Names.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#subject_alternative_names ZeroTrustDevicePostureRule#subject_alternative_names}
        '''
        result = self._values.get("subject_alternative_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def thumbprint(self) -> typing.Optional[builtins.str]:
        '''Signing certificate thumbprint.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#thumbprint ZeroTrustDevicePostureRule#thumbprint}
        '''
        result = self._values.get("thumbprint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def total_score(self) -> typing.Optional[jsii.Number]:
        '''For more details on total score, refer to the Tanium documentation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#total_score ZeroTrustDevicePostureRule#total_score}
        '''
        result = self._values.get("total_score")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''Version of OS.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#version ZeroTrustDevicePostureRule#version}
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def version_operator(self) -> typing.Optional[builtins.str]:
        '''Version Operator. Available values: "<", "<=", ">", ">=", "==".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#version_operator ZeroTrustDevicePostureRule#version_operator}
        '''
        result = self._values.get("version_operator")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustDevicePostureRuleInput(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDevicePostureRule.ZeroTrustDevicePostureRuleInputLocations",
    jsii_struct_bases=[],
    name_mapping={"paths": "paths", "trust_stores": "trustStores"},
)
class ZeroTrustDevicePostureRuleInputLocations:
    def __init__(
        self,
        *,
        paths: typing.Optional[typing.Sequence[builtins.str]] = None,
        trust_stores: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param paths: List of paths to check for client certificate on linux. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#paths ZeroTrustDevicePostureRule#paths}
        :param trust_stores: List of trust stores to check for client certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#trust_stores ZeroTrustDevicePostureRule#trust_stores}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__875c2a85668dc827e6593334f775e84fe86a6165a1873612fa2179d3896d11c4)
            check_type(argname="argument paths", value=paths, expected_type=type_hints["paths"])
            check_type(argname="argument trust_stores", value=trust_stores, expected_type=type_hints["trust_stores"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if paths is not None:
            self._values["paths"] = paths
        if trust_stores is not None:
            self._values["trust_stores"] = trust_stores

    @builtins.property
    def paths(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of paths to check for client certificate on linux.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#paths ZeroTrustDevicePostureRule#paths}
        '''
        result = self._values.get("paths")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def trust_stores(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of trust stores to check for client certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#trust_stores ZeroTrustDevicePostureRule#trust_stores}
        '''
        result = self._values.get("trust_stores")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustDevicePostureRuleInputLocations(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustDevicePostureRuleInputLocationsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDevicePostureRule.ZeroTrustDevicePostureRuleInputLocationsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9a252531ff28da0e7ae47ae1bc804b5fae256ee5764062e92d0ca99c740da84f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetPaths")
    def reset_paths(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPaths", []))

    @jsii.member(jsii_name="resetTrustStores")
    def reset_trust_stores(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTrustStores", []))

    @builtins.property
    @jsii.member(jsii_name="pathsInput")
    def paths_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "pathsInput"))

    @builtins.property
    @jsii.member(jsii_name="trustStoresInput")
    def trust_stores_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "trustStoresInput"))

    @builtins.property
    @jsii.member(jsii_name="paths")
    def paths(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "paths"))

    @paths.setter
    def paths(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99d6996976fe920dc34c0c865582ab293397993d3f51d9b9c39c2b33e4aa62bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "paths", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="trustStores")
    def trust_stores(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "trustStores"))

    @trust_stores.setter
    def trust_stores(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a4e0ffd44bd76da8cd367b7f71a7f02b2ad6c31e3a8385bb3ddc2009853ea69)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "trustStores", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDevicePostureRuleInputLocations]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDevicePostureRuleInputLocations]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDevicePostureRuleInputLocations]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea9cba5fd22fd8e98d190b2440cd9fb3f617e2a08af95dc4da61783ce18bf5b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustDevicePostureRuleInputOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDevicePostureRule.ZeroTrustDevicePostureRuleInputOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ae51fc2978637aaf2017fe16e7bef673f57d28650e8fbd343da3bc6d1b18c41e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putLocations")
    def put_locations(
        self,
        *,
        paths: typing.Optional[typing.Sequence[builtins.str]] = None,
        trust_stores: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param paths: List of paths to check for client certificate on linux. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#paths ZeroTrustDevicePostureRule#paths}
        :param trust_stores: List of trust stores to check for client certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#trust_stores ZeroTrustDevicePostureRule#trust_stores}
        '''
        value = ZeroTrustDevicePostureRuleInputLocations(
            paths=paths, trust_stores=trust_stores
        )

        return typing.cast(None, jsii.invoke(self, "putLocations", [value]))

    @jsii.member(jsii_name="resetActiveThreats")
    def reset_active_threats(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActiveThreats", []))

    @jsii.member(jsii_name="resetCertificateId")
    def reset_certificate_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateId", []))

    @jsii.member(jsii_name="resetCheckDisks")
    def reset_check_disks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCheckDisks", []))

    @jsii.member(jsii_name="resetCheckPrivateKey")
    def reset_check_private_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCheckPrivateKey", []))

    @jsii.member(jsii_name="resetCn")
    def reset_cn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCn", []))

    @jsii.member(jsii_name="resetComplianceStatus")
    def reset_compliance_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComplianceStatus", []))

    @jsii.member(jsii_name="resetConnectionId")
    def reset_connection_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectionId", []))

    @jsii.member(jsii_name="resetCountOperator")
    def reset_count_operator(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCountOperator", []))

    @jsii.member(jsii_name="resetDomain")
    def reset_domain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDomain", []))

    @jsii.member(jsii_name="resetEidLastSeen")
    def reset_eid_last_seen(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEidLastSeen", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetExists")
    def reset_exists(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExists", []))

    @jsii.member(jsii_name="resetExtendedKeyUsage")
    def reset_extended_key_usage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExtendedKeyUsage", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetInfected")
    def reset_infected(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInfected", []))

    @jsii.member(jsii_name="resetIsActive")
    def reset_is_active(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsActive", []))

    @jsii.member(jsii_name="resetIssueCount")
    def reset_issue_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIssueCount", []))

    @jsii.member(jsii_name="resetLastSeen")
    def reset_last_seen(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLastSeen", []))

    @jsii.member(jsii_name="resetLocations")
    def reset_locations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocations", []))

    @jsii.member(jsii_name="resetNetworkStatus")
    def reset_network_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkStatus", []))

    @jsii.member(jsii_name="resetOperatingSystem")
    def reset_operating_system(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperatingSystem", []))

    @jsii.member(jsii_name="resetOperationalState")
    def reset_operational_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperationalState", []))

    @jsii.member(jsii_name="resetOperator")
    def reset_operator(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperator", []))

    @jsii.member(jsii_name="resetOs")
    def reset_os(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOs", []))

    @jsii.member(jsii_name="resetOsDistroName")
    def reset_os_distro_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOsDistroName", []))

    @jsii.member(jsii_name="resetOsDistroRevision")
    def reset_os_distro_revision(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOsDistroRevision", []))

    @jsii.member(jsii_name="resetOsVersionExtra")
    def reset_os_version_extra(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOsVersionExtra", []))

    @jsii.member(jsii_name="resetOverall")
    def reset_overall(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOverall", []))

    @jsii.member(jsii_name="resetPath")
    def reset_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPath", []))

    @jsii.member(jsii_name="resetRequireAll")
    def reset_require_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequireAll", []))

    @jsii.member(jsii_name="resetRiskLevel")
    def reset_risk_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRiskLevel", []))

    @jsii.member(jsii_name="resetScore")
    def reset_score(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScore", []))

    @jsii.member(jsii_name="resetScoreOperator")
    def reset_score_operator(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScoreOperator", []))

    @jsii.member(jsii_name="resetSensorConfig")
    def reset_sensor_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSensorConfig", []))

    @jsii.member(jsii_name="resetSha256")
    def reset_sha256(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSha256", []))

    @jsii.member(jsii_name="resetState")
    def reset_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetState", []))

    @jsii.member(jsii_name="resetSubjectAlternativeNames")
    def reset_subject_alternative_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubjectAlternativeNames", []))

    @jsii.member(jsii_name="resetThumbprint")
    def reset_thumbprint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThumbprint", []))

    @jsii.member(jsii_name="resetTotalScore")
    def reset_total_score(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTotalScore", []))

    @jsii.member(jsii_name="resetVersion")
    def reset_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersion", []))

    @jsii.member(jsii_name="resetVersionOperator")
    def reset_version_operator(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersionOperator", []))

    @builtins.property
    @jsii.member(jsii_name="locations")
    def locations(self) -> ZeroTrustDevicePostureRuleInputLocationsOutputReference:
        return typing.cast(ZeroTrustDevicePostureRuleInputLocationsOutputReference, jsii.get(self, "locations"))

    @builtins.property
    @jsii.member(jsii_name="activeThreatsInput")
    def active_threats_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "activeThreatsInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateIdInput")
    def certificate_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateIdInput"))

    @builtins.property
    @jsii.member(jsii_name="checkDisksInput")
    def check_disks_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "checkDisksInput"))

    @builtins.property
    @jsii.member(jsii_name="checkPrivateKeyInput")
    def check_private_key_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "checkPrivateKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="cnInput")
    def cn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cnInput"))

    @builtins.property
    @jsii.member(jsii_name="complianceStatusInput")
    def compliance_status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "complianceStatusInput"))

    @builtins.property
    @jsii.member(jsii_name="connectionIdInput")
    def connection_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionIdInput"))

    @builtins.property
    @jsii.member(jsii_name="countOperatorInput")
    def count_operator_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "countOperatorInput"))

    @builtins.property
    @jsii.member(jsii_name="domainInput")
    def domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainInput"))

    @builtins.property
    @jsii.member(jsii_name="eidLastSeenInput")
    def eid_last_seen_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eidLastSeenInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="existsInput")
    def exists_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "existsInput"))

    @builtins.property
    @jsii.member(jsii_name="extendedKeyUsageInput")
    def extended_key_usage_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "extendedKeyUsageInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="infectedInput")
    def infected_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "infectedInput"))

    @builtins.property
    @jsii.member(jsii_name="isActiveInput")
    def is_active_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isActiveInput"))

    @builtins.property
    @jsii.member(jsii_name="issueCountInput")
    def issue_count_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "issueCountInput"))

    @builtins.property
    @jsii.member(jsii_name="lastSeenInput")
    def last_seen_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lastSeenInput"))

    @builtins.property
    @jsii.member(jsii_name="locationsInput")
    def locations_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDevicePostureRuleInputLocations]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDevicePostureRuleInputLocations]], jsii.get(self, "locationsInput"))

    @builtins.property
    @jsii.member(jsii_name="networkStatusInput")
    def network_status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkStatusInput"))

    @builtins.property
    @jsii.member(jsii_name="operatingSystemInput")
    def operating_system_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "operatingSystemInput"))

    @builtins.property
    @jsii.member(jsii_name="operationalStateInput")
    def operational_state_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "operationalStateInput"))

    @builtins.property
    @jsii.member(jsii_name="operatorInput")
    def operator_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "operatorInput"))

    @builtins.property
    @jsii.member(jsii_name="osDistroNameInput")
    def os_distro_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "osDistroNameInput"))

    @builtins.property
    @jsii.member(jsii_name="osDistroRevisionInput")
    def os_distro_revision_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "osDistroRevisionInput"))

    @builtins.property
    @jsii.member(jsii_name="osInput")
    def os_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "osInput"))

    @builtins.property
    @jsii.member(jsii_name="osVersionExtraInput")
    def os_version_extra_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "osVersionExtraInput"))

    @builtins.property
    @jsii.member(jsii_name="overallInput")
    def overall_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "overallInput"))

    @builtins.property
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property
    @jsii.member(jsii_name="requireAllInput")
    def require_all_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "requireAllInput"))

    @builtins.property
    @jsii.member(jsii_name="riskLevelInput")
    def risk_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "riskLevelInput"))

    @builtins.property
    @jsii.member(jsii_name="scoreInput")
    def score_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "scoreInput"))

    @builtins.property
    @jsii.member(jsii_name="scoreOperatorInput")
    def score_operator_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scoreOperatorInput"))

    @builtins.property
    @jsii.member(jsii_name="sensorConfigInput")
    def sensor_config_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sensorConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="sha256Input")
    def sha256_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sha256Input"))

    @builtins.property
    @jsii.member(jsii_name="stateInput")
    def state_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateInput"))

    @builtins.property
    @jsii.member(jsii_name="subjectAlternativeNamesInput")
    def subject_alternative_names_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "subjectAlternativeNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="thumbprintInput")
    def thumbprint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "thumbprintInput"))

    @builtins.property
    @jsii.member(jsii_name="totalScoreInput")
    def total_score_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "totalScoreInput"))

    @builtins.property
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property
    @jsii.member(jsii_name="versionOperatorInput")
    def version_operator_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionOperatorInput"))

    @builtins.property
    @jsii.member(jsii_name="activeThreats")
    def active_threats(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "activeThreats"))

    @active_threats.setter
    def active_threats(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3923bd6309c737206f553e0cb30f846a389bcd4e995f6483c96a79e726890b7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "activeThreats", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="certificateId")
    def certificate_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateId"))

    @certificate_id.setter
    def certificate_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c604b952c5f1b63b0c8f16f7c2c6b3f99627a0a7f2585163da6b82aabf5acbf7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="checkDisks")
    def check_disks(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "checkDisks"))

    @check_disks.setter
    def check_disks(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90330f5c151daad24b33887fc57674bd2959a0b1b44782ebe30757fb01954389)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "checkDisks", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="checkPrivateKey")
    def check_private_key(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "checkPrivateKey"))

    @check_private_key.setter
    def check_private_key(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__068a6ea52b64006b1aad82e017faf2568981a2ee5e9fda33af95c719142fb4e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "checkPrivateKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cn")
    def cn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cn"))

    @cn.setter
    def cn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__685bf9084072a330c24f4aa2141d4669191b5fd658d566efb4e39fc6f65fa291)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="complianceStatus")
    def compliance_status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "complianceStatus"))

    @compliance_status.setter
    def compliance_status(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8986d625de747aef9aefeb4c469afcb0778afa60b70fbd1cf086c91645c48ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "complianceStatus", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="connectionId")
    def connection_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectionId"))

    @connection_id.setter
    def connection_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6b03d982d2497e5bd243bae703c74220f336dc4662ce7c8b99a251b13a5f1e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="countOperator")
    def count_operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "countOperator"))

    @count_operator.setter
    def count_operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7262b280f8b2893b3f20cd5861e9e5394d74addd4d0075cd27ab3d8113b9848a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "countOperator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__415bbf4ea30267541de9b5dec6bd287a3066ff8509666f01e931807438b6cc1e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "domain", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="eidLastSeen")
    def eid_last_seen(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eidLastSeen"))

    @eid_last_seen.setter
    def eid_last_seen(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__783cb1af32b1d59d7f16ba6e1a7f147f5977afb1a73b78219da5b7863b119bc8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eidLastSeen", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__058c3b68ae5e7b4e759805880f155bb59811a0040f2eb97afdd120a56a955dd3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="exists")
    def exists(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "exists"))

    @exists.setter
    def exists(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3544ee07a580d01bb1458ff7887d74a7cd07fb384ec820bbd1902a375bb8f4de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exists", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="extendedKeyUsage")
    def extended_key_usage(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "extendedKeyUsage"))

    @extended_key_usage.setter
    def extended_key_usage(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__150d9a65cc5de0529d2776900b3141fb95c309a9b764a6f440b052e43df4f1aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "extendedKeyUsage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c6d5f86dcd01c656bd9229b223a43c6bd1b0318fabc9444f1e7df036ce4e44c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="infected")
    def infected(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "infected"))

    @infected.setter
    def infected(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6972f66ae19313e24983bdbd3c13bab6192fbcacd7b57766740f6f814a40f459)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "infected", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isActive")
    def is_active(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isActive"))

    @is_active.setter
    def is_active(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e10a51782ad201b114ddf4bb307dcb50b1f90bd33b381dc7489916b8011088a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isActive", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="issueCount")
    def issue_count(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "issueCount"))

    @issue_count.setter
    def issue_count(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d13edafe9f0eb5f9a47f21ef0fbc06ba365cac148dc535ed35df413a2323c19b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "issueCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lastSeen")
    def last_seen(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastSeen"))

    @last_seen.setter
    def last_seen(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9457d1e0a918530347d1d162acc893edaa1506500710e18f11d9c281d3cd0c53)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lastSeen", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkStatus")
    def network_status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkStatus"))

    @network_status.setter
    def network_status(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7bffea225f7090e3898086a4662958c36e9edecda11628bc1b3087fd1e14cea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkStatus", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operatingSystem")
    def operating_system(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operatingSystem"))

    @operating_system.setter
    def operating_system(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc4dca9629c55181b1688a877ce3ae284cb25643bb8cfd8a425596e0bca4b4d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operatingSystem", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operationalState")
    def operational_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operationalState"))

    @operational_state.setter
    def operational_state(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__425f8768644afe10cd339bd9c172e0c57a88a42525306a44c0a493695773cab6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operationalState", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1037eb305c92952f1bf6009cf6085eed4524056692d07a2d51faf21196efa41c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="os")
    def os(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "os"))

    @os.setter
    def os(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecb2b4bd815298fb2a90e2d73a930a44f444a6a0979c06d88e169b6433319fd0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "os", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="osDistroName")
    def os_distro_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "osDistroName"))

    @os_distro_name.setter
    def os_distro_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ccc1396407eadea6380cacf45371c3a8a72188d3865f78b88112d8a8d7961639)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "osDistroName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="osDistroRevision")
    def os_distro_revision(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "osDistroRevision"))

    @os_distro_revision.setter
    def os_distro_revision(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1cbf9581b4608e28aaaa2a5cc19bdf0eb65bb95c9634a4459b7ca253655f2e83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "osDistroRevision", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="osVersionExtra")
    def os_version_extra(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "osVersionExtra"))

    @os_version_extra.setter
    def os_version_extra(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4042d721cd05e87f0f3947e9a4b2e7e4dbe6196081911a8f62a4dfbdb78d72a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "osVersionExtra", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="overall")
    def overall(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "overall"))

    @overall.setter
    def overall(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c242383a1935db412486ed94ec7f644ac3803a76126e986e25373b7979005922)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "overall", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42e6a22f0d905d562391f8168737bff87731b094fd482db4e9b941dfb03f8236)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requireAll")
    def require_all(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "requireAll"))

    @require_all.setter
    def require_all(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe9130329f778d13d029a516411657c5a318d3db5b3be1d0ce35080b9c0bf465)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requireAll", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="riskLevel")
    def risk_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "riskLevel"))

    @risk_level.setter
    def risk_level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebcc8ed96e5158967766403c1ae21bab912a39f689696fde2089be3119460c9e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "riskLevel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="score")
    def score(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "score"))

    @score.setter
    def score(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55a50172a73223bf778841536605a6be07319833692d97cda2f16dacd720df84)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "score", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scoreOperator")
    def score_operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scoreOperator"))

    @score_operator.setter
    def score_operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03461e1137acd99295b65dc4343bcf70c7f7ae8e76a404b454cbc5976860cdbc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scoreOperator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sensorConfig")
    def sensor_config(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sensorConfig"))

    @sensor_config.setter
    def sensor_config(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a38832e6f93b1d9384a105033c879206431ae657ee878165c9c31e2438b73a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sensorConfig", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sha256")
    def sha256(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sha256"))

    @sha256.setter
    def sha256(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7628228db2da27fe63903cbd4f58307ee3e2514e2db46ce50788ba96ae24835)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sha256", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @state.setter
    def state(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0708aa4838de7497ea3369e1fcceed88bca5687d960088525caaaeaa23e0793)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "state", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subjectAlternativeNames")
    def subject_alternative_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subjectAlternativeNames"))

    @subject_alternative_names.setter
    def subject_alternative_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f526e834d94c56c64eceede319ede80c542a080553129a1b3a940c330cc7cf6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subjectAlternativeNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="thumbprint")
    def thumbprint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "thumbprint"))

    @thumbprint.setter
    def thumbprint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f6cbca64549a8e0e4722f24323a8409c0167b522aa56637ab23b4bfdedcc57f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "thumbprint", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="totalScore")
    def total_score(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "totalScore"))

    @total_score.setter
    def total_score(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4deb052f4de277a54d5f905f2c465cb24f825c04057cb0d0cc4bc6057df0c6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "totalScore", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ae8f073b8568c3e220d4e9ccc7e63fc42aa97615a018f12cf6e5d2083751e21)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="versionOperator")
    def version_operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "versionOperator"))

    @version_operator.setter
    def version_operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54a5cdb29bc9cbb635c1ed3745f791455ae0200e48a79ec517f00515121d9928)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "versionOperator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDevicePostureRuleInput]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDevicePostureRuleInput]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDevicePostureRuleInput]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb6640120906e82cf4844043f2ec33f31795bc8ea8ff578abb771f7d5a8654ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDevicePostureRule.ZeroTrustDevicePostureRuleMatch",
    jsii_struct_bases=[],
    name_mapping={"platform": "platform"},
)
class ZeroTrustDevicePostureRuleMatch:
    def __init__(self, *, platform: typing.Optional[builtins.str] = None) -> None:
        '''
        :param platform: Available values: "windows", "mac", "linux", "android", "ios", "chromeos". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#platform ZeroTrustDevicePostureRule#platform}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f60ee57ddb80ad205d751cf67996a5ef158a6ab1e86f0ebae0743b3efabbc59)
            check_type(argname="argument platform", value=platform, expected_type=type_hints["platform"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if platform is not None:
            self._values["platform"] = platform

    @builtins.property
    def platform(self) -> typing.Optional[builtins.str]:
        '''Available values: "windows", "mac", "linux", "android", "ios", "chromeos".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zero_trust_device_posture_rule#platform ZeroTrustDevicePostureRule#platform}
        '''
        result = self._values.get("platform")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroTrustDevicePostureRuleMatch(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZeroTrustDevicePostureRuleMatchList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDevicePostureRule.ZeroTrustDevicePostureRuleMatchList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__257af28e1148dec35789ba649f2bf728584d69e4871500815ea33502363d45f8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ZeroTrustDevicePostureRuleMatchOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33ffd067146c9cfe84a225c78a68e6d1abffb2e103f639eb8e0e8e6916c65087)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ZeroTrustDevicePostureRuleMatchOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69d6e82b42109b499a3aa442488e06f943bb43c654efa8ea032c96b63ad8b9e4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8df05172718c0ab115ac3d5563413d2cf772c9509d9ab048528cfea6535d867a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__11040fdeeb372b213f62c82da501c6da24597797df15abcf3dfe03679a9654a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDevicePostureRuleMatch]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDevicePostureRuleMatch]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDevicePostureRuleMatch]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3cc850342ceb46c077af2b2042220fedd673f2824a3ca27cb07577e6cc235a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ZeroTrustDevicePostureRuleMatchOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zeroTrustDevicePostureRule.ZeroTrustDevicePostureRuleMatchOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__28eec328650c66f8ce71ff573a295b869a7539311e3284e7d0562cd69f66783b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetPlatform")
    def reset_platform(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPlatform", []))

    @builtins.property
    @jsii.member(jsii_name="platformInput")
    def platform_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "platformInput"))

    @builtins.property
    @jsii.member(jsii_name="platform")
    def platform(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "platform"))

    @platform.setter
    def platform(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__507ec5a2cf9001e8bf30a0f8d1fe7e8edca99e5645646b3cc81138c4c95737a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "platform", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDevicePostureRuleMatch]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDevicePostureRuleMatch]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDevicePostureRuleMatch]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7456cbf06ab69cc130f9b6c2f0dcde052065bb29c28004c66a940c77dc9e65a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ZeroTrustDevicePostureRule",
    "ZeroTrustDevicePostureRuleConfig",
    "ZeroTrustDevicePostureRuleInput",
    "ZeroTrustDevicePostureRuleInputLocations",
    "ZeroTrustDevicePostureRuleInputLocationsOutputReference",
    "ZeroTrustDevicePostureRuleInputOutputReference",
    "ZeroTrustDevicePostureRuleMatch",
    "ZeroTrustDevicePostureRuleMatchList",
    "ZeroTrustDevicePostureRuleMatchOutputReference",
]

publication.publish()

def _typecheckingstub__fd60b48f6bf9792c09d2f75e75ecfba2938a4d14986bca399156b4cbc246dd4b(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    name: builtins.str,
    type: builtins.str,
    description: typing.Optional[builtins.str] = None,
    expiration: typing.Optional[builtins.str] = None,
    input: typing.Optional[typing.Union[ZeroTrustDevicePostureRuleInput, typing.Dict[builtins.str, typing.Any]]] = None,
    match: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDevicePostureRuleMatch, typing.Dict[builtins.str, typing.Any]]]]] = None,
    schedule: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__62e0789401a7db589386f102caa8fce22c7b5c14e94d978f4b67313c95d5bb6b(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fc17380a3e81f9d5e8c16bcfb7c4cf1e5eb49fdd4a73f414f240b3c45f410ee(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDevicePostureRuleMatch, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5032ea93ba752507c67e51361bb4240e9a8c374b606f9faa17d097759528245d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f2537df048390cb809367bd506f1e8f3c12e6a027af5e230080e3bc3399fc07(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8758a3f0c76bb9261f97e418c99bace38749f2b76a6bc842eabb52f005393126(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f05345b945d1a808ccde1cafc3adf60a6a4d6597640c381f19f0522c459f6eca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d8d9114d9f167670fef321332076433d319a5f2d458e798ff5afb12b77ec3ba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c20ba511f64042e6e59f898b0c3df6dc7d5438ba0063c937a3fec3dc4b630fb7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d71d65986f39d03f15f7ba09af383b7859278d2512ab445f38431e9ee9364c26(
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
    type: builtins.str,
    description: typing.Optional[builtins.str] = None,
    expiration: typing.Optional[builtins.str] = None,
    input: typing.Optional[typing.Union[ZeroTrustDevicePostureRuleInput, typing.Dict[builtins.str, typing.Any]]] = None,
    match: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ZeroTrustDevicePostureRuleMatch, typing.Dict[builtins.str, typing.Any]]]]] = None,
    schedule: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__184276d48f899997ed000313023e28073e0f0efa916fa54e07ee62b5dc576740(
    *,
    active_threats: typing.Optional[jsii.Number] = None,
    certificate_id: typing.Optional[builtins.str] = None,
    check_disks: typing.Optional[typing.Sequence[builtins.str]] = None,
    check_private_key: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cn: typing.Optional[builtins.str] = None,
    compliance_status: typing.Optional[builtins.str] = None,
    connection_id: typing.Optional[builtins.str] = None,
    count_operator: typing.Optional[builtins.str] = None,
    domain: typing.Optional[builtins.str] = None,
    eid_last_seen: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    exists: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    extended_key_usage: typing.Optional[typing.Sequence[builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    infected: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    is_active: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    issue_count: typing.Optional[builtins.str] = None,
    last_seen: typing.Optional[builtins.str] = None,
    locations: typing.Optional[typing.Union[ZeroTrustDevicePostureRuleInputLocations, typing.Dict[builtins.str, typing.Any]]] = None,
    network_status: typing.Optional[builtins.str] = None,
    operating_system: typing.Optional[builtins.str] = None,
    operational_state: typing.Optional[builtins.str] = None,
    operator: typing.Optional[builtins.str] = None,
    os: typing.Optional[builtins.str] = None,
    os_distro_name: typing.Optional[builtins.str] = None,
    os_distro_revision: typing.Optional[builtins.str] = None,
    os_version_extra: typing.Optional[builtins.str] = None,
    overall: typing.Optional[builtins.str] = None,
    path: typing.Optional[builtins.str] = None,
    require_all: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    risk_level: typing.Optional[builtins.str] = None,
    score: typing.Optional[jsii.Number] = None,
    score_operator: typing.Optional[builtins.str] = None,
    sensor_config: typing.Optional[builtins.str] = None,
    sha256: typing.Optional[builtins.str] = None,
    state: typing.Optional[builtins.str] = None,
    subject_alternative_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    thumbprint: typing.Optional[builtins.str] = None,
    total_score: typing.Optional[jsii.Number] = None,
    version: typing.Optional[builtins.str] = None,
    version_operator: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__875c2a85668dc827e6593334f775e84fe86a6165a1873612fa2179d3896d11c4(
    *,
    paths: typing.Optional[typing.Sequence[builtins.str]] = None,
    trust_stores: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a252531ff28da0e7ae47ae1bc804b5fae256ee5764062e92d0ca99c740da84f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99d6996976fe920dc34c0c865582ab293397993d3f51d9b9c39c2b33e4aa62bf(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a4e0ffd44bd76da8cd367b7f71a7f02b2ad6c31e3a8385bb3ddc2009853ea69(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea9cba5fd22fd8e98d190b2440cd9fb3f617e2a08af95dc4da61783ce18bf5b7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDevicePostureRuleInputLocations]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae51fc2978637aaf2017fe16e7bef673f57d28650e8fbd343da3bc6d1b18c41e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3923bd6309c737206f553e0cb30f846a389bcd4e995f6483c96a79e726890b7c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c604b952c5f1b63b0c8f16f7c2c6b3f99627a0a7f2585163da6b82aabf5acbf7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90330f5c151daad24b33887fc57674bd2959a0b1b44782ebe30757fb01954389(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__068a6ea52b64006b1aad82e017faf2568981a2ee5e9fda33af95c719142fb4e3(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__685bf9084072a330c24f4aa2141d4669191b5fd658d566efb4e39fc6f65fa291(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8986d625de747aef9aefeb4c469afcb0778afa60b70fbd1cf086c91645c48ca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6b03d982d2497e5bd243bae703c74220f336dc4662ce7c8b99a251b13a5f1e5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7262b280f8b2893b3f20cd5861e9e5394d74addd4d0075cd27ab3d8113b9848a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__415bbf4ea30267541de9b5dec6bd287a3066ff8509666f01e931807438b6cc1e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__783cb1af32b1d59d7f16ba6e1a7f147f5977afb1a73b78219da5b7863b119bc8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__058c3b68ae5e7b4e759805880f155bb59811a0040f2eb97afdd120a56a955dd3(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3544ee07a580d01bb1458ff7887d74a7cd07fb384ec820bbd1902a375bb8f4de(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__150d9a65cc5de0529d2776900b3141fb95c309a9b764a6f440b052e43df4f1aa(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c6d5f86dcd01c656bd9229b223a43c6bd1b0318fabc9444f1e7df036ce4e44c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6972f66ae19313e24983bdbd3c13bab6192fbcacd7b57766740f6f814a40f459(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e10a51782ad201b114ddf4bb307dcb50b1f90bd33b381dc7489916b8011088a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d13edafe9f0eb5f9a47f21ef0fbc06ba365cac148dc535ed35df413a2323c19b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9457d1e0a918530347d1d162acc893edaa1506500710e18f11d9c281d3cd0c53(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7bffea225f7090e3898086a4662958c36e9edecda11628bc1b3087fd1e14cea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc4dca9629c55181b1688a877ce3ae284cb25643bb8cfd8a425596e0bca4b4d9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__425f8768644afe10cd339bd9c172e0c57a88a42525306a44c0a493695773cab6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1037eb305c92952f1bf6009cf6085eed4524056692d07a2d51faf21196efa41c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecb2b4bd815298fb2a90e2d73a930a44f444a6a0979c06d88e169b6433319fd0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccc1396407eadea6380cacf45371c3a8a72188d3865f78b88112d8a8d7961639(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cbf9581b4608e28aaaa2a5cc19bdf0eb65bb95c9634a4459b7ca253655f2e83(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4042d721cd05e87f0f3947e9a4b2e7e4dbe6196081911a8f62a4dfbdb78d72a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c242383a1935db412486ed94ec7f644ac3803a76126e986e25373b7979005922(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42e6a22f0d905d562391f8168737bff87731b094fd482db4e9b941dfb03f8236(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe9130329f778d13d029a516411657c5a318d3db5b3be1d0ce35080b9c0bf465(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebcc8ed96e5158967766403c1ae21bab912a39f689696fde2089be3119460c9e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55a50172a73223bf778841536605a6be07319833692d97cda2f16dacd720df84(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03461e1137acd99295b65dc4343bcf70c7f7ae8e76a404b454cbc5976860cdbc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a38832e6f93b1d9384a105033c879206431ae657ee878165c9c31e2438b73a3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7628228db2da27fe63903cbd4f58307ee3e2514e2db46ce50788ba96ae24835(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0708aa4838de7497ea3369e1fcceed88bca5687d960088525caaaeaa23e0793(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f526e834d94c56c64eceede319ede80c542a080553129a1b3a940c330cc7cf6(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f6cbca64549a8e0e4722f24323a8409c0167b522aa56637ab23b4bfdedcc57f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4deb052f4de277a54d5f905f2c465cb24f825c04057cb0d0cc4bc6057df0c6d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ae8f073b8568c3e220d4e9ccc7e63fc42aa97615a018f12cf6e5d2083751e21(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54a5cdb29bc9cbb635c1ed3745f791455ae0200e48a79ec517f00515121d9928(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb6640120906e82cf4844043f2ec33f31795bc8ea8ff578abb771f7d5a8654ff(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDevicePostureRuleInput]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f60ee57ddb80ad205d751cf67996a5ef158a6ab1e86f0ebae0743b3efabbc59(
    *,
    platform: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__257af28e1148dec35789ba649f2bf728584d69e4871500815ea33502363d45f8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33ffd067146c9cfe84a225c78a68e6d1abffb2e103f639eb8e0e8e6916c65087(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69d6e82b42109b499a3aa442488e06f943bb43c654efa8ea032c96b63ad8b9e4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8df05172718c0ab115ac3d5563413d2cf772c9509d9ab048528cfea6535d867a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11040fdeeb372b213f62c82da501c6da24597797df15abcf3dfe03679a9654a4(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3cc850342ceb46c077af2b2042220fedd673f2824a3ca27cb07577e6cc235a4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ZeroTrustDevicePostureRuleMatch]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28eec328650c66f8ce71ff573a295b869a7539311e3284e7d0562cd69f66783b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__507ec5a2cf9001e8bf30a0f8d1fe7e8edca99e5645646b3cc81138c4c95737a1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7456cbf06ab69cc130f9b6c2f0dcde052065bb29c28004c66a940c77dc9e65a9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZeroTrustDevicePostureRuleMatch]],
) -> None:
    """Type checking stubs"""
    pass
