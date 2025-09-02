r'''
# `data_databricks_alerts_v2`

Refer to the Terraform Registry for docs: [`data_databricks_alerts_v2`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2).
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


class DataDatabricksAlertsV2(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertsV2.DataDatabricksAlertsV2",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2 databricks_alerts_v2}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        workspace_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2 databricks_alerts_v2} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#workspace_id DataDatabricksAlertsV2#workspace_id}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ca2e6aaba880dad183280c8634fa7ff8bafc5fa410023353064e47441de3ca3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataDatabricksAlertsV2Config(
            workspace_id=workspace_id,
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
        '''Generates CDKTF code for importing a DataDatabricksAlertsV2 resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDatabricksAlertsV2 to import.
        :param import_from_id: The id of the existing DataDatabricksAlertsV2 that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDatabricksAlertsV2 to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47439c8fc9a43b443fc6e8ee491c9c1e623a0c383ce734766dd63e3c246b5ea0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetWorkspaceId")
    def reset_workspace_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkspaceId", []))

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
    @jsii.member(jsii_name="results")
    def results(self) -> "DataDatabricksAlertsV2ResultsList":
        return typing.cast("DataDatabricksAlertsV2ResultsList", jsii.get(self, "results"))

    @builtins.property
    @jsii.member(jsii_name="workspaceIdInput")
    def workspace_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workspaceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="workspaceId")
    def workspace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceId"))

    @workspace_id.setter
    def workspace_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bdfb6a9a91846813d073937a433503d3c2de19d17098042388dfc11d3e363c62)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workspaceId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertsV2.DataDatabricksAlertsV2Config",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "workspace_id": "workspaceId",
    },
)
class DataDatabricksAlertsV2Config(_cdktf_9a9027ec.TerraformMetaArguments):
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
        workspace_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#workspace_id DataDatabricksAlertsV2#workspace_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__261e2ad0ea21e1b8b5e930d39fb31cdca9cdb69380384f3c9236b419f86ceb7b)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument workspace_id", value=workspace_id, expected_type=type_hints["workspace_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
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
        if workspace_id is not None:
            self._values["workspace_id"] = workspace_id

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
    def workspace_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#workspace_id DataDatabricksAlertsV2#workspace_id}.'''
        result = self._values.get("workspace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAlertsV2Config(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertsV2.DataDatabricksAlertsV2Results",
    jsii_struct_bases=[],
    name_mapping={
        "custom_description": "customDescription",
        "custom_summary": "customSummary",
        "display_name": "displayName",
        "evaluation": "evaluation",
        "parent_path": "parentPath",
        "query_text": "queryText",
        "run_as": "runAs",
        "run_as_user_name": "runAsUserName",
        "schedule": "schedule",
        "warehouse_id": "warehouseId",
    },
)
class DataDatabricksAlertsV2Results:
    def __init__(
        self,
        *,
        custom_description: typing.Optional[builtins.str] = None,
        custom_summary: typing.Optional[builtins.str] = None,
        display_name: typing.Optional[builtins.str] = None,
        evaluation: typing.Optional[typing.Union["DataDatabricksAlertsV2ResultsEvaluation", typing.Dict[builtins.str, typing.Any]]] = None,
        parent_path: typing.Optional[builtins.str] = None,
        query_text: typing.Optional[builtins.str] = None,
        run_as: typing.Optional[typing.Union["DataDatabricksAlertsV2ResultsRunAs", typing.Dict[builtins.str, typing.Any]]] = None,
        run_as_user_name: typing.Optional[builtins.str] = None,
        schedule: typing.Optional[typing.Union["DataDatabricksAlertsV2ResultsSchedule", typing.Dict[builtins.str, typing.Any]]] = None,
        warehouse_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param custom_description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#custom_description DataDatabricksAlertsV2#custom_description}.
        :param custom_summary: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#custom_summary DataDatabricksAlertsV2#custom_summary}.
        :param display_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#display_name DataDatabricksAlertsV2#display_name}.
        :param evaluation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#evaluation DataDatabricksAlertsV2#evaluation}.
        :param parent_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#parent_path DataDatabricksAlertsV2#parent_path}.
        :param query_text: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#query_text DataDatabricksAlertsV2#query_text}.
        :param run_as: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#run_as DataDatabricksAlertsV2#run_as}.
        :param run_as_user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#run_as_user_name DataDatabricksAlertsV2#run_as_user_name}.
        :param schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#schedule DataDatabricksAlertsV2#schedule}.
        :param warehouse_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#warehouse_id DataDatabricksAlertsV2#warehouse_id}.
        '''
        if isinstance(evaluation, dict):
            evaluation = DataDatabricksAlertsV2ResultsEvaluation(**evaluation)
        if isinstance(run_as, dict):
            run_as = DataDatabricksAlertsV2ResultsRunAs(**run_as)
        if isinstance(schedule, dict):
            schedule = DataDatabricksAlertsV2ResultsSchedule(**schedule)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42de5896968e30f292293c6b33938c693c397a3be61b28dd6a2d766383b6b40d)
            check_type(argname="argument custom_description", value=custom_description, expected_type=type_hints["custom_description"])
            check_type(argname="argument custom_summary", value=custom_summary, expected_type=type_hints["custom_summary"])
            check_type(argname="argument display_name", value=display_name, expected_type=type_hints["display_name"])
            check_type(argname="argument evaluation", value=evaluation, expected_type=type_hints["evaluation"])
            check_type(argname="argument parent_path", value=parent_path, expected_type=type_hints["parent_path"])
            check_type(argname="argument query_text", value=query_text, expected_type=type_hints["query_text"])
            check_type(argname="argument run_as", value=run_as, expected_type=type_hints["run_as"])
            check_type(argname="argument run_as_user_name", value=run_as_user_name, expected_type=type_hints["run_as_user_name"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
            check_type(argname="argument warehouse_id", value=warehouse_id, expected_type=type_hints["warehouse_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if custom_description is not None:
            self._values["custom_description"] = custom_description
        if custom_summary is not None:
            self._values["custom_summary"] = custom_summary
        if display_name is not None:
            self._values["display_name"] = display_name
        if evaluation is not None:
            self._values["evaluation"] = evaluation
        if parent_path is not None:
            self._values["parent_path"] = parent_path
        if query_text is not None:
            self._values["query_text"] = query_text
        if run_as is not None:
            self._values["run_as"] = run_as
        if run_as_user_name is not None:
            self._values["run_as_user_name"] = run_as_user_name
        if schedule is not None:
            self._values["schedule"] = schedule
        if warehouse_id is not None:
            self._values["warehouse_id"] = warehouse_id

    @builtins.property
    def custom_description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#custom_description DataDatabricksAlertsV2#custom_description}.'''
        result = self._values.get("custom_description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_summary(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#custom_summary DataDatabricksAlertsV2#custom_summary}.'''
        result = self._values.get("custom_summary")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def display_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#display_name DataDatabricksAlertsV2#display_name}.'''
        result = self._values.get("display_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def evaluation(self) -> typing.Optional["DataDatabricksAlertsV2ResultsEvaluation"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#evaluation DataDatabricksAlertsV2#evaluation}.'''
        result = self._values.get("evaluation")
        return typing.cast(typing.Optional["DataDatabricksAlertsV2ResultsEvaluation"], result)

    @builtins.property
    def parent_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#parent_path DataDatabricksAlertsV2#parent_path}.'''
        result = self._values.get("parent_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def query_text(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#query_text DataDatabricksAlertsV2#query_text}.'''
        result = self._values.get("query_text")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def run_as(self) -> typing.Optional["DataDatabricksAlertsV2ResultsRunAs"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#run_as DataDatabricksAlertsV2#run_as}.'''
        result = self._values.get("run_as")
        return typing.cast(typing.Optional["DataDatabricksAlertsV2ResultsRunAs"], result)

    @builtins.property
    def run_as_user_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#run_as_user_name DataDatabricksAlertsV2#run_as_user_name}.'''
        result = self._values.get("run_as_user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def schedule(self) -> typing.Optional["DataDatabricksAlertsV2ResultsSchedule"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#schedule DataDatabricksAlertsV2#schedule}.'''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional["DataDatabricksAlertsV2ResultsSchedule"], result)

    @builtins.property
    def warehouse_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#warehouse_id DataDatabricksAlertsV2#warehouse_id}.'''
        result = self._values.get("warehouse_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAlertsV2Results(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertsV2.DataDatabricksAlertsV2ResultsEffectiveRunAs",
    jsii_struct_bases=[],
    name_mapping={
        "service_principal_name": "servicePrincipalName",
        "user_name": "userName",
    },
)
class DataDatabricksAlertsV2ResultsEffectiveRunAs:
    def __init__(
        self,
        *,
        service_principal_name: typing.Optional[builtins.str] = None,
        user_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param service_principal_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#service_principal_name DataDatabricksAlertsV2#service_principal_name}.
        :param user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#user_name DataDatabricksAlertsV2#user_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69f9ab68bc7e3b67e904fe350cb06c0885b3837702d289db6dc9e90aa5dfe12e)
            check_type(argname="argument service_principal_name", value=service_principal_name, expected_type=type_hints["service_principal_name"])
            check_type(argname="argument user_name", value=user_name, expected_type=type_hints["user_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if service_principal_name is not None:
            self._values["service_principal_name"] = service_principal_name
        if user_name is not None:
            self._values["user_name"] = user_name

    @builtins.property
    def service_principal_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#service_principal_name DataDatabricksAlertsV2#service_principal_name}.'''
        result = self._values.get("service_principal_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#user_name DataDatabricksAlertsV2#user_name}.'''
        result = self._values.get("user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAlertsV2ResultsEffectiveRunAs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAlertsV2ResultsEffectiveRunAsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertsV2.DataDatabricksAlertsV2ResultsEffectiveRunAsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5d6fa3e3e943dddb764de73ef10b0c18849160a351dc9dd0af32e00a86733003)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetServicePrincipalName")
    def reset_service_principal_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServicePrincipalName", []))

    @jsii.member(jsii_name="resetUserName")
    def reset_user_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserName", []))

    @builtins.property
    @jsii.member(jsii_name="servicePrincipalNameInput")
    def service_principal_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "servicePrincipalNameInput"))

    @builtins.property
    @jsii.member(jsii_name="userNameInput")
    def user_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userNameInput"))

    @builtins.property
    @jsii.member(jsii_name="servicePrincipalName")
    def service_principal_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "servicePrincipalName"))

    @service_principal_name.setter
    def service_principal_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__103ca2f1e77e15c5b28c48f69b38e1c9c2bcdb418081ecc4bc053a6fcdd7dc45)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "servicePrincipalName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userName"))

    @user_name.setter
    def user_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__201c2bc92953d99704607968a0e657368fd79c839bd40d381c41f5c56d0c24d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksAlertsV2ResultsEffectiveRunAs]:
        return typing.cast(typing.Optional[DataDatabricksAlertsV2ResultsEffectiveRunAs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksAlertsV2ResultsEffectiveRunAs],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf48cdb85dfd48ba98e105c0bc77d32704549619ea1681f5c4c8a942c1b6c5a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertsV2.DataDatabricksAlertsV2ResultsEvaluation",
    jsii_struct_bases=[],
    name_mapping={
        "comparison_operator": "comparisonOperator",
        "empty_result_state": "emptyResultState",
        "notification": "notification",
        "source": "source",
        "threshold": "threshold",
    },
)
class DataDatabricksAlertsV2ResultsEvaluation:
    def __init__(
        self,
        *,
        comparison_operator: typing.Optional[builtins.str] = None,
        empty_result_state: typing.Optional[builtins.str] = None,
        notification: typing.Optional[typing.Union["DataDatabricksAlertsV2ResultsEvaluationNotification", typing.Dict[builtins.str, typing.Any]]] = None,
        source: typing.Optional[typing.Union["DataDatabricksAlertsV2ResultsEvaluationSource", typing.Dict[builtins.str, typing.Any]]] = None,
        threshold: typing.Optional[typing.Union["DataDatabricksAlertsV2ResultsEvaluationThreshold", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param comparison_operator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#comparison_operator DataDatabricksAlertsV2#comparison_operator}.
        :param empty_result_state: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#empty_result_state DataDatabricksAlertsV2#empty_result_state}.
        :param notification: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#notification DataDatabricksAlertsV2#notification}.
        :param source: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#source DataDatabricksAlertsV2#source}.
        :param threshold: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#threshold DataDatabricksAlertsV2#threshold}.
        '''
        if isinstance(notification, dict):
            notification = DataDatabricksAlertsV2ResultsEvaluationNotification(**notification)
        if isinstance(source, dict):
            source = DataDatabricksAlertsV2ResultsEvaluationSource(**source)
        if isinstance(threshold, dict):
            threshold = DataDatabricksAlertsV2ResultsEvaluationThreshold(**threshold)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0641486685b601b064c91749b96039c2aa51a91eba771c5f6e1de642a7a449fa)
            check_type(argname="argument comparison_operator", value=comparison_operator, expected_type=type_hints["comparison_operator"])
            check_type(argname="argument empty_result_state", value=empty_result_state, expected_type=type_hints["empty_result_state"])
            check_type(argname="argument notification", value=notification, expected_type=type_hints["notification"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument threshold", value=threshold, expected_type=type_hints["threshold"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if comparison_operator is not None:
            self._values["comparison_operator"] = comparison_operator
        if empty_result_state is not None:
            self._values["empty_result_state"] = empty_result_state
        if notification is not None:
            self._values["notification"] = notification
        if source is not None:
            self._values["source"] = source
        if threshold is not None:
            self._values["threshold"] = threshold

    @builtins.property
    def comparison_operator(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#comparison_operator DataDatabricksAlertsV2#comparison_operator}.'''
        result = self._values.get("comparison_operator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def empty_result_state(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#empty_result_state DataDatabricksAlertsV2#empty_result_state}.'''
        result = self._values.get("empty_result_state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notification(
        self,
    ) -> typing.Optional["DataDatabricksAlertsV2ResultsEvaluationNotification"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#notification DataDatabricksAlertsV2#notification}.'''
        result = self._values.get("notification")
        return typing.cast(typing.Optional["DataDatabricksAlertsV2ResultsEvaluationNotification"], result)

    @builtins.property
    def source(
        self,
    ) -> typing.Optional["DataDatabricksAlertsV2ResultsEvaluationSource"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#source DataDatabricksAlertsV2#source}.'''
        result = self._values.get("source")
        return typing.cast(typing.Optional["DataDatabricksAlertsV2ResultsEvaluationSource"], result)

    @builtins.property
    def threshold(
        self,
    ) -> typing.Optional["DataDatabricksAlertsV2ResultsEvaluationThreshold"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#threshold DataDatabricksAlertsV2#threshold}.'''
        result = self._values.get("threshold")
        return typing.cast(typing.Optional["DataDatabricksAlertsV2ResultsEvaluationThreshold"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAlertsV2ResultsEvaluation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertsV2.DataDatabricksAlertsV2ResultsEvaluationNotification",
    jsii_struct_bases=[],
    name_mapping={
        "notify_on_ok": "notifyOnOk",
        "retrigger_seconds": "retriggerSeconds",
        "subscriptions": "subscriptions",
    },
)
class DataDatabricksAlertsV2ResultsEvaluationNotification:
    def __init__(
        self,
        *,
        notify_on_ok: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        retrigger_seconds: typing.Optional[jsii.Number] = None,
        subscriptions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptions", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param notify_on_ok: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#notify_on_ok DataDatabricksAlertsV2#notify_on_ok}.
        :param retrigger_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#retrigger_seconds DataDatabricksAlertsV2#retrigger_seconds}.
        :param subscriptions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#subscriptions DataDatabricksAlertsV2#subscriptions}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa15d966523bf54684e6a5d311d5c10711288c9e4d76ccc45595059e50d3fbeb)
            check_type(argname="argument notify_on_ok", value=notify_on_ok, expected_type=type_hints["notify_on_ok"])
            check_type(argname="argument retrigger_seconds", value=retrigger_seconds, expected_type=type_hints["retrigger_seconds"])
            check_type(argname="argument subscriptions", value=subscriptions, expected_type=type_hints["subscriptions"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if notify_on_ok is not None:
            self._values["notify_on_ok"] = notify_on_ok
        if retrigger_seconds is not None:
            self._values["retrigger_seconds"] = retrigger_seconds
        if subscriptions is not None:
            self._values["subscriptions"] = subscriptions

    @builtins.property
    def notify_on_ok(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#notify_on_ok DataDatabricksAlertsV2#notify_on_ok}.'''
        result = self._values.get("notify_on_ok")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def retrigger_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#retrigger_seconds DataDatabricksAlertsV2#retrigger_seconds}.'''
        result = self._values.get("retrigger_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def subscriptions(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptions"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#subscriptions DataDatabricksAlertsV2#subscriptions}.'''
        result = self._values.get("subscriptions")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptions"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAlertsV2ResultsEvaluationNotification(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAlertsV2ResultsEvaluationNotificationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertsV2.DataDatabricksAlertsV2ResultsEvaluationNotificationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d38205ed711b503b12bdac3174be63d3218121e652a401b24229223b81ac09dd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putSubscriptions")
    def put_subscriptions(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptions", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99e42da7c4829d5465c0f1b280c462f112c622747763041c36ae34b45ea16c9a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSubscriptions", [value]))

    @jsii.member(jsii_name="resetNotifyOnOk")
    def reset_notify_on_ok(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotifyOnOk", []))

    @jsii.member(jsii_name="resetRetriggerSeconds")
    def reset_retrigger_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetriggerSeconds", []))

    @jsii.member(jsii_name="resetSubscriptions")
    def reset_subscriptions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubscriptions", []))

    @builtins.property
    @jsii.member(jsii_name="subscriptions")
    def subscriptions(
        self,
    ) -> "DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptionsList":
        return typing.cast("DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptionsList", jsii.get(self, "subscriptions"))

    @builtins.property
    @jsii.member(jsii_name="notifyOnOkInput")
    def notify_on_ok_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "notifyOnOkInput"))

    @builtins.property
    @jsii.member(jsii_name="retriggerSecondsInput")
    def retrigger_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retriggerSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="subscriptionsInput")
    def subscriptions_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptions"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptions"]]], jsii.get(self, "subscriptionsInput"))

    @builtins.property
    @jsii.member(jsii_name="notifyOnOk")
    def notify_on_ok(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "notifyOnOk"))

    @notify_on_ok.setter
    def notify_on_ok(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a86643abc0c912a3bf38c7eeb381df5423f8ca8f3db068fd8a7b078940db03f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notifyOnOk", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retriggerSeconds")
    def retrigger_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retriggerSeconds"))

    @retrigger_seconds.setter
    def retrigger_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47caf102659becbd130606da636b6dae062f4cef849ca477313a25f1e72ce4ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retriggerSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluationNotification]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluationNotification]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluationNotification]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b80f8a98426e067d70a4c720fec16d32684670258e3c4e8903fe2a3cf30687c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertsV2.DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptions",
    jsii_struct_bases=[],
    name_mapping={"destination_id": "destinationId", "user_email": "userEmail"},
)
class DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptions:
    def __init__(
        self,
        *,
        destination_id: typing.Optional[builtins.str] = None,
        user_email: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param destination_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#destination_id DataDatabricksAlertsV2#destination_id}.
        :param user_email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#user_email DataDatabricksAlertsV2#user_email}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a0a0a94733dd3d72a5542705263eaab8808e4477a67829c5c1fd952053be07b)
            check_type(argname="argument destination_id", value=destination_id, expected_type=type_hints["destination_id"])
            check_type(argname="argument user_email", value=user_email, expected_type=type_hints["user_email"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if destination_id is not None:
            self._values["destination_id"] = destination_id
        if user_email is not None:
            self._values["user_email"] = user_email

    @builtins.property
    def destination_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#destination_id DataDatabricksAlertsV2#destination_id}.'''
        result = self._values.get("destination_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_email(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#user_email DataDatabricksAlertsV2#user_email}.'''
        result = self._values.get("user_email")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptionsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertsV2.DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptionsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__08451ca90303b434911f058f2ca1b63e4205d40a4632a067625db8f910d4cb06)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5383068ed320049dbd2aefec156e024b3922a23624079f7b6b8d938819453f24)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptionsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f2c55119ae0058f2192eccd17d724fd296e06c3a244c1f80b2db51f2c1b8b00)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1354572149b85a8ad670b65486ce981177ea40cd27ef65fa5e6231e489788af4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d36652e58cc8e63651c6232c1ff72fafd5b390b05b15120c5edbfcbc6bec93a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptions]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptions]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptions]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6114bef81dbc7f0dc9c85b8eabce135d181903bac2dd6f31b160d63c997712b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertsV2.DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4bd5322a63b594e925453efaa1f0c076f6676948ba6f171f566ad43e41ae2b5a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetDestinationId")
    def reset_destination_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDestinationId", []))

    @jsii.member(jsii_name="resetUserEmail")
    def reset_user_email(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserEmail", []))

    @builtins.property
    @jsii.member(jsii_name="destinationIdInput")
    def destination_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationIdInput"))

    @builtins.property
    @jsii.member(jsii_name="userEmailInput")
    def user_email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userEmailInput"))

    @builtins.property
    @jsii.member(jsii_name="destinationId")
    def destination_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationId"))

    @destination_id.setter
    def destination_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f100e8edbefc08b83cc498bfd5a40cab1f4d7260e1a0d911fd2d6eac82d2db6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destinationId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userEmail")
    def user_email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userEmail"))

    @user_email.setter
    def user_email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a47075685aa5e9a558992359677b8f20d140cb026ccc23a670bbb5ca07bd07e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userEmail", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptions]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptions]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptions]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7e832b02c34eb8f47d08430e16852e79e0071ed1570f556432c5a919b151aef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAlertsV2ResultsEvaluationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertsV2.DataDatabricksAlertsV2ResultsEvaluationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d7723fc345ae7ddf8bbe35727060b865202f5aea3fe42ecfb06d242048d206f7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putNotification")
    def put_notification(
        self,
        *,
        notify_on_ok: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        retrigger_seconds: typing.Optional[jsii.Number] = None,
        subscriptions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptions, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param notify_on_ok: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#notify_on_ok DataDatabricksAlertsV2#notify_on_ok}.
        :param retrigger_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#retrigger_seconds DataDatabricksAlertsV2#retrigger_seconds}.
        :param subscriptions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#subscriptions DataDatabricksAlertsV2#subscriptions}.
        '''
        value = DataDatabricksAlertsV2ResultsEvaluationNotification(
            notify_on_ok=notify_on_ok,
            retrigger_seconds=retrigger_seconds,
            subscriptions=subscriptions,
        )

        return typing.cast(None, jsii.invoke(self, "putNotification", [value]))

    @jsii.member(jsii_name="putSource")
    def put_source(
        self,
        *,
        aggregation: typing.Optional[builtins.str] = None,
        display: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param aggregation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#aggregation DataDatabricksAlertsV2#aggregation}.
        :param display: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#display DataDatabricksAlertsV2#display}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#name DataDatabricksAlertsV2#name}.
        '''
        value = DataDatabricksAlertsV2ResultsEvaluationSource(
            aggregation=aggregation, display=display, name=name
        )

        return typing.cast(None, jsii.invoke(self, "putSource", [value]))

    @jsii.member(jsii_name="putThreshold")
    def put_threshold(
        self,
        *,
        column: typing.Optional[typing.Union["DataDatabricksAlertsV2ResultsEvaluationThresholdColumn", typing.Dict[builtins.str, typing.Any]]] = None,
        value: typing.Optional[typing.Union["DataDatabricksAlertsV2ResultsEvaluationThresholdValue", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param column: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#column DataDatabricksAlertsV2#column}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#value DataDatabricksAlertsV2#value}.
        '''
        value_ = DataDatabricksAlertsV2ResultsEvaluationThreshold(
            column=column, value=value
        )

        return typing.cast(None, jsii.invoke(self, "putThreshold", [value_]))

    @jsii.member(jsii_name="resetComparisonOperator")
    def reset_comparison_operator(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComparisonOperator", []))

    @jsii.member(jsii_name="resetEmptyResultState")
    def reset_empty_result_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmptyResultState", []))

    @jsii.member(jsii_name="resetNotification")
    def reset_notification(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotification", []))

    @jsii.member(jsii_name="resetSource")
    def reset_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSource", []))

    @jsii.member(jsii_name="resetThreshold")
    def reset_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreshold", []))

    @builtins.property
    @jsii.member(jsii_name="lastEvaluatedAt")
    def last_evaluated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastEvaluatedAt"))

    @builtins.property
    @jsii.member(jsii_name="notification")
    def notification(
        self,
    ) -> DataDatabricksAlertsV2ResultsEvaluationNotificationOutputReference:
        return typing.cast(DataDatabricksAlertsV2ResultsEvaluationNotificationOutputReference, jsii.get(self, "notification"))

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> "DataDatabricksAlertsV2ResultsEvaluationSourceOutputReference":
        return typing.cast("DataDatabricksAlertsV2ResultsEvaluationSourceOutputReference", jsii.get(self, "source"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(
        self,
    ) -> "DataDatabricksAlertsV2ResultsEvaluationThresholdOutputReference":
        return typing.cast("DataDatabricksAlertsV2ResultsEvaluationThresholdOutputReference", jsii.get(self, "threshold"))

    @builtins.property
    @jsii.member(jsii_name="comparisonOperatorInput")
    def comparison_operator_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "comparisonOperatorInput"))

    @builtins.property
    @jsii.member(jsii_name="emptyResultStateInput")
    def empty_result_state_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emptyResultStateInput"))

    @builtins.property
    @jsii.member(jsii_name="notificationInput")
    def notification_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluationNotification]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluationNotification]], jsii.get(self, "notificationInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceInput")
    def source_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAlertsV2ResultsEvaluationSource"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAlertsV2ResultsEvaluationSource"]], jsii.get(self, "sourceInput"))

    @builtins.property
    @jsii.member(jsii_name="thresholdInput")
    def threshold_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAlertsV2ResultsEvaluationThreshold"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAlertsV2ResultsEvaluationThreshold"]], jsii.get(self, "thresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="comparisonOperator")
    def comparison_operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comparisonOperator"))

    @comparison_operator.setter
    def comparison_operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ba53eb0144145f318ebadf97724df17e1bebc2725c48f7e6ea3b56a2a46fb72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comparisonOperator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="emptyResultState")
    def empty_result_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emptyResultState"))

    @empty_result_state.setter
    def empty_result_state(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc4cc8b2aa80ee6e46e55be985f77f3ad96470aa270fec5202b8365e38c0b9b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emptyResultState", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluation]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluation]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluation]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__084cb01d38ca040d76e9964ae9467d7ab06fee92af5bfca6115b04e8f9fcf429)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertsV2.DataDatabricksAlertsV2ResultsEvaluationSource",
    jsii_struct_bases=[],
    name_mapping={"aggregation": "aggregation", "display": "display", "name": "name"},
)
class DataDatabricksAlertsV2ResultsEvaluationSource:
    def __init__(
        self,
        *,
        aggregation: typing.Optional[builtins.str] = None,
        display: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param aggregation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#aggregation DataDatabricksAlertsV2#aggregation}.
        :param display: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#display DataDatabricksAlertsV2#display}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#name DataDatabricksAlertsV2#name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d991f580a31ee360f2ac7e5b44e2eec3a740735528c4168154bae5162b2f1cde)
            check_type(argname="argument aggregation", value=aggregation, expected_type=type_hints["aggregation"])
            check_type(argname="argument display", value=display, expected_type=type_hints["display"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if aggregation is not None:
            self._values["aggregation"] = aggregation
        if display is not None:
            self._values["display"] = display
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def aggregation(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#aggregation DataDatabricksAlertsV2#aggregation}.'''
        result = self._values.get("aggregation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def display(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#display DataDatabricksAlertsV2#display}.'''
        result = self._values.get("display")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#name DataDatabricksAlertsV2#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAlertsV2ResultsEvaluationSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAlertsV2ResultsEvaluationSourceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertsV2.DataDatabricksAlertsV2ResultsEvaluationSourceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9014eea490ad023df4c3f5a7d8fa14fbe021b6e4ce107d4c1353f6d541a6def0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAggregation")
    def reset_aggregation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAggregation", []))

    @jsii.member(jsii_name="resetDisplay")
    def reset_display(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisplay", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @builtins.property
    @jsii.member(jsii_name="aggregationInput")
    def aggregation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aggregationInput"))

    @builtins.property
    @jsii.member(jsii_name="displayInput")
    def display_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "displayInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="aggregation")
    def aggregation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "aggregation"))

    @aggregation.setter
    def aggregation(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4cb09629c2f4af78cca5e0ae51c139fc72e98fbb2bb0c989ed1383704545e8e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "aggregation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="display")
    def display(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "display"))

    @display.setter
    def display(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0bd811bf41998a43b202a6c939f76f2e9a04a7764634c4c771b50aa23040937)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "display", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c0f0ab481878e2e7b3dc21452c38c10c5ee0301728f740c90f136ef55cce615)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluationSource]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluationSource]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluationSource]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1231ae3b91fdf2d809c220be2c6a499cd4d13ad1c536d196f3c0d60cb7cde417)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertsV2.DataDatabricksAlertsV2ResultsEvaluationThreshold",
    jsii_struct_bases=[],
    name_mapping={"column": "column", "value": "value"},
)
class DataDatabricksAlertsV2ResultsEvaluationThreshold:
    def __init__(
        self,
        *,
        column: typing.Optional[typing.Union["DataDatabricksAlertsV2ResultsEvaluationThresholdColumn", typing.Dict[builtins.str, typing.Any]]] = None,
        value: typing.Optional[typing.Union["DataDatabricksAlertsV2ResultsEvaluationThresholdValue", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param column: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#column DataDatabricksAlertsV2#column}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#value DataDatabricksAlertsV2#value}.
        '''
        if isinstance(column, dict):
            column = DataDatabricksAlertsV2ResultsEvaluationThresholdColumn(**column)
        if isinstance(value, dict):
            value = DataDatabricksAlertsV2ResultsEvaluationThresholdValue(**value)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7cc8807123907cfd289662a48b3b7be7f2c499f262c918a00289c2108a45240)
            check_type(argname="argument column", value=column, expected_type=type_hints["column"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if column is not None:
            self._values["column"] = column
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def column(
        self,
    ) -> typing.Optional["DataDatabricksAlertsV2ResultsEvaluationThresholdColumn"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#column DataDatabricksAlertsV2#column}.'''
        result = self._values.get("column")
        return typing.cast(typing.Optional["DataDatabricksAlertsV2ResultsEvaluationThresholdColumn"], result)

    @builtins.property
    def value(
        self,
    ) -> typing.Optional["DataDatabricksAlertsV2ResultsEvaluationThresholdValue"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#value DataDatabricksAlertsV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional["DataDatabricksAlertsV2ResultsEvaluationThresholdValue"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAlertsV2ResultsEvaluationThreshold(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertsV2.DataDatabricksAlertsV2ResultsEvaluationThresholdColumn",
    jsii_struct_bases=[],
    name_mapping={"aggregation": "aggregation", "display": "display", "name": "name"},
)
class DataDatabricksAlertsV2ResultsEvaluationThresholdColumn:
    def __init__(
        self,
        *,
        aggregation: typing.Optional[builtins.str] = None,
        display: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param aggregation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#aggregation DataDatabricksAlertsV2#aggregation}.
        :param display: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#display DataDatabricksAlertsV2#display}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#name DataDatabricksAlertsV2#name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39a905dcd2c36b4409738c4650c43bca516e9b62611c126b42fd0737552662e6)
            check_type(argname="argument aggregation", value=aggregation, expected_type=type_hints["aggregation"])
            check_type(argname="argument display", value=display, expected_type=type_hints["display"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if aggregation is not None:
            self._values["aggregation"] = aggregation
        if display is not None:
            self._values["display"] = display
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def aggregation(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#aggregation DataDatabricksAlertsV2#aggregation}.'''
        result = self._values.get("aggregation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def display(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#display DataDatabricksAlertsV2#display}.'''
        result = self._values.get("display")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#name DataDatabricksAlertsV2#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAlertsV2ResultsEvaluationThresholdColumn(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAlertsV2ResultsEvaluationThresholdColumnOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertsV2.DataDatabricksAlertsV2ResultsEvaluationThresholdColumnOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9123b6064e99890d8465d43a8d0ff9bc46af5e6351c1258d896d57367fcf9fbb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAggregation")
    def reset_aggregation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAggregation", []))

    @jsii.member(jsii_name="resetDisplay")
    def reset_display(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisplay", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @builtins.property
    @jsii.member(jsii_name="aggregationInput")
    def aggregation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aggregationInput"))

    @builtins.property
    @jsii.member(jsii_name="displayInput")
    def display_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "displayInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="aggregation")
    def aggregation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "aggregation"))

    @aggregation.setter
    def aggregation(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b98ad7514833eef29b3da079e589489d62c8127af61768c92af95c7a8c9e050)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "aggregation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="display")
    def display(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "display"))

    @display.setter
    def display(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9150a4d27ea2662faa8ab2ab031f0885574fa3a29dc622c4387facf4c43e8366)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "display", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5b763ea1dd523ff5ebd45317df73a4416890a66ca4ce2588ddff8d9abcb3b54)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluationThresholdColumn]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluationThresholdColumn]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluationThresholdColumn]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30e99ab378dc8dd5eb9a5f2ed647a70c0b8970f39a1e3745631ea7b0ff5df7bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAlertsV2ResultsEvaluationThresholdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertsV2.DataDatabricksAlertsV2ResultsEvaluationThresholdOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d5af71af22089e3d287d6a8c410e5f3b43f720be3de54c08202e7135566bd68d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putColumn")
    def put_column(
        self,
        *,
        aggregation: typing.Optional[builtins.str] = None,
        display: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param aggregation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#aggregation DataDatabricksAlertsV2#aggregation}.
        :param display: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#display DataDatabricksAlertsV2#display}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#name DataDatabricksAlertsV2#name}.
        '''
        value = DataDatabricksAlertsV2ResultsEvaluationThresholdColumn(
            aggregation=aggregation, display=display, name=name
        )

        return typing.cast(None, jsii.invoke(self, "putColumn", [value]))

    @jsii.member(jsii_name="putValue")
    def put_value(
        self,
        *,
        bool_value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        double_value: typing.Optional[jsii.Number] = None,
        string_value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bool_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#bool_value DataDatabricksAlertsV2#bool_value}.
        :param double_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#double_value DataDatabricksAlertsV2#double_value}.
        :param string_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#string_value DataDatabricksAlertsV2#string_value}.
        '''
        value = DataDatabricksAlertsV2ResultsEvaluationThresholdValue(
            bool_value=bool_value, double_value=double_value, string_value=string_value
        )

        return typing.cast(None, jsii.invoke(self, "putValue", [value]))

    @jsii.member(jsii_name="resetColumn")
    def reset_column(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetColumn", []))

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="column")
    def column(
        self,
    ) -> DataDatabricksAlertsV2ResultsEvaluationThresholdColumnOutputReference:
        return typing.cast(DataDatabricksAlertsV2ResultsEvaluationThresholdColumnOutputReference, jsii.get(self, "column"))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(
        self,
    ) -> "DataDatabricksAlertsV2ResultsEvaluationThresholdValueOutputReference":
        return typing.cast("DataDatabricksAlertsV2ResultsEvaluationThresholdValueOutputReference", jsii.get(self, "value"))

    @builtins.property
    @jsii.member(jsii_name="columnInput")
    def column_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluationThresholdColumn]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluationThresholdColumn]], jsii.get(self, "columnInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAlertsV2ResultsEvaluationThresholdValue"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAlertsV2ResultsEvaluationThresholdValue"]], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluationThreshold]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluationThreshold]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluationThreshold]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0e6ea01f2e917faccd4022b7ba7daf26f99c75374699bc890284dfc2a7a98ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertsV2.DataDatabricksAlertsV2ResultsEvaluationThresholdValue",
    jsii_struct_bases=[],
    name_mapping={
        "bool_value": "boolValue",
        "double_value": "doubleValue",
        "string_value": "stringValue",
    },
)
class DataDatabricksAlertsV2ResultsEvaluationThresholdValue:
    def __init__(
        self,
        *,
        bool_value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        double_value: typing.Optional[jsii.Number] = None,
        string_value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bool_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#bool_value DataDatabricksAlertsV2#bool_value}.
        :param double_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#double_value DataDatabricksAlertsV2#double_value}.
        :param string_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#string_value DataDatabricksAlertsV2#string_value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1c170932c195ef6814c09bb9d92ed17b09ef39caad2a9444c5f9e9ce706038f)
            check_type(argname="argument bool_value", value=bool_value, expected_type=type_hints["bool_value"])
            check_type(argname="argument double_value", value=double_value, expected_type=type_hints["double_value"])
            check_type(argname="argument string_value", value=string_value, expected_type=type_hints["string_value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bool_value is not None:
            self._values["bool_value"] = bool_value
        if double_value is not None:
            self._values["double_value"] = double_value
        if string_value is not None:
            self._values["string_value"] = string_value

    @builtins.property
    def bool_value(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#bool_value DataDatabricksAlertsV2#bool_value}.'''
        result = self._values.get("bool_value")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def double_value(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#double_value DataDatabricksAlertsV2#double_value}.'''
        result = self._values.get("double_value")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def string_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#string_value DataDatabricksAlertsV2#string_value}.'''
        result = self._values.get("string_value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAlertsV2ResultsEvaluationThresholdValue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAlertsV2ResultsEvaluationThresholdValueOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertsV2.DataDatabricksAlertsV2ResultsEvaluationThresholdValueOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6c04e06905f083090b314766527ef5b7484b1338fdc6ec9e0cc4263159622652)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetBoolValue")
    def reset_bool_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoolValue", []))

    @jsii.member(jsii_name="resetDoubleValue")
    def reset_double_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDoubleValue", []))

    @jsii.member(jsii_name="resetStringValue")
    def reset_string_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStringValue", []))

    @builtins.property
    @jsii.member(jsii_name="boolValueInput")
    def bool_value_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "boolValueInput"))

    @builtins.property
    @jsii.member(jsii_name="doubleValueInput")
    def double_value_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "doubleValueInput"))

    @builtins.property
    @jsii.member(jsii_name="stringValueInput")
    def string_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stringValueInput"))

    @builtins.property
    @jsii.member(jsii_name="boolValue")
    def bool_value(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "boolValue"))

    @bool_value.setter
    def bool_value(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47ea609bb5a14ff13d9b3f7c3afd4c7e3b82d1e908a9d0bd98df06c9c75d396f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boolValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="doubleValue")
    def double_value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "doubleValue"))

    @double_value.setter
    def double_value(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0cae7f27b250b503adf9b73bf0d19359fa3ed5cf2f383ac5c326ebad4de3cda)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "doubleValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stringValue")
    def string_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stringValue"))

    @string_value.setter
    def string_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4be9cb0d2e8887ca015bb50be4ca7d663a0d6b16c09d346351fd9a1a34b5a2c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stringValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluationThresholdValue]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluationThresholdValue]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluationThresholdValue]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__167b15379101da19189ab492589c3c5513f38f52ae2998d7afce8cca8b97d803)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAlertsV2ResultsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertsV2.DataDatabricksAlertsV2ResultsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7b225db3f692734362709245468fd087e16bc6dda69873c6b8a6ff3d5ee46b76)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "DataDatabricksAlertsV2ResultsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed9b3d2ced28c88971fcee2750186ed2bc016c6d68df3f2922526590d1796d16)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksAlertsV2ResultsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57f3e71a1c431c8e2612292e6b536b14ff715193fae8cd6ad270961038c0d815)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ddf32eda5df2450065aef4a5ae641cb925f7b1d63e759c2d6062e36efe7d1abf)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8a22b6af0c0ee5e915935833ecb57e5d42b7d092166202b49f1be4f812d53437)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAlertsV2Results]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAlertsV2Results]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAlertsV2Results]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2af083b5edeb6cdaccae4f4ca7f7188849b4bd6bf2402bee6a34e1dab303628a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAlertsV2ResultsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertsV2.DataDatabricksAlertsV2ResultsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a2b7349a4718c040d901b5572c193acd5a8087821e1184bfa04c1404c3524221)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putEvaluation")
    def put_evaluation(
        self,
        *,
        comparison_operator: typing.Optional[builtins.str] = None,
        empty_result_state: typing.Optional[builtins.str] = None,
        notification: typing.Optional[typing.Union[DataDatabricksAlertsV2ResultsEvaluationNotification, typing.Dict[builtins.str, typing.Any]]] = None,
        source: typing.Optional[typing.Union[DataDatabricksAlertsV2ResultsEvaluationSource, typing.Dict[builtins.str, typing.Any]]] = None,
        threshold: typing.Optional[typing.Union[DataDatabricksAlertsV2ResultsEvaluationThreshold, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param comparison_operator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#comparison_operator DataDatabricksAlertsV2#comparison_operator}.
        :param empty_result_state: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#empty_result_state DataDatabricksAlertsV2#empty_result_state}.
        :param notification: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#notification DataDatabricksAlertsV2#notification}.
        :param source: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#source DataDatabricksAlertsV2#source}.
        :param threshold: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#threshold DataDatabricksAlertsV2#threshold}.
        '''
        value = DataDatabricksAlertsV2ResultsEvaluation(
            comparison_operator=comparison_operator,
            empty_result_state=empty_result_state,
            notification=notification,
            source=source,
            threshold=threshold,
        )

        return typing.cast(None, jsii.invoke(self, "putEvaluation", [value]))

    @jsii.member(jsii_name="putRunAs")
    def put_run_as(
        self,
        *,
        service_principal_name: typing.Optional[builtins.str] = None,
        user_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param service_principal_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#service_principal_name DataDatabricksAlertsV2#service_principal_name}.
        :param user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#user_name DataDatabricksAlertsV2#user_name}.
        '''
        value = DataDatabricksAlertsV2ResultsRunAs(
            service_principal_name=service_principal_name, user_name=user_name
        )

        return typing.cast(None, jsii.invoke(self, "putRunAs", [value]))

    @jsii.member(jsii_name="putSchedule")
    def put_schedule(
        self,
        *,
        pause_status: typing.Optional[builtins.str] = None,
        quartz_cron_schedule: typing.Optional[builtins.str] = None,
        timezone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param pause_status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#pause_status DataDatabricksAlertsV2#pause_status}.
        :param quartz_cron_schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#quartz_cron_schedule DataDatabricksAlertsV2#quartz_cron_schedule}.
        :param timezone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#timezone_id DataDatabricksAlertsV2#timezone_id}.
        '''
        value = DataDatabricksAlertsV2ResultsSchedule(
            pause_status=pause_status,
            quartz_cron_schedule=quartz_cron_schedule,
            timezone_id=timezone_id,
        )

        return typing.cast(None, jsii.invoke(self, "putSchedule", [value]))

    @jsii.member(jsii_name="resetCustomDescription")
    def reset_custom_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomDescription", []))

    @jsii.member(jsii_name="resetCustomSummary")
    def reset_custom_summary(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomSummary", []))

    @jsii.member(jsii_name="resetDisplayName")
    def reset_display_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisplayName", []))

    @jsii.member(jsii_name="resetEvaluation")
    def reset_evaluation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEvaluation", []))

    @jsii.member(jsii_name="resetParentPath")
    def reset_parent_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParentPath", []))

    @jsii.member(jsii_name="resetQueryText")
    def reset_query_text(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQueryText", []))

    @jsii.member(jsii_name="resetRunAs")
    def reset_run_as(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunAs", []))

    @jsii.member(jsii_name="resetRunAsUserName")
    def reset_run_as_user_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunAsUserName", []))

    @jsii.member(jsii_name="resetSchedule")
    def reset_schedule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchedule", []))

    @jsii.member(jsii_name="resetWarehouseId")
    def reset_warehouse_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWarehouseId", []))

    @builtins.property
    @jsii.member(jsii_name="createTime")
    def create_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createTime"))

    @builtins.property
    @jsii.member(jsii_name="effectiveRunAs")
    def effective_run_as(
        self,
    ) -> DataDatabricksAlertsV2ResultsEffectiveRunAsOutputReference:
        return typing.cast(DataDatabricksAlertsV2ResultsEffectiveRunAsOutputReference, jsii.get(self, "effectiveRunAs"))

    @builtins.property
    @jsii.member(jsii_name="evaluation")
    def evaluation(self) -> DataDatabricksAlertsV2ResultsEvaluationOutputReference:
        return typing.cast(DataDatabricksAlertsV2ResultsEvaluationOutputReference, jsii.get(self, "evaluation"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="lifecycleState")
    def lifecycle_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lifecycleState"))

    @builtins.property
    @jsii.member(jsii_name="ownerUserName")
    def owner_user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ownerUserName"))

    @builtins.property
    @jsii.member(jsii_name="runAs")
    def run_as(self) -> "DataDatabricksAlertsV2ResultsRunAsOutputReference":
        return typing.cast("DataDatabricksAlertsV2ResultsRunAsOutputReference", jsii.get(self, "runAs"))

    @builtins.property
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> "DataDatabricksAlertsV2ResultsScheduleOutputReference":
        return typing.cast("DataDatabricksAlertsV2ResultsScheduleOutputReference", jsii.get(self, "schedule"))

    @builtins.property
    @jsii.member(jsii_name="updateTime")
    def update_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updateTime"))

    @builtins.property
    @jsii.member(jsii_name="customDescriptionInput")
    def custom_description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customDescriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="customSummaryInput")
    def custom_summary_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customSummaryInput"))

    @builtins.property
    @jsii.member(jsii_name="displayNameInput")
    def display_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "displayNameInput"))

    @builtins.property
    @jsii.member(jsii_name="evaluationInput")
    def evaluation_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluation]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluation]], jsii.get(self, "evaluationInput"))

    @builtins.property
    @jsii.member(jsii_name="parentPathInput")
    def parent_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parentPathInput"))

    @builtins.property
    @jsii.member(jsii_name="queryTextInput")
    def query_text_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queryTextInput"))

    @builtins.property
    @jsii.member(jsii_name="runAsInput")
    def run_as_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAlertsV2ResultsRunAs"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAlertsV2ResultsRunAs"]], jsii.get(self, "runAsInput"))

    @builtins.property
    @jsii.member(jsii_name="runAsUserNameInput")
    def run_as_user_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "runAsUserNameInput"))

    @builtins.property
    @jsii.member(jsii_name="scheduleInput")
    def schedule_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAlertsV2ResultsSchedule"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAlertsV2ResultsSchedule"]], jsii.get(self, "scheduleInput"))

    @builtins.property
    @jsii.member(jsii_name="warehouseIdInput")
    def warehouse_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "warehouseIdInput"))

    @builtins.property
    @jsii.member(jsii_name="customDescription")
    def custom_description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customDescription"))

    @custom_description.setter
    def custom_description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8fe5a47a6c757398f99cb91a3f1f8d9c8dd6c7cbe2c04ee0f97e6e5b2ea2c432)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customDescription", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="customSummary")
    def custom_summary(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customSummary"))

    @custom_summary.setter
    def custom_summary(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bfe6a4d58585f5a47cadd7be8f0f2e5114e045cdb87824261bf6f4d00abed004)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customSummary", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "displayName"))

    @display_name.setter
    def display_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63d7ed007ea758bc821c070f0bffcaac2ceea0ff378722cd11d08568686f74b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "displayName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parentPath")
    def parent_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parentPath"))

    @parent_path.setter
    def parent_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6444e05de1e4787b7fde22d4912894e77db75050b2cf92c242648d7b2e7e926c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parentPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="queryText")
    def query_text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queryText"))

    @query_text.setter
    def query_text(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6762e641859f0e059eef215a5fff6926106991d24190d899187f318a8ac90786)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "queryText", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runAsUserName")
    def run_as_user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runAsUserName"))

    @run_as_user_name.setter
    def run_as_user_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b720f332c00eedca86f802803008178d9bb3cdbdaa8fde19d7d245a860dae9cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runAsUserName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="warehouseId")
    def warehouse_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "warehouseId"))

    @warehouse_id.setter
    def warehouse_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a73c4fba2027af5994d6178e8beb67623dfc413969c4a9b182f4bc45fc61a2d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "warehouseId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataDatabricksAlertsV2Results]:
        return typing.cast(typing.Optional[DataDatabricksAlertsV2Results], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksAlertsV2Results],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebc895bbc1cc2acb3932d26c90f1e7f5e5c3a767b6e0da178a3b7f5519de40b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertsV2.DataDatabricksAlertsV2ResultsRunAs",
    jsii_struct_bases=[],
    name_mapping={
        "service_principal_name": "servicePrincipalName",
        "user_name": "userName",
    },
)
class DataDatabricksAlertsV2ResultsRunAs:
    def __init__(
        self,
        *,
        service_principal_name: typing.Optional[builtins.str] = None,
        user_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param service_principal_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#service_principal_name DataDatabricksAlertsV2#service_principal_name}.
        :param user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#user_name DataDatabricksAlertsV2#user_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42f78f899052a5073d814344c2f66692a6d70fe7baf382f4cb627b02083ea3a7)
            check_type(argname="argument service_principal_name", value=service_principal_name, expected_type=type_hints["service_principal_name"])
            check_type(argname="argument user_name", value=user_name, expected_type=type_hints["user_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if service_principal_name is not None:
            self._values["service_principal_name"] = service_principal_name
        if user_name is not None:
            self._values["user_name"] = user_name

    @builtins.property
    def service_principal_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#service_principal_name DataDatabricksAlertsV2#service_principal_name}.'''
        result = self._values.get("service_principal_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#user_name DataDatabricksAlertsV2#user_name}.'''
        result = self._values.get("user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAlertsV2ResultsRunAs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAlertsV2ResultsRunAsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertsV2.DataDatabricksAlertsV2ResultsRunAsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__76240c12f2801c7c250349fe6535d1908801d39417e9c79e63fa95415c40f0c7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetServicePrincipalName")
    def reset_service_principal_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServicePrincipalName", []))

    @jsii.member(jsii_name="resetUserName")
    def reset_user_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserName", []))

    @builtins.property
    @jsii.member(jsii_name="servicePrincipalNameInput")
    def service_principal_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "servicePrincipalNameInput"))

    @builtins.property
    @jsii.member(jsii_name="userNameInput")
    def user_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userNameInput"))

    @builtins.property
    @jsii.member(jsii_name="servicePrincipalName")
    def service_principal_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "servicePrincipalName"))

    @service_principal_name.setter
    def service_principal_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fca9339b8aa2d873f94267ca5dcf28900af8cead9b18746bef7cfca1dc52739c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "servicePrincipalName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userName"))

    @user_name.setter
    def user_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08852b9eb5780b914b10d6d3d96d0d54ae26c88749c3633e0d676c83ded6780b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsRunAs]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsRunAs]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsRunAs]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4192eb80150d480652136ae082383c6204e57446dd263ca8c2c35bfbef5c5635)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertsV2.DataDatabricksAlertsV2ResultsSchedule",
    jsii_struct_bases=[],
    name_mapping={
        "pause_status": "pauseStatus",
        "quartz_cron_schedule": "quartzCronSchedule",
        "timezone_id": "timezoneId",
    },
)
class DataDatabricksAlertsV2ResultsSchedule:
    def __init__(
        self,
        *,
        pause_status: typing.Optional[builtins.str] = None,
        quartz_cron_schedule: typing.Optional[builtins.str] = None,
        timezone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param pause_status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#pause_status DataDatabricksAlertsV2#pause_status}.
        :param quartz_cron_schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#quartz_cron_schedule DataDatabricksAlertsV2#quartz_cron_schedule}.
        :param timezone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#timezone_id DataDatabricksAlertsV2#timezone_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e38e827ec22430a6bd8404944cb8b4ce788a154de7eb22f883bc966a2fb949a)
            check_type(argname="argument pause_status", value=pause_status, expected_type=type_hints["pause_status"])
            check_type(argname="argument quartz_cron_schedule", value=quartz_cron_schedule, expected_type=type_hints["quartz_cron_schedule"])
            check_type(argname="argument timezone_id", value=timezone_id, expected_type=type_hints["timezone_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if pause_status is not None:
            self._values["pause_status"] = pause_status
        if quartz_cron_schedule is not None:
            self._values["quartz_cron_schedule"] = quartz_cron_schedule
        if timezone_id is not None:
            self._values["timezone_id"] = timezone_id

    @builtins.property
    def pause_status(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#pause_status DataDatabricksAlertsV2#pause_status}.'''
        result = self._values.get("pause_status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def quartz_cron_schedule(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#quartz_cron_schedule DataDatabricksAlertsV2#quartz_cron_schedule}.'''
        result = self._values.get("quartz_cron_schedule")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timezone_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alerts_v2#timezone_id DataDatabricksAlertsV2#timezone_id}.'''
        result = self._values.get("timezone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAlertsV2ResultsSchedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAlertsV2ResultsScheduleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertsV2.DataDatabricksAlertsV2ResultsScheduleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5547d193af36aaa130011346f66b5ddf930ff6498c40397dabf46217bd0b5b63)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetPauseStatus")
    def reset_pause_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPauseStatus", []))

    @jsii.member(jsii_name="resetQuartzCronSchedule")
    def reset_quartz_cron_schedule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQuartzCronSchedule", []))

    @jsii.member(jsii_name="resetTimezoneId")
    def reset_timezone_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimezoneId", []))

    @builtins.property
    @jsii.member(jsii_name="pauseStatusInput")
    def pause_status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pauseStatusInput"))

    @builtins.property
    @jsii.member(jsii_name="quartzCronScheduleInput")
    def quartz_cron_schedule_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "quartzCronScheduleInput"))

    @builtins.property
    @jsii.member(jsii_name="timezoneIdInput")
    def timezone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timezoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="pauseStatus")
    def pause_status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pauseStatus"))

    @pause_status.setter
    def pause_status(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cdff9068a7bd973472e4fd71307a34812ea0a66a2184bff74013f00cd181bcc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pauseStatus", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="quartzCronSchedule")
    def quartz_cron_schedule(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "quartzCronSchedule"))

    @quartz_cron_schedule.setter
    def quartz_cron_schedule(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__385ed85e9b286c750c33848c26c5e492352b2b3ed567c4538dbf236fea0a6db6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "quartzCronSchedule", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timezoneId")
    def timezone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timezoneId"))

    @timezone_id.setter
    def timezone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a43a9efbb65295c266619114289cd1727f7d31e3f99ede7f1f605d49b3126cb3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timezoneId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsSchedule]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsSchedule]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsSchedule]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6520091fe2d7ea514be8b9e44c42898fee35e27318d69b402f959eb25a22cab2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataDatabricksAlertsV2",
    "DataDatabricksAlertsV2Config",
    "DataDatabricksAlertsV2Results",
    "DataDatabricksAlertsV2ResultsEffectiveRunAs",
    "DataDatabricksAlertsV2ResultsEffectiveRunAsOutputReference",
    "DataDatabricksAlertsV2ResultsEvaluation",
    "DataDatabricksAlertsV2ResultsEvaluationNotification",
    "DataDatabricksAlertsV2ResultsEvaluationNotificationOutputReference",
    "DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptions",
    "DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptionsList",
    "DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptionsOutputReference",
    "DataDatabricksAlertsV2ResultsEvaluationOutputReference",
    "DataDatabricksAlertsV2ResultsEvaluationSource",
    "DataDatabricksAlertsV2ResultsEvaluationSourceOutputReference",
    "DataDatabricksAlertsV2ResultsEvaluationThreshold",
    "DataDatabricksAlertsV2ResultsEvaluationThresholdColumn",
    "DataDatabricksAlertsV2ResultsEvaluationThresholdColumnOutputReference",
    "DataDatabricksAlertsV2ResultsEvaluationThresholdOutputReference",
    "DataDatabricksAlertsV2ResultsEvaluationThresholdValue",
    "DataDatabricksAlertsV2ResultsEvaluationThresholdValueOutputReference",
    "DataDatabricksAlertsV2ResultsList",
    "DataDatabricksAlertsV2ResultsOutputReference",
    "DataDatabricksAlertsV2ResultsRunAs",
    "DataDatabricksAlertsV2ResultsRunAsOutputReference",
    "DataDatabricksAlertsV2ResultsSchedule",
    "DataDatabricksAlertsV2ResultsScheduleOutputReference",
]

