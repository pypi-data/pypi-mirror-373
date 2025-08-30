r'''
# `data_cloudflare_zero_trust_access_infrastructure_targets`

Refer to the Terraform Registry for docs: [`data_cloudflare_zero_trust_access_infrastructure_targets`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets).
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


class DataCloudflareZeroTrustAccessInfrastructureTargets(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessInfrastructureTargets.DataCloudflareZeroTrustAccessInfrastructureTargets",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets cloudflare_zero_trust_access_infrastructure_targets}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
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
        max_items: typing.Optional[jsii.Number] = None,
        modified_after: typing.Optional[builtins.str] = None,
        modified_before: typing.Optional[builtins.str] = None,
        order: typing.Optional[builtins.str] = None,
        target_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        virtual_network_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets cloudflare_zero_trust_access_infrastructure_targets} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Account identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#account_id DataCloudflareZeroTrustAccessInfrastructureTargets#account_id}
        :param created_after: Date and time at which the target was created after (inclusive). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#created_after DataCloudflareZeroTrustAccessInfrastructureTargets#created_after}
        :param created_before: Date and time at which the target was created before (inclusive). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#created_before DataCloudflareZeroTrustAccessInfrastructureTargets#created_before}
        :param direction: The sorting direction. Available values: "asc", "desc". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#direction DataCloudflareZeroTrustAccessInfrastructureTargets#direction}
        :param hostname: Hostname of a target. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#hostname DataCloudflareZeroTrustAccessInfrastructureTargets#hostname}
        :param hostname_contains: Partial match to the hostname of a target. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#hostname_contains DataCloudflareZeroTrustAccessInfrastructureTargets#hostname_contains}
        :param ip_like: Filters for targets whose IP addresses look like the specified string. Supports ``*`` as a wildcard character. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#ip_like DataCloudflareZeroTrustAccessInfrastructureTargets#ip_like}
        :param ips: Filters for targets that have any of the following IP addresses. Specify ``ips`` multiple times in query parameter to build list of candidates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#ips DataCloudflareZeroTrustAccessInfrastructureTargets#ips}
        :param ip_v4: IPv4 address of the target. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#ip_v4 DataCloudflareZeroTrustAccessInfrastructureTargets#ip_v4}
        :param ipv4_end: Defines an IPv4 filter range's ending value (inclusive). Requires ``ipv4_start`` to be specified as well. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#ipv4_end DataCloudflareZeroTrustAccessInfrastructureTargets#ipv4_end}
        :param ipv4_start: Defines an IPv4 filter range's starting value (inclusive). Requires ``ipv4_end`` to be specified as well. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#ipv4_start DataCloudflareZeroTrustAccessInfrastructureTargets#ipv4_start}
        :param ip_v6: IPv6 address of the target. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#ip_v6 DataCloudflareZeroTrustAccessInfrastructureTargets#ip_v6}
        :param ipv6_end: Defines an IPv6 filter range's ending value (inclusive). Requires ``ipv6_start`` to be specified as well. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#ipv6_end DataCloudflareZeroTrustAccessInfrastructureTargets#ipv6_end}
        :param ipv6_start: Defines an IPv6 filter range's starting value (inclusive). Requires ``ipv6_end`` to be specified as well. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#ipv6_start DataCloudflareZeroTrustAccessInfrastructureTargets#ipv6_start}
        :param max_items: Max items to fetch, default: 1000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#max_items DataCloudflareZeroTrustAccessInfrastructureTargets#max_items}
        :param modified_after: Date and time at which the target was modified after (inclusive). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#modified_after DataCloudflareZeroTrustAccessInfrastructureTargets#modified_after}
        :param modified_before: Date and time at which the target was modified before (inclusive). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#modified_before DataCloudflareZeroTrustAccessInfrastructureTargets#modified_before}
        :param order: The field to sort by. Available values: "hostname", "created_at". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#order DataCloudflareZeroTrustAccessInfrastructureTargets#order}
        :param target_ids: Filters for targets that have any of the following UUIDs. Specify ``target_ids`` multiple times in query parameter to build list of candidates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#target_ids DataCloudflareZeroTrustAccessInfrastructureTargets#target_ids}
        :param virtual_network_id: Private virtual network identifier of the target. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#virtual_network_id DataCloudflareZeroTrustAccessInfrastructureTargets#virtual_network_id}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f46094f9a1f35724dfa12c3152d53be9525e73c53fdee57ff23caf17ec5bd2f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataCloudflareZeroTrustAccessInfrastructureTargetsConfig(
            account_id=account_id,
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
            max_items=max_items,
            modified_after=modified_after,
            modified_before=modified_before,
            order=order,
            target_ids=target_ids,
            virtual_network_id=virtual_network_id,
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
        '''Generates CDKTF code for importing a DataCloudflareZeroTrustAccessInfrastructureTargets resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataCloudflareZeroTrustAccessInfrastructureTargets to import.
        :param import_from_id: The id of the existing DataCloudflareZeroTrustAccessInfrastructureTargets that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataCloudflareZeroTrustAccessInfrastructureTargets to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5e2824065c6a063a97efa5a34909b337b6febfc56a038e9a12db60efc4dbd03)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

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

    @jsii.member(jsii_name="resetMaxItems")
    def reset_max_items(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxItems", []))

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
    def result(self) -> "DataCloudflareZeroTrustAccessInfrastructureTargetsResultList":
        return typing.cast("DataCloudflareZeroTrustAccessInfrastructureTargetsResultList", jsii.get(self, "result"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

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
    @jsii.member(jsii_name="maxItemsInput")
    def max_items_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxItemsInput"))

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
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb5acd33e82ec33923aa0f59722fd6c51645943f324da20d8a7618b23d0767e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="createdAfter")
    def created_after(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAfter"))

    @created_after.setter
    def created_after(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5f133f8903a6c585d4545e90a165489ad30c65efe93023713f4af48fc7e0c6b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdAfter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="createdBefore")
    def created_before(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdBefore"))

    @created_before.setter
    def created_before(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8d357e1d205d15e273f5bc1ff4802a67c171dfd9a2a4c24858e6ac4e8dcad51)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdBefore", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="direction")
    def direction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "direction"))

    @direction.setter
    def direction(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af124ea2b81cb1925fc7bd3fc57763db947f6c1d1f354bca99f5d3dd0a98bdce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "direction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hostname")
    def hostname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostname"))

    @hostname.setter
    def hostname(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26a6fa17280a383d9bdbfd57c05b6d549409a1f6ae4eb7a8ae1d45314e6a07e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostname", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hostnameContains")
    def hostname_contains(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostnameContains"))

    @hostname_contains.setter
    def hostname_contains(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1435fed418636943e3db3ffe0a49f5333ad790dc1aa68b5a07e5a885e58a3332)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostnameContains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipLike")
    def ip_like(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipLike"))

    @ip_like.setter
    def ip_like(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd7cc17732dc2554ae0906f6f4b9e732be5dd8250d2895f26b62fd0ca5162e57)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipLike", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ips")
    def ips(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ips"))

    @ips.setter
    def ips(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f7fbe3ba24cd2b3e6841e3ac1e53274706aa748fe1b838b04a6b1e7dafa2404)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ips", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipV4")
    def ip_v4(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipV4"))

    @ip_v4.setter
    def ip_v4(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__070aba0c9e23d2e181015449b26690b758908643fbec3db280238734ac5590af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipV4", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipv4End")
    def ipv4_end(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv4End"))

    @ipv4_end.setter
    def ipv4_end(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68a6c348d8e2dbc68cf73968e3ef31275d104826455c0494a93043e017818d3b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipv4End", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipv4Start")
    def ipv4_start(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv4Start"))

    @ipv4_start.setter
    def ipv4_start(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc44fc8215ad8b91903c1307bcc2ca245808d5de2dc754ce70487fc48912110b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipv4Start", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipV6")
    def ip_v6(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipV6"))

    @ip_v6.setter
    def ip_v6(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8d27ab177b2905ebfbefe85ef86a0cef7e5335824a5e93e447945282a9524d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipV6", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipv6End")
    def ipv6_end(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv6End"))

    @ipv6_end.setter
    def ipv6_end(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3ce4b4437fe75afb44f26dd6aff03334e0ab693e94ddb40155cd87ba515f8b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipv6End", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipv6Start")
    def ipv6_start(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv6Start"))

    @ipv6_start.setter
    def ipv6_start(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e27b91a0df43c995ac0337b330c01c364cf416d9b655fd14ca81b6f19d24586)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipv6Start", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxItems")
    def max_items(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxItems"))

    @max_items.setter
    def max_items(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f05db7ac959d08580cc1ea0ac6b1c1b9f32f68e35c2d3b7d938971902eaf88c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxItems", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="modifiedAfter")
    def modified_after(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modifiedAfter"))

    @modified_after.setter
    def modified_after(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba6e3c922db42a5be3e208322613435793074750b556bab5b6285fa50316ba0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "modifiedAfter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="modifiedBefore")
    def modified_before(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modifiedBefore"))

    @modified_before.setter
    def modified_before(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3080d55d2cfcbb3cb2f528fbaf57aa9a6579c9f47ac3f67560b7571d40c4ccd6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "modifiedBefore", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="order")
    def order(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "order"))

    @order.setter
    def order(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1e5c4d8e75813774191e85a78d30eb57ff9e4aca99b0d851b9d9377520cd424)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "order", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetIds")
    def target_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "targetIds"))

    @target_ids.setter
    def target_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfd500a65425ec1d80bc93bec600cea6157f603220757e12e5ac0d3720a010b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetIds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="virtualNetworkId")
    def virtual_network_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "virtualNetworkId"))

    @virtual_network_id.setter
    def virtual_network_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6301ce110536ad76b38b9af9677d144c489e5e8e6a0a2965e4a203d0c78a14a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "virtualNetworkId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessInfrastructureTargets.DataCloudflareZeroTrustAccessInfrastructureTargetsConfig",
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
        "max_items": "maxItems",
        "modified_after": "modifiedAfter",
        "modified_before": "modifiedBefore",
        "order": "order",
        "target_ids": "targetIds",
        "virtual_network_id": "virtualNetworkId",
    },
)
class DataCloudflareZeroTrustAccessInfrastructureTargetsConfig(
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
        max_items: typing.Optional[jsii.Number] = None,
        modified_after: typing.Optional[builtins.str] = None,
        modified_before: typing.Optional[builtins.str] = None,
        order: typing.Optional[builtins.str] = None,
        target_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        virtual_network_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Account identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#account_id DataCloudflareZeroTrustAccessInfrastructureTargets#account_id}
        :param created_after: Date and time at which the target was created after (inclusive). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#created_after DataCloudflareZeroTrustAccessInfrastructureTargets#created_after}
        :param created_before: Date and time at which the target was created before (inclusive). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#created_before DataCloudflareZeroTrustAccessInfrastructureTargets#created_before}
        :param direction: The sorting direction. Available values: "asc", "desc". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#direction DataCloudflareZeroTrustAccessInfrastructureTargets#direction}
        :param hostname: Hostname of a target. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#hostname DataCloudflareZeroTrustAccessInfrastructureTargets#hostname}
        :param hostname_contains: Partial match to the hostname of a target. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#hostname_contains DataCloudflareZeroTrustAccessInfrastructureTargets#hostname_contains}
        :param ip_like: Filters for targets whose IP addresses look like the specified string. Supports ``*`` as a wildcard character. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#ip_like DataCloudflareZeroTrustAccessInfrastructureTargets#ip_like}
        :param ips: Filters for targets that have any of the following IP addresses. Specify ``ips`` multiple times in query parameter to build list of candidates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#ips DataCloudflareZeroTrustAccessInfrastructureTargets#ips}
        :param ip_v4: IPv4 address of the target. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#ip_v4 DataCloudflareZeroTrustAccessInfrastructureTargets#ip_v4}
        :param ipv4_end: Defines an IPv4 filter range's ending value (inclusive). Requires ``ipv4_start`` to be specified as well. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#ipv4_end DataCloudflareZeroTrustAccessInfrastructureTargets#ipv4_end}
        :param ipv4_start: Defines an IPv4 filter range's starting value (inclusive). Requires ``ipv4_end`` to be specified as well. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#ipv4_start DataCloudflareZeroTrustAccessInfrastructureTargets#ipv4_start}
        :param ip_v6: IPv6 address of the target. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#ip_v6 DataCloudflareZeroTrustAccessInfrastructureTargets#ip_v6}
        :param ipv6_end: Defines an IPv6 filter range's ending value (inclusive). Requires ``ipv6_start`` to be specified as well. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#ipv6_end DataCloudflareZeroTrustAccessInfrastructureTargets#ipv6_end}
        :param ipv6_start: Defines an IPv6 filter range's starting value (inclusive). Requires ``ipv6_end`` to be specified as well. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#ipv6_start DataCloudflareZeroTrustAccessInfrastructureTargets#ipv6_start}
        :param max_items: Max items to fetch, default: 1000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#max_items DataCloudflareZeroTrustAccessInfrastructureTargets#max_items}
        :param modified_after: Date and time at which the target was modified after (inclusive). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#modified_after DataCloudflareZeroTrustAccessInfrastructureTargets#modified_after}
        :param modified_before: Date and time at which the target was modified before (inclusive). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#modified_before DataCloudflareZeroTrustAccessInfrastructureTargets#modified_before}
        :param order: The field to sort by. Available values: "hostname", "created_at". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#order DataCloudflareZeroTrustAccessInfrastructureTargets#order}
        :param target_ids: Filters for targets that have any of the following UUIDs. Specify ``target_ids`` multiple times in query parameter to build list of candidates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#target_ids DataCloudflareZeroTrustAccessInfrastructureTargets#target_ids}
        :param virtual_network_id: Private virtual network identifier of the target. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#virtual_network_id DataCloudflareZeroTrustAccessInfrastructureTargets#virtual_network_id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2926f0041f0b085f79bc8e6f943c51a9cfc5f3c960524435024074be62d4a855)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
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
            check_type(argname="argument max_items", value=max_items, expected_type=type_hints["max_items"])
            check_type(argname="argument modified_after", value=modified_after, expected_type=type_hints["modified_after"])
            check_type(argname="argument modified_before", value=modified_before, expected_type=type_hints["modified_before"])
            check_type(argname="argument order", value=order, expected_type=type_hints["order"])
            check_type(argname="argument target_ids", value=target_ids, expected_type=type_hints["target_ids"])
            check_type(argname="argument virtual_network_id", value=virtual_network_id, expected_type=type_hints["virtual_network_id"])
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
        if max_items is not None:
            self._values["max_items"] = max_items
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#account_id DataCloudflareZeroTrustAccessInfrastructureTargets#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def created_after(self) -> typing.Optional[builtins.str]:
        '''Date and time at which the target was created after (inclusive).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#created_after DataCloudflareZeroTrustAccessInfrastructureTargets#created_after}
        '''
        result = self._values.get("created_after")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def created_before(self) -> typing.Optional[builtins.str]:
        '''Date and time at which the target was created before (inclusive).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#created_before DataCloudflareZeroTrustAccessInfrastructureTargets#created_before}
        '''
        result = self._values.get("created_before")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def direction(self) -> typing.Optional[builtins.str]:
        '''The sorting direction. Available values: "asc", "desc".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#direction DataCloudflareZeroTrustAccessInfrastructureTargets#direction}
        '''
        result = self._values.get("direction")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hostname(self) -> typing.Optional[builtins.str]:
        '''Hostname of a target.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#hostname DataCloudflareZeroTrustAccessInfrastructureTargets#hostname}
        '''
        result = self._values.get("hostname")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hostname_contains(self) -> typing.Optional[builtins.str]:
        '''Partial match to the hostname of a target.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#hostname_contains DataCloudflareZeroTrustAccessInfrastructureTargets#hostname_contains}
        '''
        result = self._values.get("hostname_contains")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ip_like(self) -> typing.Optional[builtins.str]:
        '''Filters for targets whose IP addresses look like the specified string. Supports ``*`` as a wildcard character.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#ip_like DataCloudflareZeroTrustAccessInfrastructureTargets#ip_like}
        '''
        result = self._values.get("ip_like")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ips(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Filters for targets that have any of the following IP addresses.

        Specify
        ``ips`` multiple times in query parameter to build list of candidates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#ips DataCloudflareZeroTrustAccessInfrastructureTargets#ips}
        '''
        result = self._values.get("ips")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ip_v4(self) -> typing.Optional[builtins.str]:
        '''IPv4 address of the target.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#ip_v4 DataCloudflareZeroTrustAccessInfrastructureTargets#ip_v4}
        '''
        result = self._values.get("ip_v4")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ipv4_end(self) -> typing.Optional[builtins.str]:
        '''Defines an IPv4 filter range's ending value (inclusive). Requires ``ipv4_start`` to be specified as well.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#ipv4_end DataCloudflareZeroTrustAccessInfrastructureTargets#ipv4_end}
        '''
        result = self._values.get("ipv4_end")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ipv4_start(self) -> typing.Optional[builtins.str]:
        '''Defines an IPv4 filter range's starting value (inclusive). Requires ``ipv4_end`` to be specified as well.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#ipv4_start DataCloudflareZeroTrustAccessInfrastructureTargets#ipv4_start}
        '''
        result = self._values.get("ipv4_start")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ip_v6(self) -> typing.Optional[builtins.str]:
        '''IPv6 address of the target.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#ip_v6 DataCloudflareZeroTrustAccessInfrastructureTargets#ip_v6}
        '''
        result = self._values.get("ip_v6")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ipv6_end(self) -> typing.Optional[builtins.str]:
        '''Defines an IPv6 filter range's ending value (inclusive). Requires ``ipv6_start`` to be specified as well.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#ipv6_end DataCloudflareZeroTrustAccessInfrastructureTargets#ipv6_end}
        '''
        result = self._values.get("ipv6_end")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ipv6_start(self) -> typing.Optional[builtins.str]:
        '''Defines an IPv6 filter range's starting value (inclusive). Requires ``ipv6_end`` to be specified as well.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#ipv6_start DataCloudflareZeroTrustAccessInfrastructureTargets#ipv6_start}
        '''
        result = self._values.get("ipv6_start")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_items(self) -> typing.Optional[jsii.Number]:
        '''Max items to fetch, default: 1000.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#max_items DataCloudflareZeroTrustAccessInfrastructureTargets#max_items}
        '''
        result = self._values.get("max_items")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def modified_after(self) -> typing.Optional[builtins.str]:
        '''Date and time at which the target was modified after (inclusive).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#modified_after DataCloudflareZeroTrustAccessInfrastructureTargets#modified_after}
        '''
        result = self._values.get("modified_after")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def modified_before(self) -> typing.Optional[builtins.str]:
        '''Date and time at which the target was modified before (inclusive).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#modified_before DataCloudflareZeroTrustAccessInfrastructureTargets#modified_before}
        '''
        result = self._values.get("modified_before")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def order(self) -> typing.Optional[builtins.str]:
        '''The field to sort by. Available values: "hostname", "created_at".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#order DataCloudflareZeroTrustAccessInfrastructureTargets#order}
        '''
        result = self._values.get("order")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Filters for targets that have any of the following UUIDs.

        Specify
        ``target_ids`` multiple times in query parameter to build list of
        candidates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#target_ids DataCloudflareZeroTrustAccessInfrastructureTargets#target_ids}
        '''
        result = self._values.get("target_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def virtual_network_id(self) -> typing.Optional[builtins.str]:
        '''Private virtual network identifier of the target.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/zero_trust_access_infrastructure_targets#virtual_network_id DataCloudflareZeroTrustAccessInfrastructureTargets#virtual_network_id}
        '''
        result = self._values.get("virtual_network_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessInfrastructureTargetsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessInfrastructureTargets.DataCloudflareZeroTrustAccessInfrastructureTargetsResult",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessInfrastructureTargetsResult:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessInfrastructureTargetsResult(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessInfrastructureTargets.DataCloudflareZeroTrustAccessInfrastructureTargetsResultIp",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessInfrastructureTargetsResultIp:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessInfrastructureTargetsResultIp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessInfrastructureTargets.DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpIpv4",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpIpv4:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpIpv4(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpIpv4OutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessInfrastructureTargets.DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpIpv4OutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dab7d913667ea48b5c6bbe7da699c1e851f50ef6ac1555a5d8acc6285d13cf94)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpIpv4]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpIpv4], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpIpv4],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b0d510b6af99a96f5a91ede8f32488830d8f5f82d0ec760446fda5b9c359115)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessInfrastructureTargets.DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpIpv6",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpIpv6:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpIpv6(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpIpv6OutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessInfrastructureTargets.DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpIpv6OutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__197e198cbe7a02644beb6488d862aae880e34639234ca4d13eb71e6b097d2b5c)
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
    ) -> typing.Optional[DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpIpv6]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpIpv6], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpIpv6],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51199a8d5331db5b066aad81735540a613a40b6f689fc75ef9384fa22237dc4c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessInfrastructureTargets.DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f4e662fbf5efd1e557b73a7f4ee896329f81f1e75123a04101bf0811c7c403b7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="ipv4")
    def ipv4(
        self,
    ) -> DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpIpv4OutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpIpv4OutputReference, jsii.get(self, "ipv4"))

    @builtins.property
    @jsii.member(jsii_name="ipv6")
    def ipv6(
        self,
    ) -> DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpIpv6OutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpIpv6OutputReference, jsii.get(self, "ipv6"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessInfrastructureTargetsResultIp]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessInfrastructureTargetsResultIp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessInfrastructureTargetsResultIp],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__381d7c1a9b319159b4a7c0708db61cdf1cf6ecfa89d6fd51c5d02f057f1bed7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessInfrastructureTargetsResultList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessInfrastructureTargets.DataCloudflareZeroTrustAccessInfrastructureTargetsResultList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__04726a1f02611d25392d39064fe83e71ed6f25b0719c8cb4969cddc445d6af72)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataCloudflareZeroTrustAccessInfrastructureTargetsResultOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2286f33aa6bcd212106af022bccf545f3b99bbcaf6b387eb91f270f51df3d34c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataCloudflareZeroTrustAccessInfrastructureTargetsResultOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab7288f2aeb94056ca7cd526595d832ff5895453b061ced30e1cfeeebbfe0e4c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__06a86aac8652d1457406a77141bed8885512d6013b3242f9d46bad614063e403)
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
            type_hints = typing.get_type_hints(_typecheckingstub__dbec45d2d1c944652cf743a6b9882eab6c6e3a63d88abc945ceba4d5c961e4fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataCloudflareZeroTrustAccessInfrastructureTargetsResultOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareZeroTrustAccessInfrastructureTargets.DataCloudflareZeroTrustAccessInfrastructureTargetsResultOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c2e47f6500ef93ad205c97e9d474627cf5e3644956d64b14515858036aba3e87)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

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
    ) -> DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpOutputReference:
        return typing.cast(DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpOutputReference, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="modifiedAt")
    def modified_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modifiedAt"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataCloudflareZeroTrustAccessInfrastructureTargetsResult]:
        return typing.cast(typing.Optional[DataCloudflareZeroTrustAccessInfrastructureTargetsResult], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataCloudflareZeroTrustAccessInfrastructureTargetsResult],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8294c1807191c5c8f4902068242357698caa99a65432e99bb59bf3e7164bce20)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataCloudflareZeroTrustAccessInfrastructureTargets",
    "DataCloudflareZeroTrustAccessInfrastructureTargetsConfig",
    "DataCloudflareZeroTrustAccessInfrastructureTargetsResult",
    "DataCloudflareZeroTrustAccessInfrastructureTargetsResultIp",
    "DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpIpv4",
    "DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpIpv4OutputReference",
    "DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpIpv6",
    "DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpIpv6OutputReference",
    "DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpOutputReference",
    "DataCloudflareZeroTrustAccessInfrastructureTargetsResultList",
    "DataCloudflareZeroTrustAccessInfrastructureTargetsResultOutputReference",
]

