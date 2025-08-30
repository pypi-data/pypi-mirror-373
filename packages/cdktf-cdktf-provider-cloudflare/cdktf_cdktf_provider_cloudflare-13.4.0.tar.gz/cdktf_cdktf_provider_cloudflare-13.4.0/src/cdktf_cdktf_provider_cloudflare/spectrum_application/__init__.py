r'''
# `cloudflare_spectrum_application`

Refer to the Terraform Registry for docs: [`cloudflare_spectrum_application`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application).
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


class SpectrumApplication(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.spectrumApplication.SpectrumApplication",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application cloudflare_spectrum_application}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        dns: typing.Union["SpectrumApplicationDns", typing.Dict[builtins.str, typing.Any]],
        protocol: builtins.str,
        zone_id: builtins.str,
        argo_smart_routing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        edge_ips: typing.Optional[typing.Union["SpectrumApplicationEdgeIps", typing.Dict[builtins.str, typing.Any]]] = None,
        ip_firewall: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        origin_direct: typing.Optional[typing.Sequence[builtins.str]] = None,
        origin_dns: typing.Optional[typing.Union["SpectrumApplicationOriginDns", typing.Dict[builtins.str, typing.Any]]] = None,
        origin_port: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        proxy_protocol: typing.Optional[builtins.str] = None,
        tls: typing.Optional[builtins.str] = None,
        traffic_type: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application cloudflare_spectrum_application} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param dns: The name and type of DNS record for the Spectrum application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#dns SpectrumApplication#dns}
        :param protocol: The port configuration at Cloudflare's edge. May specify a single port, for example ``"tcp/1000"``, or a range of ports, for example ``"tcp/1000-2000"``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#protocol SpectrumApplication#protocol}
        :param zone_id: Zone identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#zone_id SpectrumApplication#zone_id}
        :param argo_smart_routing: Enables Argo Smart Routing for this application. Notes: Only available for TCP applications with traffic_type set to "direct". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#argo_smart_routing SpectrumApplication#argo_smart_routing}
        :param edge_ips: The anycast edge IP configuration for the hostname of this application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#edge_ips SpectrumApplication#edge_ips}
        :param ip_firewall: Enables IP Access Rules for this application. Notes: Only available for TCP applications. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#ip_firewall SpectrumApplication#ip_firewall}
        :param origin_direct: List of origin IP addresses. Array may contain multiple IP addresses for load balancing. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#origin_direct SpectrumApplication#origin_direct}
        :param origin_dns: The name and type of DNS record for the Spectrum application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#origin_dns SpectrumApplication#origin_dns}
        :param origin_port: The destination port at the origin. Only specified in conjunction with origin_dns. May use an integer to specify a single origin port, for example ``1000``, or a string to specify a range of origin ports, for example ``"1000-2000"``. Notes: If specifying a port range, the number of ports in the range must match the number of ports specified in the "protocol" field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#origin_port SpectrumApplication#origin_port}
        :param proxy_protocol: Enables Proxy Protocol to the origin. Refer to `Enable Proxy protocol <https://developers.cloudflare.com/spectrum/getting-started/proxy-protocol/>`_ for implementation details on PROXY Protocol V1, PROXY Protocol V2, and Simple Proxy Protocol. Available values: "off", "v1", "v2", "simple". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#proxy_protocol SpectrumApplication#proxy_protocol}
        :param tls: The type of TLS termination associated with the application. Available values: "off", "flexible", "full", "strict". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#tls SpectrumApplication#tls}
        :param traffic_type: Determines how data travels from the edge to your origin. When set to "direct", Spectrum will send traffic directly to your origin, and the application's type is derived from the ``protocol``. When set to "http" or "https", Spectrum will apply Cloudflare's HTTP/HTTPS features as it sends traffic to your origin, and the application type matches this property exactly. Available values: "direct", "http", "https". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#traffic_type SpectrumApplication#traffic_type}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8e7269c60d0bf30788128bf753648f2772a51e2b93dd530ae05428cd50cbaa5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = SpectrumApplicationConfig(
            dns=dns,
            protocol=protocol,
            zone_id=zone_id,
            argo_smart_routing=argo_smart_routing,
            edge_ips=edge_ips,
            ip_firewall=ip_firewall,
            origin_direct=origin_direct,
            origin_dns=origin_dns,
            origin_port=origin_port,
            proxy_protocol=proxy_protocol,
            tls=tls,
            traffic_type=traffic_type,
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
        '''Generates CDKTF code for importing a SpectrumApplication resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the SpectrumApplication to import.
        :param import_from_id: The id of the existing SpectrumApplication that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the SpectrumApplication to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15c212381095dad64980a02f89a7e92208e70f3462d0c7cd6e89122e61395f19)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putDns")
    def put_dns(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: The name of the DNS record associated with the application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#name SpectrumApplication#name}
        :param type: The type of DNS record associated with the application. Available values: "CNAME", "ADDRESS". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#type SpectrumApplication#type}
        '''
        value = SpectrumApplicationDns(name=name, type=type)

        return typing.cast(None, jsii.invoke(self, "putDns", [value]))

    @jsii.member(jsii_name="putEdgeIps")
    def put_edge_ips(
        self,
        *,
        connectivity: typing.Optional[builtins.str] = None,
        ips: typing.Optional[typing.Sequence[builtins.str]] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connectivity: The IP versions supported for inbound connections on Spectrum anycast IPs. Available values: "all", "ipv4", "ipv6". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#connectivity SpectrumApplication#connectivity}
        :param ips: The array of customer owned IPs we broadcast via anycast for this hostname and application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#ips SpectrumApplication#ips}
        :param type: The type of edge IP configuration specified. Dynamically allocated edge IPs use Spectrum anycast IPs in accordance with the connectivity you specify. Only valid with CNAME DNS names. Available values: "dynamic", "static". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#type SpectrumApplication#type}
        '''
        value = SpectrumApplicationEdgeIps(
            connectivity=connectivity, ips=ips, type=type
        )

        return typing.cast(None, jsii.invoke(self, "putEdgeIps", [value]))

    @jsii.member(jsii_name="putOriginDns")
    def put_origin_dns(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        ttl: typing.Optional[jsii.Number] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: The name of the DNS record associated with the origin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#name SpectrumApplication#name}
        :param ttl: The TTL of our resolution of your DNS record in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#ttl SpectrumApplication#ttl}
        :param type: The type of DNS record associated with the origin. "" is used to specify a combination of A/AAAA records. Available values: "", "A", "AAAA", "SRV". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#type SpectrumApplication#type}
        '''
        value = SpectrumApplicationOriginDns(name=name, ttl=ttl, type=type)

        return typing.cast(None, jsii.invoke(self, "putOriginDns", [value]))

    @jsii.member(jsii_name="resetArgoSmartRouting")
    def reset_argo_smart_routing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetArgoSmartRouting", []))

    @jsii.member(jsii_name="resetEdgeIps")
    def reset_edge_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEdgeIps", []))

    @jsii.member(jsii_name="resetIpFirewall")
    def reset_ip_firewall(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpFirewall", []))

    @jsii.member(jsii_name="resetOriginDirect")
    def reset_origin_direct(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOriginDirect", []))

    @jsii.member(jsii_name="resetOriginDns")
    def reset_origin_dns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOriginDns", []))

    @jsii.member(jsii_name="resetOriginPort")
    def reset_origin_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOriginPort", []))

    @jsii.member(jsii_name="resetProxyProtocol")
    def reset_proxy_protocol(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProxyProtocol", []))

    @jsii.member(jsii_name="resetTls")
    def reset_tls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTls", []))

    @jsii.member(jsii_name="resetTrafficType")
    def reset_traffic_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTrafficType", []))

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
    @jsii.member(jsii_name="createdOn")
    def created_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdOn"))

    @builtins.property
    @jsii.member(jsii_name="dns")
    def dns(self) -> "SpectrumApplicationDnsOutputReference":
        return typing.cast("SpectrumApplicationDnsOutputReference", jsii.get(self, "dns"))

    @builtins.property
    @jsii.member(jsii_name="edgeIps")
    def edge_ips(self) -> "SpectrumApplicationEdgeIpsOutputReference":
        return typing.cast("SpectrumApplicationEdgeIpsOutputReference", jsii.get(self, "edgeIps"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="modifiedOn")
    def modified_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modifiedOn"))

    @builtins.property
    @jsii.member(jsii_name="originDns")
    def origin_dns(self) -> "SpectrumApplicationOriginDnsOutputReference":
        return typing.cast("SpectrumApplicationOriginDnsOutputReference", jsii.get(self, "originDns"))

    @builtins.property
    @jsii.member(jsii_name="argoSmartRoutingInput")
    def argo_smart_routing_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "argoSmartRoutingInput"))

    @builtins.property
    @jsii.member(jsii_name="dnsInput")
    def dns_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "SpectrumApplicationDns"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "SpectrumApplicationDns"]], jsii.get(self, "dnsInput"))

    @builtins.property
    @jsii.member(jsii_name="edgeIpsInput")
    def edge_ips_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "SpectrumApplicationEdgeIps"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "SpectrumApplicationEdgeIps"]], jsii.get(self, "edgeIpsInput"))

    @builtins.property
    @jsii.member(jsii_name="ipFirewallInput")
    def ip_firewall_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "ipFirewallInput"))

    @builtins.property
    @jsii.member(jsii_name="originDirectInput")
    def origin_direct_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "originDirectInput"))

    @builtins.property
    @jsii.member(jsii_name="originDnsInput")
    def origin_dns_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "SpectrumApplicationOriginDns"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "SpectrumApplicationOriginDns"]], jsii.get(self, "originDnsInput"))

    @builtins.property
    @jsii.member(jsii_name="originPortInput")
    def origin_port_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], jsii.get(self, "originPortInput"))

    @builtins.property
    @jsii.member(jsii_name="protocolInput")
    def protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "protocolInput"))

    @builtins.property
    @jsii.member(jsii_name="proxyProtocolInput")
    def proxy_protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "proxyProtocolInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsInput")
    def tls_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tlsInput"))

    @builtins.property
    @jsii.member(jsii_name="trafficTypeInput")
    def traffic_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "trafficTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneIdInput")
    def zone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="argoSmartRouting")
    def argo_smart_routing(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "argoSmartRouting"))

    @argo_smart_routing.setter
    def argo_smart_routing(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e50b08bdda95e883198f9b2b41356c019a6ce26cf62157ece7327b75dd59cbf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "argoSmartRouting", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipFirewall")
    def ip_firewall(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ipFirewall"))

    @ip_firewall.setter
    def ip_firewall(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa9e0ba6c272c583f0c9c0b411d490d9c8a06624d829d72c46a9dcb791113881)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipFirewall", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="originDirect")
    def origin_direct(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "originDirect"))

    @origin_direct.setter
    def origin_direct(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__460221a74368371a7780adbe49dab46608969c7587390b541f1e255bf10dbefe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "originDirect", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="originPort")
    def origin_port(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "originPort"))

    @origin_port.setter
    def origin_port(self, value: typing.Mapping[builtins.str, typing.Any]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f874986f01d1769481036653cab1f98ce4373cb84ccec97469561d6a2927d9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "originPort", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="protocol")
    def protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "protocol"))

    @protocol.setter
    def protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__219cb25cafe297192df49f185cb8213c6846685287ee1736a7d9414e8b6113a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "protocol", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="proxyProtocol")
    def proxy_protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "proxyProtocol"))

    @proxy_protocol.setter
    def proxy_protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3aa012a6012a17c97dd6b2961affafb1341bfee73ddf56d4f37cf8b48310cb75)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "proxyProtocol", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tls")
    def tls(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tls"))

    @tls.setter
    def tls(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3444aae11d3077ee471acb430a3422f5b3a601290f22f99620b168d3869f4c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tls", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="trafficType")
    def traffic_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "trafficType"))

    @traffic_type.setter
    def traffic_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04053f913ef82b2d23202b1e8a10171ab6367d8b0a6b64646e4298700e79e9d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "trafficType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de488c1d9b769fba325b421924dbd4f98604a539fc1d06a3248a31d4d63d6241)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.spectrumApplication.SpectrumApplicationConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "dns": "dns",
        "protocol": "protocol",
        "zone_id": "zoneId",
        "argo_smart_routing": "argoSmartRouting",
        "edge_ips": "edgeIps",
        "ip_firewall": "ipFirewall",
        "origin_direct": "originDirect",
        "origin_dns": "originDns",
        "origin_port": "originPort",
        "proxy_protocol": "proxyProtocol",
        "tls": "tls",
        "traffic_type": "trafficType",
    },
)
class SpectrumApplicationConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        dns: typing.Union["SpectrumApplicationDns", typing.Dict[builtins.str, typing.Any]],
        protocol: builtins.str,
        zone_id: builtins.str,
        argo_smart_routing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        edge_ips: typing.Optional[typing.Union["SpectrumApplicationEdgeIps", typing.Dict[builtins.str, typing.Any]]] = None,
        ip_firewall: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        origin_direct: typing.Optional[typing.Sequence[builtins.str]] = None,
        origin_dns: typing.Optional[typing.Union["SpectrumApplicationOriginDns", typing.Dict[builtins.str, typing.Any]]] = None,
        origin_port: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        proxy_protocol: typing.Optional[builtins.str] = None,
        tls: typing.Optional[builtins.str] = None,
        traffic_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param dns: The name and type of DNS record for the Spectrum application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#dns SpectrumApplication#dns}
        :param protocol: The port configuration at Cloudflare's edge. May specify a single port, for example ``"tcp/1000"``, or a range of ports, for example ``"tcp/1000-2000"``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#protocol SpectrumApplication#protocol}
        :param zone_id: Zone identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#zone_id SpectrumApplication#zone_id}
        :param argo_smart_routing: Enables Argo Smart Routing for this application. Notes: Only available for TCP applications with traffic_type set to "direct". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#argo_smart_routing SpectrumApplication#argo_smart_routing}
        :param edge_ips: The anycast edge IP configuration for the hostname of this application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#edge_ips SpectrumApplication#edge_ips}
        :param ip_firewall: Enables IP Access Rules for this application. Notes: Only available for TCP applications. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#ip_firewall SpectrumApplication#ip_firewall}
        :param origin_direct: List of origin IP addresses. Array may contain multiple IP addresses for load balancing. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#origin_direct SpectrumApplication#origin_direct}
        :param origin_dns: The name and type of DNS record for the Spectrum application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#origin_dns SpectrumApplication#origin_dns}
        :param origin_port: The destination port at the origin. Only specified in conjunction with origin_dns. May use an integer to specify a single origin port, for example ``1000``, or a string to specify a range of origin ports, for example ``"1000-2000"``. Notes: If specifying a port range, the number of ports in the range must match the number of ports specified in the "protocol" field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#origin_port SpectrumApplication#origin_port}
        :param proxy_protocol: Enables Proxy Protocol to the origin. Refer to `Enable Proxy protocol <https://developers.cloudflare.com/spectrum/getting-started/proxy-protocol/>`_ for implementation details on PROXY Protocol V1, PROXY Protocol V2, and Simple Proxy Protocol. Available values: "off", "v1", "v2", "simple". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#proxy_protocol SpectrumApplication#proxy_protocol}
        :param tls: The type of TLS termination associated with the application. Available values: "off", "flexible", "full", "strict". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#tls SpectrumApplication#tls}
        :param traffic_type: Determines how data travels from the edge to your origin. When set to "direct", Spectrum will send traffic directly to your origin, and the application's type is derived from the ``protocol``. When set to "http" or "https", Spectrum will apply Cloudflare's HTTP/HTTPS features as it sends traffic to your origin, and the application type matches this property exactly. Available values: "direct", "http", "https". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#traffic_type SpectrumApplication#traffic_type}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(dns, dict):
            dns = SpectrumApplicationDns(**dns)
        if isinstance(edge_ips, dict):
            edge_ips = SpectrumApplicationEdgeIps(**edge_ips)
        if isinstance(origin_dns, dict):
            origin_dns = SpectrumApplicationOriginDns(**origin_dns)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a941c87dad8ccd85454b8867438f4271df02a7d9ec9b9bd03268762e1ac2482)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument dns", value=dns, expected_type=type_hints["dns"])
            check_type(argname="argument protocol", value=protocol, expected_type=type_hints["protocol"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
            check_type(argname="argument argo_smart_routing", value=argo_smart_routing, expected_type=type_hints["argo_smart_routing"])
            check_type(argname="argument edge_ips", value=edge_ips, expected_type=type_hints["edge_ips"])
            check_type(argname="argument ip_firewall", value=ip_firewall, expected_type=type_hints["ip_firewall"])
            check_type(argname="argument origin_direct", value=origin_direct, expected_type=type_hints["origin_direct"])
            check_type(argname="argument origin_dns", value=origin_dns, expected_type=type_hints["origin_dns"])
            check_type(argname="argument origin_port", value=origin_port, expected_type=type_hints["origin_port"])
            check_type(argname="argument proxy_protocol", value=proxy_protocol, expected_type=type_hints["proxy_protocol"])
            check_type(argname="argument tls", value=tls, expected_type=type_hints["tls"])
            check_type(argname="argument traffic_type", value=traffic_type, expected_type=type_hints["traffic_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "dns": dns,
            "protocol": protocol,
            "zone_id": zone_id,
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
        if argo_smart_routing is not None:
            self._values["argo_smart_routing"] = argo_smart_routing
        if edge_ips is not None:
            self._values["edge_ips"] = edge_ips
        if ip_firewall is not None:
            self._values["ip_firewall"] = ip_firewall
        if origin_direct is not None:
            self._values["origin_direct"] = origin_direct
        if origin_dns is not None:
            self._values["origin_dns"] = origin_dns
        if origin_port is not None:
            self._values["origin_port"] = origin_port
        if proxy_protocol is not None:
            self._values["proxy_protocol"] = proxy_protocol
        if tls is not None:
            self._values["tls"] = tls
        if traffic_type is not None:
            self._values["traffic_type"] = traffic_type

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
    def dns(self) -> "SpectrumApplicationDns":
        '''The name and type of DNS record for the Spectrum application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#dns SpectrumApplication#dns}
        '''
        result = self._values.get("dns")
        assert result is not None, "Required property 'dns' is missing"
        return typing.cast("SpectrumApplicationDns", result)

    @builtins.property
    def protocol(self) -> builtins.str:
        '''The port configuration at Cloudflare's edge.

        May specify a single port, for example ``"tcp/1000"``, or a range of ports, for example ``"tcp/1000-2000"``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#protocol SpectrumApplication#protocol}
        '''
        result = self._values.get("protocol")
        assert result is not None, "Required property 'protocol' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def zone_id(self) -> builtins.str:
        '''Zone identifier.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#zone_id SpectrumApplication#zone_id}
        '''
        result = self._values.get("zone_id")
        assert result is not None, "Required property 'zone_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def argo_smart_routing(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enables Argo Smart Routing for this application. Notes: Only available for TCP applications with traffic_type set to "direct".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#argo_smart_routing SpectrumApplication#argo_smart_routing}
        '''
        result = self._values.get("argo_smart_routing")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def edge_ips(self) -> typing.Optional["SpectrumApplicationEdgeIps"]:
        '''The anycast edge IP configuration for the hostname of this application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#edge_ips SpectrumApplication#edge_ips}
        '''
        result = self._values.get("edge_ips")
        return typing.cast(typing.Optional["SpectrumApplicationEdgeIps"], result)

    @builtins.property
    def ip_firewall(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enables IP Access Rules for this application. Notes: Only available for TCP applications.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#ip_firewall SpectrumApplication#ip_firewall}
        '''
        result = self._values.get("ip_firewall")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def origin_direct(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of origin IP addresses. Array may contain multiple IP addresses for load balancing.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#origin_direct SpectrumApplication#origin_direct}
        '''
        result = self._values.get("origin_direct")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def origin_dns(self) -> typing.Optional["SpectrumApplicationOriginDns"]:
        '''The name and type of DNS record for the Spectrum application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#origin_dns SpectrumApplication#origin_dns}
        '''
        result = self._values.get("origin_dns")
        return typing.cast(typing.Optional["SpectrumApplicationOriginDns"], result)

    @builtins.property
    def origin_port(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''The destination port at the origin.

        Only specified in conjunction with origin_dns. May use an integer to specify a single origin port, for example ``1000``, or a string to specify a range of origin ports, for example ``"1000-2000"``.
        Notes: If specifying a port range, the number of ports in the range must match the number of ports specified in the "protocol" field.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#origin_port SpectrumApplication#origin_port}
        '''
        result = self._values.get("origin_port")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def proxy_protocol(self) -> typing.Optional[builtins.str]:
        '''Enables Proxy Protocol to the origin.

        Refer to `Enable Proxy protocol <https://developers.cloudflare.com/spectrum/getting-started/proxy-protocol/>`_ for implementation details on PROXY Protocol V1, PROXY Protocol V2, and Simple Proxy Protocol.
        Available values: "off", "v1", "v2", "simple".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#proxy_protocol SpectrumApplication#proxy_protocol}
        '''
        result = self._values.get("proxy_protocol")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tls(self) -> typing.Optional[builtins.str]:
        '''The type of TLS termination associated with the application. Available values: "off", "flexible", "full", "strict".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#tls SpectrumApplication#tls}
        '''
        result = self._values.get("tls")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def traffic_type(self) -> typing.Optional[builtins.str]:
        '''Determines how data travels from the edge to your origin.

        When set to "direct", Spectrum will send traffic directly to your origin, and the application's type is derived from the ``protocol``. When set to "http" or "https", Spectrum will apply Cloudflare's HTTP/HTTPS features as it sends traffic to your origin, and the application type matches this property exactly.
        Available values: "direct", "http", "https".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#traffic_type SpectrumApplication#traffic_type}
        '''
        result = self._values.get("traffic_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SpectrumApplicationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.spectrumApplication.SpectrumApplicationDns",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "type": "type"},
)
class SpectrumApplicationDns:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: The name of the DNS record associated with the application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#name SpectrumApplication#name}
        :param type: The type of DNS record associated with the application. Available values: "CNAME", "ADDRESS". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#type SpectrumApplication#type}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cf84338e2c80f7292bf92c541a8fb85010c4035785e392430a414c24eff09a1)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the DNS record associated with the application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#name SpectrumApplication#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''The type of DNS record associated with the application. Available values: "CNAME", "ADDRESS".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#type SpectrumApplication#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SpectrumApplicationDns(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SpectrumApplicationDnsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.spectrumApplication.SpectrumApplicationDnsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d748324be59d3eac9bc22b4a648ff2d6e12bae8e1ad5f02184f1f41b8e4fd77b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dec398cd605276aaf603e06a1c1378ef19be107b856c927543dd924ae86dcb1b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51c5f9777e78686250f301a27b98937372febf221adead8dda97f3bbd0fcb746)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SpectrumApplicationDns]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SpectrumApplicationDns]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SpectrumApplicationDns]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9207346fd7f10861c7a42b9e40b28478c573bd1677cff1856a2682611011f0d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.spectrumApplication.SpectrumApplicationEdgeIps",
    jsii_struct_bases=[],
    name_mapping={"connectivity": "connectivity", "ips": "ips", "type": "type"},
)
class SpectrumApplicationEdgeIps:
    def __init__(
        self,
        *,
        connectivity: typing.Optional[builtins.str] = None,
        ips: typing.Optional[typing.Sequence[builtins.str]] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connectivity: The IP versions supported for inbound connections on Spectrum anycast IPs. Available values: "all", "ipv4", "ipv6". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#connectivity SpectrumApplication#connectivity}
        :param ips: The array of customer owned IPs we broadcast via anycast for this hostname and application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#ips SpectrumApplication#ips}
        :param type: The type of edge IP configuration specified. Dynamically allocated edge IPs use Spectrum anycast IPs in accordance with the connectivity you specify. Only valid with CNAME DNS names. Available values: "dynamic", "static". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#type SpectrumApplication#type}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2d1f7038b0975c26c6d4d6cae31639b7a4c0b7313c58df1a741fe4eaf6ac4c3)
            check_type(argname="argument connectivity", value=connectivity, expected_type=type_hints["connectivity"])
            check_type(argname="argument ips", value=ips, expected_type=type_hints["ips"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if connectivity is not None:
            self._values["connectivity"] = connectivity
        if ips is not None:
            self._values["ips"] = ips
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def connectivity(self) -> typing.Optional[builtins.str]:
        '''The IP versions supported for inbound connections on Spectrum anycast IPs. Available values: "all", "ipv4", "ipv6".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#connectivity SpectrumApplication#connectivity}
        '''
        result = self._values.get("connectivity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ips(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The array of customer owned IPs we broadcast via anycast for this hostname and application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#ips SpectrumApplication#ips}
        '''
        result = self._values.get("ips")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''The type of edge IP configuration specified.

        Dynamically allocated edge IPs use Spectrum anycast IPs in accordance with the connectivity you specify. Only valid with CNAME DNS names.
        Available values: "dynamic", "static".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#type SpectrumApplication#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SpectrumApplicationEdgeIps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SpectrumApplicationEdgeIpsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.spectrumApplication.SpectrumApplicationEdgeIpsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f95a091c0f8182ff1dd2fee266e2fbeb64d34480f01d1a3ec55192719caabf12)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetConnectivity")
    def reset_connectivity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectivity", []))

    @jsii.member(jsii_name="resetIps")
    def reset_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIps", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @builtins.property
    @jsii.member(jsii_name="connectivityInput")
    def connectivity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectivityInput"))

    @builtins.property
    @jsii.member(jsii_name="ipsInput")
    def ips_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "ipsInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="connectivity")
    def connectivity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectivity"))

    @connectivity.setter
    def connectivity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ecc546a0e2250ceee50667ec70bfecf3040ba8ed9684656e07e9ecae0950cb6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectivity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ips")
    def ips(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ips"))

    @ips.setter
    def ips(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8d8d3d26a05f6821dd84a023e418aa251d6497b3304093901b391bbd6c99f1e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ips", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e27c80c86d7d90a76b3ce2b64be67fccf086e44f01d11cd0ed005d28fab9727)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SpectrumApplicationEdgeIps]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SpectrumApplicationEdgeIps]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SpectrumApplicationEdgeIps]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fffbd2853a2112cabbc4e107f422a159926057faccc73e89f42dab1b703188f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.spectrumApplication.SpectrumApplicationOriginDns",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "ttl": "ttl", "type": "type"},
)
class SpectrumApplicationOriginDns:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        ttl: typing.Optional[jsii.Number] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: The name of the DNS record associated with the origin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#name SpectrumApplication#name}
        :param ttl: The TTL of our resolution of your DNS record in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#ttl SpectrumApplication#ttl}
        :param type: The type of DNS record associated with the origin. "" is used to specify a combination of A/AAAA records. Available values: "", "A", "AAAA", "SRV". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#type SpectrumApplication#type}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae0d32f731f9dada99bc46364e3a4fea709e6a8753a10e6a61f5bbb5c4f03d39)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument ttl", value=ttl, expected_type=type_hints["ttl"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if ttl is not None:
            self._values["ttl"] = ttl
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the DNS record associated with the origin.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#name SpectrumApplication#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ttl(self) -> typing.Optional[jsii.Number]:
        '''The TTL of our resolution of your DNS record in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#ttl SpectrumApplication#ttl}
        '''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''The type of DNS record associated with the origin.

        "" is used to specify a combination of A/AAAA records.
        Available values: "", "A", "AAAA", "SRV".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/spectrum_application#type SpectrumApplication#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SpectrumApplicationOriginDns(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SpectrumApplicationOriginDnsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.spectrumApplication.SpectrumApplicationOriginDnsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__368f433f040359b3de60c635c7c38e656ec86ecf9b7a04096b87fcdb18007a85)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetTtl")
    def reset_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTtl", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="ttlInput")
    def ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ttlInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd4f4ad0229a39ba7ba9097b9cee99c5acec2ce34b1c3652fcc6f6b0a1ed8cd7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ttl"))

    @ttl.setter
    def ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b23531bb7d360152b331c53d6f0e687085bf606427486fbb9d0662a0619c8217)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ttl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__026fbc643aaa25b37580cabc8526e9a8dd65a3eb5d39d7c5523a4daf3a5fcc67)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SpectrumApplicationOriginDns]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SpectrumApplicationOriginDns]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SpectrumApplicationOriginDns]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25ba577887ab8c519ad3baa5ded72d4366e101b3e48c2b54cffbe8cf0310eb0e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "SpectrumApplication",
    "SpectrumApplicationConfig",
    "SpectrumApplicationDns",
    "SpectrumApplicationDnsOutputReference",
    "SpectrumApplicationEdgeIps",
    "SpectrumApplicationEdgeIpsOutputReference",
    "SpectrumApplicationOriginDns",
    "SpectrumApplicationOriginDnsOutputReference",
]