publication.publish()

def _typecheckingstub__7ca2e6aaba880dad183280c8634fa7ff8bafc5fa410023353064e47441de3ca3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    workspace_id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__47439c8fc9a43b443fc6e8ee491c9c1e623a0c383ce734766dd63e3c246b5ea0(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bdfb6a9a91846813d073937a433503d3c2de19d17098042388dfc11d3e363c62(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__261e2ad0ea21e1b8b5e930d39fb31cdca9cdb69380384f3c9236b419f86ceb7b(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    workspace_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42de5896968e30f292293c6b33938c693c397a3be61b28dd6a2d766383b6b40d(
    *,
    custom_description: typing.Optional[builtins.str] = None,
    custom_summary: typing.Optional[builtins.str] = None,
    display_name: typing.Optional[builtins.str] = None,
    evaluation: typing.Optional[typing.Union[DataDatabricksAlertsV2ResultsEvaluation, typing.Dict[builtins.str, typing.Any]]] = None,
    parent_path: typing.Optional[builtins.str] = None,
    query_text: typing.Optional[builtins.str] = None,
    run_as: typing.Optional[typing.Union[DataDatabricksAlertsV2ResultsRunAs, typing.Dict[builtins.str, typing.Any]]] = None,
    run_as_user_name: typing.Optional[builtins.str] = None,
    schedule: typing.Optional[typing.Union[DataDatabricksAlertsV2ResultsSchedule, typing.Dict[builtins.str, typing.Any]]] = None,
    warehouse_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69f9ab68bc7e3b67e904fe350cb06c0885b3837702d289db6dc9e90aa5dfe12e(
    *,
    service_principal_name: typing.Optional[builtins.str] = None,
    user_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d6fa3e3e943dddb764de73ef10b0c18849160a351dc9dd0af32e00a86733003(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__103ca2f1e77e15c5b28c48f69b38e1c9c2bcdb418081ecc4bc053a6fcdd7dc45(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__201c2bc92953d99704607968a0e657368fd79c839bd40d381c41f5c56d0c24d3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf48cdb85dfd48ba98e105c0bc77d32704549619ea1681f5c4c8a942c1b6c5a9(
    value: typing.Optional[DataDatabricksAlertsV2ResultsEffectiveRunAs],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0641486685b601b064c91749b96039c2aa51a91eba771c5f6e1de642a7a449fa(
    *,
    comparison_operator: typing.Optional[builtins.str] = None,
    empty_result_state: typing.Optional[builtins.str] = None,
    notification: typing.Optional[typing.Union[DataDatabricksAlertsV2ResultsEvaluationNotification, typing.Dict[builtins.str, typing.Any]]] = None,
    source: typing.Optional[typing.Union[DataDatabricksAlertsV2ResultsEvaluationSource, typing.Dict[builtins.str, typing.Any]]] = None,
    threshold: typing.Optional[typing.Union[DataDatabricksAlertsV2ResultsEvaluationThreshold, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa15d966523bf54684e6a5d311d5c10711288c9e4d76ccc45595059e50d3fbeb(
    *,
    notify_on_ok: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    retrigger_seconds: typing.Optional[jsii.Number] = None,
    subscriptions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptions, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d38205ed711b503b12bdac3174be63d3218121e652a401b24229223b81ac09dd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99e42da7c4829d5465c0f1b280c462f112c622747763041c36ae34b45ea16c9a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptions, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a86643abc0c912a3bf38c7eeb381df5423f8ca8f3db068fd8a7b078940db03f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47caf102659becbd130606da636b6dae062f4cef849ca477313a25f1e72ce4ea(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b80f8a98426e067d70a4c720fec16d32684670258e3c4e8903fe2a3cf30687c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluationNotification]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a0a0a94733dd3d72a5542705263eaab8808e4477a67829c5c1fd952053be07b(
    *,
    destination_id: typing.Optional[builtins.str] = None,
    user_email: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08451ca90303b434911f058f2ca1b63e4205d40a4632a067625db8f910d4cb06(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5383068ed320049dbd2aefec156e024b3922a23624079f7b6b8d938819453f24(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f2c55119ae0058f2192eccd17d724fd296e06c3a244c1f80b2db51f2c1b8b00(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1354572149b85a8ad670b65486ce981177ea40cd27ef65fa5e6231e489788af4(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d36652e58cc8e63651c6232c1ff72fafd5b390b05b15120c5edbfcbc6bec93a4(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6114bef81dbc7f0dc9c85b8eabce135d181903bac2dd6f31b160d63c997712b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptions]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4bd5322a63b594e925453efaa1f0c076f6676948ba6f171f566ad43e41ae2b5a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f100e8edbefc08b83cc498bfd5a40cab1f4d7260e1a0d911fd2d6eac82d2db6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a47075685aa5e9a558992359677b8f20d140cb026ccc23a670bbb5ca07bd07e5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7e832b02c34eb8f47d08430e16852e79e0071ed1570f556432c5a919b151aef(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluationNotificationSubscriptions]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7723fc345ae7ddf8bbe35727060b865202f5aea3fe42ecfb06d242048d206f7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ba53eb0144145f318ebadf97724df17e1bebc2725c48f7e6ea3b56a2a46fb72(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc4cc8b2aa80ee6e46e55be985f77f3ad96470aa270fec5202b8365e38c0b9b6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__084cb01d38ca040d76e9964ae9467d7ab06fee92af5bfca6115b04e8f9fcf429(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluation]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d991f580a31ee360f2ac7e5b44e2eec3a740735528c4168154bae5162b2f1cde(
    *,
    aggregation: typing.Optional[builtins.str] = None,
    display: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9014eea490ad023df4c3f5a7d8fa14fbe021b6e4ce107d4c1353f6d541a6def0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4cb09629c2f4af78cca5e0ae51c139fc72e98fbb2bb0c989ed1383704545e8e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0bd811bf41998a43b202a6c939f76f2e9a04a7764634c4c771b50aa23040937(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c0f0ab481878e2e7b3dc21452c38c10c5ee0301728f740c90f136ef55cce615(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1231ae3b91fdf2d809c220be2c6a499cd4d13ad1c536d196f3c0d60cb7cde417(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluationSource]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7cc8807123907cfd289662a48b3b7be7f2c499f262c918a00289c2108a45240(
    *,
    column: typing.Optional[typing.Union[DataDatabricksAlertsV2ResultsEvaluationThresholdColumn, typing.Dict[builtins.str, typing.Any]]] = None,
    value: typing.Optional[typing.Union[DataDatabricksAlertsV2ResultsEvaluationThresholdValue, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39a905dcd2c36b4409738c4650c43bca516e9b62611c126b42fd0737552662e6(
    *,
    aggregation: typing.Optional[builtins.str] = None,
    display: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9123b6064e99890d8465d43a8d0ff9bc46af5e6351c1258d896d57367fcf9fbb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b98ad7514833eef29b3da079e589489d62c8127af61768c92af95c7a8c9e050(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9150a4d27ea2662faa8ab2ab031f0885574fa3a29dc622c4387facf4c43e8366(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5b763ea1dd523ff5ebd45317df73a4416890a66ca4ce2588ddff8d9abcb3b54(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30e99ab378dc8dd5eb9a5f2ed647a70c0b8970f39a1e3745631ea7b0ff5df7bf(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluationThresholdColumn]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5af71af22089e3d287d6a8c410e5f3b43f720be3de54c08202e7135566bd68d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0e6ea01f2e917faccd4022b7ba7daf26f99c75374699bc890284dfc2a7a98ea(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluationThreshold]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1c170932c195ef6814c09bb9d92ed17b09ef39caad2a9444c5f9e9ce706038f(
    *,
    bool_value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    double_value: typing.Optional[jsii.Number] = None,
    string_value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c04e06905f083090b314766527ef5b7484b1338fdc6ec9e0cc4263159622652(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47ea609bb5a14ff13d9b3f7c3afd4c7e3b82d1e908a9d0bd98df06c9c75d396f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0cae7f27b250b503adf9b73bf0d19359fa3ed5cf2f383ac5c326ebad4de3cda(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4be9cb0d2e8887ca015bb50be4ca7d663a0d6b16c09d346351fd9a1a34b5a2c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__167b15379101da19189ab492589c3c5513f38f52ae2998d7afce8cca8b97d803(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsEvaluationThresholdValue]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b225db3f692734362709245468fd087e16bc6dda69873c6b8a6ff3d5ee46b76(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed9b3d2ced28c88971fcee2750186ed2bc016c6d68df3f2922526590d1796d16(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57f3e71a1c431c8e2612292e6b536b14ff715193fae8cd6ad270961038c0d815(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddf32eda5df2450065aef4a5ae641cb925f7b1d63e759c2d6062e36efe7d1abf(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a22b6af0c0ee5e915935833ecb57e5d42b7d092166202b49f1be4f812d53437(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2af083b5edeb6cdaccae4f4ca7f7188849b4bd6bf2402bee6a34e1dab303628a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAlertsV2Results]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2b7349a4718c040d901b5572c193acd5a8087821e1184bfa04c1404c3524221(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8fe5a47a6c757398f99cb91a3f1f8d9c8dd6c7cbe2c04ee0f97e6e5b2ea2c432(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bfe6a4d58585f5a47cadd7be8f0f2e5114e045cdb87824261bf6f4d00abed004(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63d7ed007ea758bc821c070f0bffcaac2ceea0ff378722cd11d08568686f74b3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6444e05de1e4787b7fde22d4912894e77db75050b2cf92c242648d7b2e7e926c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6762e641859f0e059eef215a5fff6926106991d24190d899187f318a8ac90786(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b720f332c00eedca86f802803008178d9bb3cdbdaa8fde19d7d245a860dae9cc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a73c4fba2027af5994d6178e8beb67623dfc413969c4a9b182f4bc45fc61a2d2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebc895bbc1cc2acb3932d26c90f1e7f5e5c3a767b6e0da178a3b7f5519de40b1(
    value: typing.Optional[DataDatabricksAlertsV2Results],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42f78f899052a5073d814344c2f66692a6d70fe7baf382f4cb627b02083ea3a7(
    *,
    service_principal_name: typing.Optional[builtins.str] = None,
    user_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76240c12f2801c7c250349fe6535d1908801d39417e9c79e63fa95415c40f0c7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fca9339b8aa2d873f94267ca5dcf28900af8cead9b18746bef7cfca1dc52739c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08852b9eb5780b914b10d6d3d96d0d54ae26c88749c3633e0d676c83ded6780b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4192eb80150d480652136ae082383c6204e57446dd263ca8c2c35bfbef5c5635(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsRunAs]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e38e827ec22430a6bd8404944cb8b4ce788a154de7eb22f883bc966a2fb949a(
    *,
    pause_status: typing.Optional[builtins.str] = None,
    quartz_cron_schedule: typing.Optional[builtins.str] = None,
    timezone_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5547d193af36aaa130011346f66b5ddf930ff6498c40397dabf46217bd0b5b63(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cdff9068a7bd973472e4fd71307a34812ea0a66a2184bff74013f00cd181bcc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__385ed85e9b286c750c33848c26c5e492352b2b3ed567c4538dbf236fea0a6db6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a43a9efbb65295c266619114289cd1727f7d31e3f99ede7f1f605d49b3126cb3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6520091fe2d7ea514be8b9e44c42898fee35e27318d69b402f959eb25a22cab2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertsV2ResultsSchedule]],
) -> None:
    """Type checking stubs"""
    pass
