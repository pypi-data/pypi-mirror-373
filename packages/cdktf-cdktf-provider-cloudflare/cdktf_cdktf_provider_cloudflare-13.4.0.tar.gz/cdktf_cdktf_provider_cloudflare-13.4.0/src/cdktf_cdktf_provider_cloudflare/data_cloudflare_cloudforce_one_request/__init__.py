r'''
# `data_cloudflare_cloudforce_one_request`

Refer to the Terraform Registry for docs: [`data_cloudflare_cloudforce_one_request`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request).
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


class DataCloudflareCloudforceOneRequest(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareCloudforceOneRequest.DataCloudflareCloudforceOneRequest",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request cloudflare_cloudforce_one_request}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        filter: typing.Optional[typing.Union["DataCloudflareCloudforceOneRequestFilter", typing.Dict[builtins.str, typing.Any]]] = None,
        request_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request cloudflare_cloudforce_one_request} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#account_id DataCloudflareCloudforceOneRequest#account_id}
        :param filter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#filter DataCloudflareCloudforceOneRequest#filter}.
        :param request_id: UUID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#request_id DataCloudflareCloudforceOneRequest#request_id}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8264e549c48db37346ea83b836dc0d562d2f6e0bd7e0e327c2393be92a84b726)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataCloudflareCloudforceOneRequestConfig(
            account_id=account_id,
            filter=filter,
            request_id=request_id,
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
        '''Generates CDKTF code for importing a DataCloudflareCloudforceOneRequest resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataCloudflareCloudforceOneRequest to import.
        :param import_from_id: The id of the existing DataCloudflareCloudforceOneRequest that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataCloudflareCloudforceOneRequest to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38e3651d12229cf54f738f4a53e000ce853358417f51bafb601d1a36fee12046)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putFilter")
    def put_filter(
        self,
        *,
        page: jsii.Number,
        per_page: jsii.Number,
        completed_after: typing.Optional[builtins.str] = None,
        completed_before: typing.Optional[builtins.str] = None,
        created_after: typing.Optional[builtins.str] = None,
        created_before: typing.Optional[builtins.str] = None,
        request_type: typing.Optional[builtins.str] = None,
        sort_by: typing.Optional[builtins.str] = None,
        sort_order: typing.Optional[builtins.str] = None,
        status: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param page: Page number of results. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#page DataCloudflareCloudforceOneRequest#page}
        :param per_page: Number of results per page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#per_page DataCloudflareCloudforceOneRequest#per_page}
        :param completed_after: Retrieve requests completed after this time. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#completed_after DataCloudflareCloudforceOneRequest#completed_after}
        :param completed_before: Retrieve requests completed before this time. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#completed_before DataCloudflareCloudforceOneRequest#completed_before}
        :param created_after: Retrieve requests created after this time. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#created_after DataCloudflareCloudforceOneRequest#created_after}
        :param created_before: Retrieve requests created before this time. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#created_before DataCloudflareCloudforceOneRequest#created_before}
        :param request_type: Requested information from request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#request_type DataCloudflareCloudforceOneRequest#request_type}
        :param sort_by: Field to sort results by. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#sort_by DataCloudflareCloudforceOneRequest#sort_by}
        :param sort_order: Sort order (asc or desc). Available values: "asc", "desc". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#sort_order DataCloudflareCloudforceOneRequest#sort_order}
        :param status: Request Status. Available values: "open", "accepted", "reported", "approved", "completed", "declined". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#status DataCloudflareCloudforceOneRequest#status}
        '''
        value = DataCloudflareCloudforceOneRequestFilter(
            page=page,
            per_page=per_page,
            completed_after=completed_after,
            completed_before=completed_before,
            created_after=created_after,
            created_before=created_before,
            request_type=request_type,
            sort_by=sort_by,
            sort_order=sort_order,
            status=status,
        )

        return typing.cast(None, jsii.invoke(self, "putFilter", [value]))

    @jsii.member(jsii_name="resetFilter")
    def reset_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilter", []))

    @jsii.member(jsii_name="resetRequestId")
    def reset_request_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequestId", []))

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
    @jsii.member(jsii_name="completed")
    def completed(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "completed"))

    @builtins.property
    @jsii.member(jsii_name="content")
    def content(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "content"))

    @builtins.property
    @jsii.member(jsii_name="created")
    def created(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "created"))

    @builtins.property
    @jsii.member(jsii_name="filter")
    def filter(self) -> "DataCloudflareCloudforceOneRequestFilterOutputReference":
        return typing.cast("DataCloudflareCloudforceOneRequestFilterOutputReference", jsii.get(self, "filter"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="messageTokens")
    def message_tokens(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "messageTokens"))

    @builtins.property
    @jsii.member(jsii_name="priority")
    def priority(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "priority"))

    @builtins.property
    @jsii.member(jsii_name="readableId")
    def readable_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "readableId"))

    @builtins.property
    @jsii.member(jsii_name="request")
    def request(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "request"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="summary")
    def summary(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "summary"))

    @builtins.property
    @jsii.member(jsii_name="tlp")
    def tlp(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlp"))

    @builtins.property
    @jsii.member(jsii_name="tokens")
    def tokens(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokens"))

    @builtins.property
    @jsii.member(jsii_name="updated")
    def updated(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updated"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="filterInput")
    def filter_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataCloudflareCloudforceOneRequestFilter"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataCloudflareCloudforceOneRequestFilter"]], jsii.get(self, "filterInput"))

    @builtins.property
    @jsii.member(jsii_name="requestIdInput")
    def request_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "requestIdInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07ffcf22bd2c2f59e19ee030c483fc56e82dab45a49728dbd88b366ce8cb827f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requestId")
    def request_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "requestId"))

    @request_id.setter
    def request_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01b6997faed744da42ce7a5713febe0741aa50feb8075b85ab99e938ddaf6007)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requestId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareCloudforceOneRequest.DataCloudflareCloudforceOneRequestConfig",
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
        "request_id": "requestId",
    },
)
class DataCloudflareCloudforceOneRequestConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        filter: typing.Optional[typing.Union["DataCloudflareCloudforceOneRequestFilter", typing.Dict[builtins.str, typing.Any]]] = None,
        request_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#account_id DataCloudflareCloudforceOneRequest#account_id}
        :param filter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#filter DataCloudflareCloudforceOneRequest#filter}.
        :param request_id: UUID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#request_id DataCloudflareCloudforceOneRequest#request_id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(filter, dict):
            filter = DataCloudflareCloudforceOneRequestFilter(**filter)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a894f892c49026fa237f48bb8c6e4cd11f8ad2707559230dffa0455828697d41)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument filter", value=filter, expected_type=type_hints["filter"])
            check_type(argname="argument request_id", value=request_id, expected_type=type_hints["request_id"])
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
        if request_id is not None:
            self._values["request_id"] = request_id

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#account_id DataCloudflareCloudforceOneRequest#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def filter(self) -> typing.Optional["DataCloudflareCloudforceOneRequestFilter"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#filter DataCloudflareCloudforceOneRequest#filter}.'''
        result = self._values.get("filter")
        return typing.cast(typing.Optional["DataCloudflareCloudforceOneRequestFilter"], result)

    @builtins.property
    def request_id(self) -> typing.Optional[builtins.str]:
        '''UUID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#request_id DataCloudflareCloudforceOneRequest#request_id}
        '''
        result = self._values.get("request_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareCloudforceOneRequestConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareCloudforceOneRequest.DataCloudflareCloudforceOneRequestFilter",
    jsii_struct_bases=[],
    name_mapping={
        "page": "page",
        "per_page": "perPage",
        "completed_after": "completedAfter",
        "completed_before": "completedBefore",
        "created_after": "createdAfter",
        "created_before": "createdBefore",
        "request_type": "requestType",
        "sort_by": "sortBy",
        "sort_order": "sortOrder",
        "status": "status",
    },
)
class DataCloudflareCloudforceOneRequestFilter:
    def __init__(
        self,
        *,
        page: jsii.Number,
        per_page: jsii.Number,
        completed_after: typing.Optional[builtins.str] = None,
        completed_before: typing.Optional[builtins.str] = None,
        created_after: typing.Optional[builtins.str] = None,
        created_before: typing.Optional[builtins.str] = None,
        request_type: typing.Optional[builtins.str] = None,
        sort_by: typing.Optional[builtins.str] = None,
        sort_order: typing.Optional[builtins.str] = None,
        status: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param page: Page number of results. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#page DataCloudflareCloudforceOneRequest#page}
        :param per_page: Number of results per page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#per_page DataCloudflareCloudforceOneRequest#per_page}
        :param completed_after: Retrieve requests completed after this time. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#completed_after DataCloudflareCloudforceOneRequest#completed_after}
        :param completed_before: Retrieve requests completed before this time. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#completed_before DataCloudflareCloudforceOneRequest#completed_before}
        :param created_after: Retrieve requests created after this time. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#created_after DataCloudflareCloudforceOneRequest#created_after}
        :param created_before: Retrieve requests created before this time. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#created_before DataCloudflareCloudforceOneRequest#created_before}
        :param request_type: Requested information from request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#request_type DataCloudflareCloudforceOneRequest#request_type}
        :param sort_by: Field to sort results by. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#sort_by DataCloudflareCloudforceOneRequest#sort_by}
        :param sort_order: Sort order (asc or desc). Available values: "asc", "desc". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#sort_order DataCloudflareCloudforceOneRequest#sort_order}
        :param status: Request Status. Available values: "open", "accepted", "reported", "approved", "completed", "declined". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#status DataCloudflareCloudforceOneRequest#status}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d50be6aefbc96264aa983b6d21da5f192499c1310160cad1a237adf91f3e8be)
            check_type(argname="argument page", value=page, expected_type=type_hints["page"])
            check_type(argname="argument per_page", value=per_page, expected_type=type_hints["per_page"])
            check_type(argname="argument completed_after", value=completed_after, expected_type=type_hints["completed_after"])
            check_type(argname="argument completed_before", value=completed_before, expected_type=type_hints["completed_before"])
            check_type(argname="argument created_after", value=created_after, expected_type=type_hints["created_after"])
            check_type(argname="argument created_before", value=created_before, expected_type=type_hints["created_before"])
            check_type(argname="argument request_type", value=request_type, expected_type=type_hints["request_type"])
            check_type(argname="argument sort_by", value=sort_by, expected_type=type_hints["sort_by"])
            check_type(argname="argument sort_order", value=sort_order, expected_type=type_hints["sort_order"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "page": page,
            "per_page": per_page,
        }
        if completed_after is not None:
            self._values["completed_after"] = completed_after
        if completed_before is not None:
            self._values["completed_before"] = completed_before
        if created_after is not None:
            self._values["created_after"] = created_after
        if created_before is not None:
            self._values["created_before"] = created_before
        if request_type is not None:
            self._values["request_type"] = request_type
        if sort_by is not None:
            self._values["sort_by"] = sort_by
        if sort_order is not None:
            self._values["sort_order"] = sort_order
        if status is not None:
            self._values["status"] = status

    @builtins.property
    def page(self) -> jsii.Number:
        '''Page number of results.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#page DataCloudflareCloudforceOneRequest#page}
        '''
        result = self._values.get("page")
        assert result is not None, "Required property 'page' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def per_page(self) -> jsii.Number:
        '''Number of results per page.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#per_page DataCloudflareCloudforceOneRequest#per_page}
        '''
        result = self._values.get("per_page")
        assert result is not None, "Required property 'per_page' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def completed_after(self) -> typing.Optional[builtins.str]:
        '''Retrieve requests completed after this time.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#completed_after DataCloudflareCloudforceOneRequest#completed_after}
        '''
        result = self._values.get("completed_after")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def completed_before(self) -> typing.Optional[builtins.str]:
        '''Retrieve requests completed before this time.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#completed_before DataCloudflareCloudforceOneRequest#completed_before}
        '''
        result = self._values.get("completed_before")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def created_after(self) -> typing.Optional[builtins.str]:
        '''Retrieve requests created after this time.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#created_after DataCloudflareCloudforceOneRequest#created_after}
        '''
        result = self._values.get("created_after")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def created_before(self) -> typing.Optional[builtins.str]:
        '''Retrieve requests created before this time.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#created_before DataCloudflareCloudforceOneRequest#created_before}
        '''
        result = self._values.get("created_before")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def request_type(self) -> typing.Optional[builtins.str]:
        '''Requested information from request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#request_type DataCloudflareCloudforceOneRequest#request_type}
        '''
        result = self._values.get("request_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sort_by(self) -> typing.Optional[builtins.str]:
        '''Field to sort results by.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#sort_by DataCloudflareCloudforceOneRequest#sort_by}
        '''
        result = self._values.get("sort_by")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sort_order(self) -> typing.Optional[builtins.str]:
        '''Sort order (asc or desc). Available values: "asc", "desc".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#sort_order DataCloudflareCloudforceOneRequest#sort_order}
        '''
        result = self._values.get("sort_order")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def status(self) -> typing.Optional[builtins.str]:
        '''Request Status. Available values: "open", "accepted", "reported", "approved", "completed", "declined".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/data-sources/cloudforce_one_request#status DataCloudflareCloudforceOneRequest#status}
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCloudflareCloudforceOneRequestFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCloudflareCloudforceOneRequestFilterOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.dataCloudflareCloudforceOneRequest.DataCloudflareCloudforceOneRequestFilterOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f02b9256d92292c2f4150c2cebf9e272168c473da4a6c60ca4ef09d65c3c87da)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCompletedAfter")
    def reset_completed_after(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCompletedAfter", []))

    @jsii.member(jsii_name="resetCompletedBefore")
    def reset_completed_before(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCompletedBefore", []))

    @jsii.member(jsii_name="resetCreatedAfter")
    def reset_created_after(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatedAfter", []))

    @jsii.member(jsii_name="resetCreatedBefore")
    def reset_created_before(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatedBefore", []))

    @jsii.member(jsii_name="resetRequestType")
    def reset_request_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequestType", []))

    @jsii.member(jsii_name="resetSortBy")
    def reset_sort_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSortBy", []))

    @jsii.member(jsii_name="resetSortOrder")
    def reset_sort_order(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSortOrder", []))

    @jsii.member(jsii_name="resetStatus")
    def reset_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatus", []))

    @builtins.property
    @jsii.member(jsii_name="completedAfterInput")
    def completed_after_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "completedAfterInput"))

    @builtins.property
    @jsii.member(jsii_name="completedBeforeInput")
    def completed_before_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "completedBeforeInput"))

    @builtins.property
    @jsii.member(jsii_name="createdAfterInput")
    def created_after_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdAfterInput"))

    @builtins.property
    @jsii.member(jsii_name="createdBeforeInput")
    def created_before_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdBeforeInput"))

    @builtins.property
    @jsii.member(jsii_name="pageInput")
    def page_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "pageInput"))

    @builtins.property
    @jsii.member(jsii_name="perPageInput")
    def per_page_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "perPageInput"))

    @builtins.property
    @jsii.member(jsii_name="requestTypeInput")
    def request_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "requestTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="sortByInput")
    def sort_by_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sortByInput"))

    @builtins.property
    @jsii.member(jsii_name="sortOrderInput")
    def sort_order_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sortOrderInput"))

    @builtins.property
    @jsii.member(jsii_name="statusInput")
    def status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusInput"))

    @builtins.property
    @jsii.member(jsii_name="completedAfter")
    def completed_after(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "completedAfter"))

    @completed_after.setter
    def completed_after(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db79f5c5a96ff3ac1748826c30e1cc54009cace813ca95fea3a61743c8ef6efd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "completedAfter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="completedBefore")
    def completed_before(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "completedBefore"))

    @completed_before.setter
    def completed_before(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01a358d9406839ea217f422fa7bd3e41f2da599652c65ff37855994ba3d960b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "completedBefore", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="createdAfter")
    def created_after(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAfter"))

    @created_after.setter
    def created_after(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b08d321fa305bf779d812ec53456fec029bee93f72e3efb8a22491c1f8e77e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdAfter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="createdBefore")
    def created_before(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdBefore"))

    @created_before.setter
    def created_before(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22dd2b4cfac73797cd7ab62719a05f4c61b8edde6165c1b6c391a3fab40c5993)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdBefore", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="page")
    def page(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "page"))

    @page.setter
    def page(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a162b722755c5d69d1c7568fd9f0accbffa5c14bf78ffc1685a581a882c3463)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "page", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="perPage")
    def per_page(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "perPage"))

    @per_page.setter
    def per_page(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b9be5fe8a1d89158553af731f4e88da5896a5fc117ae1d4066d41f576dd8e7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "perPage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requestType")
    def request_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "requestType"))

    @request_type.setter
    def request_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c2383cefe57e9cc5ff3e59484480566625ee30806d8c8fed0526065da27007e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requestType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sortBy")
    def sort_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sortBy"))

    @sort_by.setter
    def sort_by(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30d3409943a978bb20150da3917c9e633bea4b3a9c8c768ac43a2b3b73d10fca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sortBy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sortOrder")
    def sort_order(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sortOrder"))

    @sort_order.setter
    def sort_order(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f0e1c6edefc1f764947b381af98fcedfbce94d5c77c8cc91938474e5aa93ba2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sortOrder", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f651acb8545eb705f4d418ee2548921d3dc5ccd987c4f258c098b7a7a43b3cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareCloudforceOneRequestFilter]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareCloudforceOneRequestFilter]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareCloudforceOneRequestFilter]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6ac2094af6d450aa31adfb3232136485e692956d676f4d00b8ad3192a5fe8f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataCloudflareCloudforceOneRequest",
    "DataCloudflareCloudforceOneRequestConfig",
    "DataCloudflareCloudforceOneRequestFilter",
    "DataCloudflareCloudforceOneRequestFilterOutputReference",
]

publication.publish()

def _typecheckingstub__8264e549c48db37346ea83b836dc0d562d2f6e0bd7e0e327c2393be92a84b726(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    filter: typing.Optional[typing.Union[DataCloudflareCloudforceOneRequestFilter, typing.Dict[builtins.str, typing.Any]]] = None,
    request_id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__38e3651d12229cf54f738f4a53e000ce853358417f51bafb601d1a36fee12046(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07ffcf22bd2c2f59e19ee030c483fc56e82dab45a49728dbd88b366ce8cb827f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01b6997faed744da42ce7a5713febe0741aa50feb8075b85ab99e938ddaf6007(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a894f892c49026fa237f48bb8c6e4cd11f8ad2707559230dffa0455828697d41(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    filter: typing.Optional[typing.Union[DataCloudflareCloudforceOneRequestFilter, typing.Dict[builtins.str, typing.Any]]] = None,
    request_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d50be6aefbc96264aa983b6d21da5f192499c1310160cad1a237adf91f3e8be(
    *,
    page: jsii.Number,
    per_page: jsii.Number,
    completed_after: typing.Optional[builtins.str] = None,
    completed_before: typing.Optional[builtins.str] = None,
    created_after: typing.Optional[builtins.str] = None,
    created_before: typing.Optional[builtins.str] = None,
    request_type: typing.Optional[builtins.str] = None,
    sort_by: typing.Optional[builtins.str] = None,
    sort_order: typing.Optional[builtins.str] = None,
    status: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f02b9256d92292c2f4150c2cebf9e272168c473da4a6c60ca4ef09d65c3c87da(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db79f5c5a96ff3ac1748826c30e1cc54009cace813ca95fea3a61743c8ef6efd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01a358d9406839ea217f422fa7bd3e41f2da599652c65ff37855994ba3d960b3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b08d321fa305bf779d812ec53456fec029bee93f72e3efb8a22491c1f8e77e7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22dd2b4cfac73797cd7ab62719a05f4c61b8edde6165c1b6c391a3fab40c5993(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a162b722755c5d69d1c7568fd9f0accbffa5c14bf78ffc1685a581a882c3463(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b9be5fe8a1d89158553af731f4e88da5896a5fc117ae1d4066d41f576dd8e7a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c2383cefe57e9cc5ff3e59484480566625ee30806d8c8fed0526065da27007e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30d3409943a978bb20150da3917c9e633bea4b3a9c8c768ac43a2b3b73d10fca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f0e1c6edefc1f764947b381af98fcedfbce94d5c77c8cc91938474e5aa93ba2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f651acb8545eb705f4d418ee2548921d3dc5ccd987c4f258c098b7a7a43b3cc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6ac2094af6d450aa31adfb3232136485e692956d676f4d00b8ad3192a5fe8f4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataCloudflareCloudforceOneRequestFilter]],
) -> None:
    """Type checking stubs"""
    pass
