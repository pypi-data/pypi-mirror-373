r'''
# `cloudflare_custom_hostname`

Refer to the Terraform Registry for docs: [`cloudflare_custom_hostname`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname).
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


class CustomHostname(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.customHostname.CustomHostname",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname cloudflare_custom_hostname}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        hostname: builtins.str,
        ssl: typing.Union["CustomHostnameSsl", typing.Dict[builtins.str, typing.Any]],
        zone_id: builtins.str,
        custom_metadata: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        custom_origin_server: typing.Optional[builtins.str] = None,
        custom_origin_sni: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname cloudflare_custom_hostname} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param hostname: The custom hostname that will point to your hostname via CNAME. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#hostname CustomHostname#hostname}
        :param ssl: SSL properties used when creating the custom hostname. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#ssl CustomHostname#ssl}
        :param zone_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#zone_id CustomHostname#zone_id}
        :param custom_metadata: Unique key/value metadata for this hostname. These are per-hostname (customer) settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#custom_metadata CustomHostname#custom_metadata}
        :param custom_origin_server: a valid hostname that’s been added to your DNS zone as an A, AAAA, or CNAME record. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#custom_origin_server CustomHostname#custom_origin_server}
        :param custom_origin_sni: A hostname that will be sent to your custom origin server as SNI for TLS handshake. This can be a valid subdomain of the zone or custom origin server name or the string ':request_host_header:' which will cause the host header in the request to be used as SNI. Not configurable with default/fallback origin server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#custom_origin_sni CustomHostname#custom_origin_sni}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2999243784abde236613791702b528a1f4896b54dcf17adba234a389d1841b3d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = CustomHostnameConfig(
            hostname=hostname,
            ssl=ssl,
            zone_id=zone_id,
            custom_metadata=custom_metadata,
            custom_origin_server=custom_origin_server,
            custom_origin_sni=custom_origin_sni,
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
        '''Generates CDKTF code for importing a CustomHostname resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the CustomHostname to import.
        :param import_from_id: The id of the existing CustomHostname that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the CustomHostname to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21de9577f0d51f1369fb2d48f23491d36f2e50c4b122cff4a36b30a5d741793e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putSsl")
    def put_ssl(
        self,
        *,
        bundle_method: typing.Optional[builtins.str] = None,
        certificate_authority: typing.Optional[builtins.str] = None,
        cloudflare_branding: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        custom_cert_bundle: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CustomHostnameSslCustomCertBundle", typing.Dict[builtins.str, typing.Any]]]]] = None,
        custom_certificate: typing.Optional[builtins.str] = None,
        custom_key: typing.Optional[builtins.str] = None,
        method: typing.Optional[builtins.str] = None,
        settings: typing.Optional[typing.Union["CustomHostnameSslSettings", typing.Dict[builtins.str, typing.Any]]] = None,
        type: typing.Optional[builtins.str] = None,
        wildcard: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param bundle_method: A ubiquitous bundle has the highest probability of being verified everywhere, even by clients using outdated or unusual trust stores. An optimal bundle uses the shortest chain and newest intermediates. And the force bundle verifies the chain, but does not otherwise modify it. Available values: "ubiquitous", "optimal", "force". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#bundle_method CustomHostname#bundle_method}
        :param certificate_authority: The Certificate Authority that will issue the certificate Available values: "digicert", "google", "lets_encrypt", "ssl_com". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#certificate_authority CustomHostname#certificate_authority}
        :param cloudflare_branding: Whether or not to add Cloudflare Branding for the order. This will add a subdomain of sni.cloudflaressl.com as the Common Name if set to true Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#cloudflare_branding CustomHostname#cloudflare_branding}
        :param custom_cert_bundle: Array of custom certificate and key pairs (1 or 2 pairs allowed). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#custom_cert_bundle CustomHostname#custom_cert_bundle}
        :param custom_certificate: If a custom uploaded certificate is used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#custom_certificate CustomHostname#custom_certificate}
        :param custom_key: The key for a custom uploaded certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#custom_key CustomHostname#custom_key}
        :param method: Domain control validation (DCV) method used for this hostname. Available values: "http", "txt", "email". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#method CustomHostname#method}
        :param settings: SSL specific settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#settings CustomHostname#settings}
        :param type: Level of validation to be used for this hostname. Domain validation (dv) must be used. Available values: "dv". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#type CustomHostname#type}
        :param wildcard: Indicates whether the certificate covers a wildcard. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#wildcard CustomHostname#wildcard}
        '''
        value = CustomHostnameSsl(
            bundle_method=bundle_method,
            certificate_authority=certificate_authority,
            cloudflare_branding=cloudflare_branding,
            custom_cert_bundle=custom_cert_bundle,
            custom_certificate=custom_certificate,
            custom_key=custom_key,
            method=method,
            settings=settings,
            type=type,
            wildcard=wildcard,
        )

        return typing.cast(None, jsii.invoke(self, "putSsl", [value]))

    @jsii.member(jsii_name="resetCustomMetadata")
    def reset_custom_metadata(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomMetadata", []))

    @jsii.member(jsii_name="resetCustomOriginServer")
    def reset_custom_origin_server(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomOriginServer", []))

    @jsii.member(jsii_name="resetCustomOriginSni")
    def reset_custom_origin_sni(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomOriginSni", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="ownershipVerification")
    def ownership_verification(
        self,
    ) -> "CustomHostnameOwnershipVerificationOutputReference":
        return typing.cast("CustomHostnameOwnershipVerificationOutputReference", jsii.get(self, "ownershipVerification"))

    @builtins.property
    @jsii.member(jsii_name="ownershipVerificationHttp")
    def ownership_verification_http(
        self,
    ) -> "CustomHostnameOwnershipVerificationHttpOutputReference":
        return typing.cast("CustomHostnameOwnershipVerificationHttpOutputReference", jsii.get(self, "ownershipVerificationHttp"))

    @builtins.property
    @jsii.member(jsii_name="ssl")
    def ssl(self) -> "CustomHostnameSslOutputReference":
        return typing.cast("CustomHostnameSslOutputReference", jsii.get(self, "ssl"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="verificationErrors")
    def verification_errors(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "verificationErrors"))

    @builtins.property
    @jsii.member(jsii_name="customMetadataInput")
    def custom_metadata_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "customMetadataInput"))

    @builtins.property
    @jsii.member(jsii_name="customOriginServerInput")
    def custom_origin_server_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customOriginServerInput"))

    @builtins.property
    @jsii.member(jsii_name="customOriginSniInput")
    def custom_origin_sni_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customOriginSniInput"))

    @builtins.property
    @jsii.member(jsii_name="hostnameInput")
    def hostname_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostnameInput"))

    @builtins.property
    @jsii.member(jsii_name="sslInput")
    def ssl_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "CustomHostnameSsl"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "CustomHostnameSsl"]], jsii.get(self, "sslInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneIdInput")
    def zone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="customMetadata")
    def custom_metadata(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "customMetadata"))

    @custom_metadata.setter
    def custom_metadata(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de637288db3c09f8cabeb56459d8d32edce0ca73cf35b168a739e59a09c8f11b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customMetadata", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="customOriginServer")
    def custom_origin_server(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customOriginServer"))

    @custom_origin_server.setter
    def custom_origin_server(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02076b152f8b46094262d0027dfc930a81477e4f6a717130f57de2ac269c0a60)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customOriginServer", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="customOriginSni")
    def custom_origin_sni(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customOriginSni"))

    @custom_origin_sni.setter
    def custom_origin_sni(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ec17de835603301487ab088d7c0b1e989e68675fc038ca2dc41f555e5256987)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customOriginSni", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hostname")
    def hostname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostname"))

    @hostname.setter
    def hostname(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__363b224feee645a6e9d647a4835702b51ad748047425bfa39d8ec804c062a95b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostname", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7f5ec58ac1d08057ceabff7f21b9fe0ead80236bfe3a796dba741f79d7f3777)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.customHostname.CustomHostnameConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "hostname": "hostname",
        "ssl": "ssl",
        "zone_id": "zoneId",
        "custom_metadata": "customMetadata",
        "custom_origin_server": "customOriginServer",
        "custom_origin_sni": "customOriginSni",
    },
)
class CustomHostnameConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        hostname: builtins.str,
        ssl: typing.Union["CustomHostnameSsl", typing.Dict[builtins.str, typing.Any]],
        zone_id: builtins.str,
        custom_metadata: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        custom_origin_server: typing.Optional[builtins.str] = None,
        custom_origin_sni: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param hostname: The custom hostname that will point to your hostname via CNAME. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#hostname CustomHostname#hostname}
        :param ssl: SSL properties used when creating the custom hostname. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#ssl CustomHostname#ssl}
        :param zone_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#zone_id CustomHostname#zone_id}
        :param custom_metadata: Unique key/value metadata for this hostname. These are per-hostname (customer) settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#custom_metadata CustomHostname#custom_metadata}
        :param custom_origin_server: a valid hostname that’s been added to your DNS zone as an A, AAAA, or CNAME record. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#custom_origin_server CustomHostname#custom_origin_server}
        :param custom_origin_sni: A hostname that will be sent to your custom origin server as SNI for TLS handshake. This can be a valid subdomain of the zone or custom origin server name or the string ':request_host_header:' which will cause the host header in the request to be used as SNI. Not configurable with default/fallback origin server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#custom_origin_sni CustomHostname#custom_origin_sni}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(ssl, dict):
            ssl = CustomHostnameSsl(**ssl)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92de60c9769d9bcda063e9f820f1972e69185c791f003143b549bdc4352855b2)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument hostname", value=hostname, expected_type=type_hints["hostname"])
            check_type(argname="argument ssl", value=ssl, expected_type=type_hints["ssl"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
            check_type(argname="argument custom_metadata", value=custom_metadata, expected_type=type_hints["custom_metadata"])
            check_type(argname="argument custom_origin_server", value=custom_origin_server, expected_type=type_hints["custom_origin_server"])
            check_type(argname="argument custom_origin_sni", value=custom_origin_sni, expected_type=type_hints["custom_origin_sni"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "hostname": hostname,
            "ssl": ssl,
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
        if custom_metadata is not None:
            self._values["custom_metadata"] = custom_metadata
        if custom_origin_server is not None:
            self._values["custom_origin_server"] = custom_origin_server
        if custom_origin_sni is not None:
            self._values["custom_origin_sni"] = custom_origin_sni

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
    def hostname(self) -> builtins.str:
        '''The custom hostname that will point to your hostname via CNAME.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#hostname CustomHostname#hostname}
        '''
        result = self._values.get("hostname")
        assert result is not None, "Required property 'hostname' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ssl(self) -> "CustomHostnameSsl":
        '''SSL properties used when creating the custom hostname.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#ssl CustomHostname#ssl}
        '''
        result = self._values.get("ssl")
        assert result is not None, "Required property 'ssl' is missing"
        return typing.cast("CustomHostnameSsl", result)

    @builtins.property
    def zone_id(self) -> builtins.str:
        '''Identifier.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#zone_id CustomHostname#zone_id}
        '''
        result = self._values.get("zone_id")
        assert result is not None, "Required property 'zone_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def custom_metadata(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Unique key/value metadata for this hostname. These are per-hostname (customer) settings.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#custom_metadata CustomHostname#custom_metadata}
        '''
        result = self._values.get("custom_metadata")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def custom_origin_server(self) -> typing.Optional[builtins.str]:
        '''a valid hostname that’s been added to your DNS zone as an A, AAAA, or CNAME record.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#custom_origin_server CustomHostname#custom_origin_server}
        '''
        result = self._values.get("custom_origin_server")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_origin_sni(self) -> typing.Optional[builtins.str]:
        '''A hostname that will be sent to your custom origin server as SNI for TLS handshake.

        This can be a valid subdomain of the zone or custom origin server name or the string ':request_host_header:' which will cause the host header in the request to be used as SNI. Not configurable with default/fallback origin server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#custom_origin_sni CustomHostname#custom_origin_sni}
        '''
        result = self._values.get("custom_origin_sni")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomHostnameConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.customHostname.CustomHostnameOwnershipVerification",
    jsii_struct_bases=[],
    name_mapping={},
)
class CustomHostnameOwnershipVerification:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomHostnameOwnershipVerification(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.customHostname.CustomHostnameOwnershipVerificationHttp",
    jsii_struct_bases=[],
    name_mapping={},
)
class CustomHostnameOwnershipVerificationHttp:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomHostnameOwnershipVerificationHttp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CustomHostnameOwnershipVerificationHttpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.customHostname.CustomHostnameOwnershipVerificationHttpOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5f2d37e4d1e24a7b55b3480f3216f9515a608f00028f96d44c726b36ba06193a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="httpBody")
    def http_body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "httpBody"))

    @builtins.property
    @jsii.member(jsii_name="httpUrl")
    def http_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "httpUrl"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CustomHostnameOwnershipVerificationHttp]:
        return typing.cast(typing.Optional[CustomHostnameOwnershipVerificationHttp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CustomHostnameOwnershipVerificationHttp],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1398ecb7061e026eb11d56fdc901305e2852b7a88728f4d08dfebba235b1aaa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CustomHostnameOwnershipVerificationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.customHostname.CustomHostnameOwnershipVerificationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__209346042af89a0bc875a843de2ce1367fe99857ac5b83e6083e53323238187a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CustomHostnameOwnershipVerification]:
        return typing.cast(typing.Optional[CustomHostnameOwnershipVerification], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CustomHostnameOwnershipVerification],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93a0df507c9de2e5e4ebb6106a895825380deb94af2cba395f682b797f2d4e21)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.customHostname.CustomHostnameSsl",
    jsii_struct_bases=[],
    name_mapping={
        "bundle_method": "bundleMethod",
        "certificate_authority": "certificateAuthority",
        "cloudflare_branding": "cloudflareBranding",
        "custom_cert_bundle": "customCertBundle",
        "custom_certificate": "customCertificate",
        "custom_key": "customKey",
        "method": "method",
        "settings": "settings",
        "type": "type",
        "wildcard": "wildcard",
    },
)
class CustomHostnameSsl:
    def __init__(
        self,
        *,
        bundle_method: typing.Optional[builtins.str] = None,
        certificate_authority: typing.Optional[builtins.str] = None,
        cloudflare_branding: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        custom_cert_bundle: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CustomHostnameSslCustomCertBundle", typing.Dict[builtins.str, typing.Any]]]]] = None,
        custom_certificate: typing.Optional[builtins.str] = None,
        custom_key: typing.Optional[builtins.str] = None,
        method: typing.Optional[builtins.str] = None,
        settings: typing.Optional[typing.Union["CustomHostnameSslSettings", typing.Dict[builtins.str, typing.Any]]] = None,
        type: typing.Optional[builtins.str] = None,
        wildcard: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param bundle_method: A ubiquitous bundle has the highest probability of being verified everywhere, even by clients using outdated or unusual trust stores. An optimal bundle uses the shortest chain and newest intermediates. And the force bundle verifies the chain, but does not otherwise modify it. Available values: "ubiquitous", "optimal", "force". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#bundle_method CustomHostname#bundle_method}
        :param certificate_authority: The Certificate Authority that will issue the certificate Available values: "digicert", "google", "lets_encrypt", "ssl_com". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#certificate_authority CustomHostname#certificate_authority}
        :param cloudflare_branding: Whether or not to add Cloudflare Branding for the order. This will add a subdomain of sni.cloudflaressl.com as the Common Name if set to true Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#cloudflare_branding CustomHostname#cloudflare_branding}
        :param custom_cert_bundle: Array of custom certificate and key pairs (1 or 2 pairs allowed). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#custom_cert_bundle CustomHostname#custom_cert_bundle}
        :param custom_certificate: If a custom uploaded certificate is used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#custom_certificate CustomHostname#custom_certificate}
        :param custom_key: The key for a custom uploaded certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#custom_key CustomHostname#custom_key}
        :param method: Domain control validation (DCV) method used for this hostname. Available values: "http", "txt", "email". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#method CustomHostname#method}
        :param settings: SSL specific settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#settings CustomHostname#settings}
        :param type: Level of validation to be used for this hostname. Domain validation (dv) must be used. Available values: "dv". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#type CustomHostname#type}
        :param wildcard: Indicates whether the certificate covers a wildcard. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#wildcard CustomHostname#wildcard}
        '''
        if isinstance(settings, dict):
            settings = CustomHostnameSslSettings(**settings)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc12e44f1709e7306d76aaf1846782a7280b06d4803bc4a6014452681f512800)
            check_type(argname="argument bundle_method", value=bundle_method, expected_type=type_hints["bundle_method"])
            check_type(argname="argument certificate_authority", value=certificate_authority, expected_type=type_hints["certificate_authority"])
            check_type(argname="argument cloudflare_branding", value=cloudflare_branding, expected_type=type_hints["cloudflare_branding"])
            check_type(argname="argument custom_cert_bundle", value=custom_cert_bundle, expected_type=type_hints["custom_cert_bundle"])
            check_type(argname="argument custom_certificate", value=custom_certificate, expected_type=type_hints["custom_certificate"])
            check_type(argname="argument custom_key", value=custom_key, expected_type=type_hints["custom_key"])
            check_type(argname="argument method", value=method, expected_type=type_hints["method"])
            check_type(argname="argument settings", value=settings, expected_type=type_hints["settings"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument wildcard", value=wildcard, expected_type=type_hints["wildcard"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bundle_method is not None:
            self._values["bundle_method"] = bundle_method
        if certificate_authority is not None:
            self._values["certificate_authority"] = certificate_authority
        if cloudflare_branding is not None:
            self._values["cloudflare_branding"] = cloudflare_branding
        if custom_cert_bundle is not None:
            self._values["custom_cert_bundle"] = custom_cert_bundle
        if custom_certificate is not None:
            self._values["custom_certificate"] = custom_certificate
        if custom_key is not None:
            self._values["custom_key"] = custom_key
        if method is not None:
            self._values["method"] = method
        if settings is not None:
            self._values["settings"] = settings
        if type is not None:
            self._values["type"] = type
        if wildcard is not None:
            self._values["wildcard"] = wildcard

    @builtins.property
    def bundle_method(self) -> typing.Optional[builtins.str]:
        '''A ubiquitous bundle has the highest probability of being verified everywhere, even by clients using outdated or unusual trust stores.

        An optimal bundle uses the shortest chain and newest intermediates. And the force bundle verifies the chain, but does not otherwise modify it.
        Available values: "ubiquitous", "optimal", "force".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#bundle_method CustomHostname#bundle_method}
        '''
        result = self._values.get("bundle_method")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_authority(self) -> typing.Optional[builtins.str]:
        '''The Certificate Authority that will issue the certificate Available values: "digicert", "google", "lets_encrypt", "ssl_com".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#certificate_authority CustomHostname#certificate_authority}
        '''
        result = self._values.get("certificate_authority")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cloudflare_branding(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether or not to add Cloudflare Branding for the order.

        This will add a subdomain of sni.cloudflaressl.com as the Common Name if set to true

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#cloudflare_branding CustomHostname#cloudflare_branding}
        '''
        result = self._values.get("cloudflare_branding")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def custom_cert_bundle(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CustomHostnameSslCustomCertBundle"]]]:
        '''Array of custom certificate and key pairs (1 or 2 pairs allowed).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#custom_cert_bundle CustomHostname#custom_cert_bundle}
        '''
        result = self._values.get("custom_cert_bundle")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CustomHostnameSslCustomCertBundle"]]], result)

    @builtins.property
    def custom_certificate(self) -> typing.Optional[builtins.str]:
        '''If a custom uploaded certificate is used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#custom_certificate CustomHostname#custom_certificate}
        '''
        result = self._values.get("custom_certificate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_key(self) -> typing.Optional[builtins.str]:
        '''The key for a custom uploaded certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#custom_key CustomHostname#custom_key}
        '''
        result = self._values.get("custom_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def method(self) -> typing.Optional[builtins.str]:
        '''Domain control validation (DCV) method used for this hostname. Available values: "http", "txt", "email".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#method CustomHostname#method}
        '''
        result = self._values.get("method")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def settings(self) -> typing.Optional["CustomHostnameSslSettings"]:
        '''SSL specific settings.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#settings CustomHostname#settings}
        '''
        result = self._values.get("settings")
        return typing.cast(typing.Optional["CustomHostnameSslSettings"], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Level of validation to be used for this hostname. Domain validation (dv) must be used. Available values: "dv".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#type CustomHostname#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def wildcard(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates whether the certificate covers a wildcard.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#wildcard CustomHostname#wildcard}
        '''
        result = self._values.get("wildcard")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomHostnameSsl(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.customHostname.CustomHostnameSslCustomCertBundle",
    jsii_struct_bases=[],
    name_mapping={
        "custom_certificate": "customCertificate",
        "custom_key": "customKey",
    },
)
class CustomHostnameSslCustomCertBundle:
    def __init__(
        self,
        *,
        custom_certificate: builtins.str,
        custom_key: builtins.str,
    ) -> None:
        '''
        :param custom_certificate: If a custom uploaded certificate is used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#custom_certificate CustomHostname#custom_certificate}
        :param custom_key: The key for a custom uploaded certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#custom_key CustomHostname#custom_key}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1820d8b2b1c8f562189872e6324410c220313c41e19d1722f1eda82f65038c2)
            check_type(argname="argument custom_certificate", value=custom_certificate, expected_type=type_hints["custom_certificate"])
            check_type(argname="argument custom_key", value=custom_key, expected_type=type_hints["custom_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "custom_certificate": custom_certificate,
            "custom_key": custom_key,
        }

    @builtins.property
    def custom_certificate(self) -> builtins.str:
        '''If a custom uploaded certificate is used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#custom_certificate CustomHostname#custom_certificate}
        '''
        result = self._values.get("custom_certificate")
        assert result is not None, "Required property 'custom_certificate' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def custom_key(self) -> builtins.str:
        '''The key for a custom uploaded certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#custom_key CustomHostname#custom_key}
        '''
        result = self._values.get("custom_key")
        assert result is not None, "Required property 'custom_key' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomHostnameSslCustomCertBundle(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CustomHostnameSslCustomCertBundleList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.customHostname.CustomHostnameSslCustomCertBundleList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b623893c942f2722fff1f6c3d0a1092167b36133e69b943cc543c29da15baf49)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "CustomHostnameSslCustomCertBundleOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__049a8e9a18c97c8cc5beeca60594331c23c8d022bdebc9ad5f3e01f1cf111e74)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CustomHostnameSslCustomCertBundleOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f36e2053aee93292f4dcd702e6894ceedd3c768cb9e81c66a601518ba80e4a7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8166b05ea68b06ad15d31a1ae91205a6749dba104082c521683fc469a87f601b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__57fb0f66a6bf9be854ba07c1e77d95f978d84378fe8c9d750809e0ecda6dda78)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CustomHostnameSslCustomCertBundle]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CustomHostnameSslCustomCertBundle]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CustomHostnameSslCustomCertBundle]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce6ff0cc92e2941cd67f71018f77c6b3c60e831e74216672df55004e61b085f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CustomHostnameSslCustomCertBundleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.customHostname.CustomHostnameSslCustomCertBundleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__233d721ac502e60c187d93d18b51fb8d22b5bb131fd08467be17c98c891022b3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="customCertificateInput")
    def custom_certificate_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customCertificateInput"))

    @builtins.property
    @jsii.member(jsii_name="customKeyInput")
    def custom_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="customCertificate")
    def custom_certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customCertificate"))

    @custom_certificate.setter
    def custom_certificate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a3c2f572ad0e6d145f0740c759ae6492e5e8ef37f3976f1fda93a36f5a92b98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customCertificate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="customKey")
    def custom_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customKey"))

    @custom_key.setter
    def custom_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7785ef891b5ef15c088cc8e730cc38efcbf3f4257ff5058c12a334e92ea35948)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CustomHostnameSslCustomCertBundle]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CustomHostnameSslCustomCertBundle]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CustomHostnameSslCustomCertBundle]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d87a829ea657f1c30e54cd6091893b26ef4003a472950feb525149edaf2fe1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CustomHostnameSslOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.customHostname.CustomHostnameSslOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__663b21926d1a54503d78b2d4f735c9aca12fdb5ae279b330f54b2c392771d9ff)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putCustomCertBundle")
    def put_custom_cert_bundle(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CustomHostnameSslCustomCertBundle, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f35996564a0562b00d3413f4feccd5d619998f1d51d991c567cd9466e47883e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCustomCertBundle", [value]))

    @jsii.member(jsii_name="putSettings")
    def put_settings(
        self,
        *,
        ciphers: typing.Optional[typing.Sequence[builtins.str]] = None,
        early_hints: typing.Optional[builtins.str] = None,
        http2: typing.Optional[builtins.str] = None,
        min_tls_version: typing.Optional[builtins.str] = None,
        tls13: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param ciphers: An allowlist of ciphers for TLS termination. These ciphers must be in the BoringSSL format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#ciphers CustomHostname#ciphers}
        :param early_hints: Whether or not Early Hints is enabled. Available values: "on", "off". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#early_hints CustomHostname#early_hints}
        :param http2: Whether or not HTTP2 is enabled. Available values: "on", "off". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#http2 CustomHostname#http2}
        :param min_tls_version: The minimum TLS version supported. Available values: "1.0", "1.1", "1.2", "1.3". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#min_tls_version CustomHostname#min_tls_version}
        :param tls13: Whether or not TLS 1.3 is enabled. Available values: "on", "off". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#tls_1_3 CustomHostname#tls_1_3}
        '''
        value = CustomHostnameSslSettings(
            ciphers=ciphers,
            early_hints=early_hints,
            http2=http2,
            min_tls_version=min_tls_version,
            tls13=tls13,
        )

        return typing.cast(None, jsii.invoke(self, "putSettings", [value]))

    @jsii.member(jsii_name="resetBundleMethod")
    def reset_bundle_method(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBundleMethod", []))

    @jsii.member(jsii_name="resetCertificateAuthority")
    def reset_certificate_authority(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateAuthority", []))

    @jsii.member(jsii_name="resetCloudflareBranding")
    def reset_cloudflare_branding(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudflareBranding", []))

    @jsii.member(jsii_name="resetCustomCertBundle")
    def reset_custom_cert_bundle(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomCertBundle", []))

    @jsii.member(jsii_name="resetCustomCertificate")
    def reset_custom_certificate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomCertificate", []))

    @jsii.member(jsii_name="resetCustomKey")
    def reset_custom_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomKey", []))

    @jsii.member(jsii_name="resetMethod")
    def reset_method(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMethod", []))

    @jsii.member(jsii_name="resetSettings")
    def reset_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSettings", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @jsii.member(jsii_name="resetWildcard")
    def reset_wildcard(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWildcard", []))

    @builtins.property
    @jsii.member(jsii_name="customCertBundle")
    def custom_cert_bundle(self) -> CustomHostnameSslCustomCertBundleList:
        return typing.cast(CustomHostnameSslCustomCertBundleList, jsii.get(self, "customCertBundle"))

    @builtins.property
    @jsii.member(jsii_name="settings")
    def settings(self) -> "CustomHostnameSslSettingsOutputReference":
        return typing.cast("CustomHostnameSslSettingsOutputReference", jsii.get(self, "settings"))

    @builtins.property
    @jsii.member(jsii_name="bundleMethodInput")
    def bundle_method_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bundleMethodInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateAuthorityInput")
    def certificate_authority_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateAuthorityInput"))

    @builtins.property
    @jsii.member(jsii_name="cloudflareBrandingInput")
    def cloudflare_branding_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "cloudflareBrandingInput"))

    @builtins.property
    @jsii.member(jsii_name="customCertBundleInput")
    def custom_cert_bundle_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CustomHostnameSslCustomCertBundle]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CustomHostnameSslCustomCertBundle]]], jsii.get(self, "customCertBundleInput"))

    @builtins.property
    @jsii.member(jsii_name="customCertificateInput")
    def custom_certificate_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customCertificateInput"))

    @builtins.property
    @jsii.member(jsii_name="customKeyInput")
    def custom_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="methodInput")
    def method_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "methodInput"))

    @builtins.property
    @jsii.member(jsii_name="settingsInput")
    def settings_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "CustomHostnameSslSettings"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "CustomHostnameSslSettings"]], jsii.get(self, "settingsInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="wildcardInput")
    def wildcard_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "wildcardInput"))

    @builtins.property
    @jsii.member(jsii_name="bundleMethod")
    def bundle_method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bundleMethod"))

    @bundle_method.setter
    def bundle_method(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c97ba19a6ac11f627b545d07a0327b7d9cf1a8c0091a83a68daf3481c4fdecb8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bundleMethod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="certificateAuthority")
    def certificate_authority(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateAuthority"))

    @certificate_authority.setter
    def certificate_authority(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9779f8b0329e88dbfb19f33d0d45829d723e93f3f5ade778d27ac6b08e81a1e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateAuthority", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cloudflareBranding")
    def cloudflare_branding(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "cloudflareBranding"))

    @cloudflare_branding.setter
    def cloudflare_branding(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f75bf85de4cc5a3534a57491500609acc25295be5be2a05ff53dea7fbfcdb58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cloudflareBranding", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="customCertificate")
    def custom_certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customCertificate"))

    @custom_certificate.setter
    def custom_certificate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab006b228066d0af31787afa383737ad92ddaf689224e83b46712c043778f675)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customCertificate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="customKey")
    def custom_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customKey"))

    @custom_key.setter
    def custom_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1a17f48c8383f7951c15a68c937b4eeb9aaf84fa5bfd982844b43fccdaebad2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="method")
    def method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "method"))

    @method.setter
    def method(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9e2de89b77607e5aff34672908dcb182073e6fe3c4fa61ade9555ecfb70f544)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "method", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2c0d2d525d3d1cc7fa385eb5eb440e702571958440dd7ee017cb0e947b7ace5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wildcard")
    def wildcard(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "wildcard"))

    @wildcard.setter
    def wildcard(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d358764a9cd67efbaf1964f84aae15a5a4a8672b5e69832e8fcbc23a96def96)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wildcard", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CustomHostnameSsl]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CustomHostnameSsl]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CustomHostnameSsl]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb007a5472eef671f96f7a063117b5b43385031e8f8e37fb07c59c7d4ed78003)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.customHostname.CustomHostnameSslSettings",
    jsii_struct_bases=[],
    name_mapping={
        "ciphers": "ciphers",
        "early_hints": "earlyHints",
        "http2": "http2",
        "min_tls_version": "minTlsVersion",
        "tls13": "tls13",
    },
)
class CustomHostnameSslSettings:
    def __init__(
        self,
        *,
        ciphers: typing.Optional[typing.Sequence[builtins.str]] = None,
        early_hints: typing.Optional[builtins.str] = None,
        http2: typing.Optional[builtins.str] = None,
        min_tls_version: typing.Optional[builtins.str] = None,
        tls13: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param ciphers: An allowlist of ciphers for TLS termination. These ciphers must be in the BoringSSL format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#ciphers CustomHostname#ciphers}
        :param early_hints: Whether or not Early Hints is enabled. Available values: "on", "off". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#early_hints CustomHostname#early_hints}
        :param http2: Whether or not HTTP2 is enabled. Available values: "on", "off". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#http2 CustomHostname#http2}
        :param min_tls_version: The minimum TLS version supported. Available values: "1.0", "1.1", "1.2", "1.3". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#min_tls_version CustomHostname#min_tls_version}
        :param tls13: Whether or not TLS 1.3 is enabled. Available values: "on", "off". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#tls_1_3 CustomHostname#tls_1_3}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__593a8a11482b32c6ed97b27a2b618398ef4cb94d84bb4979aadeda397ee3e340)
            check_type(argname="argument ciphers", value=ciphers, expected_type=type_hints["ciphers"])
            check_type(argname="argument early_hints", value=early_hints, expected_type=type_hints["early_hints"])
            check_type(argname="argument http2", value=http2, expected_type=type_hints["http2"])
            check_type(argname="argument min_tls_version", value=min_tls_version, expected_type=type_hints["min_tls_version"])
            check_type(argname="argument tls13", value=tls13, expected_type=type_hints["tls13"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if ciphers is not None:
            self._values["ciphers"] = ciphers
        if early_hints is not None:
            self._values["early_hints"] = early_hints
        if http2 is not None:
            self._values["http2"] = http2
        if min_tls_version is not None:
            self._values["min_tls_version"] = min_tls_version
        if tls13 is not None:
            self._values["tls13"] = tls13

    @builtins.property
    def ciphers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''An allowlist of ciphers for TLS termination. These ciphers must be in the BoringSSL format.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#ciphers CustomHostname#ciphers}
        '''
        result = self._values.get("ciphers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def early_hints(self) -> typing.Optional[builtins.str]:
        '''Whether or not Early Hints is enabled. Available values: "on", "off".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#early_hints CustomHostname#early_hints}
        '''
        result = self._values.get("early_hints")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def http2(self) -> typing.Optional[builtins.str]:
        '''Whether or not HTTP2 is enabled. Available values: "on", "off".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#http2 CustomHostname#http2}
        '''
        result = self._values.get("http2")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_tls_version(self) -> typing.Optional[builtins.str]:
        '''The minimum TLS version supported. Available values: "1.0", "1.1", "1.2", "1.3".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#min_tls_version CustomHostname#min_tls_version}
        '''
        result = self._values.get("min_tls_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tls13(self) -> typing.Optional[builtins.str]:
        '''Whether or not TLS 1.3 is enabled. Available values: "on", "off".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/custom_hostname#tls_1_3 CustomHostname#tls_1_3}
        '''
        result = self._values.get("tls13")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomHostnameSslSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CustomHostnameSslSettingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.customHostname.CustomHostnameSslSettingsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5b01769ef59599079079f042d71ac2bd8391552e42f94a42dce9e11b0be6323a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCiphers")
    def reset_ciphers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCiphers", []))

    @jsii.member(jsii_name="resetEarlyHints")
    def reset_early_hints(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEarlyHints", []))

    @jsii.member(jsii_name="resetHttp2")
    def reset_http2(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttp2", []))

    @jsii.member(jsii_name="resetMinTlsVersion")
    def reset_min_tls_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinTlsVersion", []))

    @jsii.member(jsii_name="resetTls13")
    def reset_tls13(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTls13", []))

    @builtins.property
    @jsii.member(jsii_name="ciphersInput")
    def ciphers_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "ciphersInput"))

    @builtins.property
    @jsii.member(jsii_name="earlyHintsInput")
    def early_hints_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "earlyHintsInput"))

    @builtins.property
    @jsii.member(jsii_name="http2Input")
    def http2_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "http2Input"))

    @builtins.property
    @jsii.member(jsii_name="minTlsVersionInput")
    def min_tls_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "minTlsVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="tls13Input")
    def tls13_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tls13Input"))

    @builtins.property
    @jsii.member(jsii_name="ciphers")
    def ciphers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ciphers"))

    @ciphers.setter
    def ciphers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da6f1f055ef36bd33ce870164d7f3cf0988af48323fb195a99b6f16719b9f66d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ciphers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="earlyHints")
    def early_hints(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "earlyHints"))

    @early_hints.setter
    def early_hints(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3786b21f012c5d7e829d1969b950eabead5123723dceb873a4cd316b4d491106)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "earlyHints", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="http2")
    def http2(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "http2"))

    @http2.setter
    def http2(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cec400a996dd35fa39c4c8a51e4caaa9601875aa249b71efa2a83c5ecdbee397)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "http2", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minTlsVersion")
    def min_tls_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minTlsVersion"))

    @min_tls_version.setter
    def min_tls_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8bc1c7e0865fd96dc0bea1da610986cd451220ddede47ae11e343ec47440cb0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minTlsVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tls13")
    def tls13(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tls13"))

    @tls13.setter
    def tls13(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b858a16170a5e0a792ae9b6ccaf06c6d27c0b35c151b4a507a8f458586a89f66)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tls13", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CustomHostnameSslSettings]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CustomHostnameSslSettings]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CustomHostnameSslSettings]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a52417683c4e3fd49606e70fc485ac37a8ea2b7da535a37a13086c1080a6727)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "CustomHostname",
    "CustomHostnameConfig",
    "CustomHostnameOwnershipVerification",
    "CustomHostnameOwnershipVerificationHttp",
    "CustomHostnameOwnershipVerificationHttpOutputReference",
    "CustomHostnameOwnershipVerificationOutputReference",
    "CustomHostnameSsl",
    "CustomHostnameSslCustomCertBundle",
    "CustomHostnameSslCustomCertBundleList",
    "CustomHostnameSslCustomCertBundleOutputReference",
    "CustomHostnameSslOutputReference",
    "CustomHostnameSslSettings",
    "CustomHostnameSslSettingsOutputReference",
]

