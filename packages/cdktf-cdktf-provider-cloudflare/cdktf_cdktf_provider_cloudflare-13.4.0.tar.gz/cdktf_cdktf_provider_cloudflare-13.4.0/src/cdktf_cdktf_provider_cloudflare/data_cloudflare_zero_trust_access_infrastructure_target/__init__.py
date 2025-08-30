r'''
# `data_cloudflare_zero_trust_access_infrastructure_target`

Refer to the Terraform Registry for docs: [`data_cloudflare_zero_trust_access_infrastructure_target`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target).
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


class DataCloudflareZeroTrustAccessInfrastructureTarget(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessInfrastructureTarget.DataCloudflareZeroTrustAccessInfrastructureTarget",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target cloudflare_zero_trust_access_infrastructure_target}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        filter: typing.Optional[typing.Union["DataCloudflareZeroTrustAccessInfrastructureTargetFilter", typing.Dict[builtins.str, typing.Any]]] = None,
        target_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target cloudflare_zero_trust_access_infrastructure_target} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Account identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#account_id DataCloudflareZeroTrustAccessInfrastructureTarget#account_id}
        :param filter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#filter DataCloudflareZeroTrustAccessInfrastructureTarget#filter}.
        :param target_id: Target identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#target_id DataCloudflareZeroTrustAccessInfrastructureTarget#target_id}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53ad8396ae177658c0a314d2d1469cd57dec156ccefafb091a140c633a7b4700)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataCloudflareZeroTrustAccessInfrastructureTargetConfig(
            account_id=account_id,
            filter=filter,
            target_id=target_id,
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
        '''Generates CDKTF code for importing a DataCloudflareZeroTrustAccessInfrastructureTarget resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataCloudflareZeroTrustAccessInfrastructureTarget to import.
        :param import_from_id: The id of the existing DataCloudflareZeroTrustAccessInfrastructureTarget that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataCloudflareZeroTrustAccessInfrastructureTarget to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4ff14354a701f3f64bb184ffe511c614b32184e0c75c4e5a86af155bbd20687)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putFilter")
    def put_filter(
        self,
        *,
        created_after: typing.Optional[builtins.str] = None,
        created_before: typing.Optional[builtins.str] = None,
        direction: typing.Optional[builtins.str] = None,
        hostname: typing.Optional[builtins.str] = None,
        hostname_contains: typing.Optional[builtins.str] = None,
        ip_like: typing.Optional[builtins.str] = None,
        ips: typing.Optional[typing.Sequence[builtins.str]] = None,
        ip_v4: typing.Optional[builtins.str] = None,
        ipv4_end: typing.Optional[builtins.str] = None,
        ipv4_start: typing.Optional[builtins.str] = None,
        ip_v6: typing.Optional[builtins.str] = None,
        ipv6_end: typing.Optional[builtins.str] = None,
        ipv6_start: typing.Optional[builtins.str] = None,
        modified_after: typing.Optional[builtins.str] = None,
        modified_before: typing.Optional[builtins.str] = None,
        order: typing.Optional[builtins.str] = None,
        target_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        virtual_network_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param created_after: Date and time at which the target was created after (inclusive). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#created_after DataCloudflareZeroTrustAccessInfrastructureTarget#created_after}
        :param created_before: Date and time at which the target was created before (inclusive). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#created_before DataCloudflareZeroTrustAccessInfrastructureTarget#created_before}
        :param direction: The sorting direction. Available values: "asc", "desc". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#direction DataCloudflareZeroTrustAccessInfrastructureTarget#direction}
        :param hostname: Hostname of a target. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#hostname DataCloudflareZeroTrustAccessInfrastructureTarget#hostname}
        :param hostname_contains: Partial match to the hostname of a target. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#hostname_contains DataCloudflareZeroTrustAccessInfrastructureTarget#hostname_contains}
        :param ip_like: Filters for targets whose IP addresses look like the specified string. Supports ``*`` as a wildcard character. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#ip_like DataCloudflareZeroTrustAccessInfrastructureTarget#ip_like}
        :param ips: Filters for targets that have any of the following IP addresses. Specify ``ips`` multiple times in query parameter to build list of candidates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#ips DataCloudflareZeroTrustAccessInfrastructureTarget#ips}
        :param ip_v4: IPv4 address of the target. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#ip_v4 DataCloudflareZeroTrustAccessInfrastructureTarget#ip_v4}
        :param ipv4_end: Defines an IPv4 filter range's ending value (inclusive). Requires ``ipv4_start`` to be specified as well. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#ipv4_end DataCloudflareZeroTrustAccessInfrastructureTarget#ipv4_end}
        :param ipv4_start: Defines an IPv4 filter range's starting value (inclusive). Requires ``ipv4_end`` to be specified as well. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#ipv4_start DataCloudflareZeroTrustAccessInfrastructureTarget#ipv4_start}
        :param ip_v6: IPv6 address of the target. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#ip_v6 DataCloudflareZeroTrustAccessInfrastructureTarget#ip_v6}
        :param ipv6_end: Defines an IPv6 filter range's ending value (inclusive). Requires ``ipv6_start`` to be specified as well. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#ipv6_end DataCloudflareZeroTrustAccessInfrastructureTarget#ipv6_end}
        :param ipv6_start: Defines an IPv6 filter range's starting value (inclusive). Requires ``ipv6_end`` to be specified as well. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#ipv6_start DataCloudflareZeroTrustAccessInfrastructureTarget#ipv6_start}
        :param modified_after: Date and time at which the target was modified after (inclusive). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#modified_after DataCloudflareZeroTrustAccessInfrastructureTarget#modified_after}
        :param modified_before: Date and time at which the target was modified before (inclusive). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#modified_before DataCloudflareZeroTrustAccessInfrastructureTarget#modified_before}
        :param order: The field to sort by. Available values: "hostname", "created_at". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#order DataCloudflareZeroTrustAccessInfrastructureTarget#order}
        :param target_ids: Filters for targets that have any of the following UUIDs. Specify ``target_ids`` multiple times in query parameter to build list of candidates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#target_ids DataCloudflareZeroTrustAccessInfrastructureTarget#target_ids}
        :param virtual_network_id: Private virtual network identifier of the target. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#virtual_network_id DataCloudflareZeroTrustAccessInfrastructureTarget#virtual_network_id}
        '''
        value = DataCloudflareZeroTrustAccessInfrastructureTargetFilter(
            created_after=created_after,
            created_before=created_before,
            direction=direction,
            hostname=hostname,
            hostname_contains=hostname_contains,
            ip_like=ip_like,
            ips=ips,
            ip_v4=ip_v4,
            ipv4_end=ipv4_end,
            ipv4_start=ipv4_start,
            ip_v6=ip_v6,
            ipv6_end=ipv6_end,
            ipv6_start=ipv6_start,
            modified_after=modified_after,
            modified_before=modified_before,
            order=order,
            target_ids=target_ids,
            virtual_network_id=virtual_network_id,
        )

        return typing.cast(None, jsii.invoke(self, "putFilter", [value]))

    @jsii.member(jsii_name="resetFilter")
    def reset_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilter", []))

    @jsii.member(jsii_name="resetTargetId")
    def reset_target_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetId", []))

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
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="filter")
    def filter(
        self,
    ) -> "DataCloudflareZeroTrustAccessInfrastructureTargetFilterOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessInfrastructureTargetFilterOutputReference", jsii.get(self, "filter"))

    @builtins.property
    @jsii.member(jsii_name="hostname")
    def hostname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostname"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(
        self,
    ) -> "DataCloudflareZeroTrustAccessInfrastructureTargetIpOutputReference":
        return typing.cast("DataCloudflareZeroTrustAccessInfrastructureTargetIpOutputReference", jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="modifiedAt")
    def modified_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modifiedAt"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="filterInput")
    def filter_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataCloudflareZeroTrustAccessInfrastructureTargetFilter"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataCloudflareZeroTrustAccessInfrastructureTargetFilter"]], jsii.get(self, "filterInput"))

    @builtins.property
    @jsii.member(jsii_name="targetIdInput")
    def target_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetIdInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab6c62fb57f291bc664db58a0ea21652bf20321b9c9fcaf2332c48ae56bb7198)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetId")
    def target_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetId"))

    @target_id.setter
    def target_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f51a7d0019b4f5147a1d787f98b04300bc2086b58803e69ed68ee027b82e5ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessInfrastructureTarget.DataCloudflareZeroTrustAccessInfrastructureTargetConfig",
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
        "target_id": "targetId",
    },
)
class DataCloudflareZeroTrustAccessInfrastructureTargetConfig(
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
        filter: typing.Optional[typing.Union["DataCloudflareZeroTrustAccessInfrastructureTargetFilter", typing.Dict[builtins.str, typing.Any]]] = None,
        target_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Account identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#account_id DataCloudflareZeroTrustAccessInfrastructureTarget#account_id}
        :param filter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#filter DataCloudflareZeroTrustAccessInfrastructureTarget#filter}.
        :param target_id: Target identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#target_id DataCloudflareZeroTrustAccessInfrastructureTarget#target_id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(filter, dict):
            filter = DataCloudflareZeroTrustAccessInfrastructureTargetFilter(**filter)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4145eb2d91328043ef9d1d8bceb4f307ce490e84782cf3e0c2879c9122ef132d)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument filter", value=filter, expected_type=type_hints["filter"])
            check_type(argname="argument target_id", value=target_id, expected_type=type_hints["target_id"])
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
        if target_id is not None:
            self._values["target_id"] = target_id

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
        '''Account identifier.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#account_id DataCloudflareZeroTrustAccessInfrastructureTarget#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def filter(
        self,
    ) -> typing.Optional["DataCloudflareZeroTrustAccessInfrastructureTargetFilter"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#filter DataCloudflareZeroTrustAccessInfrastructureTarget#filter}.'''
        result = self._values.get("filter")
        return typing.cast(typing.Optional["DataCloudflareZeroTrustAccessInfrastructureTargetFilter"], result)

    @builtins.property
    def target_id(self) -> typing.Optional[builtins.str]:
        '''Target identifier.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#target_id DataCloudflareZeroTrustAccessInfrastructureTarget#target_id}
        '''
        result = self._values.get("target_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessInfrastructureTargetConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessInfrastructureTarget.DataCloudflareZeroTrustAccessInfrastructureTargetFilter",
    jsii_struct_bases=[],
    name_mapping={
        "created_after": "createdAfter",
        "created_before": "createdBefore",
        "direction": "direction",
        "hostname": "hostname",
        "hostname_contains": "hostnameContains",
        "ip_like": "ipLike",
        "ips": "ips",
        "ip_v4": "ipV4",
        "ipv4_end": "ipv4End",
        "ipv4_start": "ipv4Start",
        "ip_v6": "ipV6",
        "ipv6_end": "ipv6End",
        "ipv6_start": "ipv6Start",
        "modified_after": "modifiedAfter",
        "modified_before": "modifiedBefore",
        "order": "order",
        "target_ids": "targetIds",
        "virtual_network_id": "virtualNetworkId",
    },
)
class DataCloudflareZeroTrustAccessInfrastructureTargetFilter:
    def __init__(
        self,
        *,
        created_after: typing.Optional[builtins.str] = None,
        created_before: typing.Optional[builtins.str] = None,
        direction: typing.Optional[builtins.str] = None,
        hostname: typing.Optional[builtins.str] = None,
        hostname_contains: typing.Optional[builtins.str] = None,
        ip_like: typing.Optional[builtins.str] = None,
        ips: typing.Optional[typing.Sequence[builtins.str]] = None,
        ip_v4: typing.Optional[builtins.str] = None,
        ipv4_end: typing.Optional[builtins.str] = None,
        ipv4_start: typing.Optional[builtins.str] = None,
        ip_v6: typing.Optional[builtins.str] = None,
        ipv6_end: typing.Optional[builtins.str] = None,
        ipv6_start: typing.Optional[builtins.str] = None,
        modified_after: typing.Optional[builtins.str] = None,
        modified_before: typing.Optional[builtins.str] = None,
        order: typing.Optional[builtins.str] = None,
        target_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        virtual_network_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param created_after: Date and time at which the target was created after (inclusive). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#created_after DataCloudflareZeroTrustAccessInfrastructureTarget#created_after}
        :param created_before: Date and time at which the target was created before (inclusive). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#created_before DataCloudflareZeroTrustAccessInfrastructureTarget#created_before}
        :param direction: The sorting direction. Available values: "asc", "desc". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#direction DataCloudflareZeroTrustAccessInfrastructureTarget#direction}
        :param hostname: Hostname of a target. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#hostname DataCloudflareZeroTrustAccessInfrastructureTarget#hostname}
        :param hostname_contains: Partial match to the hostname of a target. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#hostname_contains DataCloudflareZeroTrustAccessInfrastructureTarget#hostname_contains}
        :param ip_like: Filters for targets whose IP addresses look like the specified string. Supports ``*`` as a wildcard character. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#ip_like DataCloudflareZeroTrustAccessInfrastructureTarget#ip_like}
        :param ips: Filters for targets that have any of the following IP addresses. Specify ``ips`` multiple times in query parameter to build list of candidates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#ips DataCloudflareZeroTrustAccessInfrastructureTarget#ips}
        :param ip_v4: IPv4 address of the target. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#ip_v4 DataCloudflareZeroTrustAccessInfrastructureTarget#ip_v4}
        :param ipv4_end: Defines an IPv4 filter range's ending value (inclusive). Requires ``ipv4_start`` to be specified as well. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#ipv4_end DataCloudflareZeroTrustAccessInfrastructureTarget#ipv4_end}
        :param ipv4_start: Defines an IPv4 filter range's starting value (inclusive). Requires ``ipv4_end`` to be specified as well. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#ipv4_start DataCloudflareZeroTrustAccessInfrastructureTarget#ipv4_start}
        :param ip_v6: IPv6 address of the target. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#ip_v6 DataCloudflareZeroTrustAccessInfrastructureTarget#ip_v6}
        :param ipv6_end: Defines an IPv6 filter range's ending value (inclusive). Requires ``ipv6_start`` to be specified as well. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#ipv6_end DataCloudflareZeroTrustAccessInfrastructureTarget#ipv6_end}
        :param ipv6_start: Defines an IPv6 filter range's starting value (inclusive). Requires ``ipv6_end`` to be specified as well. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#ipv6_start DataCloudflareZeroTrustAccessInfrastructureTarget#ipv6_start}
        :param modified_after: Date and time at which the target was modified after (inclusive). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#modified_after DataCloudflareZeroTrustAccessInfrastructureTarget#modified_after}
        :param modified_before: Date and time at which the target was modified before (inclusive). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#modified_before DataCloudflareZeroTrustAccessInfrastructureTarget#modified_before}
        :param order: The field to sort by. Available values: "hostname", "created_at". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#order DataCloudflareZeroTrustAccessInfrastructureTarget#order}
        :param target_ids: Filters for targets that have any of the following UUIDs. Specify ``target_ids`` multiple times in query parameter to build list of candidates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#target_ids DataCloudflareZeroTrustAccessInfrastructureTarget#target_ids}
        :param virtual_network_id: Private virtual network identifier of the target. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#virtual_network_id DataCloudflareZeroTrustAccessInfrastructureTarget#virtual_network_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd81a2d4eea260e47b5a249bedc9586b5a984bb985a0b1095abd9c631e590826)
            check_type(argname="argument created_after", value=created_after, expected_type=type_hints["created_after"])
            check_type(argname="argument created_before", value=created_before, expected_type=type_hints["created_before"])
            check_type(argname="argument direction", value=direction, expected_type=type_hints["direction"])
            check_type(argname="argument hostname", value=hostname, expected_type=type_hints["hostname"])
            check_type(argname="argument hostname_contains", value=hostname_contains, expected_type=type_hints["hostname_contains"])
            check_type(argname="argument ip_like", value=ip_like, expected_type=type_hints["ip_like"])
            check_type(argname="argument ips", value=ips, expected_type=type_hints["ips"])
            check_type(argname="argument ip_v4", value=ip_v4, expected_type=type_hints["ip_v4"])
            check_type(argname="argument ipv4_end", value=ipv4_end, expected_type=type_hints["ipv4_end"])
            check_type(argname="argument ipv4_start", value=ipv4_start, expected_type=type_hints["ipv4_start"])
            check_type(argname="argument ip_v6", value=ip_v6, expected_type=type_hints["ip_v6"])
            check_type(argname="argument ipv6_end", value=ipv6_end, expected_type=type_hints["ipv6_end"])
            check_type(argname="argument ipv6_start", value=ipv6_start, expected_type=type_hints["ipv6_start"])
            check_type(argname="argument modified_after", value=modified_after, expected_type=type_hints["modified_after"])
            check_type(argname="argument modified_before", value=modified_before, expected_type=type_hints["modified_before"])
            check_type(argname="argument order", value=order, expected_type=type_hints["order"])
            check_type(argname="argument target_ids", value=target_ids, expected_type=type_hints["target_ids"])
            check_type(argname="argument virtual_network_id", value=virtual_network_id, expected_type=type_hints["virtual_network_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if created_after is not None:
            self._values["created_after"] = created_after
        if created_before is not None:
            self._values["created_before"] = created_before
        if direction is not None:
            self._values["direction"] = direction
        if hostname is not None:
            self._values["hostname"] = hostname
        if hostname_contains is not None:
            self._values["hostname_contains"] = hostname_contains
        if ip_like is not None:
            self._values["ip_like"] = ip_like
        if ips is not None:
            self._values["ips"] = ips
        if ip_v4 is not None:
            self._values["ip_v4"] = ip_v4
        if ipv4_end is not None:
            self._values["ipv4_end"] = ipv4_end
        if ipv4_start is not None:
            self._values["ipv4_start"] = ipv4_start
        if ip_v6 is not None:
            self._values["ip_v6"] = ip_v6
        if ipv6_end is not None:
            self._values["ipv6_end"] = ipv6_end
        if ipv6_start is not None:
            self._values["ipv6_start"] = ipv6_start
        if modified_after is not None:
            self._values["modified_after"] = modified_after
        if modified_before is not None:
            self._values["modified_before"] = modified_before
        if order is not None:
            self._values["order"] = order
        if target_ids is not None:
            self._values["target_ids"] = target_ids
        if virtual_network_id is not None:
            self._values["virtual_network_id"] = virtual_network_id

    @builtins.property
    def created_after(self) -> typing.Optional[builtins.str]:
        '''Date and time at which the target was created after (inclusive).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#created_after DataCloudflareZeroTrustAccessInfrastructureTarget#created_after}
        '''
        result = self._values.get("created_after")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def created_before(self) -> typing.Optional[builtins.str]:
        '''Date and time at which the target was created before (inclusive).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#created_before DataCloudflareZeroTrustAccessInfrastructureTarget#created_before}
        '''
        result = self._values.get("created_before")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def direction(self) -> typing.Optional[builtins.str]:
        '''The sorting direction. Available values: "asc", "desc".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#direction DataCloudflareZeroTrustAccessInfrastructureTarget#direction}
        '''
        result = self._values.get("direction")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hostname(self) -> typing.Optional[builtins.str]:
        '''Hostname of a target.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#hostname DataCloudflareZeroTrustAccessInfrastructureTarget#hostname}
        '''
        result = self._values.get("hostname")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hostname_contains(self) -> typing.Optional[builtins.str]:
        '''Partial match to the hostname of a target.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#hostname_contains DataCloudflareZeroTrustAccessInfrastructureTarget#hostname_contains}
        '''
        result = self._values.get("hostname_contains")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ip_like(self) -> typing.Optional[builtins.str]:
        '''Filters for targets whose IP addresses look like the specified string. Supports ``*`` as a wildcard character.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#ip_like DataCloudflareZeroTrustAccessInfrastructureTarget#ip_like}
        '''
        result = self._values.get("ip_like")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ips(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Filters for targets that have any of the following IP addresses.

        Specify
        ``ips`` multiple times in query parameter to build list of candidates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#ips DataCloudflareZeroTrustAccessInfrastructureTarget#ips}
        '''
        result = self._values.get("ips")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ip_v4(self) -> typing.Optional[builtins.str]:
        '''IPv4 address of the target.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#ip_v4 DataCloudflareZeroTrustAccessInfrastructureTarget#ip_v4}
        '''
        result = self._values.get("ip_v4")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ipv4_end(self) -> typing.Optional[builtins.str]:
        '''Defines an IPv4 filter range's ending value (inclusive). Requires ``ipv4_start`` to be specified as well.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#ipv4_end DataCloudflareZeroTrustAccessInfrastructureTarget#ipv4_end}
        '''
        result = self._values.get("ipv4_end")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ipv4_start(self) -> typing.Optional[builtins.str]:
        '''Defines an IPv4 filter range's starting value (inclusive). Requires ``ipv4_end`` to be specified as well.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#ipv4_start DataCloudflareZeroTrustAccessInfrastructureTarget#ipv4_start}
        '''
        result = self._values.get("ipv4_start")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ip_v6(self) -> typing.Optional[builtins.str]:
        '''IPv6 address of the target.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#ip_v6 DataCloudflareZeroTrustAccessInfrastructureTarget#ip_v6}
        '''
        result = self._values.get("ip_v6")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ipv6_end(self) -> typing.Optional[builtins.str]:
        '''Defines an IPv6 filter range's ending value (inclusive). Requires ``ipv6_start`` to be specified as well.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#ipv6_end DataCloudflareZeroTrustAccessInfrastructureTarget#ipv6_end}
        '''
        result = self._values.get("ipv6_end")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ipv6_start(self) -> typing.Optional[builtins.str]:
        '''Defines an IPv6 filter range's starting value (inclusive). Requires ``ipv6_end`` to be specified as well.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#ipv6_start DataCloudflareZeroTrustAccessInfrastructureTarget#ipv6_start}
        '''
        result = self._values.get("ipv6_start")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def modified_after(self) -> typing.Optional[builtins.str]:
        '''Date and time at which the target was modified after (inclusive).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#modified_after DataCloudflareZeroTrustAccessInfrastructureTarget#modified_after}
        '''
        result = self._values.get("modified_after")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def modified_before(self) -> typing.Optional[builtins.str]:
        '''Date and time at which the target was modified before (inclusive).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#modified_before DataCloudflareZeroTrustAccessInfrastructureTarget#modified_before}
        '''
        result = self._values.get("modified_before")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def order(self) -> typing.Optional[builtins.str]:
        '''The field to sort by. Available values: "hostname", "created_at".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#order DataCloudflareZeroTrustAccessInfrastructureTarget#order}
        '''
        result = self._values.get("order")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Filters for targets that have any of the following UUIDs.

        Specify
        ``target_ids`` multiple times in query parameter to build list of
        candidates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#target_ids DataCloudflareZeroTrustAccessInfrastructureTarget#target_ids}
        '''
        result = self._values.get("target_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def virtual_network_id(self) -> typing.Optional[builtins.str]:
        '''Private virtual network identifier of the target.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_target#virtual_network_id DataCloudflareZeroTrustAccessInfrastructureTarget#virtual_network_id}
        '''
        result = self._values.get("virtual_network_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessInfrastructureTargetFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessInfrastructureTargetFilterOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessInfrastructureTarget.DataCloudflareZeroTrustAccessInfrastructureTargetFilterOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__04d0ab88b5a2bf4a48fee6106edd9e4b436794724937d3ead2cde0668a36aa9a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCreatedAfter")
    def reset_created_after(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatedAfter", []))

    @jsii.member(jsii_name="resetCreatedBefore")
    def reset_created_before(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatedBefore", []))

    @jsii.member(jsii_name="resetDirection")
    def reset_direction(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDirection", []))

    @jsii.member(jsii_name="resetHostname")
    def reset_hostname(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHostname", []))

    @jsii.member(jsii_name="resetHostnameContains")
    def reset_hostname_contains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHostnameContains", []))

    @jsii.member(jsii_name="resetIpLike")
    def reset_ip_like(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpLike", []))

    @jsii.member(jsii_name="resetIps")
    def reset_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIps", []))

    @jsii.member(jsii_name="resetIpV4")
    def reset_ip_v4(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpV4", []))

    @jsii.member(jsii_name="resetIpv4End")
    def reset_ipv4_end(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpv4End", []))

    @jsii.member(jsii_name="resetIpv4Start")
    def reset_ipv4_start(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpv4Start", []))

    @jsii.member(jsii_name="resetIpV6")
    def reset_ip_v6(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpV6", []))

    @jsii.member(jsii_name="resetIpv6End")
    def reset_ipv6_end(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpv6End", []))

    @jsii.member(jsii_name="resetIpv6Start")
    def reset_ipv6_start(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpv6Start", []))

    @jsii.member(jsii_name="resetModifiedAfter")
    def reset_modified_after(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetModifiedAfter", []))

    @jsii.member(jsii_name="resetModifiedBefore")
    def reset_modified_before(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetModifiedBefore", []))

    @jsii.member(jsii_name="resetOrder")
    def reset_order(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrder", []))

    @jsii.member(jsii_name="resetTargetIds")
    def reset_target_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetIds", []))

    @jsii.member(jsii_name="resetVirtualNetworkId")
    def reset_virtual_network_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVirtualNetworkId", []))

    @builtins.property
    @jsii.member(jsii_name="createdAfterInput")
    def created_after_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdAfterInput"))

    @builtins.property
    @jsii.member(jsii_name="createdBeforeInput")
    def created_before_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdBeforeInput"))

    @builtins.property
    @jsii.member(jsii_name="directionInput")
    def direction_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "directionInput"))

    @builtins.property
    @jsii.member(jsii_name="hostnameContainsInput")
    def hostname_contains_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostnameContainsInput"))

    @builtins.property
    @jsii.member(jsii_name="hostnameInput")
    def hostname_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostnameInput"))

    @builtins.property
    @jsii.member(jsii_name="ipLikeInput")
    def ip_like_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipLikeInput"))

    @builtins.property
    @jsii.member(jsii_name="ipsInput")
    def ips_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "ipsInput"))

    @builtins.property
    @jsii.member(jsii_name="ipv4EndInput")
    def ipv4_end_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipv4EndInput"))

    @builtins.property
    @jsii.member(jsii_name="ipV4Input")
    def ip_v4_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipV4Input"))

    @builtins.property
    @jsii.member(jsii_name="ipv4StartInput")
    def ipv4_start_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipv4StartInput"))

    @builtins.property
    @jsii.member(jsii_name="ipv6EndInput")
    def ipv6_end_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipv6EndInput"))

    @builtins.property
    @jsii.member(jsii_name="ipV6Input")
    def ip_v6_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipV6Input"))

    @builtins.property
    @jsii.member(jsii_name="ipv6StartInput")
    def ipv6_start_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipv6StartInput"))

    @builtins.property
    @jsii.member(jsii_name="modifiedAfterInput")
    def modified_after_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modifiedAfterInput"))

    @builtins.property
    @jsii.member(jsii_name="modifiedBeforeInput")
    def modified_before_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modifiedBeforeInput"))

    @builtins.property
    @jsii.member(jsii_name="orderInput")
    def order_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "orderInput"))

    @builtins.property
    @jsii.member(jsii_name="targetIdsInput")
    def target_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "targetIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="virtualNetworkIdInput")
    def virtual_network_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "virtualNetworkIdInput"))

    @builtins.property
    @jsii.member(jsii_name="createdAfter")
    def created_after(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAfter"))

    @created_after.setter
    def created_after(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5728d4e030dcf6c6f261234d6b64d304124a0134831c4c04942bf0094e582aab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdAfter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="createdBefore")
    def created_before(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdBefore"))

    @created_before.setter
    def created_before(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ec3a11699fd3fe85e200fe8d8b1e491c7e51355ad3664af4d6c0d7ad31b6c67)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdBefore", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="direction")
    def direction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "direction"))

    @direction.setter
    def direction(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1231c8ae33faf91077eabb60c0df9430cb8dc0b1b39b34ce4f4d2b08663ef1e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "direction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hostname")
    def hostname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostname"))

    @hostname.setter
    def hostname(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54ee5e3aefb47fa38dba4acd50f92a9b88f975962c50850c697fdbaa6c6a9063)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostname", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hostnameContains")
    def hostname_contains(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostnameContains"))

    @hostname_contains.setter
    def hostname_contains(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__232cd2e0dbe0f60151d1eb01a94deeb0ca121bb67be103a41c5a257869da089a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostnameContains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipLike")
    def ip_like(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipLike"))

    @ip_like.setter
    def ip_like(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25a54d458ebe1c01f3b240490c652177a1d33c2e67ef79e94e574b1d56363f13)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipLike", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ips")
    def ips(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ips"))

    @ips.setter
    def ips(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cca270a240045f35e7d0906da7620a60d411984a8b130deaf135b4426143b1e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ips", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipV4")
    def ip_v4(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipV4"))

    @ip_v4.setter
    def ip_v4(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6c207f5b8b8f1b14fe648f2871282c7af98546411d6b73991b8f2644e536431)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipV4", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipv4End")
    def ipv4_end(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv4End"))

    @ipv4_end.setter
    def ipv4_end(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e190cd98e7dfb47b0cf933af041323214f62b36fee9d397979b8ccc15c48b4a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipv4End", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipv4Start")
    def ipv4_start(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv4Start"))

    @ipv4_start.setter
    def ipv4_start(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b3c93fab7e0f897e1ae0c3561549ea5b44dd8de146dc4c28c91e0d42a750dc2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipv4Start", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipV6")
    def ip_v6(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipV6"))

    @ip_v6.setter
    def ip_v6(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0498b3ee456c48d749f9f286195e16293162f343e1cabd2fe68b86c49063243c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipV6", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipv6End")
    def ipv6_end(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv6End"))

    @ipv6_end.setter
    def ipv6_end(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47d208af05b5313a40f753fcf384196d4e50513544e4be57e9991470a24b2169)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipv6End", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipv6Start")
    def ipv6_start(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv6Start"))

    @ipv6_start.setter
    def ipv6_start(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d251ffae434f870ac5ddb08238ae42ff35a9209ff3bd44acc1f8fe0607adb30)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipv6Start", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="modifiedAfter")
    def modified_after(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modifiedAfter"))

    @modified_after.setter
    def modified_after(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31e7c5235af19513c163dc374bf8ce087366225cc89ba4a8cf5c6571ee467468)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "modifiedAfter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="modifiedBefore")
    def modified_before(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modifiedBefore"))

    @modified_before.setter
    def modified_before(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c492e149ba3803470b771ec50ab4f216df0ddf67813225d42615d01688d3f539)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "modifiedBefore", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="order")
    def order(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "order"))

    @order.setter
    def order(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bec23ed9fe08794823e5dacf04b56abea96b3540386dd7f380f6b0c100fcc1e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "order", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetIds")
    def target_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "targetIds"))

    @target_ids.setter
    def target_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc7c596281312fddf2436cb28afb269b96d5a10f72dea85ed758298d9b99492a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetIds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="virtualNetworkId")
    def virtual_network_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "virtualNetworkId"))

    @virtual_network_id.setter
    def virtual_network_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__705c6bdba0fadae4de616eeb8768a798dd304288648bb2d124f17d92283cadbc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "virtualNetworkId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareZeroTrustAccessInfrastructureTargetFilter]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareZeroTrustAccessInfrastructureTargetFilter]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareZeroTrustAccessInfrastructureTargetFilter]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20c51446c1c339649d3c9a85ad31ecd4e970c89056e965b8f1a123dd77fd87fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessInfrastructureTarget.DataCloudflareZeroTrustAccessInfrastructureTargetIp",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessInfrastructureTargetIp:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessInfrastructureTargetIp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessInfrastructureTarget.DataCloudflareZeroTrustAccessInfrastructureTargetIpIpv4",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessInfrastructureTargetIpIpv4:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessInfrastructureTargetIpIpv4(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessInfrastructureTargetIpIpv4OutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessInfrastructureTarget.DataCloudflareZeroTrustAccessInfrastructureTargetIpIpv4OutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4e9528028359006a7738cd03682333015cb4d2ff2eb90f9935196bd020791003)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="ipAddr")
    def ip_addr(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipAddr"))

    @builtins.property
    @jsii.member(jsii_name="virtualNetworkId")
    def virtual_network_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "virtualNetworkId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessInfrastructureTargetIpIpv4]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessInfrastructureTargetIpIpv4], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessInfrastructureTargetIpIpv4],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47ce80a14916acbb5d36e688ca6bbad0b4a798b7d7a78b6022c84b70e35c7a94)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessInfrastructureTarget.DataCloudflareZeroTrustAccessInfrastructureTargetIpIpv6",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessInfrastructureTargetIpIpv6:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessInfrastructureTargetIpIpv6(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessInfrastructureTargetIpIpv6OutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessInfrastructureTarget.DataCloudflareZeroTrustAccessInfrastructureTargetIpIpv6OutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a50f2453918555ebe2428c086becde1e42481bcb4b7f37606d5cbce9013d8d2d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="ipAddr")
    def ip_addr(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipAddr"))

    @builtins.property
    @jsii.member(jsii_name="virtualNetworkId")
    def virtual_network_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "virtualNetworkId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessInfrastructureTargetIpIpv6]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessInfrastructureTargetIpIpv6], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessInfrastructureTargetIpIpv6],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eef27ee91f7b900871a5dabd107115e7d9e00ded753c27f5d28454d3eeb8a04d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessInfrastructureTargetIpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessInfrastructureTarget.DataCloudflareZeroTrustAccessInfrastructureTargetIpOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9e8b54d950f276232a639fb2e069409ab29d48f0424628456d3a36ecd8a21fb1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="ipv4")
    def ipv4(
        self,
    ) -> DataCloudflareZeroTrustAccessInfrastructureTargetIpIpv4OutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessInfrastructureTargetIpIpv4OutputReference, jsii.get(self, "ipv4"))

    @builtins.property
    @jsii.member(jsii_name="ipv6")
    def ipv6(
        self,
    ) -> DataCloudflareZeroTrustAccessInfrastructureTargetIpIpv6OutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessInfrastructureTargetIpIpv6OutputReference, jsii.get(self, "ipv6"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessInfrastructureTargetIp]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessInfrastructureTargetIp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessInfrastructureTargetIp],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f07412491d274137a08accad6d20dc27401131d8963c61af11154c196842226)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataCloudflareZeroTrustAccessInfrastructureTarget",
    "DataCloudflareZeroTrustAccessInfrastructureTargetConfig",
    "DataCloudflareZeroTrustAccessInfrastructureTargetFilter",
    "DataCloudflareZeroTrustAccessInfrastructureTargetFilterOutputReference",
    "DataCloudflareZeroTrustAccessInfrastructureTargetIp",
    "DataCloudflareZeroTrustAccessInfrastructureTargetIpIpv4",
    "DataCloudflareZeroTrustAccessInfrastructureTargetIpIpv4OutputReference",
    "DataCloudflareZeroTrustAccessInfrastructureTargetIpIpv6",
    "DataCloudflareZeroTrustAccessInfrastructureTargetIpIpv6OutputReference",
    "DataCloudflareZeroTrustAccessInfrastructureTargetIpOutputReference",
]

publication.publish()

def _typecheckingstub__53ad8396ae177658c0a314d2d1469cd57dec156ccefafb091a140c633a7b4700(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    filter: typing.Optional[typing.Union[DataCloudflareZeroTrustAccessInfrastructureTargetFilter, typing.Dict[builtins.str, typing.Any]]] = None,
    target_id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__a4ff14354a701f3f64bb184ffe511c614b32184e0c75c4e5a86af155bbd20687(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab6c62fb57f291bc664db58a0ea21652bf20321b9c9fcaf2332c48ae56bb7198(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f51a7d0019b4f5147a1d787f98b04300bc2086b58803e69ed68ee027b82e5ea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4145eb2d91328043ef9d1d8bceb4f307ce490e84782cf3e0c2879c9122ef132d(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    filter: typing.Optional[typing.Union[DataCloudflareZeroTrustAccessInfrastructureTargetFilter, typing.Dict[builtins.str, typing.Any]]] = None,
    target_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd81a2d4eea260e47b5a249bedc9586b5a984bb985a0b1095abd9c631e590826(
    *,
    created_after: typing.Optional[builtins.str] = None,
    created_before: typing.Optional[builtins.str] = None,
    direction: typing.Optional[builtins.str] = None,
    hostname: typing.Optional[builtins.str] = None,
    hostname_contains: typing.Optional[builtins.str] = None,
    ip_like: typing.Optional[builtins.str] = None,
    ips: typing.Optional[typing.Sequence[builtins.str]] = None,
    ip_v4: typing.Optional[builtins.str] = None,
    ipv4_end: typing.Optional[builtins.str] = None,
    ipv4_start: typing.Optional[builtins.str] = None,
    ip_v6: typing.Optional[builtins.str] = None,
    ipv6_end: typing.Optional[builtins.str] = None,
    ipv6_start: typing.Optional[builtins.str] = None,
    modified_after: typing.Optional[builtins.str] = None,
    modified_before: typing.Optional[builtins.str] = None,
    order: typing.Optional[builtins.str] = None,
    target_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    virtual_network_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04d0ab88b5a2bf4a48fee6106edd9e4b436794724937d3ead2cde0668a36aa9a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5728d4e030dcf6c6f261234d6b64d304124a0134831c4c04942bf0094e582aab(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ec3a11699fd3fe85e200fe8d8b1e491c7e51355ad3664af4d6c0d7ad31b6c67(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1231c8ae33faf91077eabb60c0df9430cb8dc0b1b39b34ce4f4d2b08663ef1e2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54ee5e3aefb47fa38dba4acd50f92a9b88f975962c50850c697fdbaa6c6a9063(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__232cd2e0dbe0f60151d1eb01a94deeb0ca121bb67be103a41c5a257869da089a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25a54d458ebe1c01f3b240490c652177a1d33c2e67ef79e94e574b1d56363f13(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cca270a240045f35e7d0906da7620a60d411984a8b130deaf135b4426143b1e9(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6c207f5b8b8f1b14fe648f2871282c7af98546411d6b73991b8f2644e536431(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e190cd98e7dfb47b0cf933af041323214f62b36fee9d397979b8ccc15c48b4a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b3c93fab7e0f897e1ae0c3561549ea5b44dd8de146dc4c28c91e0d42a750dc2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0498b3ee456c48d749f9f286195e16293162f343e1cabd2fe68b86c49063243c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47d208af05b5313a40f753fcf384196d4e50513544e4be57e9991470a24b2169(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d251ffae434f870ac5ddb08238ae42ff35a9209ff3bd44acc1f8fe0607adb30(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31e7c5235af19513c163dc374bf8ce087366225cc89ba4a8cf5c6571ee467468(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c492e149ba3803470b771ec50ab4f216df0ddf67813225d42615d01688d3f539(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bec23ed9fe08794823e5dacf04b56abea96b3540386dd7f380f6b0c100fcc1e1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc7c596281312fddf2436cb28afb269b96d5a10f72dea85ed758298d9b99492a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__705c6bdba0fadae4de616eeb8768a798dd304288648bb2d124f17d92283cadbc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20c51446c1c339649d3c9a85ad31ecd4e970c89056e965b8f1a123dd77fd87fc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareZeroTrustAccessInfrastructureTargetFilter]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e9528028359006a7738cd03682333015cb4d2ff2eb90f9935196bd020791003(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47ce80a14916acbb5d36e688ca6bbad0b4a798b7d7a78b6022c84b70e35c7a94(
    value: typing.Optional[DataCloudflareZeroTrustAccessInfrastructureTargetIpIpv4],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a50f2453918555ebe2428c086becde1e42481bcb4b7f37606d5cbce9013d8d2d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eef27ee91f7b900871a5dabd107115e7d9e00ded753c27f5d28454d3eeb8a04d(
    value: typing.Optional[DataCloudflareZeroTrustAccessInfrastructureTargetIpIpv6],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e8b54d950f276232a639fb2e069409ab29d48f0424628456d3a36ecd8a21fb1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f07412491d274137a08accad6d20dc27401131d8963c61af11154c196842226(
    value: typing.Optional[DataCloudflareZeroTrustAccessInfrastructureTargetIp],
) -> None:
    """Type checking stubs"""
    pass
