r'''
# `databricks_online_table`

Refer to the Terraform Registry for docs: [`databricks_online_table`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table).
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


class OnlineTable(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTable",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table databricks_online_table}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        spec: typing.Optional[typing.Union["OnlineTableSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        timeouts: typing.Optional[typing.Union["OnlineTableTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table databricks_online_table} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#name OnlineTable#name}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#id OnlineTable#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param spec: spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#spec OnlineTable#spec}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#timeouts OnlineTable#timeouts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27c06822f3f60b687daf57df13eb2b83d2728eee5fa660afdf453be352d0aa47)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = OnlineTableConfig(
            name=name,
            id=id,
            spec=spec,
            timeouts=timeouts,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a OnlineTable resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the OnlineTable to import.
        :param import_from_id: The id of the existing OnlineTable that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the OnlineTable to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcca8e128ee248e68ced102a11111bc0cc83f8bc4d620ddaa491012a7bcee551)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putSpec")
    def put_spec(
        self,
        *,
        perform_full_copy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        primary_key_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        run_continuously: typing.Optional[typing.Union["OnlineTableSpecRunContinuously", typing.Dict[builtins.str, typing.Any]]] = None,
        run_triggered: typing.Optional[typing.Union["OnlineTableSpecRunTriggered", typing.Dict[builtins.str, typing.Any]]] = None,
        source_table_full_name: typing.Optional[builtins.str] = None,
        timeseries_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param perform_full_copy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#perform_full_copy OnlineTable#perform_full_copy}.
        :param primary_key_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#primary_key_columns OnlineTable#primary_key_columns}.
        :param run_continuously: run_continuously block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#run_continuously OnlineTable#run_continuously}
        :param run_triggered: run_triggered block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#run_triggered OnlineTable#run_triggered}
        :param source_table_full_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#source_table_full_name OnlineTable#source_table_full_name}.
        :param timeseries_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#timeseries_key OnlineTable#timeseries_key}.
        '''
        value = OnlineTableSpec(
            perform_full_copy=perform_full_copy,
            primary_key_columns=primary_key_columns,
            run_continuously=run_continuously,
            run_triggered=run_triggered,
            source_table_full_name=source_table_full_name,
            timeseries_key=timeseries_key,
        )

        return typing.cast(None, jsii.invoke(self, "putSpec", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(self, *, create: typing.Optional[builtins.str] = None) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#create OnlineTable#create}.
        '''
        value = OnlineTableTimeouts(create=create)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetSpec")
    def reset_spec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpec", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

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
    @jsii.member(jsii_name="spec")
    def spec(self) -> "OnlineTableSpecOutputReference":
        return typing.cast("OnlineTableSpecOutputReference", jsii.get(self, "spec"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> "OnlineTableStatusList":
        return typing.cast("OnlineTableStatusList", jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="tableServingUrl")
    def table_serving_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tableServingUrl"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "OnlineTableTimeoutsOutputReference":
        return typing.cast("OnlineTableTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="unityCatalogProvisioningState")
    def unity_catalog_provisioning_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unityCatalogProvisioningState"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="specInput")
    def spec_input(self) -> typing.Optional["OnlineTableSpec"]:
        return typing.cast(typing.Optional["OnlineTableSpec"], jsii.get(self, "specInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "OnlineTableTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "OnlineTableTimeouts"]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5eb7cfecf51a0ac5bbe0085ae4497824b11bca30b5c9e929e208d18a8a4807c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e107276014a6be8f7fcae2aa5cf48f1bc9e290b1afe79d5e6828a0c0d5c48259)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "name": "name",
        "id": "id",
        "spec": "spec",
        "timeouts": "timeouts",
    },
)
class OnlineTableConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        spec: typing.Optional[typing.Union["OnlineTableSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        timeouts: typing.Optional[typing.Union["OnlineTableTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#name OnlineTable#name}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#id OnlineTable#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param spec: spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#spec OnlineTable#spec}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#timeouts OnlineTable#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(spec, dict):
            spec = OnlineTableSpec(**spec)
        if isinstance(timeouts, dict):
            timeouts = OnlineTableTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a3767cc98d57ab0d09715fb8bd46bc42450df671a1fdf21e3bb40d5b8795e6a)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument spec", value=spec, expected_type=type_hints["spec"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
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
        if id is not None:
            self._values["id"] = id
        if spec is not None:
            self._values["spec"] = spec
        if timeouts is not None:
            self._values["timeouts"] = timeouts

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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#name OnlineTable#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#id OnlineTable#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spec(self) -> typing.Optional["OnlineTableSpec"]:
        '''spec block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#spec OnlineTable#spec}
        '''
        result = self._values.get("spec")
        return typing.cast(typing.Optional["OnlineTableSpec"], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["OnlineTableTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#timeouts OnlineTable#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["OnlineTableTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OnlineTableConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableSpec",
    jsii_struct_bases=[],
    name_mapping={
        "perform_full_copy": "performFullCopy",
        "primary_key_columns": "primaryKeyColumns",
        "run_continuously": "runContinuously",
        "run_triggered": "runTriggered",
        "source_table_full_name": "sourceTableFullName",
        "timeseries_key": "timeseriesKey",
    },
)
class OnlineTableSpec:
    def __init__(
        self,
        *,
        perform_full_copy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        primary_key_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        run_continuously: typing.Optional[typing.Union["OnlineTableSpecRunContinuously", typing.Dict[builtins.str, typing.Any]]] = None,
        run_triggered: typing.Optional[typing.Union["OnlineTableSpecRunTriggered", typing.Dict[builtins.str, typing.Any]]] = None,
        source_table_full_name: typing.Optional[builtins.str] = None,
        timeseries_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param perform_full_copy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#perform_full_copy OnlineTable#perform_full_copy}.
        :param primary_key_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#primary_key_columns OnlineTable#primary_key_columns}.
        :param run_continuously: run_continuously block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#run_continuously OnlineTable#run_continuously}
        :param run_triggered: run_triggered block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#run_triggered OnlineTable#run_triggered}
        :param source_table_full_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#source_table_full_name OnlineTable#source_table_full_name}.
        :param timeseries_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#timeseries_key OnlineTable#timeseries_key}.
        '''
        if isinstance(run_continuously, dict):
            run_continuously = OnlineTableSpecRunContinuously(**run_continuously)
        if isinstance(run_triggered, dict):
            run_triggered = OnlineTableSpecRunTriggered(**run_triggered)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbf59fe27eb8845f54f6f77d30e70f050a5c7fa7a5f26b55f0ce31a77c4633d4)
            check_type(argname="argument perform_full_copy", value=perform_full_copy, expected_type=type_hints["perform_full_copy"])
            check_type(argname="argument primary_key_columns", value=primary_key_columns, expected_type=type_hints["primary_key_columns"])
            check_type(argname="argument run_continuously", value=run_continuously, expected_type=type_hints["run_continuously"])
            check_type(argname="argument run_triggered", value=run_triggered, expected_type=type_hints["run_triggered"])
            check_type(argname="argument source_table_full_name", value=source_table_full_name, expected_type=type_hints["source_table_full_name"])
            check_type(argname="argument timeseries_key", value=timeseries_key, expected_type=type_hints["timeseries_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if perform_full_copy is not None:
            self._values["perform_full_copy"] = perform_full_copy
        if primary_key_columns is not None:
            self._values["primary_key_columns"] = primary_key_columns
        if run_continuously is not None:
            self._values["run_continuously"] = run_continuously
        if run_triggered is not None:
            self._values["run_triggered"] = run_triggered
        if source_table_full_name is not None:
            self._values["source_table_full_name"] = source_table_full_name
        if timeseries_key is not None:
            self._values["timeseries_key"] = timeseries_key

    @builtins.property
    def perform_full_copy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#perform_full_copy OnlineTable#perform_full_copy}.'''
        result = self._values.get("perform_full_copy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def primary_key_columns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#primary_key_columns OnlineTable#primary_key_columns}.'''
        result = self._values.get("primary_key_columns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def run_continuously(self) -> typing.Optional["OnlineTableSpecRunContinuously"]:
        '''run_continuously block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#run_continuously OnlineTable#run_continuously}
        '''
        result = self._values.get("run_continuously")
        return typing.cast(typing.Optional["OnlineTableSpecRunContinuously"], result)

    @builtins.property
    def run_triggered(self) -> typing.Optional["OnlineTableSpecRunTriggered"]:
        '''run_triggered block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#run_triggered OnlineTable#run_triggered}
        '''
        result = self._values.get("run_triggered")
        return typing.cast(typing.Optional["OnlineTableSpecRunTriggered"], result)

    @builtins.property
    def source_table_full_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#source_table_full_name OnlineTable#source_table_full_name}.'''
        result = self._values.get("source_table_full_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeseries_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#timeseries_key OnlineTable#timeseries_key}.'''
        result = self._values.get("timeseries_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OnlineTableSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OnlineTableSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c4a79b9cb2b6908fe67d8544cb00d8c8e5cb3e82ac6ffc7167944bcf129a0126)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putRunContinuously")
    def put_run_continuously(self) -> None:
        value = OnlineTableSpecRunContinuously()

        return typing.cast(None, jsii.invoke(self, "putRunContinuously", [value]))

    @jsii.member(jsii_name="putRunTriggered")
    def put_run_triggered(self) -> None:
        value = OnlineTableSpecRunTriggered()

        return typing.cast(None, jsii.invoke(self, "putRunTriggered", [value]))

    @jsii.member(jsii_name="resetPerformFullCopy")
    def reset_perform_full_copy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPerformFullCopy", []))

    @jsii.member(jsii_name="resetPrimaryKeyColumns")
    def reset_primary_key_columns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrimaryKeyColumns", []))

    @jsii.member(jsii_name="resetRunContinuously")
    def reset_run_continuously(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunContinuously", []))

    @jsii.member(jsii_name="resetRunTriggered")
    def reset_run_triggered(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunTriggered", []))

    @jsii.member(jsii_name="resetSourceTableFullName")
    def reset_source_table_full_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceTableFullName", []))

    @jsii.member(jsii_name="resetTimeseriesKey")
    def reset_timeseries_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeseriesKey", []))

    @builtins.property
    @jsii.member(jsii_name="pipelineId")
    def pipeline_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pipelineId"))

    @builtins.property
    @jsii.member(jsii_name="runContinuously")
    def run_continuously(self) -> "OnlineTableSpecRunContinuouslyOutputReference":
        return typing.cast("OnlineTableSpecRunContinuouslyOutputReference", jsii.get(self, "runContinuously"))

    @builtins.property
    @jsii.member(jsii_name="runTriggered")
    def run_triggered(self) -> "OnlineTableSpecRunTriggeredOutputReference":
        return typing.cast("OnlineTableSpecRunTriggeredOutputReference", jsii.get(self, "runTriggered"))

    @builtins.property
    @jsii.member(jsii_name="performFullCopyInput")
    def perform_full_copy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "performFullCopyInput"))

    @builtins.property
    @jsii.member(jsii_name="primaryKeyColumnsInput")
    def primary_key_columns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "primaryKeyColumnsInput"))

    @builtins.property
    @jsii.member(jsii_name="runContinuouslyInput")
    def run_continuously_input(
        self,
    ) -> typing.Optional["OnlineTableSpecRunContinuously"]:
        return typing.cast(typing.Optional["OnlineTableSpecRunContinuously"], jsii.get(self, "runContinuouslyInput"))

    @builtins.property
    @jsii.member(jsii_name="runTriggeredInput")
    def run_triggered_input(self) -> typing.Optional["OnlineTableSpecRunTriggered"]:
        return typing.cast(typing.Optional["OnlineTableSpecRunTriggered"], jsii.get(self, "runTriggeredInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceTableFullNameInput")
    def source_table_full_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceTableFullNameInput"))

    @builtins.property
    @jsii.member(jsii_name="timeseriesKeyInput")
    def timeseries_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timeseriesKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="performFullCopy")
    def perform_full_copy(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "performFullCopy"))

    @perform_full_copy.setter
    def perform_full_copy(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f4d9d371a82b586dba871ac38d9e63838afe4b66e4e625d47f4e9bbd1ec6d44)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "performFullCopy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="primaryKeyColumns")
    def primary_key_columns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "primaryKeyColumns"))

    @primary_key_columns.setter
    def primary_key_columns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d57a2a5960a7c9dc1bb667f372b4a92561ae3ff51ff681d430cd2dbf231f92d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "primaryKeyColumns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceTableFullName")
    def source_table_full_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceTableFullName"))

    @source_table_full_name.setter
    def source_table_full_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75209609e8bd2d8320ba8b16befcc41632d83214f4d9ba65526d3924012ba4a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceTableFullName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeseriesKey")
    def timeseries_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeseriesKey"))

    @timeseries_key.setter
    def timeseries_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b81c6040f90cd42f6042b85219111adf4d314c5acc1b47cb51684a26d0694667)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeseriesKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OnlineTableSpec]:
        return typing.cast(typing.Optional[OnlineTableSpec], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[OnlineTableSpec]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a58cc1a14bb1694cf218fcae8aa860e236fe3ce08930164f58fed033a25cc5ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableSpecRunContinuously",
    jsii_struct_bases=[],
    name_mapping={},
)
class OnlineTableSpecRunContinuously:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OnlineTableSpecRunContinuously(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OnlineTableSpecRunContinuouslyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableSpecRunContinuouslyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__195a80f8e297fbf10d776b3e3d4585e0ba17fb5f41ab07ed2e0a312134355309)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OnlineTableSpecRunContinuously]:
        return typing.cast(typing.Optional[OnlineTableSpecRunContinuously], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OnlineTableSpecRunContinuously],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0ac6ee496655f79f2d0dedd6c2881c07a8ec95d4b8de7e59ebba69fdbae7b8c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableSpecRunTriggered",
    jsii_struct_bases=[],
    name_mapping={},
)
class OnlineTableSpecRunTriggered:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OnlineTableSpecRunTriggered(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OnlineTableSpecRunTriggeredOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableSpecRunTriggeredOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6664e9e69039354f910373742f87117e142f3b3d2d9c18f2f30ebfa99dc7d16b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OnlineTableSpecRunTriggered]:
        return typing.cast(typing.Optional[OnlineTableSpecRunTriggered], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OnlineTableSpecRunTriggered],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c7bc5e4dc5adf8a55342a9fa5a00a2ac1c3661c23362fc8aaa915592a6d60b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class OnlineTableStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OnlineTableStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableStatusContinuousUpdateStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class OnlineTableStatusContinuousUpdateStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OnlineTableStatusContinuousUpdateStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableStatusContinuousUpdateStatusInitialPipelineSyncProgress",
    jsii_struct_bases=[],
    name_mapping={},
)
class OnlineTableStatusContinuousUpdateStatusInitialPipelineSyncProgress:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OnlineTableStatusContinuousUpdateStatusInitialPipelineSyncProgress(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OnlineTableStatusContinuousUpdateStatusInitialPipelineSyncProgressList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableStatusContinuousUpdateStatusInitialPipelineSyncProgressList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d0a3ece67db4497ed67f41dfdcaba5a440f9b1455cbcc9a41c57a8bb4d81919f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OnlineTableStatusContinuousUpdateStatusInitialPipelineSyncProgressOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3638c07db8a63ecfb8b319045cad201c5f829d5551fac9287ac71c7095797cdc)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OnlineTableStatusContinuousUpdateStatusInitialPipelineSyncProgressOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbf6b994367114290c7773095eabafa6f0cbe1a513798417f7f5c39ab5337bb7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d36f8dcd7ce9e08cc19e588ecd360725d67cbe069c21d2100568cf525da7986a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7f3d1e65eba5e4311b58b34d1cfadf0ccadb78bd034183fd78d2c0081376c7ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class OnlineTableStatusContinuousUpdateStatusInitialPipelineSyncProgressOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableStatusContinuousUpdateStatusInitialPipelineSyncProgressOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__37b60522c947a881edadb10f5d81c77e0e5e82650a98e89939243c7e7127653d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="estimatedCompletionTimeSeconds")
    def estimated_completion_time_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "estimatedCompletionTimeSeconds"))

    @builtins.property
    @jsii.member(jsii_name="latestVersionCurrentlyProcessing")
    def latest_version_currently_processing(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "latestVersionCurrentlyProcessing"))

    @builtins.property
    @jsii.member(jsii_name="syncedRowCount")
    def synced_row_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "syncedRowCount"))

    @builtins.property
    @jsii.member(jsii_name="syncProgressCompletion")
    def sync_progress_completion(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "syncProgressCompletion"))

    @builtins.property
    @jsii.member(jsii_name="totalRowCount")
    def total_row_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "totalRowCount"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OnlineTableStatusContinuousUpdateStatusInitialPipelineSyncProgress]:
        return typing.cast(typing.Optional[OnlineTableStatusContinuousUpdateStatusInitialPipelineSyncProgress], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OnlineTableStatusContinuousUpdateStatusInitialPipelineSyncProgress],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c092da377a9f2d730dd7517bfb1a4e2c34726468d09526070b059a7a171d37d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OnlineTableStatusContinuousUpdateStatusList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableStatusContinuousUpdateStatusList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ab032e44c7aed681cce0617036495610d360f6cd65b9d513637f652c1a83c979)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OnlineTableStatusContinuousUpdateStatusOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f3b97a183568deafe652d0a229f3354f0995b3a8a3ee2dd94e8d2814dcbc26c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OnlineTableStatusContinuousUpdateStatusOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3b08e2d834eafd9ceb914d9c66f668d4451e6f8f3e451dfdd085ade1ad595e6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e98dd85f7ca0f05ee7f09dadbe426abdfe8638f675eb0b2dca1e6aa740131128)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7dbb8ef48237ce3667ce75e30294877e094b1782b7fba4bc48343b80f366d5e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class OnlineTableStatusContinuousUpdateStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableStatusContinuousUpdateStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dcde011f3d77dca567139a5341259b36584067d884e457e4f23f67ba217d148e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="initialPipelineSyncProgress")
    def initial_pipeline_sync_progress(
        self,
    ) -> OnlineTableStatusContinuousUpdateStatusInitialPipelineSyncProgressList:
        return typing.cast(OnlineTableStatusContinuousUpdateStatusInitialPipelineSyncProgressList, jsii.get(self, "initialPipelineSyncProgress"))

    @builtins.property
    @jsii.member(jsii_name="lastProcessedCommitVersion")
    def last_processed_commit_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lastProcessedCommitVersion"))

    @builtins.property
    @jsii.member(jsii_name="timestamp")
    def timestamp(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timestamp"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OnlineTableStatusContinuousUpdateStatus]:
        return typing.cast(typing.Optional[OnlineTableStatusContinuousUpdateStatus], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OnlineTableStatusContinuousUpdateStatus],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fdb41bb6f8691b47391a9b240e164c4f91ab88fa66fc6342e5b33c0380f96dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableStatusFailedStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class OnlineTableStatusFailedStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OnlineTableStatusFailedStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OnlineTableStatusFailedStatusList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableStatusFailedStatusList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__846a25deffed53932c167328fa0c8daeb9938282862cb03ecf31cee229ab43cb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "OnlineTableStatusFailedStatusOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__128ba04dd43a15d64935d23f852299e8a0914c3c0ca6cad4e35618fd4e4c9cd5)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OnlineTableStatusFailedStatusOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af8af02c77a3ed1038fcf41d9db893bd705806a315e6ff6a94e075a03a898072)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ac218c577f89e4f194565500906c8e20f293450ebee14252e5133c2aacec56fe)
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
            type_hints = typing.get_type_hints(_typecheckingstub__063cf235d433a79985c8180e8707b1de55473ebb4d8416c1006dcbb76912e0cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class OnlineTableStatusFailedStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableStatusFailedStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c91bc9a03fe45a74c15a8d0f756adaa982760a898902c67792cc100f7b06a906)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="lastProcessedCommitVersion")
    def last_processed_commit_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lastProcessedCommitVersion"))

    @builtins.property
    @jsii.member(jsii_name="timestamp")
    def timestamp(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timestamp"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OnlineTableStatusFailedStatus]:
        return typing.cast(typing.Optional[OnlineTableStatusFailedStatus], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OnlineTableStatusFailedStatus],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8616ef33bc8c3401e29c9fc1cbadfbe5ab3b76e3155d46904b6487319acec4d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OnlineTableStatusList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableStatusList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3570a065f973c8606b8328a0d5e6ac29b79966aaf624001b8374aa265337a460)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "OnlineTableStatusOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9c1504e98f79dfbc2bc4ca492a6ac59e2756638dabe41307bc608b0071f238a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OnlineTableStatusOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2dcd76eb96c661d1f2ec02b224826c5113b32e54f9382b998e14d8aab6f791a8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__17bc485fd0939566038e02e819b8b5d80740c523d9ef7e25453998dfb3291076)
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
            type_hints = typing.get_type_hints(_typecheckingstub__105570f54f668e0db515a544b3fcf6af40fc508e81c970012341b7550b668163)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class OnlineTableStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__aeaa0a4a041d33943bdf5039ad9f51ce33f4e1264e573e5abd35c79ed8d543e6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="continuousUpdateStatus")
    def continuous_update_status(self) -> OnlineTableStatusContinuousUpdateStatusList:
        return typing.cast(OnlineTableStatusContinuousUpdateStatusList, jsii.get(self, "continuousUpdateStatus"))

    @builtins.property
    @jsii.member(jsii_name="detailedState")
    def detailed_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "detailedState"))

    @builtins.property
    @jsii.member(jsii_name="failedStatus")
    def failed_status(self) -> OnlineTableStatusFailedStatusList:
        return typing.cast(OnlineTableStatusFailedStatusList, jsii.get(self, "failedStatus"))

    @builtins.property
    @jsii.member(jsii_name="message")
    def message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "message"))

    @builtins.property
    @jsii.member(jsii_name="provisioningStatus")
    def provisioning_status(self) -> "OnlineTableStatusProvisioningStatusList":
        return typing.cast("OnlineTableStatusProvisioningStatusList", jsii.get(self, "provisioningStatus"))

    @builtins.property
    @jsii.member(jsii_name="triggeredUpdateStatus")
    def triggered_update_status(self) -> "OnlineTableStatusTriggeredUpdateStatusList":
        return typing.cast("OnlineTableStatusTriggeredUpdateStatusList", jsii.get(self, "triggeredUpdateStatus"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OnlineTableStatus]:
        return typing.cast(typing.Optional[OnlineTableStatus], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[OnlineTableStatus]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c510ff7d2875135505ea7f3b3547f8e23523b6b2c4475244fcc592917e49b542)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableStatusProvisioningStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class OnlineTableStatusProvisioningStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OnlineTableStatusProvisioningStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableStatusProvisioningStatusInitialPipelineSyncProgress",
    jsii_struct_bases=[],
    name_mapping={},
)
class OnlineTableStatusProvisioningStatusInitialPipelineSyncProgress:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OnlineTableStatusProvisioningStatusInitialPipelineSyncProgress(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OnlineTableStatusProvisioningStatusInitialPipelineSyncProgressList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableStatusProvisioningStatusInitialPipelineSyncProgressList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0ffa48f49796df85fd9b56a671a6716aa714a610eaa66251496a86e6198582fb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OnlineTableStatusProvisioningStatusInitialPipelineSyncProgressOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0d7420fe67ca2afcbb4d3399e9e30804b1206903d16fd925b3fea31fa6716d0)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OnlineTableStatusProvisioningStatusInitialPipelineSyncProgressOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5f80478b2be607ee137c7f5d4157434038d5315c96dc921e75f7485092965ce)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9ad1f1804144e523db76f018a00563866e20d0f28e5acec646015d23f83f10f6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f1ce86aab962979b821c276ac9f79268e75d5982b61b42cea941bc8370dd8142)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class OnlineTableStatusProvisioningStatusInitialPipelineSyncProgressOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableStatusProvisioningStatusInitialPipelineSyncProgressOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0ca1b7ebc02b03b8f2fa21727104fa1283da9c33a1c6ccf0b528c45a8088c81e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="estimatedCompletionTimeSeconds")
    def estimated_completion_time_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "estimatedCompletionTimeSeconds"))

    @builtins.property
    @jsii.member(jsii_name="latestVersionCurrentlyProcessing")
    def latest_version_currently_processing(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "latestVersionCurrentlyProcessing"))

    @builtins.property
    @jsii.member(jsii_name="syncedRowCount")
    def synced_row_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "syncedRowCount"))

    @builtins.property
    @jsii.member(jsii_name="syncProgressCompletion")
    def sync_progress_completion(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "syncProgressCompletion"))

    @builtins.property
    @jsii.member(jsii_name="totalRowCount")
    def total_row_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "totalRowCount"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OnlineTableStatusProvisioningStatusInitialPipelineSyncProgress]:
        return typing.cast(typing.Optional[OnlineTableStatusProvisioningStatusInitialPipelineSyncProgress], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OnlineTableStatusProvisioningStatusInitialPipelineSyncProgress],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b95e55000a72967bbc10fcec0fc9739c5d22fd88eeee52a0d7812ea79bd191c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OnlineTableStatusProvisioningStatusList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableStatusProvisioningStatusList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d6ecd0515dfac61a23fcdc8e5f5456759b267c76a855fb4d76f43ba22a7085dc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OnlineTableStatusProvisioningStatusOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b84856feb689ccdd4474842fd512aaf95553f35983c43daf3c08f635e2f7fbd)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OnlineTableStatusProvisioningStatusOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__929b04b699d880e147ee97f5b55e207e5ea650bcdebf5be83fc1a7f764a4c79a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2b5fa27d817a9ee76001a89c7704dc3855bf8a901ffb9c1862ca390c372fdf5f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__78329b329d71daf54339fa450c9fc0e0b5cf8bbd2f21211001de5b981012dfdd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class OnlineTableStatusProvisioningStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableStatusProvisioningStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__499439bb0975a6e5dc999b2449510d8838263f11d89ebd8eaa7312ffeafa4064)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="initialPipelineSyncProgress")
    def initial_pipeline_sync_progress(
        self,
    ) -> OnlineTableStatusProvisioningStatusInitialPipelineSyncProgressList:
        return typing.cast(OnlineTableStatusProvisioningStatusInitialPipelineSyncProgressList, jsii.get(self, "initialPipelineSyncProgress"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OnlineTableStatusProvisioningStatus]:
        return typing.cast(typing.Optional[OnlineTableStatusProvisioningStatus], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OnlineTableStatusProvisioningStatus],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b089e9b8e7e7d208e32faae3e964caf56d7552beccf43dbdafd2393e40f23662)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableStatusTriggeredUpdateStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class OnlineTableStatusTriggeredUpdateStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OnlineTableStatusTriggeredUpdateStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OnlineTableStatusTriggeredUpdateStatusList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableStatusTriggeredUpdateStatusList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0049fe4b91253dac2918854a332d10a5c34d17b119f53ec0b9e0723f403a25f4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OnlineTableStatusTriggeredUpdateStatusOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b79605870999f806c189be50ead3f750408c1107d0e8b9b3725f984d3d332882)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OnlineTableStatusTriggeredUpdateStatusOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5cf7d52e86d6ba129eb9c48ca23bd576aeba36214d067f9f215e6e351f4eea66)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6cd3b1183eff2c9ba7559b0924da5bc2c14de37753bdbd9c99a549106d2407af)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0cbc7501c12a89cd51d9eb5daf017b2d09294509cc18abddcf6720fc68729819)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class OnlineTableStatusTriggeredUpdateStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableStatusTriggeredUpdateStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7156cec948a1321fa0b763aa6ccd2d8e66883ba4c225bd9ec62b10c05fe9324e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="lastProcessedCommitVersion")
    def last_processed_commit_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lastProcessedCommitVersion"))

    @builtins.property
    @jsii.member(jsii_name="timestamp")
    def timestamp(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timestamp"))

    @builtins.property
    @jsii.member(jsii_name="triggeredUpdateProgress")
    def triggered_update_progress(
        self,
    ) -> "OnlineTableStatusTriggeredUpdateStatusTriggeredUpdateProgressList":
        return typing.cast("OnlineTableStatusTriggeredUpdateStatusTriggeredUpdateProgressList", jsii.get(self, "triggeredUpdateProgress"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OnlineTableStatusTriggeredUpdateStatus]:
        return typing.cast(typing.Optional[OnlineTableStatusTriggeredUpdateStatus], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OnlineTableStatusTriggeredUpdateStatus],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1fb685505ed103ac402cf13aa9ad79f34b7a413210df12555eb36279b7527e7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableStatusTriggeredUpdateStatusTriggeredUpdateProgress",
    jsii_struct_bases=[],
    name_mapping={},
)
class OnlineTableStatusTriggeredUpdateStatusTriggeredUpdateProgress:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OnlineTableStatusTriggeredUpdateStatusTriggeredUpdateProgress(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OnlineTableStatusTriggeredUpdateStatusTriggeredUpdateProgressList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableStatusTriggeredUpdateStatusTriggeredUpdateProgressList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__be427b6a471dc7f6bb1cd8e3ad0a3c21c1a6c49b321b8d3074b383de1d225e86)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OnlineTableStatusTriggeredUpdateStatusTriggeredUpdateProgressOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b06bd7ab57ff57501bee1d42c57ca6e213832360354ac96b4e716aa4731b254d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OnlineTableStatusTriggeredUpdateStatusTriggeredUpdateProgressOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e628ca1c3a84363b48604727004820d77bb5040c9f3ddff7752da7c9e75c4be2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e9489b3be114e8fad10415c91612419b175dcafb193fae2af51c7104496a972f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__70a1916edd5a439147b7d429495be8d438aaeefe1df04df53262c20923b2e8a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class OnlineTableStatusTriggeredUpdateStatusTriggeredUpdateProgressOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableStatusTriggeredUpdateStatusTriggeredUpdateProgressOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5a0752e7ee62c0c4c1a9f08946c9d3dee91fc0202c09f9a50c98699374475c48)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="estimatedCompletionTimeSeconds")
    def estimated_completion_time_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "estimatedCompletionTimeSeconds"))

    @builtins.property
    @jsii.member(jsii_name="latestVersionCurrentlyProcessing")
    def latest_version_currently_processing(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "latestVersionCurrentlyProcessing"))

    @builtins.property
    @jsii.member(jsii_name="syncedRowCount")
    def synced_row_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "syncedRowCount"))

    @builtins.property
    @jsii.member(jsii_name="syncProgressCompletion")
    def sync_progress_completion(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "syncProgressCompletion"))

    @builtins.property
    @jsii.member(jsii_name="totalRowCount")
    def total_row_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "totalRowCount"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OnlineTableStatusTriggeredUpdateStatusTriggeredUpdateProgress]:
        return typing.cast(typing.Optional[OnlineTableStatusTriggeredUpdateStatusTriggeredUpdateProgress], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OnlineTableStatusTriggeredUpdateStatusTriggeredUpdateProgress],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__909bf46f41305a47b0bb57997551a79b23dbad0813645a91c08ad7e7d4faf518)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create"},
)
class OnlineTableTimeouts:
    def __init__(self, *, create: typing.Optional[builtins.str] = None) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#create OnlineTable#create}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcffe72bf70eee6c4fa80aeaa50de557505acc1f1d4fcbd603e24f9c28f1f9b9)
            check_type(argname="argument create", value=create, expected_type=type_hints["create"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/online_table#create OnlineTable#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OnlineTableTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OnlineTableTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.onlineTable.OnlineTableTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__30712e5fc684e7060be875a9e90e89769ffe521b50b54b6995eeead3f5024f0b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @builtins.property
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a7be0fcb6eb365ab7f51d5097954d3b03dd0b4c2dc2ff6b3ace99988932d8a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OnlineTableTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OnlineTableTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OnlineTableTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6285a22818d22992f998dbcff1292e9f6b68ddb4182546847149ba3a34276600)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "OnlineTable",
    "OnlineTableConfig",
    "OnlineTableSpec",
    "OnlineTableSpecOutputReference",
    "OnlineTableSpecRunContinuously",
    "OnlineTableSpecRunContinuouslyOutputReference",
    "OnlineTableSpecRunTriggered",
    "OnlineTableSpecRunTriggeredOutputReference",
    "OnlineTableStatus",
    "OnlineTableStatusContinuousUpdateStatus",
    "OnlineTableStatusContinuousUpdateStatusInitialPipelineSyncProgress",
    "OnlineTableStatusContinuousUpdateStatusInitialPipelineSyncProgressList",
    "OnlineTableStatusContinuousUpdateStatusInitialPipelineSyncProgressOutputReference",
    "OnlineTableStatusContinuousUpdateStatusList",
    "OnlineTableStatusContinuousUpdateStatusOutputReference",
    "OnlineTableStatusFailedStatus",
    "OnlineTableStatusFailedStatusList",
    "OnlineTableStatusFailedStatusOutputReference",
    "OnlineTableStatusList",
    "OnlineTableStatusOutputReference",
    "OnlineTableStatusProvisioningStatus",
    "OnlineTableStatusProvisioningStatusInitialPipelineSyncProgress",
    "OnlineTableStatusProvisioningStatusInitialPipelineSyncProgressList",
    "OnlineTableStatusProvisioningStatusInitialPipelineSyncProgressOutputReference",
    "OnlineTableStatusProvisioningStatusList",
    "OnlineTableStatusProvisioningStatusOutputReference",
    "OnlineTableStatusTriggeredUpdateStatus",
    "OnlineTableStatusTriggeredUpdateStatusList",
    "OnlineTableStatusTriggeredUpdateStatusOutputReference",
    "OnlineTableStatusTriggeredUpdateStatusTriggeredUpdateProgress",
    "OnlineTableStatusTriggeredUpdateStatusTriggeredUpdateProgressList",
    "OnlineTableStatusTriggeredUpdateStatusTriggeredUpdateProgressOutputReference",
    "OnlineTableTimeouts",
    "OnlineTableTimeoutsOutputReference",
]