publication.publish()

def _typecheckingstub__2999243784abde236613791702b528a1f4896b54dcf17adba234a389d1841b3d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    hostname: builtins.str,
    ssl: typing.Union[CustomHostnameSsl, typing.Dict[builtins.str, typing.Any]],
    zone_id: builtins.str,
    custom_metadata: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    custom_origin_server: typing.Optional[builtins.str] = None,
    custom_origin_sni: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__21de9577f0d51f1369fb2d48f23491d36f2e50c4b122cff4a36b30a5d741793e(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de637288db3c09f8cabeb56459d8d32edce0ca73cf35b168a739e59a09c8f11b(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02076b152f8b46094262d0027dfc930a81477e4f6a717130f57de2ac269c0a60(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ec17de835603301487ab088d7c0b1e989e68675fc038ca2dc41f555e5256987(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__363b224feee645a6e9d647a4835702b51ad748047425bfa39d8ec804c062a95b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7f5ec58ac1d08057ceabff7f21b9fe0ead80236bfe3a796dba741f79d7f3777(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92de60c9769d9bcda063e9f820f1972e69185c791f003143b549bdc4352855b2(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    hostname: builtins.str,
    ssl: typing.Union[CustomHostnameSsl, typing.Dict[builtins.str, typing.Any]],
    zone_id: builtins.str,
    custom_metadata: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    custom_origin_server: typing.Optional[builtins.str] = None,
    custom_origin_sni: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f2d37e4d1e24a7b55b3480f3216f9515a608f00028f96d44c726b36ba06193a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1398ecb7061e026eb11d56fdc901305e2852b7a88728f4d08dfebba235b1aaa(
    value: typing.Optional[CustomHostnameOwnershipVerificationHttp],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__209346042af89a0bc875a843de2ce1367fe99857ac5b83e6083e53323238187a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93a0df507c9de2e5e4ebb6106a895825380deb94af2cba395f682b797f2d4e21(
    value: typing.Optional[CustomHostnameOwnershipVerification],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc12e44f1709e7306d76aaf1846782a7280b06d4803bc4a6014452681f512800(
    *,
    bundle_method: typing.Optional[builtins.str] = None,
    certificate_authority: typing.Optional[builtins.str] = None,
    cloudflare_branding: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    custom_cert_bundle: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CustomHostnameSslCustomCertBundle, typing.Dict[builtins.str, typing.Any]]]]] = None,
    custom_certificate: typing.Optional[builtins.str] = None,
    custom_key: typing.Optional[builtins.str] = None,
    method: typing.Optional[builtins.str] = None,
    settings: typing.Optional[typing.Union[CustomHostnameSslSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    type: typing.Optional[builtins.str] = None,
    wildcard: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1820d8b2b1c8f562189872e6324410c220313c41e19d1722f1eda82f65038c2(
    *,
    custom_certificate: builtins.str,
    custom_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b623893c942f2722fff1f6c3d0a1092167b36133e69b943cc543c29da15baf49(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__049a8e9a18c97c8cc5beeca60594331c23c8d022bdebc9ad5f3e01f1cf111e74(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f36e2053aee93292f4dcd702e6894ceedd3c768cb9e81c66a601518ba80e4a7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8166b05ea68b06ad15d31a1ae91205a6749dba104082c521683fc469a87f601b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57fb0f66a6bf9be854ba07c1e77d95f978d84378fe8c9d750809e0ecda6dda78(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce6ff0cc92e2941cd67f71018f77c6b3c60e831e74216672df55004e61b085f6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CustomHostnameSslCustomCertBundle]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__233d721ac502e60c187d93d18b51fb8d22b5bb131fd08467be17c98c891022b3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a3c2f572ad0e6d145f0740c759ae6492e5e8ef37f3976f1fda93a36f5a92b98(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7785ef891b5ef15c088cc8e730cc38efcbf3f4257ff5058c12a334e92ea35948(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d87a829ea657f1c30e54cd6091893b26ef4003a472950feb525149edaf2fe1c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CustomHostnameSslCustomCertBundle]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__663b21926d1a54503d78b2d4f735c9aca12fdb5ae279b330f54b2c392771d9ff(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f35996564a0562b00d3413f4feccd5d619998f1d51d991c567cd9466e47883e(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CustomHostnameSslCustomCertBundle, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c97ba19a6ac11f627b545d07a0327b7d9cf1a8c0091a83a68daf3481c4fdecb8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9779f8b0329e88dbfb19f33d0d45829d723e93f3f5ade778d27ac6b08e81a1e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f75bf85de4cc5a3534a57491500609acc25295be5be2a05ff53dea7fbfcdb58(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab006b228066d0af31787afa383737ad92ddaf689224e83b46712c043778f675(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1a17f48c8383f7951c15a68c937b4eeb9aaf84fa5bfd982844b43fccdaebad2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9e2de89b77607e5aff34672908dcb182073e6fe3c4fa61ade9555ecfb70f544(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2c0d2d525d3d1cc7fa385eb5eb440e702571958440dd7ee017cb0e947b7ace5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d358764a9cd67efbaf1964f84aae15a5a4a8672b5e69832e8fcbc23a96def96(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb007a5472eef671f96f7a063117b5b43385031e8f8e37fb07c59c7d4ed78003(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CustomHostnameSsl]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__593a8a11482b32c6ed97b27a2b618398ef4cb94d84bb4979aadeda397ee3e340(
    *,
    ciphers: typing.Optional[typing.Sequence[builtins.str]] = None,
    early_hints: typing.Optional[builtins.str] = None,
    http2: typing.Optional[builtins.str] = None,
    min_tls_version: typing.Optional[builtins.str] = None,
    tls13: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b01769ef59599079079f042d71ac2bd8391552e42f94a42dce9e11b0be6323a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da6f1f055ef36bd33ce870164d7f3cf0988af48323fb195a99b6f16719b9f66d(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3786b21f012c5d7e829d1969b950eabead5123723dceb873a4cd316b4d491106(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cec400a996dd35fa39c4c8a51e4caaa9601875aa249b71efa2a83c5ecdbee397(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8bc1c7e0865fd96dc0bea1da610986cd451220ddede47ae11e343ec47440cb0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b858a16170a5e0a792ae9b6ccaf06c6d27c0b35c151b4a507a8f458586a89f66(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a52417683c4e3fd49606e70fc485ac37a8ea2b7da535a37a13086c1080a6727(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CustomHostnameSslSettings]],
) -> None:
    """Type checking stubs"""
    pass
