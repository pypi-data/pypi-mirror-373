r'''
# `cloudflare_zone_cache_variants`

Refer to the Terraform Registry for docs: [`cloudflare_zone_cache_variants`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants).
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


class ZoneCacheVariants(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zoneCacheVariants.ZoneCacheVariants",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants cloudflare_zone_cache_variants}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        value: typing.Union["ZoneCacheVariantsValue", typing.Dict[builtins.str, typing.Any]],
        zone_id: builtins.str,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants cloudflare_zone_cache_variants} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param value: Value of the zone setting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#value ZoneCacheVariants#value}
        :param zone_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#zone_id ZoneCacheVariants#zone_id}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6182c0f5085287c30b04cfcc97155c89b372750ee22d9009b7669a3e95c3e960)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = ZoneCacheVariantsConfig(
            value=value,
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
        '''Generates CDKTF code for importing a ZoneCacheVariants resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ZoneCacheVariants to import.
        :param import_from_id: The id of the existing ZoneCacheVariants that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ZoneCacheVariants to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fa85c49221adb6b53855914f514e397ce395a3772779ebe1c3276f395c5a43c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putValue")
    def put_value(
        self,
        *,
        avif: typing.Optional[typing.Sequence[builtins.str]] = None,
        bmp: typing.Optional[typing.Sequence[builtins.str]] = None,
        gif: typing.Optional[typing.Sequence[builtins.str]] = None,
        jp2: typing.Optional[typing.Sequence[builtins.str]] = None,
        jpeg: typing.Optional[typing.Sequence[builtins.str]] = None,
        jpg: typing.Optional[typing.Sequence[builtins.str]] = None,
        jpg2: typing.Optional[typing.Sequence[builtins.str]] = None,
        png: typing.Optional[typing.Sequence[builtins.str]] = None,
        tif: typing.Optional[typing.Sequence[builtins.str]] = None,
        tiff: typing.Optional[typing.Sequence[builtins.str]] = None,
        webp: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param avif: List of strings with the MIME types of all the variants that should be served for avif. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#avif ZoneCacheVariants#avif}
        :param bmp: List of strings with the MIME types of all the variants that should be served for bmp. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#bmp ZoneCacheVariants#bmp}
        :param gif: List of strings with the MIME types of all the variants that should be served for gif. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#gif ZoneCacheVariants#gif}
        :param jp2: List of strings with the MIME types of all the variants that should be served for jp2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#jp2 ZoneCacheVariants#jp2}
        :param jpeg: List of strings with the MIME types of all the variants that should be served for jpeg. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#jpeg ZoneCacheVariants#jpeg}
        :param jpg: List of strings with the MIME types of all the variants that should be served for jpg. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#jpg ZoneCacheVariants#jpg}
        :param jpg2: List of strings with the MIME types of all the variants that should be served for jpg2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#jpg2 ZoneCacheVariants#jpg2}
        :param png: List of strings with the MIME types of all the variants that should be served for png. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#png ZoneCacheVariants#png}
        :param tif: List of strings with the MIME types of all the variants that should be served for tif. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#tif ZoneCacheVariants#tif}
        :param tiff: List of strings with the MIME types of all the variants that should be served for tiff. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#tiff ZoneCacheVariants#tiff}
        :param webp: List of strings with the MIME types of all the variants that should be served for webp. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#webp ZoneCacheVariants#webp}
        '''
        value = ZoneCacheVariantsValue(
            avif=avif,
            bmp=bmp,
            gif=gif,
            jp2=jp2,
            jpeg=jpeg,
            jpg=jpg,
            jpg2=jpg2,
            png=png,
            tif=tif,
            tiff=tiff,
            webp=webp,
        )

        return typing.cast(None, jsii.invoke(self, "putValue", [value]))

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
    @jsii.member(jsii_name="editable")
    def editable(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "editable"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="modifiedOn")
    def modified_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modifiedOn"))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> "ZoneCacheVariantsValueOutputReference":
        return typing.cast("ZoneCacheVariantsValueOutputReference", jsii.get(self, "value"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZoneCacheVariantsValue"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ZoneCacheVariantsValue"]], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneIdInput")
    def zone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b7119257035a242880c47b1f6f5d7f0edb1b3cf0be52ef5baf37383806ead6e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zoneCacheVariants.ZoneCacheVariantsConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "value": "value",
        "zone_id": "zoneId",
    },
)
class ZoneCacheVariantsConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        value: typing.Union["ZoneCacheVariantsValue", typing.Dict[builtins.str, typing.Any]],
        zone_id: builtins.str,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param value: Value of the zone setting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#value ZoneCacheVariants#value}
        :param zone_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#zone_id ZoneCacheVariants#zone_id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(value, dict):
            value = ZoneCacheVariantsValue(**value)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ecb5647116c380ffb859538a69ac283a47c20e45b6455ca8798f72eb53fde79)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "value": value,
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
    def value(self) -> "ZoneCacheVariantsValue":
        '''Value of the zone setting.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#value ZoneCacheVariants#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast("ZoneCacheVariantsValue", result)

    @builtins.property
    def zone_id(self) -> builtins.str:
        '''Identifier.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#zone_id ZoneCacheVariants#zone_id}
        '''
        result = self._values.get("zone_id")
        assert result is not None, "Required property 'zone_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZoneCacheVariantsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.zoneCacheVariants.ZoneCacheVariantsValue",
    jsii_struct_bases=[],
    name_mapping={
        "avif": "avif",
        "bmp": "bmp",
        "gif": "gif",
        "jp2": "jp2",
        "jpeg": "jpeg",
        "jpg": "jpg",
        "jpg2": "jpg2",
        "png": "png",
        "tif": "tif",
        "tiff": "tiff",
        "webp": "webp",
    },
)
class ZoneCacheVariantsValue:
    def __init__(
        self,
        *,
        avif: typing.Optional[typing.Sequence[builtins.str]] = None,
        bmp: typing.Optional[typing.Sequence[builtins.str]] = None,
        gif: typing.Optional[typing.Sequence[builtins.str]] = None,
        jp2: typing.Optional[typing.Sequence[builtins.str]] = None,
        jpeg: typing.Optional[typing.Sequence[builtins.str]] = None,
        jpg: typing.Optional[typing.Sequence[builtins.str]] = None,
        jpg2: typing.Optional[typing.Sequence[builtins.str]] = None,
        png: typing.Optional[typing.Sequence[builtins.str]] = None,
        tif: typing.Optional[typing.Sequence[builtins.str]] = None,
        tiff: typing.Optional[typing.Sequence[builtins.str]] = None,
        webp: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param avif: List of strings with the MIME types of all the variants that should be served for avif. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#avif ZoneCacheVariants#avif}
        :param bmp: List of strings with the MIME types of all the variants that should be served for bmp. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#bmp ZoneCacheVariants#bmp}
        :param gif: List of strings with the MIME types of all the variants that should be served for gif. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#gif ZoneCacheVariants#gif}
        :param jp2: List of strings with the MIME types of all the variants that should be served for jp2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#jp2 ZoneCacheVariants#jp2}
        :param jpeg: List of strings with the MIME types of all the variants that should be served for jpeg. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#jpeg ZoneCacheVariants#jpeg}
        :param jpg: List of strings with the MIME types of all the variants that should be served for jpg. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#jpg ZoneCacheVariants#jpg}
        :param jpg2: List of strings with the MIME types of all the variants that should be served for jpg2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#jpg2 ZoneCacheVariants#jpg2}
        :param png: List of strings with the MIME types of all the variants that should be served for png. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#png ZoneCacheVariants#png}
        :param tif: List of strings with the MIME types of all the variants that should be served for tif. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#tif ZoneCacheVariants#tif}
        :param tiff: List of strings with the MIME types of all the variants that should be served for tiff. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#tiff ZoneCacheVariants#tiff}
        :param webp: List of strings with the MIME types of all the variants that should be served for webp. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#webp ZoneCacheVariants#webp}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c4ef09a3a4818f30d740116bd19f5db193bbf0c51d0a3ced078fda7f8f2ef83)
            check_type(argname="argument avif", value=avif, expected_type=type_hints["avif"])
            check_type(argname="argument bmp", value=bmp, expected_type=type_hints["bmp"])
            check_type(argname="argument gif", value=gif, expected_type=type_hints["gif"])
            check_type(argname="argument jp2", value=jp2, expected_type=type_hints["jp2"])
            check_type(argname="argument jpeg", value=jpeg, expected_type=type_hints["jpeg"])
            check_type(argname="argument jpg", value=jpg, expected_type=type_hints["jpg"])
            check_type(argname="argument jpg2", value=jpg2, expected_type=type_hints["jpg2"])
            check_type(argname="argument png", value=png, expected_type=type_hints["png"])
            check_type(argname="argument tif", value=tif, expected_type=type_hints["tif"])
            check_type(argname="argument tiff", value=tiff, expected_type=type_hints["tiff"])
            check_type(argname="argument webp", value=webp, expected_type=type_hints["webp"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if avif is not None:
            self._values["avif"] = avif
        if bmp is not None:
            self._values["bmp"] = bmp
        if gif is not None:
            self._values["gif"] = gif
        if jp2 is not None:
            self._values["jp2"] = jp2
        if jpeg is not None:
            self._values["jpeg"] = jpeg
        if jpg is not None:
            self._values["jpg"] = jpg
        if jpg2 is not None:
            self._values["jpg2"] = jpg2
        if png is not None:
            self._values["png"] = png
        if tif is not None:
            self._values["tif"] = tif
        if tiff is not None:
            self._values["tiff"] = tiff
        if webp is not None:
            self._values["webp"] = webp

    @builtins.property
    def avif(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of strings with the MIME types of all the variants that should be served for avif.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#avif ZoneCacheVariants#avif}
        '''
        result = self._values.get("avif")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bmp(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of strings with the MIME types of all the variants that should be served for bmp.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#bmp ZoneCacheVariants#bmp}
        '''
        result = self._values.get("bmp")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def gif(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of strings with the MIME types of all the variants that should be served for gif.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#gif ZoneCacheVariants#gif}
        '''
        result = self._values.get("gif")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def jp2(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of strings with the MIME types of all the variants that should be served for jp2.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#jp2 ZoneCacheVariants#jp2}
        '''
        result = self._values.get("jp2")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def jpeg(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of strings with the MIME types of all the variants that should be served for jpeg.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#jpeg ZoneCacheVariants#jpeg}
        '''
        result = self._values.get("jpeg")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def jpg(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of strings with the MIME types of all the variants that should be served for jpg.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#jpg ZoneCacheVariants#jpg}
        '''
        result = self._values.get("jpg")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def jpg2(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of strings with the MIME types of all the variants that should be served for jpg2.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#jpg2 ZoneCacheVariants#jpg2}
        '''
        result = self._values.get("jpg2")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def png(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of strings with the MIME types of all the variants that should be served for png.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#png ZoneCacheVariants#png}
        '''
        result = self._values.get("png")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tif(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of strings with the MIME types of all the variants that should be served for tif.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#tif ZoneCacheVariants#tif}
        '''
        result = self._values.get("tif")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tiff(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of strings with the MIME types of all the variants that should be served for tiff.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#tiff ZoneCacheVariants#tiff}
        '''
        result = self._values.get("tiff")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def webp(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of strings with the MIME types of all the variants that should be served for webp.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/zone_cache_variants#webp ZoneCacheVariants#webp}
        '''
        result = self._values.get("webp")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZoneCacheVariantsValue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZoneCacheVariantsValueOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.zoneCacheVariants.ZoneCacheVariantsValueOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fbc1710dca203195664aa9768f13fad6db82d4290c6b35af5e751015b1ba2312)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAvif")
    def reset_avif(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAvif", []))

    @jsii.member(jsii_name="resetBmp")
    def reset_bmp(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBmp", []))

    @jsii.member(jsii_name="resetGif")
    def reset_gif(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGif", []))

    @jsii.member(jsii_name="resetJp2")
    def reset_jp2(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJp2", []))

    @jsii.member(jsii_name="resetJpeg")
    def reset_jpeg(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJpeg", []))

    @jsii.member(jsii_name="resetJpg")
    def reset_jpg(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJpg", []))

    @jsii.member(jsii_name="resetJpg2")
    def reset_jpg2(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJpg2", []))

    @jsii.member(jsii_name="resetPng")
    def reset_png(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPng", []))

    @jsii.member(jsii_name="resetTif")
    def reset_tif(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTif", []))

    @jsii.member(jsii_name="resetTiff")
    def reset_tiff(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTiff", []))

    @jsii.member(jsii_name="resetWebp")
    def reset_webp(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWebp", []))

    @builtins.property
    @jsii.member(jsii_name="avifInput")
    def avif_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "avifInput"))

    @builtins.property
    @jsii.member(jsii_name="bmpInput")
    def bmp_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "bmpInput"))

    @builtins.property
    @jsii.member(jsii_name="gifInput")
    def gif_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "gifInput"))

    @builtins.property
    @jsii.member(jsii_name="jp2Input")
    def jp2_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "jp2Input"))

    @builtins.property
    @jsii.member(jsii_name="jpegInput")
    def jpeg_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "jpegInput"))

    @builtins.property
    @jsii.member(jsii_name="jpg2Input")
    def jpg2_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "jpg2Input"))

    @builtins.property
    @jsii.member(jsii_name="jpgInput")
    def jpg_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "jpgInput"))

    @builtins.property
    @jsii.member(jsii_name="pngInput")
    def png_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "pngInput"))

    @builtins.property
    @jsii.member(jsii_name="tiffInput")
    def tiff_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tiffInput"))

    @builtins.property
    @jsii.member(jsii_name="tifInput")
    def tif_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tifInput"))

    @builtins.property
    @jsii.member(jsii_name="webpInput")
    def webp_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "webpInput"))

    @builtins.property
    @jsii.member(jsii_name="avif")
    def avif(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "avif"))

    @avif.setter
    def avif(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcd73908888234d343c60933f8ff7044dd51a0991c7358f316bd271684fc3cff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "avif", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bmp")
    def bmp(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "bmp"))

    @bmp.setter
    def bmp(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d9e5e21ecdc44ca9266ddec7db263f54614ca1340eeb2ae99c26281653e5d6f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bmp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gif")
    def gif(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "gif"))

    @gif.setter
    def gif(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8de66ab8435b85fcf61e8e21ae8c7aa0e6697cc017a02fda5dac2611f1bb2c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gif", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jp2")
    def jp2(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "jp2"))

    @jp2.setter
    def jp2(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fb32af37e236a0a1fd40e86710be7eeae93a65e75694c865adefbdbfccba50c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jp2", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jpeg")
    def jpeg(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "jpeg"))

    @jpeg.setter
    def jpeg(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2de3afcf703b0f8a01585915634d50d1770176ef5d8f0d2e9db52dab2a4ea01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jpeg", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jpg")
    def jpg(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "jpg"))

    @jpg.setter
    def jpg(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e97a49cffb8a4d95a84ad15f9bb891deeb55578ca2ca8c7cd4d65ef4866bd687)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jpg", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jpg2")
    def jpg2(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "jpg2"))

    @jpg2.setter
    def jpg2(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c288c05d7b055150715a8dae0e810b8924c87bfe2b680c47aeb608515ca2c0e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jpg2", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="png")
    def png(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "png"))

    @png.setter
    def png(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__781f09091bd0f0cf91bed57e0a5c48ef63b117f9f2488f104594a92f0ce330fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "png", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tif")
    def tif(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tif"))

    @tif.setter
    def tif(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d48b39ffb0c57b4068c16f3f0eb5940905f31ae92b2e2788f048e087bb5bb95)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tif", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tiff")
    def tiff(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tiff"))

    @tiff.setter
    def tiff(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__081c4527ff0ab675f66b6b058ac650f3233a6179c5e602bed7a373467e084edd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tiff", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="webp")
    def webp(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "webp"))

    @webp.setter
    def webp(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0e6d566495cbe8d75d260d38f9b65ab47e0e5bea6d0d797024a0880542f6400)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "webp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZoneCacheVariantsValue]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZoneCacheVariantsValue]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZoneCacheVariantsValue]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54b3a42b5f029b33e602cb550a962381bb8b562d8e39a25f899d71840b98b792)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ZoneCacheVariants",
    "ZoneCacheVariantsConfig",
    "ZoneCacheVariantsValue",
    "ZoneCacheVariantsValueOutputReference",
]

publication.publish()

def _typecheckingstub__6182c0f5085287c30b04cfcc97155c89b372750ee22d9009b7669a3e95c3e960(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    value: typing.Union[ZoneCacheVariantsValue, typing.Dict[builtins.str, typing.Any]],
    zone_id: builtins.str,
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

def _typecheckingstub__5fa85c49221adb6b53855914f514e397ce395a3772779ebe1c3276f395c5a43c(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b7119257035a242880c47b1f6f5d7f0edb1b3cf0be52ef5baf37383806ead6e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ecb5647116c380ffb859538a69ac283a47c20e45b6455ca8798f72eb53fde79(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    value: typing.Union[ZoneCacheVariantsValue, typing.Dict[builtins.str, typing.Any]],
    zone_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c4ef09a3a4818f30d740116bd19f5db193bbf0c51d0a3ced078fda7f8f2ef83(
    *,
    avif: typing.Optional[typing.Sequence[builtins.str]] = None,
    bmp: typing.Optional[typing.Sequence[builtins.str]] = None,
    gif: typing.Optional[typing.Sequence[builtins.str]] = None,
    jp2: typing.Optional[typing.Sequence[builtins.str]] = None,
    jpeg: typing.Optional[typing.Sequence[builtins.str]] = None,
    jpg: typing.Optional[typing.Sequence[builtins.str]] = None,
    jpg2: typing.Optional[typing.Sequence[builtins.str]] = None,
    png: typing.Optional[typing.Sequence[builtins.str]] = None,
    tif: typing.Optional[typing.Sequence[builtins.str]] = None,
    tiff: typing.Optional[typing.Sequence[builtins.str]] = None,
    webp: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbc1710dca203195664aa9768f13fad6db82d4290c6b35af5e751015b1ba2312(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcd73908888234d343c60933f8ff7044dd51a0991c7358f316bd271684fc3cff(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d9e5e21ecdc44ca9266ddec7db263f54614ca1340eeb2ae99c26281653e5d6f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8de66ab8435b85fcf61e8e21ae8c7aa0e6697cc017a02fda5dac2611f1bb2c9(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fb32af37e236a0a1fd40e86710be7eeae93a65e75694c865adefbdbfccba50c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2de3afcf703b0f8a01585915634d50d1770176ef5d8f0d2e9db52dab2a4ea01(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e97a49cffb8a4d95a84ad15f9bb891deeb55578ca2ca8c7cd4d65ef4866bd687(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c288c05d7b055150715a8dae0e810b8924c87bfe2b680c47aeb608515ca2c0e4(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__781f09091bd0f0cf91bed57e0a5c48ef63b117f9f2488f104594a92f0ce330fe(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d48b39ffb0c57b4068c16f3f0eb5940905f31ae92b2e2788f048e087bb5bb95(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__081c4527ff0ab675f66b6b058ac650f3233a6179c5e602bed7a373467e084edd(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0e6d566495cbe8d75d260d38f9b65ab47e0e5bea6d0d797024a0880542f6400(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54b3a42b5f029b33e602cb550a962381bb8b562d8e39a25f899d71840b98b792(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ZoneCacheVariantsValue]],
) -> None:
    """Type checking stubs"""
    pass