publication.publish()

def _typecheckingstub__1f46094f9a1f35724dfa12c3152d53be9525e73c53fdee57ff23caf17ec5bd2f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
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
    max_items: typing.Optional[jsii.Number] = None,
    modified_after: typing.Optional[builtins.str] = None,
    modified_before: typing.Optional[builtins.str] = None,
    order: typing.Optional[builtins.str] = None,
    target_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    virtual_network_id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__c5e2824065c6a063a97efa5a34909b337b6febfc56a038e9a12db60efc4dbd03(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb5acd33e82ec33923aa0f59722fd6c51645943f324da20d8a7618b23d0767e9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5f133f8903a6c585d4545e90a165489ad30c65efe93023713f4af48fc7e0c6b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8d357e1d205d15e273f5bc1ff4802a67c171dfd9a2a4c24858e6ac4e8dcad51(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af124ea2b81cb1925fc7bd3fc57763db947f6c1d1f354bca99f5d3dd0a98bdce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26a6fa17280a383d9bdbfd57c05b6d549409a1f6ae4eb7a8ae1d45314e6a07e3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1435fed418636943e3db3ffe0a49f5333ad790dc1aa68b5a07e5a885e58a3332(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd7cc17732dc2554ae0906f6f4b9e732be5dd8250d2895f26b62fd0ca5162e57(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f7fbe3ba24cd2b3e6841e3ac1e53274706aa748fe1b838b04a6b1e7dafa2404(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__070aba0c9e23d2e181015449b26690b758908643fbec3db280238734ac5590af(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68a6c348d8e2dbc68cf73968e3ef31275d104826455c0494a93043e017818d3b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc44fc8215ad8b91903c1307bcc2ca245808d5de2dc754ce70487fc48912110b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8d27ab177b2905ebfbefe85ef86a0cef7e5335824a5e93e447945282a9524d3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3ce4b4437fe75afb44f26dd6aff03334e0ab693e94ddb40155cd87ba515f8b7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e27b91a0df43c995ac0337b330c01c364cf416d9b655fd14ca81b6f19d24586(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f05db7ac959d08580cc1ea0ac6b1c1b9f32f68e35c2d3b7d938971902eaf88c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba6e3c922db42a5be3e208322613435793074750b556bab5b6285fa50316ba0a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3080d55d2cfcbb3cb2f528fbaf57aa9a6579c9f47ac3f67560b7571d40c4ccd6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1e5c4d8e75813774191e85a78d30eb57ff9e4aca99b0d851b9d9377520cd424(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfd500a65425ec1d80bc93bec600cea6157f603220757e12e5ac0d3720a010b2(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6301ce110536ad76b38b9af9677d144c489e5e8e6a0a2965e4a203d0c78a14a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2926f0041f0b085f79bc8e6f943c51a9cfc5f3c960524435024074be62d4a855(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
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
    max_items: typing.Optional[jsii.Number] = None,
    modified_after: typing.Optional[builtins.str] = None,
    modified_before: typing.Optional[builtins.str] = None,
    order: typing.Optional[builtins.str] = None,
    target_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    virtual_network_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dab7d913667ea48b5c6bbe7da699c1e851f50ef6ac1555a5d8acc6285d13cf94(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b0d510b6af99a96f5a91ede8f32488830d8f5f82d0ec760446fda5b9c359115(
    value: typing.Optional[DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpIpv4],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__197e198cbe7a02644beb6488d862aae880e34639234ca4d13eb71e6b097d2b5c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51199a8d5331db5b066aad81735540a613a40b6f689fc75ef9384fa22237dc4c(
    value: typing.Optional[DataCloudflareZeroTrustAccessInfrastructureTargetsResultIpIpv6],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4e662fbf5efd1e557b73a7f4ee896329f81f1e75123a04101bf0811c7c403b7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__381d7c1a9b319159b4a7c0708db61cdf1cf6ecfa89d6fd51c5d02f057f1bed7a(
    value: typing.Optional[DataCloudflareZeroTrustAccessInfrastructureTargetsResultIp],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04726a1f02611d25392d39064fe83e71ed6f25b0719c8cb4969cddc445d6af72(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2286f33aa6bcd212106af022bccf545f3b99bbcaf6b387eb91f270f51df3d34c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab7288f2aeb94056ca7cd526595d832ff5895453b061ced30e1cfeeebbfe0e4c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06a86aac8652d1457406a77141bed8885512d6013b3242f9d46bad614063e403(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbec45d2d1c944652cf743a6b9882eab6c6e3a63d88abc945ceba4d5c961e4fc(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2e47f6500ef93ad205c97e9d474627cf5e3644956d64b14515858036aba3e87(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8294c1807191c5c8f4902068242357698caa99a65432e99bb59bf3e7164bce20(
    value: typing.Optional[DataCloudflareZeroTrustAccessInfrastructureTargetsResult],
) -> None:
    """Type checking stubs"""
    pass