publication.publish()

def _typecheckingstub__a8e7269c60d0bf30788128bf753648f2772a51e2b93dd530ae05428cd50cbaa5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    dns: typing.Union[SpectrumApplicationDns, typing.Dict[builtins.str, typing.Any]],
    protocol: builtins.str,
    zone_id: builtins.str,
    argo_smart_routing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    edge_ips: typing.Optional[typing.Union[SpectrumApplicationEdgeIps, typing.Dict[builtins.str, typing.Any]]] = None,
    ip_firewall: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    origin_direct: typing.Optional[typing.Sequence[builtins.str]] = None,
    origin_dns: typing.Optional[typing.Union[SpectrumApplicationOriginDns, typing.Dict[builtins.str, typing.Any]]] = None,
    origin_port: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    proxy_protocol: typing.Optional[builtins.str] = None,
    tls: typing.Optional[builtins.str] = None,
    traffic_type: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__15c212381095dad64980a02f89a7e92208e70f3462d0c7cd6e89122e61395f19(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e50b08bdda95e883198f9b2b41356c019a6ce26cf62157ece7327b75dd59cbf(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa9e0ba6c272c583f0c9c0b411d490d9c8a06624d829d72c46a9dcb791113881(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__460221a74368371a7780adbe49dab46608969c7587390b541f1e255bf10dbefe(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f874986f01d1769481036653cab1f98ce4373cb84ccec97469561d6a2927d9f(
    value: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__219cb25cafe297192df49f185cb8213c6846685287ee1736a7d9414e8b6113a3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3aa012a6012a17c97dd6b2961affafb1341bfee73ddf56d4f37cf8b48310cb75(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3444aae11d3077ee471acb430a3422f5b3a601290f22f99620b168d3869f4c9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04053f913ef82b2d23202b1e8a10171ab6367d8b0a6b64646e4298700e79e9d1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de488c1d9b769fba325b421924dbd4f98604a539fc1d06a3248a31d4d63d6241(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a941c87dad8ccd85454b8867438f4271df02a7d9ec9b9bd03268762e1ac2482(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    dns: typing.Union[SpectrumApplicationDns, typing.Dict[builtins.str, typing.Any]],
    protocol: builtins.str,
    zone_id: builtins.str,
    argo_smart_routing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    edge_ips: typing.Optional[typing.Union[SpectrumApplicationEdgeIps, typing.Dict[builtins.str, typing.Any]]] = None,
    ip_firewall: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    origin_direct: typing.Optional[typing.Sequence[builtins.str]] = None,
    origin_dns: typing.Optional[typing.Union[SpectrumApplicationOriginDns, typing.Dict[builtins.str, typing.Any]]] = None,
    origin_port: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    proxy_protocol: typing.Optional[builtins.str] = None,
    tls: typing.Optional[builtins.str] = None,
    traffic_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cf84338e2c80f7292bf92c541a8fb85010c4035785e392430a414c24eff09a1(
    *,
    name: typing.Optional[builtins.str] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d748324be59d3eac9bc22b4a648ff2d6e12bae8e1ad5f02184f1f41b8e4fd77b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dec398cd605276aaf603e06a1c1378ef19be107b856c927543dd924ae86dcb1b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51c5f9777e78686250f301a27b98937372febf221adead8dda97f3bbd0fcb746(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9207346fd7f10861c7a42b9e40b28478c573bd1677cff1856a2682611011f0d1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SpectrumApplicationDns]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2d1f7038b0975c26c6d4d6cae31639b7a4c0b7313c58df1a741fe4eaf6ac4c3(
    *,
    connectivity: typing.Optional[builtins.str] = None,
    ips: typing.Optional[typing.Sequence[builtins.str]] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f95a091c0f8182ff1dd2fee266e2fbeb64d34480f01d1a3ec55192719caabf12(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ecc546a0e2250ceee50667ec70bfecf3040ba8ed9684656e07e9ecae0950cb6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8d8d3d26a05f6821dd84a023e418aa251d6497b3304093901b391bbd6c99f1e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e27c80c86d7d90a76b3ce2b64be67fccf086e44f01d11cd0ed005d28fab9727(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fffbd2853a2112cabbc4e107f422a159926057faccc73e89f42dab1b703188f2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SpectrumApplicationEdgeIps]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae0d32f731f9dada99bc46364e3a4fea709e6a8753a10e6a61f5bbb5c4f03d39(
    *,
    name: typing.Optional[builtins.str] = None,
    ttl: typing.Optional[jsii.Number] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__368f433f040359b3de60c635c7c38e656ec86ecf9b7a04096b87fcdb18007a85(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd4f4ad0229a39ba7ba9097b9cee99c5acec2ce34b1c3652fcc6f6b0a1ed8cd7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b23531bb7d360152b331c53d6f0e687085bf606427486fbb9d0662a0619c8217(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__026fbc643aaa25b37580cabc8526e9a8dd65a3eb5d39d7c5523a4daf3a5fcc67(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25ba577887ab8c519ad3baa5ded72d4366e101b3e48c2b54cffbe8cf0310eb0e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SpectrumApplicationOriginDns]],
) -> None:
    """Type checking stubs"""
    pass
