r'''
# `cloudflare_logpush_job`

Refer to the Terraform Registry for docs: [`cloudflare_logpush_job`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job).
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


class LogpushJob(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.logpushJob.LogpushJob",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job cloudflare_logpush_job}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        destination_conf: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
        dataset: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        filter: typing.Optional[builtins.str] = None,
        frequency: typing.Optional[builtins.str] = None,
        kind: typing.Optional[builtins.str] = None,
        logpull_options: typing.Optional[builtins.str] = None,
        max_upload_bytes: typing.Optional[jsii.Number] = None,
        max_upload_interval_seconds: typing.Optional[jsii.Number] = None,
        max_upload_records: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        output_options: typing.Optional[typing.Union["LogpushJobOutputOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        ownership_challenge: typing.Optional[builtins.str] = None,
        zone_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job cloudflare_logpush_job} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param destination_conf: Uniquely identifies a resource (such as an s3 bucket) where data. will be pushed. Additional configuration parameters supported by the destination may be included. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#destination_conf LogpushJob#destination_conf}
        :param account_id: The Account ID to use for this endpoint. Mutually exclusive with the Zone ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#account_id LogpushJob#account_id}
        :param dataset: Name of the dataset. A list of supported datasets can be found on the `Developer Docs <https://developers.cloudflare.com/logs/reference/log-fields/>`_. Available values: "access_requests", "audit_logs", "audit_logs_v2", "biso_user_actions", "casb_findings", "device_posture_results", "dlp_forensic_copies", "dns_firewall_logs", "dns_logs", "email_security_alerts", "firewall_events", "gateway_dns", "gateway_http", "gateway_network", "http_requests", "magic_ids_detections", "nel_reports", "network_analytics_logs", "page_shield_events", "sinkhole_http_logs", "spectrum_events", "ssh_logs", "workers_trace_events", "zaraz_events", "zero_trust_network_sessions". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#dataset LogpushJob#dataset}
        :param enabled: Flag that indicates if the job is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#enabled LogpushJob#enabled}
        :param filter: The filters to select the events to include and/or remove from your logs. For more information, refer to `Filters <https://developers.cloudflare.com/logs/reference/filters/>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#filter LogpushJob#filter}
        :param frequency: This field is deprecated. Please use ``max_upload_*`` parameters instead. . The frequency at which Cloudflare sends batches of logs to your destination. Setting frequency to high sends your logs in larger quantities of smaller files. Setting frequency to low sends logs in smaller quantities of larger files. Available values: "high", "low". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#frequency LogpushJob#frequency}
        :param kind: The kind parameter (optional) is used to differentiate between Logpush and Edge Log Delivery jobs (when supported by the dataset). Available values: "", "edge". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#kind LogpushJob#kind}
        :param logpull_options: This field is deprecated. Use ``output_options`` instead. Configuration string. It specifies things like requested fields and timestamp formats. If migrating from the logpull api, copy the url (full url or just the query string) of your call here, and logpush will keep on making this call for you, setting start and end times appropriately. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#logpull_options LogpushJob#logpull_options}
        :param max_upload_bytes: The maximum uncompressed file size of a batch of logs. This setting value must be between ``5 MB`` and ``1 GB``, or ``0`` to disable it. Note that you cannot set a minimum file size; this means that log files may be much smaller than this batch size. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#max_upload_bytes LogpushJob#max_upload_bytes}
        :param max_upload_interval_seconds: The maximum interval in seconds for log batches. This setting must be between 30 and 300 seconds (5 minutes), or ``0`` to disable it. Note that you cannot specify a minimum interval for log batches; this means that log files may be sent in shorter intervals than this. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#max_upload_interval_seconds LogpushJob#max_upload_interval_seconds}
        :param max_upload_records: The maximum number of log lines per batch. This setting must be between 1000 and 1,000,000 lines, or ``0`` to disable it. Note that you cannot specify a minimum number of log lines per batch; this means that log files may contain many fewer lines than this. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#max_upload_records LogpushJob#max_upload_records}
        :param name: Optional human readable job name. Not unique. Cloudflare suggests. that you set this to a meaningful string, like the domain name, to make it easier to identify your job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#name LogpushJob#name}
        :param output_options: The structured replacement for ``logpull_options``. When including this field, the ``logpull_option`` field will be ignored. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#output_options LogpushJob#output_options}
        :param ownership_challenge: Ownership challenge token to prove destination ownership. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#ownership_challenge LogpushJob#ownership_challenge}
        :param zone_id: The Zone ID to use for this endpoint. Mutually exclusive with the Account ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#zone_id LogpushJob#zone_id}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d86643149f5e360885d2ce2f87756f1ce02fdfc9fa9c23fa50edc5a567132715)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = LogpushJobConfig(
            destination_conf=destination_conf,
            account_id=account_id,
            dataset=dataset,
            enabled=enabled,
            filter=filter,
            frequency=frequency,
            kind=kind,
            logpull_options=logpull_options,
            max_upload_bytes=max_upload_bytes,
            max_upload_interval_seconds=max_upload_interval_seconds,
            max_upload_records=max_upload_records,
            name=name,
            output_options=output_options,
            ownership_challenge=ownership_challenge,
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
        '''Generates CDKTF code for importing a LogpushJob resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the LogpushJob to import.
        :param import_from_id: The id of the existing LogpushJob that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the LogpushJob to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51553e62b6de4309a4587da509f3989ec84c64aeafc9bb97218e80ac5f57cba3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putOutputOptions")
    def put_output_options(
        self,
        *,
        batch_prefix: typing.Optional[builtins.str] = None,
        batch_suffix: typing.Optional[builtins.str] = None,
        cve202144228: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        field_delimiter: typing.Optional[builtins.str] = None,
        field_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        output_type: typing.Optional[builtins.str] = None,
        record_delimiter: typing.Optional[builtins.str] = None,
        record_prefix: typing.Optional[builtins.str] = None,
        record_suffix: typing.Optional[builtins.str] = None,
        record_template: typing.Optional[builtins.str] = None,
        sample_rate: typing.Optional[jsii.Number] = None,
        timestamp_format: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param batch_prefix: String to be prepended before each batch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#batch_prefix LogpushJob#batch_prefix}
        :param batch_suffix: String to be appended after each batch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#batch_suffix LogpushJob#batch_suffix}
        :param cve202144228: If set to true, will cause all occurrences of ``${`` in the generated files to be replaced with ``x{``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#cve_2021_44228 LogpushJob#cve_2021_44228}
        :param field_delimiter: String to join fields. This field be ignored when ``record_template`` is set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#field_delimiter LogpushJob#field_delimiter}
        :param field_names: List of field names to be included in the Logpush output. For the moment, there is no option to add all fields at once, so you must specify all the fields names you are interested in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#field_names LogpushJob#field_names}
        :param output_type: Specifies the output type, such as ``ndjson`` or ``csv``. This sets default values for the rest of the settings, depending on the chosen output type. Some formatting rules, like string quoting, are different between output types. Available values: "ndjson", "csv". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#output_type LogpushJob#output_type}
        :param record_delimiter: String to be inserted in-between the records as separator. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#record_delimiter LogpushJob#record_delimiter}
        :param record_prefix: String to be prepended before each record. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#record_prefix LogpushJob#record_prefix}
        :param record_suffix: String to be appended after each record. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#record_suffix LogpushJob#record_suffix}
        :param record_template: String to use as template for each record instead of the default json key value mapping. All fields used in the template must be present in ``field_names`` as well, otherwise they will end up as null. Format as a Go ``text/template`` without any standard functions, like conditionals, loops, sub-templates, etc. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#record_template LogpushJob#record_template}
        :param sample_rate: Floating number to specify sampling rate. Sampling is applied on top of filtering, and regardless of the current ``sample_interval`` of the data. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#sample_rate LogpushJob#sample_rate}
        :param timestamp_format: String to specify the format for timestamps, such as ``unixnano``, ``unix``, or ``rfc3339``. Available values: "unixnano", "unix", "rfc3339". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#timestamp_format LogpushJob#timestamp_format}
        '''
        value = LogpushJobOutputOptions(
            batch_prefix=batch_prefix,
            batch_suffix=batch_suffix,
            cve202144228=cve202144228,
            field_delimiter=field_delimiter,
            field_names=field_names,
            output_type=output_type,
            record_delimiter=record_delimiter,
            record_prefix=record_prefix,
            record_suffix=record_suffix,
            record_template=record_template,
            sample_rate=sample_rate,
            timestamp_format=timestamp_format,
        )

        return typing.cast(None, jsii.invoke(self, "putOutputOptions", [value]))

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="resetDataset")
    def reset_dataset(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataset", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetFilter")
    def reset_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilter", []))

    @jsii.member(jsii_name="resetFrequency")
    def reset_frequency(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFrequency", []))

    @jsii.member(jsii_name="resetKind")
    def reset_kind(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKind", []))

    @jsii.member(jsii_name="resetLogpullOptions")
    def reset_logpull_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogpullOptions", []))

    @jsii.member(jsii_name="resetMaxUploadBytes")
    def reset_max_upload_bytes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxUploadBytes", []))

    @jsii.member(jsii_name="resetMaxUploadIntervalSeconds")
    def reset_max_upload_interval_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxUploadIntervalSeconds", []))

    @jsii.member(jsii_name="resetMaxUploadRecords")
    def reset_max_upload_records(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxUploadRecords", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetOutputOptions")
    def reset_output_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOutputOptions", []))

    @jsii.member(jsii_name="resetOwnershipChallenge")
    def reset_ownership_challenge(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOwnershipChallenge", []))

    @jsii.member(jsii_name="resetZoneId")
    def reset_zone_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetZoneId", []))

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
    @jsii.member(jsii_name="errorMessage")
    def error_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "errorMessage"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="lastComplete")
    def last_complete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastComplete"))

    @builtins.property
    @jsii.member(jsii_name="lastError")
    def last_error(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastError"))

    @builtins.property
    @jsii.member(jsii_name="outputOptions")
    def output_options(self) -> "LogpushJobOutputOptionsOutputReference":
        return typing.cast("LogpushJobOutputOptionsOutputReference", jsii.get(self, "outputOptions"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="datasetInput")
    def dataset_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "datasetInput"))

    @builtins.property
    @jsii.member(jsii_name="destinationConfInput")
    def destination_conf_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationConfInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="filterInput")
    def filter_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "filterInput"))

    @builtins.property
    @jsii.member(jsii_name="frequencyInput")
    def frequency_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "frequencyInput"))

    @builtins.property
    @jsii.member(jsii_name="kindInput")
    def kind_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kindInput"))

    @builtins.property
    @jsii.member(jsii_name="logpullOptionsInput")
    def logpull_options_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logpullOptionsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxUploadBytesInput")
    def max_upload_bytes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxUploadBytesInput"))

    @builtins.property
    @jsii.member(jsii_name="maxUploadIntervalSecondsInput")
    def max_upload_interval_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxUploadIntervalSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxUploadRecordsInput")
    def max_upload_records_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxUploadRecordsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="outputOptionsInput")
    def output_options_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "LogpushJobOutputOptions"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "LogpushJobOutputOptions"]], jsii.get(self, "outputOptionsInput"))

    @builtins.property
    @jsii.member(jsii_name="ownershipChallengeInput")
    def ownership_challenge_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ownershipChallengeInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneIdInput")
    def zone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39f61739c4a80fdea83bfe661c3199d56ae1020d97833b6368b5da2a6b1bd2e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dataset")
    def dataset(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataset"))

    @dataset.setter
    def dataset(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__383022d63018c6faf0089d7038c4f1071e3c9ac5c799dabe672e1096bd4a5d3e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataset", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="destinationConf")
    def destination_conf(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationConf"))

    @destination_conf.setter
    def destination_conf(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8be08cf4c661f2a1cb2a0bae9148ee664d6381d80deab47d4be90012a31757cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destinationConf", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__56fda018d72ae3d054e3214fc5191ea11a9225a7cea34c0a363ce3ff34b5959f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="filter")
    def filter(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "filter"))

    @filter.setter
    def filter(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4771bb9ec783b677bcbe28557320e01e3fb44891e2061739e4fbdf032a1c6e6f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "filter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="frequency")
    def frequency(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "frequency"))

    @frequency.setter
    def frequency(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__689b916d33d1e6824d1e4eafaafa0afe256336727e375944360e9a97b6bdc0c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "frequency", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="kind")
    def kind(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kind"))

    @kind.setter
    def kind(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ae1f1c9d599e9bcb9ffe92617a88e3f434297affc91e989ea68ab5aed90873d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kind", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logpullOptions")
    def logpull_options(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logpullOptions"))

    @logpull_options.setter
    def logpull_options(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c981421c1dc0a47ac5d145f350946a50cb97066b5e1a6806a40d58909a6b279)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logpullOptions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxUploadBytes")
    def max_upload_bytes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxUploadBytes"))

    @max_upload_bytes.setter
    def max_upload_bytes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__256280cfe7fe90d7e4b8d68fc9081bee4507c70e653b8706cbf771901fdd6365)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxUploadBytes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxUploadIntervalSeconds")
    def max_upload_interval_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxUploadIntervalSeconds"))

    @max_upload_interval_seconds.setter
    def max_upload_interval_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ee816558665932236ac49631970a799f930ddbdfbb82271a3a47fdbe13e3a46)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxUploadIntervalSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxUploadRecords")
    def max_upload_records(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxUploadRecords"))

    @max_upload_records.setter
    def max_upload_records(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b247839ed9ecd4ba6c15dc7aca993811fd40151087f1e76bdfbaf105b56988ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxUploadRecords", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2982bc4f92880206df1d3e3717417d29a0dcfdca8034e95dc6b76676a7490482)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ownershipChallenge")
    def ownership_challenge(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ownershipChallenge"))

    @ownership_challenge.setter
    def ownership_challenge(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4435894eb17e973b428eb54cc2b69e81583bcd6bf4cffb5d1422a8db9ff9eab2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ownershipChallenge", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4482f2d2848eda272dd31af58ac33912d3233862ae1e65be6c2869d0742ebd4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.logpushJob.LogpushJobConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "destination_conf": "destinationConf",
        "account_id": "accountId",
        "dataset": "dataset",
        "enabled": "enabled",
        "filter": "filter",
        "frequency": "frequency",
        "kind": "kind",
        "logpull_options": "logpullOptions",
        "max_upload_bytes": "maxUploadBytes",
        "max_upload_interval_seconds": "maxUploadIntervalSeconds",
        "max_upload_records": "maxUploadRecords",
        "name": "name",
        "output_options": "outputOptions",
        "ownership_challenge": "ownershipChallenge",
        "zone_id": "zoneId",
    },
)
class LogpushJobConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        destination_conf: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
        dataset: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        filter: typing.Optional[builtins.str] = None,
        frequency: typing.Optional[builtins.str] = None,
        kind: typing.Optional[builtins.str] = None,
        logpull_options: typing.Optional[builtins.str] = None,
        max_upload_bytes: typing.Optional[jsii.Number] = None,
        max_upload_interval_seconds: typing.Optional[jsii.Number] = None,
        max_upload_records: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        output_options: typing.Optional[typing.Union["LogpushJobOutputOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        ownership_challenge: typing.Optional[builtins.str] = None,
        zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param destination_conf: Uniquely identifies a resource (such as an s3 bucket) where data. will be pushed. Additional configuration parameters supported by the destination may be included. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#destination_conf LogpushJob#destination_conf}
        :param account_id: The Account ID to use for this endpoint. Mutually exclusive with the Zone ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#account_id LogpushJob#account_id}
        :param dataset: Name of the dataset. A list of supported datasets can be found on the `Developer Docs <https://developers.cloudflare.com/logs/reference/log-fields/>`_. Available values: "access_requests", "audit_logs", "audit_logs_v2", "biso_user_actions", "casb_findings", "device_posture_results", "dlp_forensic_copies", "dns_firewall_logs", "dns_logs", "email_security_alerts", "firewall_events", "gateway_dns", "gateway_http", "gateway_network", "http_requests", "magic_ids_detections", "nel_reports", "network_analytics_logs", "page_shield_events", "sinkhole_http_logs", "spectrum_events", "ssh_logs", "workers_trace_events", "zaraz_events", "zero_trust_network_sessions". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#dataset LogpushJob#dataset}
        :param enabled: Flag that indicates if the job is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#enabled LogpushJob#enabled}
        :param filter: The filters to select the events to include and/or remove from your logs. For more information, refer to `Filters <https://developers.cloudflare.com/logs/reference/filters/>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#filter LogpushJob#filter}
        :param frequency: This field is deprecated. Please use ``max_upload_*`` parameters instead. . The frequency at which Cloudflare sends batches of logs to your destination. Setting frequency to high sends your logs in larger quantities of smaller files. Setting frequency to low sends logs in smaller quantities of larger files. Available values: "high", "low". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#frequency LogpushJob#frequency}
        :param kind: The kind parameter (optional) is used to differentiate between Logpush and Edge Log Delivery jobs (when supported by the dataset). Available values: "", "edge". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#kind LogpushJob#kind}
        :param logpull_options: This field is deprecated. Use ``output_options`` instead. Configuration string. It specifies things like requested fields and timestamp formats. If migrating from the logpull api, copy the url (full url or just the query string) of your call here, and logpush will keep on making this call for you, setting start and end times appropriately. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#logpull_options LogpushJob#logpull_options}
        :param max_upload_bytes: The maximum uncompressed file size of a batch of logs. This setting value must be between ``5 MB`` and ``1 GB``, or ``0`` to disable it. Note that you cannot set a minimum file size; this means that log files may be much smaller than this batch size. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#max_upload_bytes LogpushJob#max_upload_bytes}
        :param max_upload_interval_seconds: The maximum interval in seconds for log batches. This setting must be between 30 and 300 seconds (5 minutes), or ``0`` to disable it. Note that you cannot specify a minimum interval for log batches; this means that log files may be sent in shorter intervals than this. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#max_upload_interval_seconds LogpushJob#max_upload_interval_seconds}
        :param max_upload_records: The maximum number of log lines per batch. This setting must be between 1000 and 1,000,000 lines, or ``0`` to disable it. Note that you cannot specify a minimum number of log lines per batch; this means that log files may contain many fewer lines than this. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#max_upload_records LogpushJob#max_upload_records}
        :param name: Optional human readable job name. Not unique. Cloudflare suggests. that you set this to a meaningful string, like the domain name, to make it easier to identify your job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#name LogpushJob#name}
        :param output_options: The structured replacement for ``logpull_options``. When including this field, the ``logpull_option`` field will be ignored. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#output_options LogpushJob#output_options}
        :param ownership_challenge: Ownership challenge token to prove destination ownership. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#ownership_challenge LogpushJob#ownership_challenge}
        :param zone_id: The Zone ID to use for this endpoint. Mutually exclusive with the Account ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#zone_id LogpushJob#zone_id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(output_options, dict):
            output_options = LogpushJobOutputOptions(**output_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07fa106b6d4d9d3d61e8373909c2cf82dc6ad097bfbbabeae6e60db7a2a06e59)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument destination_conf", value=destination_conf, expected_type=type_hints["destination_conf"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument dataset", value=dataset, expected_type=type_hints["dataset"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument filter", value=filter, expected_type=type_hints["filter"])
            check_type(argname="argument frequency", value=frequency, expected_type=type_hints["frequency"])
            check_type(argname="argument kind", value=kind, expected_type=type_hints["kind"])
            check_type(argname="argument logpull_options", value=logpull_options, expected_type=type_hints["logpull_options"])
            check_type(argname="argument max_upload_bytes", value=max_upload_bytes, expected_type=type_hints["max_upload_bytes"])
            check_type(argname="argument max_upload_interval_seconds", value=max_upload_interval_seconds, expected_type=type_hints["max_upload_interval_seconds"])
            check_type(argname="argument max_upload_records", value=max_upload_records, expected_type=type_hints["max_upload_records"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument output_options", value=output_options, expected_type=type_hints["output_options"])
            check_type(argname="argument ownership_challenge", value=ownership_challenge, expected_type=type_hints["ownership_challenge"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination_conf": destination_conf,
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
        if account_id is not None:
            self._values["account_id"] = account_id
        if dataset is not None:
            self._values["dataset"] = dataset
        if enabled is not None:
            self._values["enabled"] = enabled
        if filter is not None:
            self._values["filter"] = filter
        if frequency is not None:
            self._values["frequency"] = frequency
        if kind is not None:
            self._values["kind"] = kind
        if logpull_options is not None:
            self._values["logpull_options"] = logpull_options
        if max_upload_bytes is not None:
            self._values["max_upload_bytes"] = max_upload_bytes
        if max_upload_interval_seconds is not None:
            self._values["max_upload_interval_seconds"] = max_upload_interval_seconds
        if max_upload_records is not None:
            self._values["max_upload_records"] = max_upload_records
        if name is not None:
            self._values["name"] = name
        if output_options is not None:
            self._values["output_options"] = output_options
        if ownership_challenge is not None:
            self._values["ownership_challenge"] = ownership_challenge
        if zone_id is not None:
            self._values["zone_id"] = zone_id

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
    def destination_conf(self) -> builtins.str:
        '''Uniquely identifies a resource (such as an s3 bucket) where data.

        will be pushed. Additional configuration parameters supported by the destination may be included.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#destination_conf LogpushJob#destination_conf}
        '''
        result = self._values.get("destination_conf")
        assert result is not None, "Required property 'destination_conf' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[builtins.str]:
        '''The Account ID to use for this endpoint. Mutually exclusive with the Zone ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#account_id LogpushJob#account_id}
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dataset(self) -> typing.Optional[builtins.str]:
        '''Name of the dataset.

        A list of supported datasets can be found on the `Developer Docs <https://developers.cloudflare.com/logs/reference/log-fields/>`_.
        Available values: "access_requests", "audit_logs", "audit_logs_v2", "biso_user_actions", "casb_findings", "device_posture_results", "dlp_forensic_copies", "dns_firewall_logs", "dns_logs", "email_security_alerts", "firewall_events", "gateway_dns", "gateway_http", "gateway_network", "http_requests", "magic_ids_detections", "nel_reports", "network_analytics_logs", "page_shield_events", "sinkhole_http_logs", "spectrum_events", "ssh_logs", "workers_trace_events", "zaraz_events", "zero_trust_network_sessions".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#dataset LogpushJob#dataset}
        '''
        result = self._values.get("dataset")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag that indicates if the job is enabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#enabled LogpushJob#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def filter(self) -> typing.Optional[builtins.str]:
        '''The filters to select the events to include and/or remove from your logs. For more information, refer to `Filters <https://developers.cloudflare.com/logs/reference/filters/>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#filter LogpushJob#filter}
        '''
        result = self._values.get("filter")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def frequency(self) -> typing.Optional[builtins.str]:
        '''This field is deprecated.

        Please use ``max_upload_*`` parameters instead. . The frequency at which Cloudflare sends batches of logs to your destination. Setting frequency to high sends your logs in larger quantities of smaller files. Setting frequency to low sends logs in smaller quantities of larger files.
        Available values: "high", "low".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#frequency LogpushJob#frequency}
        '''
        result = self._values.get("frequency")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kind(self) -> typing.Optional[builtins.str]:
        '''The kind parameter (optional) is used to differentiate between Logpush and Edge Log Delivery jobs (when supported by the dataset).

        Available values: "", "edge".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#kind LogpushJob#kind}
        '''
        result = self._values.get("kind")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def logpull_options(self) -> typing.Optional[builtins.str]:
        '''This field is deprecated.

        Use ``output_options`` instead. Configuration string. It specifies things like requested fields and timestamp formats. If migrating from the logpull api, copy the url (full url or just the query string) of your call here, and logpush will keep on making this call for you, setting start and end times appropriately.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#logpull_options LogpushJob#logpull_options}
        '''
        result = self._values.get("logpull_options")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_upload_bytes(self) -> typing.Optional[jsii.Number]:
        '''The maximum uncompressed file size of a batch of logs.

        This setting value must be between ``5 MB`` and ``1 GB``, or ``0`` to disable it. Note that you cannot set a minimum file size; this means that log files may be much smaller than this batch size.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#max_upload_bytes LogpushJob#max_upload_bytes}
        '''
        result = self._values.get("max_upload_bytes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_upload_interval_seconds(self) -> typing.Optional[jsii.Number]:
        '''The maximum interval in seconds for log batches.

        This setting must be between 30 and 300 seconds (5 minutes), or ``0`` to disable it. Note that you cannot specify a minimum interval for log batches; this means that log files may be sent in shorter intervals than this.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#max_upload_interval_seconds LogpushJob#max_upload_interval_seconds}
        '''
        result = self._values.get("max_upload_interval_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_upload_records(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of log lines per batch.

        This setting must be between 1000 and 1,000,000 lines, or ``0`` to disable it. Note that you cannot specify a minimum number of log lines per batch; this means that log files may contain many fewer lines than this.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#max_upload_records LogpushJob#max_upload_records}
        '''
        result = self._values.get("max_upload_records")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Optional human readable job name.

        Not unique. Cloudflare suggests. that you set this to a meaningful string, like the domain name, to make it easier to identify your job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#name LogpushJob#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def output_options(self) -> typing.Optional["LogpushJobOutputOptions"]:
        '''The structured replacement for ``logpull_options``. When including this field, the ``logpull_option`` field will be ignored.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#output_options LogpushJob#output_options}
        '''
        result = self._values.get("output_options")
        return typing.cast(typing.Optional["LogpushJobOutputOptions"], result)

    @builtins.property
    def ownership_challenge(self) -> typing.Optional[builtins.str]:
        '''Ownership challenge token to prove destination ownership.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#ownership_challenge LogpushJob#ownership_challenge}
        '''
        result = self._values.get("ownership_challenge")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def zone_id(self) -> typing.Optional[builtins.str]:
        '''The Zone ID to use for this endpoint. Mutually exclusive with the Account ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#zone_id LogpushJob#zone_id}
        '''
        result = self._values.get("zone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LogpushJobConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.logpushJob.LogpushJobOutputOptions",
    jsii_struct_bases=[],
    name_mapping={
        "batch_prefix": "batchPrefix",
        "batch_suffix": "batchSuffix",
        "cve202144228": "cve202144228",
        "field_delimiter": "fieldDelimiter",
        "field_names": "fieldNames",
        "output_type": "outputType",
        "record_delimiter": "recordDelimiter",
        "record_prefix": "recordPrefix",
        "record_suffix": "recordSuffix",
        "record_template": "recordTemplate",
        "sample_rate": "sampleRate",
        "timestamp_format": "timestampFormat",
    },
)
class LogpushJobOutputOptions:
    def __init__(
        self,
        *,
        batch_prefix: typing.Optional[builtins.str] = None,
        batch_suffix: typing.Optional[builtins.str] = None,
        cve202144228: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        field_delimiter: typing.Optional[builtins.str] = None,
        field_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        output_type: typing.Optional[builtins.str] = None,
        record_delimiter: typing.Optional[builtins.str] = None,
        record_prefix: typing.Optional[builtins.str] = None,
        record_suffix: typing.Optional[builtins.str] = None,
        record_template: typing.Optional[builtins.str] = None,
        sample_rate: typing.Optional[jsii.Number] = None,
        timestamp_format: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param batch_prefix: String to be prepended before each batch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#batch_prefix LogpushJob#batch_prefix}
        :param batch_suffix: String to be appended after each batch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#batch_suffix LogpushJob#batch_suffix}
        :param cve202144228: If set to true, will cause all occurrences of ``${`` in the generated files to be replaced with ``x{``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#cve_2021_44228 LogpushJob#cve_2021_44228}
        :param field_delimiter: String to join fields. This field be ignored when ``record_template`` is set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#field_delimiter LogpushJob#field_delimiter}
        :param field_names: List of field names to be included in the Logpush output. For the moment, there is no option to add all fields at once, so you must specify all the fields names you are interested in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#field_names LogpushJob#field_names}
        :param output_type: Specifies the output type, such as ``ndjson`` or ``csv``. This sets default values for the rest of the settings, depending on the chosen output type. Some formatting rules, like string quoting, are different between output types. Available values: "ndjson", "csv". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#output_type LogpushJob#output_type}
        :param record_delimiter: String to be inserted in-between the records as separator. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#record_delimiter LogpushJob#record_delimiter}
        :param record_prefix: String to be prepended before each record. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#record_prefix LogpushJob#record_prefix}
        :param record_suffix: String to be appended after each record. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#record_suffix LogpushJob#record_suffix}
        :param record_template: String to use as template for each record instead of the default json key value mapping. All fields used in the template must be present in ``field_names`` as well, otherwise they will end up as null. Format as a Go ``text/template`` without any standard functions, like conditionals, loops, sub-templates, etc. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#record_template LogpushJob#record_template}
        :param sample_rate: Floating number to specify sampling rate. Sampling is applied on top of filtering, and regardless of the current ``sample_interval`` of the data. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#sample_rate LogpushJob#sample_rate}
        :param timestamp_format: String to specify the format for timestamps, such as ``unixnano``, ``unix``, or ``rfc3339``. Available values: "unixnano", "unix", "rfc3339". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#timestamp_format LogpushJob#timestamp_format}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22b73b43d0591e348427b169f9471b005342712f47e115359c25993e519cfeae)
            check_type(argname="argument batch_prefix", value=batch_prefix, expected_type=type_hints["batch_prefix"])
            check_type(argname="argument batch_suffix", value=batch_suffix, expected_type=type_hints["batch_suffix"])
            check_type(argname="argument cve202144228", value=cve202144228, expected_type=type_hints["cve202144228"])
            check_type(argname="argument field_delimiter", value=field_delimiter, expected_type=type_hints["field_delimiter"])
            check_type(argname="argument field_names", value=field_names, expected_type=type_hints["field_names"])
            check_type(argname="argument output_type", value=output_type, expected_type=type_hints["output_type"])
            check_type(argname="argument record_delimiter", value=record_delimiter, expected_type=type_hints["record_delimiter"])
            check_type(argname="argument record_prefix", value=record_prefix, expected_type=type_hints["record_prefix"])
            check_type(argname="argument record_suffix", value=record_suffix, expected_type=type_hints["record_suffix"])
            check_type(argname="argument record_template", value=record_template, expected_type=type_hints["record_template"])
            check_type(argname="argument sample_rate", value=sample_rate, expected_type=type_hints["sample_rate"])
            check_type(argname="argument timestamp_format", value=timestamp_format, expected_type=type_hints["timestamp_format"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if batch_prefix is not None:
            self._values["batch_prefix"] = batch_prefix
        if batch_suffix is not None:
            self._values["batch_suffix"] = batch_suffix
        if cve202144228 is not None:
            self._values["cve202144228"] = cve202144228
        if field_delimiter is not None:
            self._values["field_delimiter"] = field_delimiter
        if field_names is not None:
            self._values["field_names"] = field_names
        if output_type is not None:
            self._values["output_type"] = output_type
        if record_delimiter is not None:
            self._values["record_delimiter"] = record_delimiter
        if record_prefix is not None:
            self._values["record_prefix"] = record_prefix
        if record_suffix is not None:
            self._values["record_suffix"] = record_suffix
        if record_template is not None:
            self._values["record_template"] = record_template
        if sample_rate is not None:
            self._values["sample_rate"] = sample_rate
        if timestamp_format is not None:
            self._values["timestamp_format"] = timestamp_format

    @builtins.property
    def batch_prefix(self) -> typing.Optional[builtins.str]:
        '''String to be prepended before each batch.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#batch_prefix LogpushJob#batch_prefix}
        '''
        result = self._values.get("batch_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def batch_suffix(self) -> typing.Optional[builtins.str]:
        '''String to be appended after each batch.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#batch_suffix LogpushJob#batch_suffix}
        '''
        result = self._values.get("batch_suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cve202144228(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set to true, will cause all occurrences of ``${`` in the generated files to be replaced with ``x{``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#cve_2021_44228 LogpushJob#cve_2021_44228}
        '''
        result = self._values.get("cve202144228")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def field_delimiter(self) -> typing.Optional[builtins.str]:
        '''String to join fields. This field be ignored when ``record_template`` is set.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#field_delimiter LogpushJob#field_delimiter}
        '''
        result = self._values.get("field_delimiter")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def field_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of field names to be included in the Logpush output.

        For the moment, there is no option to add all fields at once, so you must specify all the fields names you are interested in.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#field_names LogpushJob#field_names}
        '''
        result = self._values.get("field_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def output_type(self) -> typing.Optional[builtins.str]:
        '''Specifies the output type, such as ``ndjson`` or ``csv``.

        This sets default values for the rest of the settings, depending on the chosen output type. Some formatting rules, like string quoting, are different between output types.
        Available values: "ndjson", "csv".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#output_type LogpushJob#output_type}
        '''
        result = self._values.get("output_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def record_delimiter(self) -> typing.Optional[builtins.str]:
        '''String to be inserted in-between the records as separator.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#record_delimiter LogpushJob#record_delimiter}
        '''
        result = self._values.get("record_delimiter")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def record_prefix(self) -> typing.Optional[builtins.str]:
        '''String to be prepended before each record.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#record_prefix LogpushJob#record_prefix}
        '''
        result = self._values.get("record_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def record_suffix(self) -> typing.Optional[builtins.str]:
        '''String to be appended after each record.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#record_suffix LogpushJob#record_suffix}
        '''
        result = self._values.get("record_suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def record_template(self) -> typing.Optional[builtins.str]:
        '''String to use as template for each record instead of the default json key value mapping.

        All fields used in the template must be present in ``field_names`` as well, otherwise they will end up as null. Format as a Go ``text/template`` without any standard functions, like conditionals, loops, sub-templates, etc.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#record_template LogpushJob#record_template}
        '''
        result = self._values.get("record_template")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sample_rate(self) -> typing.Optional[jsii.Number]:
        '''Floating number to specify sampling rate.

        Sampling is applied on top of filtering, and regardless of the current ``sample_interval`` of the data.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#sample_rate LogpushJob#sample_rate}
        '''
        result = self._values.get("sample_rate")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def timestamp_format(self) -> typing.Optional[builtins.str]:
        '''String to specify the format for timestamps, such as ``unixnano``, ``unix``, or ``rfc3339``. Available values: "unixnano", "unix", "rfc3339".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.9.0/docs/resources/logpush_job#timestamp_format LogpushJob#timestamp_format}
        '''
        result = self._values.get("timestamp_format")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LogpushJobOutputOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LogpushJobOutputOptionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.logpushJob.LogpushJobOutputOptionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__901674ea92fdb14e38d3361788d000932ca162076c85058400dace33bb802ddb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetBatchPrefix")
    def reset_batch_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBatchPrefix", []))

    @jsii.member(jsii_name="resetBatchSuffix")
    def reset_batch_suffix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBatchSuffix", []))

    @jsii.member(jsii_name="resetCve202144228")
    def reset_cve202144228(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCve202144228", []))

    @jsii.member(jsii_name="resetFieldDelimiter")
    def reset_field_delimiter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFieldDelimiter", []))

    @jsii.member(jsii_name="resetFieldNames")
    def reset_field_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFieldNames", []))

    @jsii.member(jsii_name="resetOutputType")
    def reset_output_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOutputType", []))

    @jsii.member(jsii_name="resetRecordDelimiter")
    def reset_record_delimiter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRecordDelimiter", []))

    @jsii.member(jsii_name="resetRecordPrefix")
    def reset_record_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRecordPrefix", []))

    @jsii.member(jsii_name="resetRecordSuffix")
    def reset_record_suffix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRecordSuffix", []))

    @jsii.member(jsii_name="resetRecordTemplate")
    def reset_record_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRecordTemplate", []))

    @jsii.member(jsii_name="resetSampleRate")
    def reset_sample_rate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSampleRate", []))

    @jsii.member(jsii_name="resetTimestampFormat")
    def reset_timestamp_format(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimestampFormat", []))

    @builtins.property
    @jsii.member(jsii_name="batchPrefixInput")
    def batch_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "batchPrefixInput"))

    @builtins.property
    @jsii.member(jsii_name="batchSuffixInput")
    def batch_suffix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "batchSuffixInput"))

    @builtins.property
    @jsii.member(jsii_name="cve202144228Input")
    def cve202144228_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "cve202144228Input"))

    @builtins.property
    @jsii.member(jsii_name="fieldDelimiterInput")
    def field_delimiter_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fieldDelimiterInput"))

    @builtins.property
    @jsii.member(jsii_name="fieldNamesInput")
    def field_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "fieldNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="outputTypeInput")
    def output_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "outputTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="recordDelimiterInput")
    def record_delimiter_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "recordDelimiterInput"))

    @builtins.property
    @jsii.member(jsii_name="recordPrefixInput")
    def record_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "recordPrefixInput"))

    @builtins.property
    @jsii.member(jsii_name="recordSuffixInput")
    def record_suffix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "recordSuffixInput"))

    @builtins.property
    @jsii.member(jsii_name="recordTemplateInput")
    def record_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "recordTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="sampleRateInput")
    def sample_rate_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sampleRateInput"))

    @builtins.property
    @jsii.member(jsii_name="timestampFormatInput")
    def timestamp_format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timestampFormatInput"))

    @builtins.property
    @jsii.member(jsii_name="batchPrefix")
    def batch_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "batchPrefix"))

    @batch_prefix.setter
    def batch_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46e397eeaa4bfadfd40755f2f34c33725638662436022052763e5dd705a7ff32)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "batchPrefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="batchSuffix")
    def batch_suffix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "batchSuffix"))

    @batch_suffix.setter
    def batch_suffix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5eaf6d646b49ad960d6e2af1e91429a0e3c3446e1f715e87ca7bd45c83fac581)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "batchSuffix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cve202144228")
    def cve202144228(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "cve202144228"))

    @cve202144228.setter
    def cve202144228(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9de76dc277d3e77353e7614c7657f901dceab2c3c42cf7f43d41356ef3aa3f93)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cve202144228", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="fieldDelimiter")
    def field_delimiter(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fieldDelimiter"))

    @field_delimiter.setter
    def field_delimiter(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49e9d5985f5dad1b17cd30230f0ad177982dbb88c20e2e7e3e87e8e0a27e29f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fieldDelimiter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="fieldNames")
    def field_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "fieldNames"))

    @field_names.setter
    def field_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37c043d1de5c1334e3a60622b65c8f2b88c6c0f0884b8b87577c763ceba21818)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fieldNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="outputType")
    def output_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputType"))

    @output_type.setter
    def output_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7873b594a5012ae6879c353d18fd3b31e4bd713d8d470230a6b17c6dcc1a6183)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "outputType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="recordDelimiter")
    def record_delimiter(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "recordDelimiter"))

    @record_delimiter.setter
    def record_delimiter(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99d297f1cb70f2eb221086ba0b58000bd3e4e258f4e7d5e204126acf8a369409)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "recordDelimiter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="recordPrefix")
    def record_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "recordPrefix"))

    @record_prefix.setter
    def record_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15b899d7e277f7a5269e056c5281e99ff796c095263dd4b62b1d7d0b9bbfe00f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "recordPrefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="recordSuffix")
    def record_suffix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "recordSuffix"))

    @record_suffix.setter
    def record_suffix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00006b3950ca105b1d62db9feac53a6896227043e533863b7adde345677842ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "recordSuffix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="recordTemplate")
    def record_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "recordTemplate"))

    @record_template.setter
    def record_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__432e502ed696cf9d5b1fd05d491cd1371f165630967e36d75c41b718069aa4ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "recordTemplate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sampleRate")
    def sample_rate(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sampleRate"))

    @sample_rate.setter
    def sample_rate(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce65cb55538aa84431e767061bd034c922ea28585be3140e3374fde4d468a6ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sampleRate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timestampFormat")
    def timestamp_format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timestampFormat"))

    @timestamp_format.setter
    def timestamp_format(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a6f063fa9ae435d92ff23d5f10acb5db2d0806a499b0ac3ebf483f86094e8b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timestampFormat", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LogpushJobOutputOptions]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LogpushJobOutputOptions]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LogpushJobOutputOptions]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b575d1de07e0870c561f4224db3477e9e4728c564b848d273f1d0aea160de9a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "LogpushJob",
    "LogpushJobConfig",
    "LogpushJobOutputOptions",
    "LogpushJobOutputOptionsOutputReference",
]

publication.publish()

def _typecheckingstub__d86643149f5e360885d2ce2f87756f1ce02fdfc9fa9c23fa50edc5a567132715(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    destination_conf: builtins.str,
    account_id: typing.Optional[builtins.str] = None,
    dataset: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    filter: typing.Optional[builtins.str] = None,
    frequency: typing.Optional[builtins.str] = None,
    kind: typing.Optional[builtins.str] = None,
    logpull_options: typing.Optional[builtins.str] = None,
    max_upload_bytes: typing.Optional[jsii.Number] = None,
    max_upload_interval_seconds: typing.Optional[jsii.Number] = None,
    max_upload_records: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    output_options: typing.Optional[typing.Union[LogpushJobOutputOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ownership_challenge: typing.Optional[builtins.str] = None,
    zone_id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__51553e62b6de4309a4587da509f3989ec84c64aeafc9bb97218e80ac5f57cba3(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39f61739c4a80fdea83bfe661c3199d56ae1020d97833b6368b5da2a6b1bd2e7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__383022d63018c6faf0089d7038c4f1071e3c9ac5c799dabe672e1096bd4a5d3e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8be08cf4c661f2a1cb2a0bae9148ee664d6381d80deab47d4be90012a31757cc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56fda018d72ae3d054e3214fc5191ea11a9225a7cea34c0a363ce3ff34b5959f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4771bb9ec783b677bcbe28557320e01e3fb44891e2061739e4fbdf032a1c6e6f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__689b916d33d1e6824d1e4eafaafa0afe256336727e375944360e9a97b6bdc0c6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ae1f1c9d599e9bcb9ffe92617a88e3f434297affc91e989ea68ab5aed90873d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c981421c1dc0a47ac5d145f350946a50cb97066b5e1a6806a40d58909a6b279(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__256280cfe7fe90d7e4b8d68fc9081bee4507c70e653b8706cbf771901fdd6365(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ee816558665932236ac49631970a799f930ddbdfbb82271a3a47fdbe13e3a46(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b247839ed9ecd4ba6c15dc7aca993811fd40151087f1e76bdfbaf105b56988ca(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2982bc4f92880206df1d3e3717417d29a0dcfdca8034e95dc6b76676a7490482(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4435894eb17e973b428eb54cc2b69e81583bcd6bf4cffb5d1422a8db9ff9eab2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4482f2d2848eda272dd31af58ac33912d3233862ae1e65be6c2869d0742ebd4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07fa106b6d4d9d3d61e8373909c2cf82dc6ad097bfbbabeae6e60db7a2a06e59(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    destination_conf: builtins.str,
    account_id: typing.Optional[builtins.str] = None,
    dataset: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    filter: typing.Optional[builtins.str] = None,
    frequency: typing.Optional[builtins.str] = None,
    kind: typing.Optional[builtins.str] = None,
    logpull_options: typing.Optional[builtins.str] = None,
    max_upload_bytes: typing.Optional[jsii.Number] = None,
    max_upload_interval_seconds: typing.Optional[jsii.Number] = None,
    max_upload_records: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    output_options: typing.Optional[typing.Union[LogpushJobOutputOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ownership_challenge: typing.Optional[builtins.str] = None,
    zone_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22b73b43d0591e348427b169f9471b005342712f47e115359c25993e519cfeae(
    *,
    batch_prefix: typing.Optional[builtins.str] = None,
    batch_suffix: typing.Optional[builtins.str] = None,
    cve202144228: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    field_delimiter: typing.Optional[builtins.str] = None,
    field_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    output_type: typing.Optional[builtins.str] = None,
    record_delimiter: typing.Optional[builtins.str] = None,
    record_prefix: typing.Optional[builtins.str] = None,
    record_suffix: typing.Optional[builtins.str] = None,
    record_template: typing.Optional[builtins.str] = None,
    sample_rate: typing.Optional[jsii.Number] = None,
    timestamp_format: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__901674ea92fdb14e38d3361788d000932ca162076c85058400dace33bb802ddb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46e397eeaa4bfadfd40755f2f34c33725638662436022052763e5dd705a7ff32(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5eaf6d646b49ad960d6e2af1e91429a0e3c3446e1f715e87ca7bd45c83fac581(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9de76dc277d3e77353e7614c7657f901dceab2c3c42cf7f43d41356ef3aa3f93(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49e9d5985f5dad1b17cd30230f0ad177982dbb88c20e2e7e3e87e8e0a27e29f8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37c043d1de5c1334e3a60622b65c8f2b88c6c0f0884b8b87577c763ceba21818(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7873b594a5012ae6879c353d18fd3b31e4bd713d8d470230a6b17c6dcc1a6183(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99d297f1cb70f2eb221086ba0b58000bd3e4e258f4e7d5e204126acf8a369409(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15b899d7e277f7a5269e056c5281e99ff796c095263dd4b62b1d7d0b9bbfe00f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00006b3950ca105b1d62db9feac53a6896227043e533863b7adde345677842ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__432e502ed696cf9d5b1fd05d491cd1371f165630967e36d75c41b718069aa4ef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce65cb55538aa84431e767061bd034c922ea28585be3140e3374fde4d468a6ae(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a6f063fa9ae435d92ff23d5f10acb5db2d0806a499b0ac3ebf483f86094e8b0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b575d1de07e0870c561f4224db3477e9e4728c564b848d273f1d0aea160de9a6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LogpushJobOutputOptions]],
) -> None:
    """Type checking stubs"""
    pass
