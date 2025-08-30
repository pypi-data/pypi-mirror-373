r'''
# `cloudflare_queue_consumer`

Refer to the Terraform Registry for docs: [`cloudflare_queue_consumer`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer).
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


class QueueConsumer(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.queueConsumer.QueueConsumer",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer cloudflare_queue_consumer}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        queue_id: builtins.str,
        consumer_id: typing.Optional[builtins.str] = None,
        dead_letter_queue: typing.Optional[builtins.str] = None,
        script_name: typing.Optional[builtins.str] = None,
        settings: typing.Optional[typing.Union["QueueConsumerSettings", typing.Dict[builtins.str, typing.Any]]] = None,
        type: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer cloudflare_queue_consumer} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: A Resource identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#account_id QueueConsumer#account_id}
        :param queue_id: A Resource identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#queue_id QueueConsumer#queue_id}
        :param consumer_id: A Resource identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#consumer_id QueueConsumer#consumer_id}
        :param dead_letter_queue: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#dead_letter_queue QueueConsumer#dead_letter_queue}.
        :param script_name: Name of a Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#script_name QueueConsumer#script_name}
        :param settings: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#settings QueueConsumer#settings}.
        :param type: Available values: "worker", "http_pull". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#type QueueConsumer#type}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb742809ec55487c19a5de3fc3ea692b0f1de63ff87c0db0d2c95f18dbb77379)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = QueueConsumerConfig(
            account_id=account_id,
            queue_id=queue_id,
            consumer_id=consumer_id,
            dead_letter_queue=dead_letter_queue,
            script_name=script_name,
            settings=settings,
            type=type,
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
        '''Generates CDKTF code for importing a QueueConsumer resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the QueueConsumer to import.
        :param import_from_id: The id of the existing QueueConsumer that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the QueueConsumer to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ef28cd02c460e219c3a5fdbd034dca1964d7b68b7c5ad1dca6c7a09e269e8db)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putSettings")
    def put_settings(
        self,
        *,
        batch_size: typing.Optional[jsii.Number] = None,
        max_concurrency: typing.Optional[jsii.Number] = None,
        max_retries: typing.Optional[jsii.Number] = None,
        max_wait_time_ms: typing.Optional[jsii.Number] = None,
        retry_delay: typing.Optional[jsii.Number] = None,
        visibility_timeout_ms: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param batch_size: The maximum number of messages to include in a batch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#batch_size QueueConsumer#batch_size}
        :param max_concurrency: Maximum number of concurrent consumers that may consume from this Queue. Set to ``null`` to automatically opt in to the platform's maximum (recommended). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#max_concurrency QueueConsumer#max_concurrency}
        :param max_retries: The maximum number of retries. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#max_retries QueueConsumer#max_retries}
        :param max_wait_time_ms: The number of milliseconds to wait for a batch to fill up before attempting to deliver it. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#max_wait_time_ms QueueConsumer#max_wait_time_ms}
        :param retry_delay: The number of seconds to delay before making the message available for another attempt. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#retry_delay QueueConsumer#retry_delay}
        :param visibility_timeout_ms: The number of milliseconds that a message is exclusively leased. After the timeout, the message becomes available for another attempt. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#visibility_timeout_ms QueueConsumer#visibility_timeout_ms}
        '''
        value = QueueConsumerSettings(
            batch_size=batch_size,
            max_concurrency=max_concurrency,
            max_retries=max_retries,
            max_wait_time_ms=max_wait_time_ms,
            retry_delay=retry_delay,
            visibility_timeout_ms=visibility_timeout_ms,
        )

        return typing.cast(None, jsii.invoke(self, "putSettings", [value]))

    @jsii.member(jsii_name="resetConsumerId")
    def reset_consumer_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConsumerId", []))

    @jsii.member(jsii_name="resetDeadLetterQueue")
    def reset_dead_letter_queue(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeadLetterQueue", []))

    @jsii.member(jsii_name="resetScriptName")
    def reset_script_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScriptName", []))

    @jsii.member(jsii_name="resetSettings")
    def reset_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSettings", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

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
    @jsii.member(jsii_name="script")
    def script(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "script"))

    @builtins.property
    @jsii.member(jsii_name="settings")
    def settings(self) -> "QueueConsumerSettingsOutputReference":
        return typing.cast("QueueConsumerSettingsOutputReference", jsii.get(self, "settings"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="consumerIdInput")
    def consumer_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "consumerIdInput"))

    @builtins.property
    @jsii.member(jsii_name="deadLetterQueueInput")
    def dead_letter_queue_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deadLetterQueueInput"))

    @builtins.property
    @jsii.member(jsii_name="queueIdInput")
    def queue_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queueIdInput"))

    @builtins.property
    @jsii.member(jsii_name="scriptNameInput")
    def script_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scriptNameInput"))

    @builtins.property
    @jsii.member(jsii_name="settingsInput")
    def settings_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "QueueConsumerSettings"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "QueueConsumerSettings"]], jsii.get(self, "settingsInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__17b16d7268ef465a4f77b8f50071270c6d6f87c820f3d4d44f3bbcd92190201b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="consumerId")
    def consumer_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "consumerId"))

    @consumer_id.setter
    def consumer_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcb09bce8c25a8b9a99ca73530272ce84e960e3858ab10ce9cae012b5719bd1a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "consumerId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deadLetterQueue")
    def dead_letter_queue(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deadLetterQueue"))

    @dead_letter_queue.setter
    def dead_letter_queue(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3cd9440c7c4543af175ed37d8cbffe6b579bc3aeafc9a516349697869984d21)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deadLetterQueue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="queueId")
    def queue_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queueId"))

    @queue_id.setter
    def queue_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5900cb6ead178e36c248690f2ae3c850bee4b4786c3cb9337b091d797490624)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "queueId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scriptName")
    def script_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scriptName"))

    @script_name.setter
    def script_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de4f1c9cb55dffff8d9bbff1c06fa57bf342b8ba23b96f826863f89656810f6c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scriptName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0993c52a453b05634fff0d112d6db3cd9117853a1f216cd51d42ee5f1e044283)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.queueConsumer.QueueConsumerConfig",
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
        "queue_id": "queueId",
        "consumer_id": "consumerId",
        "dead_letter_queue": "deadLetterQueue",
        "script_name": "scriptName",
        "settings": "settings",
        "type": "type",
    },
)
class QueueConsumerConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        queue_id: builtins.str,
        consumer_id: typing.Optional[builtins.str] = None,
        dead_letter_queue: typing.Optional[builtins.str] = None,
        script_name: typing.Optional[builtins.str] = None,
        settings: typing.Optional[typing.Union["QueueConsumerSettings", typing.Dict[builtins.str, typing.Any]]] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: A Resource identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#account_id QueueConsumer#account_id}
        :param queue_id: A Resource identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#queue_id QueueConsumer#queue_id}
        :param consumer_id: A Resource identifier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#consumer_id QueueConsumer#consumer_id}
        :param dead_letter_queue: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#dead_letter_queue QueueConsumer#dead_letter_queue}.
        :param script_name: Name of a Worker. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#script_name QueueConsumer#script_name}
        :param settings: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#settings QueueConsumer#settings}.
        :param type: Available values: "worker", "http_pull". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#type QueueConsumer#type}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(settings, dict):
            settings = QueueConsumerSettings(**settings)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc8eeefa9bc816b9bfc40736b8548c9c8d61699912249962b72973376447665e)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument queue_id", value=queue_id, expected_type=type_hints["queue_id"])
            check_type(argname="argument consumer_id", value=consumer_id, expected_type=type_hints["consumer_id"])
            check_type(argname="argument dead_letter_queue", value=dead_letter_queue, expected_type=type_hints["dead_letter_queue"])
            check_type(argname="argument script_name", value=script_name, expected_type=type_hints["script_name"])
            check_type(argname="argument settings", value=settings, expected_type=type_hints["settings"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
            "queue_id": queue_id,
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
        if consumer_id is not None:
            self._values["consumer_id"] = consumer_id
        if dead_letter_queue is not None:
            self._values["dead_letter_queue"] = dead_letter_queue
        if script_name is not None:
            self._values["script_name"] = script_name
        if settings is not None:
            self._values["settings"] = settings
        if type is not None:
            self._values["type"] = type

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
        '''A Resource identifier.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#account_id QueueConsumer#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def queue_id(self) -> builtins.str:
        '''A Resource identifier.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#queue_id QueueConsumer#queue_id}
        '''
        result = self._values.get("queue_id")
        assert result is not None, "Required property 'queue_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def consumer_id(self) -> typing.Optional[builtins.str]:
        '''A Resource identifier.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#consumer_id QueueConsumer#consumer_id}
        '''
        result = self._values.get("consumer_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dead_letter_queue(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#dead_letter_queue QueueConsumer#dead_letter_queue}.'''
        result = self._values.get("dead_letter_queue")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def script_name(self) -> typing.Optional[builtins.str]:
        '''Name of a Worker.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#script_name QueueConsumer#script_name}
        '''
        result = self._values.get("script_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def settings(self) -> typing.Optional["QueueConsumerSettings"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#settings QueueConsumer#settings}.'''
        result = self._values.get("settings")
        return typing.cast(typing.Optional["QueueConsumerSettings"], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Available values: "worker", "http_pull".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#type QueueConsumer#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QueueConsumerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.queueConsumer.QueueConsumerSettings",
    jsii_struct_bases=[],
    name_mapping={
        "batch_size": "batchSize",
        "max_concurrency": "maxConcurrency",
        "max_retries": "maxRetries",
        "max_wait_time_ms": "maxWaitTimeMs",
        "retry_delay": "retryDelay",
        "visibility_timeout_ms": "visibilityTimeoutMs",
    },
)
class QueueConsumerSettings:
    def __init__(
        self,
        *,
        batch_size: typing.Optional[jsii.Number] = None,
        max_concurrency: typing.Optional[jsii.Number] = None,
        max_retries: typing.Optional[jsii.Number] = None,
        max_wait_time_ms: typing.Optional[jsii.Number] = None,
        retry_delay: typing.Optional[jsii.Number] = None,
        visibility_timeout_ms: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param batch_size: The maximum number of messages to include in a batch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#batch_size QueueConsumer#batch_size}
        :param max_concurrency: Maximum number of concurrent consumers that may consume from this Queue. Set to ``null`` to automatically opt in to the platform's maximum (recommended). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#max_concurrency QueueConsumer#max_concurrency}
        :param max_retries: The maximum number of retries. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#max_retries QueueConsumer#max_retries}
        :param max_wait_time_ms: The number of milliseconds to wait for a batch to fill up before attempting to deliver it. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#max_wait_time_ms QueueConsumer#max_wait_time_ms}
        :param retry_delay: The number of seconds to delay before making the message available for another attempt. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#retry_delay QueueConsumer#retry_delay}
        :param visibility_timeout_ms: The number of milliseconds that a message is exclusively leased. After the timeout, the message becomes available for another attempt. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#visibility_timeout_ms QueueConsumer#visibility_timeout_ms}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1599bd84e0843b4b19de653d3ff3731ca1e816125d0c01f52ac2100469276796)
            check_type(argname="argument batch_size", value=batch_size, expected_type=type_hints["batch_size"])
            check_type(argname="argument max_concurrency", value=max_concurrency, expected_type=type_hints["max_concurrency"])
            check_type(argname="argument max_retries", value=max_retries, expected_type=type_hints["max_retries"])
            check_type(argname="argument max_wait_time_ms", value=max_wait_time_ms, expected_type=type_hints["max_wait_time_ms"])
            check_type(argname="argument retry_delay", value=retry_delay, expected_type=type_hints["retry_delay"])
            check_type(argname="argument visibility_timeout_ms", value=visibility_timeout_ms, expected_type=type_hints["visibility_timeout_ms"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if batch_size is not None:
            self._values["batch_size"] = batch_size
        if max_concurrency is not None:
            self._values["max_concurrency"] = max_concurrency
        if max_retries is not None:
            self._values["max_retries"] = max_retries
        if max_wait_time_ms is not None:
            self._values["max_wait_time_ms"] = max_wait_time_ms
        if retry_delay is not None:
            self._values["retry_delay"] = retry_delay
        if visibility_timeout_ms is not None:
            self._values["visibility_timeout_ms"] = visibility_timeout_ms

    @builtins.property
    def batch_size(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of messages to include in a batch.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#batch_size QueueConsumer#batch_size}
        '''
        result = self._values.get("batch_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_concurrency(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of concurrent consumers that may consume from this Queue.

        Set to ``null`` to automatically opt in to the platform's maximum (recommended).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#max_concurrency QueueConsumer#max_concurrency}
        '''
        result = self._values.get("max_concurrency")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_retries(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of retries.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#max_retries QueueConsumer#max_retries}
        '''
        result = self._values.get("max_retries")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_wait_time_ms(self) -> typing.Optional[jsii.Number]:
        '''The number of milliseconds to wait for a batch to fill up before attempting to deliver it.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#max_wait_time_ms QueueConsumer#max_wait_time_ms}
        '''
        result = self._values.get("max_wait_time_ms")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def retry_delay(self) -> typing.Optional[jsii.Number]:
        '''The number of seconds to delay before making the message available for another attempt.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#retry_delay QueueConsumer#retry_delay}
        '''
        result = self._values.get("retry_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def visibility_timeout_ms(self) -> typing.Optional[jsii.Number]:
        '''The number of milliseconds that a message is exclusively leased.

        After the timeout, the message becomes available for another attempt.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/queue_consumer#visibility_timeout_ms QueueConsumer#visibility_timeout_ms}
        '''
        result = self._values.get("visibility_timeout_ms")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QueueConsumerSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QueueConsumerSettingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.queueConsumer.QueueConsumerSettingsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dbb7fab106e990912a46666b28346a4f441d0346b6200956b2c80c69362ed182)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetBatchSize")
    def reset_batch_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBatchSize", []))

    @jsii.member(jsii_name="resetMaxConcurrency")
    def reset_max_concurrency(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxConcurrency", []))

    @jsii.member(jsii_name="resetMaxRetries")
    def reset_max_retries(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxRetries", []))

    @jsii.member(jsii_name="resetMaxWaitTimeMs")
    def reset_max_wait_time_ms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxWaitTimeMs", []))

    @jsii.member(jsii_name="resetRetryDelay")
    def reset_retry_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetryDelay", []))

    @jsii.member(jsii_name="resetVisibilityTimeoutMs")
    def reset_visibility_timeout_ms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVisibilityTimeoutMs", []))

    @builtins.property
    @jsii.member(jsii_name="batchSizeInput")
    def batch_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "batchSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="maxConcurrencyInput")
    def max_concurrency_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxConcurrencyInput"))

    @builtins.property
    @jsii.member(jsii_name="maxRetriesInput")
    def max_retries_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxRetriesInput"))

    @builtins.property
    @jsii.member(jsii_name="maxWaitTimeMsInput")
    def max_wait_time_ms_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxWaitTimeMsInput"))

    @builtins.property
    @jsii.member(jsii_name="retryDelayInput")
    def retry_delay_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retryDelayInput"))

    @builtins.property
    @jsii.member(jsii_name="visibilityTimeoutMsInput")
    def visibility_timeout_ms_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "visibilityTimeoutMsInput"))

    @builtins.property
    @jsii.member(jsii_name="batchSize")
    def batch_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "batchSize"))

    @batch_size.setter
    def batch_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbc1132a256343cf1b4bced25c03eced251e12c7f612fda7f52ad7e03e47db5e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "batchSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxConcurrency")
    def max_concurrency(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxConcurrency"))

    @max_concurrency.setter
    def max_concurrency(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd60451753cca10f533557f4c4606904edb6dcbfa296381bc65a9ee1cfd0ca98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxConcurrency", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxRetries")
    def max_retries(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxRetries"))

    @max_retries.setter
    def max_retries(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__465166bac29c192610258e485734055ac8e95a7967634f7f099f504381835ab4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxRetries", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxWaitTimeMs")
    def max_wait_time_ms(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxWaitTimeMs"))

    @max_wait_time_ms.setter
    def max_wait_time_ms(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3cdc9c320461933f50848a6ab465b021d28e85c2df2dd00b7990d143d7474ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxWaitTimeMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retryDelay")
    def retry_delay(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retryDelay"))

    @retry_delay.setter
    def retry_delay(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6126f10266a9beb2fa0364f447b6efeea0f06dd24b7aeb501a916717ef9ecc37)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retryDelay", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="visibilityTimeoutMs")
    def visibility_timeout_ms(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "visibilityTimeoutMs"))

    @visibility_timeout_ms.setter
    def visibility_timeout_ms(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f429b4affc0af4a2ff2f547fb292822e7a2d05e0763f568f32e41d8b8b8940cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "visibilityTimeoutMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, QueueConsumerSettings]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, QueueConsumerSettings]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, QueueConsumerSettings]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfb764cc7ff9c93e14e1c289b5f21c76031b514c135a4423dd72a5a20b987f8a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "QueueConsumer",
    "QueueConsumerConfig",
    "QueueConsumerSettings",
    "QueueConsumerSettingsOutputReference",
]

publication.publish()

def _typecheckingstub__fb742809ec55487c19a5de3fc3ea692b0f1de63ff87c0db0d2c95f18dbb77379(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    queue_id: builtins.str,
    consumer_id: typing.Optional[builtins.str] = None,
    dead_letter_queue: typing.Optional[builtins.str] = None,
    script_name: typing.Optional[builtins.str] = None,
    settings: typing.Optional[typing.Union[QueueConsumerSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    type: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__7ef28cd02c460e219c3a5fdbd034dca1964d7b68b7c5ad1dca6c7a09e269e8db(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17b16d7268ef465a4f77b8f50071270c6d6f87c820f3d4d44f3bbcd92190201b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcb09bce8c25a8b9a99ca73530272ce84e960e3858ab10ce9cae012b5719bd1a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3cd9440c7c4543af175ed37d8cbffe6b579bc3aeafc9a516349697869984d21(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5900cb6ead178e36c248690f2ae3c850bee4b4786c3cb9337b091d797490624(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de4f1c9cb55dffff8d9bbff1c06fa57bf342b8ba23b96f826863f89656810f6c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0993c52a453b05634fff0d112d6db3cd9117853a1f216cd51d42ee5f1e044283(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc8eeefa9bc816b9bfc40736b8548c9c8d61699912249962b72973376447665e(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    queue_id: builtins.str,
    consumer_id: typing.Optional[builtins.str] = None,
    dead_letter_queue: typing.Optional[builtins.str] = None,
    script_name: typing.Optional[builtins.str] = None,
    settings: typing.Optional[typing.Union[QueueConsumerSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1599bd84e0843b4b19de653d3ff3731ca1e816125d0c01f52ac2100469276796(
    *,
    batch_size: typing.Optional[jsii.Number] = None,
    max_concurrency: typing.Optional[jsii.Number] = None,
    max_retries: typing.Optional[jsii.Number] = None,
    max_wait_time_ms: typing.Optional[jsii.Number] = None,
    retry_delay: typing.Optional[jsii.Number] = None,
    visibility_timeout_ms: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbb7fab106e990912a46666b28346a4f441d0346b6200956b2c80c69362ed182(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbc1132a256343cf1b4bced25c03eced251e12c7f612fda7f52ad7e03e47db5e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd60451753cca10f533557f4c4606904edb6dcbfa296381bc65a9ee1cfd0ca98(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__465166bac29c192610258e485734055ac8e95a7967634f7f099f504381835ab4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3cdc9c320461933f50848a6ab465b021d28e85c2df2dd00b7990d143d7474ae(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6126f10266a9beb2fa0364f447b6efeea0f06dd24b7aeb501a916717ef9ecc37(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f429b4affc0af4a2ff2f547fb292822e7a2d05e0763f568f32e41d8b8b8940cf(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfb764cc7ff9c93e14e1c289b5f21c76031b514c135a4423dd72a5a20b987f8a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, QueueConsumerSettings]],
) -> None:
    """Type checking stubs"""
    pass