publication.publish()

def _typecheckingstub__27c06822f3f60b687daf57df13eb2b83d2728eee5fa660afdf453be352d0aa47(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    id: typing.Optional[builtins.str] = None,
    spec: typing.Optional[typing.Union[OnlineTableSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    timeouts: typing.Optional[typing.Union[OnlineTableTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__dcca8e128ee248e68ced102a11111bc0cc83f8bc4d620ddaa491012a7bcee551(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5eb7cfecf51a0ac5bbe0085ae4497824b11bca30b5c9e929e208d18a8a4807c1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e107276014a6be8f7fcae2aa5cf48f1bc9e290b1afe79d5e6828a0c0d5c48259(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a3767cc98d57ab0d09715fb8bd46bc42450df671a1fdf21e3bb40d5b8795e6a(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    id: typing.Optional[builtins.str] = None,
    spec: typing.Optional[typing.Union[OnlineTableSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    timeouts: typing.Optional[typing.Union[OnlineTableTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbf59fe27eb8845f54f6f77d30e70f050a5c7fa7a5f26b55f0ce31a77c4633d4(
    *,
    perform_full_copy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    primary_key_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
    run_continuously: typing.Optional[typing.Union[OnlineTableSpecRunContinuously, typing.Dict[builtins.str, typing.Any]]] = None,
    run_triggered: typing.Optional[typing.Union[OnlineTableSpecRunTriggered, typing.Dict[builtins.str, typing.Any]]] = None,
    source_table_full_name: typing.Optional[builtins.str] = None,
    timeseries_key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4a79b9cb2b6908fe67d8544cb00d8c8e5cb3e82ac6ffc7167944bcf129a0126(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f4d9d371a82b586dba871ac38d9e63838afe4b66e4e625d47f4e9bbd1ec6d44(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d57a2a5960a7c9dc1bb667f372b4a92561ae3ff51ff681d430cd2dbf231f92d(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75209609e8bd2d8320ba8b16befcc41632d83214f4d9ba65526d3924012ba4a1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b81c6040f90cd42f6042b85219111adf4d314c5acc1b47cb51684a26d0694667(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a58cc1a14bb1694cf218fcae8aa860e236fe3ce08930164f58fed033a25cc5ca(
    value: typing.Optional[OnlineTableSpec],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__195a80f8e297fbf10d776b3e3d4585e0ba17fb5f41ab07ed2e0a312134355309(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0ac6ee496655f79f2d0dedd6c2881c07a8ec95d4b8de7e59ebba69fdbae7b8c(
    value: typing.Optional[OnlineTableSpecRunContinuously],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6664e9e69039354f910373742f87117e142f3b3d2d9c18f2f30ebfa99dc7d16b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c7bc5e4dc5adf8a55342a9fa5a00a2ac1c3661c23362fc8aaa915592a6d60b1(
    value: typing.Optional[OnlineTableSpecRunTriggered],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0a3ece67db4497ed67f41dfdcaba5a440f9b1455cbcc9a41c57a8bb4d81919f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3638c07db8a63ecfb8b319045cad201c5f829d5551fac9287ac71c7095797cdc(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbf6b994367114290c7773095eabafa6f0cbe1a513798417f7f5c39ab5337bb7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d36f8dcd7ce9e08cc19e588ecd360725d67cbe069c21d2100568cf525da7986a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f3d1e65eba5e4311b58b34d1cfadf0ccadb78bd034183fd78d2c0081376c7ee(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37b60522c947a881edadb10f5d81c77e0e5e82650a98e89939243c7e7127653d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c092da377a9f2d730dd7517bfb1a4e2c34726468d09526070b059a7a171d37d(
    value: typing.Optional[OnlineTableStatusContinuousUpdateStatusInitialPipelineSyncProgress],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab032e44c7aed681cce0617036495610d360f6cd65b9d513637f652c1a83c979(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f3b97a183568deafe652d0a229f3354f0995b3a8a3ee2dd94e8d2814dcbc26c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3b08e2d834eafd9ceb914d9c66f668d4451e6f8f3e451dfdd085ade1ad595e6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e98dd85f7ca0f05ee7f09dadbe426abdfe8638f675eb0b2dca1e6aa740131128(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7dbb8ef48237ce3667ce75e30294877e094b1782b7fba4bc48343b80f366d5e2(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcde011f3d77dca567139a5341259b36584067d884e457e4f23f67ba217d148e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fdb41bb6f8691b47391a9b240e164c4f91ab88fa66fc6342e5b33c0380f96dc(
    value: typing.Optional[OnlineTableStatusContinuousUpdateStatus],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__846a25deffed53932c167328fa0c8daeb9938282862cb03ecf31cee229ab43cb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__128ba04dd43a15d64935d23f852299e8a0914c3c0ca6cad4e35618fd4e4c9cd5(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af8af02c77a3ed1038fcf41d9db893bd705806a315e6ff6a94e075a03a898072(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac218c577f89e4f194565500906c8e20f293450ebee14252e5133c2aacec56fe(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__063cf235d433a79985c8180e8707b1de55473ebb4d8416c1006dcbb76912e0cc(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c91bc9a03fe45a74c15a8d0f756adaa982760a898902c67792cc100f7b06a906(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8616ef33bc8c3401e29c9fc1cbadfbe5ab3b76e3155d46904b6487319acec4d(
    value: typing.Optional[OnlineTableStatusFailedStatus],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3570a065f973c8606b8328a0d5e6ac29b79966aaf624001b8374aa265337a460(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9c1504e98f79dfbc2bc4ca492a6ac59e2756638dabe41307bc608b0071f238a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2dcd76eb96c661d1f2ec02b224826c5113b32e54f9382b998e14d8aab6f791a8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17bc485fd0939566038e02e819b8b5d80740c523d9ef7e25453998dfb3291076(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__105570f54f668e0db515a544b3fcf6af40fc508e81c970012341b7550b668163(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aeaa0a4a041d33943bdf5039ad9f51ce33f4e1264e573e5abd35c79ed8d543e6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c510ff7d2875135505ea7f3b3547f8e23523b6b2c4475244fcc592917e49b542(
    value: typing.Optional[OnlineTableStatus],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ffa48f49796df85fd9b56a671a6716aa714a610eaa66251496a86e6198582fb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0d7420fe67ca2afcbb4d3399e9e30804b1206903d16fd925b3fea31fa6716d0(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5f80478b2be607ee137c7f5d4157434038d5315c96dc921e75f7485092965ce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ad1f1804144e523db76f018a00563866e20d0f28e5acec646015d23f83f10f6(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1ce86aab962979b821c276ac9f79268e75d5982b61b42cea941bc8370dd8142(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ca1b7ebc02b03b8f2fa21727104fa1283da9c33a1c6ccf0b528c45a8088c81e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b95e55000a72967bbc10fcec0fc9739c5d22fd88eeee52a0d7812ea79bd191c(
    value: typing.Optional[OnlineTableStatusProvisioningStatusInitialPipelineSyncProgress],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6ecd0515dfac61a23fcdc8e5f5456759b267c76a855fb4d76f43ba22a7085dc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b84856feb689ccdd4474842fd512aaf95553f35983c43daf3c08f635e2f7fbd(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__929b04b699d880e147ee97f5b55e207e5ea650bcdebf5be83fc1a7f764a4c79a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b5fa27d817a9ee76001a89c7704dc3855bf8a901ffb9c1862ca390c372fdf5f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78329b329d71daf54339fa450c9fc0e0b5cf8bbd2f21211001de5b981012dfdd(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__499439bb0975a6e5dc999b2449510d8838263f11d89ebd8eaa7312ffeafa4064(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b089e9b8e7e7d208e32faae3e964caf56d7552beccf43dbdafd2393e40f23662(
    value: typing.Optional[OnlineTableStatusProvisioningStatus],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0049fe4b91253dac2918854a332d10a5c34d17b119f53ec0b9e0723f403a25f4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b79605870999f806c189be50ead3f750408c1107d0e8b9b3725f984d3d332882(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5cf7d52e86d6ba129eb9c48ca23bd576aeba36214d067f9f215e6e351f4eea66(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cd3b1183eff2c9ba7559b0924da5bc2c14de37753bdbd9c99a549106d2407af(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cbc7501c12a89cd51d9eb5daf017b2d09294509cc18abddcf6720fc68729819(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7156cec948a1321fa0b763aa6ccd2d8e66883ba4c225bd9ec62b10c05fe9324e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fb685505ed103ac402cf13aa9ad79f34b7a413210df12555eb36279b7527e7a(
    value: typing.Optional[OnlineTableStatusTriggeredUpdateStatus],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be427b6a471dc7f6bb1cd8e3ad0a3c21c1a6c49b321b8d3074b383de1d225e86(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b06bd7ab57ff57501bee1d42c57ca6e213832360354ac96b4e716aa4731b254d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e628ca1c3a84363b48604727004820d77bb5040c9f3ddff7752da7c9e75c4be2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9489b3be114e8fad10415c91612419b175dcafb193fae2af51c7104496a972f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70a1916edd5a439147b7d429495be8d438aaeefe1df04df53262c20923b2e8a6(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a0752e7ee62c0c4c1a9f08946c9d3dee91fc0202c09f9a50c98699374475c48(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__909bf46f41305a47b0bb57997551a79b23dbad0813645a91c08ad7e7d4faf518(
    value: typing.Optional[OnlineTableStatusTriggeredUpdateStatusTriggeredUpdateProgress],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcffe72bf70eee6c4fa80aeaa50de557505acc1f1d4fcbd603e24f9c28f1f9b9(
    *,
    create: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30712e5fc684e7060be875a9e90e89769ffe521b50b54b6995eeead3f5024f0b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a7be0fcb6eb365ab7f51d5097954d3b03dd0b4c2dc2ff6b3ace99988932d8a3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6285a22818d22992f998dbcff1292e9f6b68ddb4182546847149ba3a34276600(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OnlineTableTimeouts]],
) -> None:
    """Type checking stubs"""
    pass
