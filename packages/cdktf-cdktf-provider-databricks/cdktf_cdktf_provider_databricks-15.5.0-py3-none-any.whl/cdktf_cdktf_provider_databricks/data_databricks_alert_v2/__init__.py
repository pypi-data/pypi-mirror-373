r'''
# `data_databricks_alert_v2`

Refer to the Terraform Registry for docs: [`data_databricks_alert_v2`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2).
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


class DataDatabricksAlertV2(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertV2.DataDatabricksAlertV2",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2 databricks_alert_v2}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        custom_description: typing.Optional[builtins.str] = None,
        custom_summary: typing.Optional[builtins.str] = None,
        display_name: typing.Optional[builtins.str] = None,
        evaluation: typing.Optional[typing.Union["DataDatabricksAlertV2Evaluation", typing.Dict[builtins.str, typing.Any]]] = None,
        parent_path: typing.Optional[builtins.str] = None,
        query_text: typing.Optional[builtins.str] = None,
        run_as: typing.Optional[typing.Union["DataDatabricksAlertV2RunAs", typing.Dict[builtins.str, typing.Any]]] = None,
        run_as_user_name: typing.Optional[builtins.str] = None,
        schedule: typing.Optional[typing.Union["DataDatabricksAlertV2Schedule", typing.Dict[builtins.str, typing.Any]]] = None,
        warehouse_id: typing.Optional[builtins.str] = None,
        workspace_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2 databricks_alert_v2} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param custom_description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#custom_description DataDatabricksAlertV2#custom_description}.
        :param custom_summary: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#custom_summary DataDatabricksAlertV2#custom_summary}.
        :param display_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#display_name DataDatabricksAlertV2#display_name}.
        :param evaluation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#evaluation DataDatabricksAlertV2#evaluation}.
        :param parent_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#parent_path DataDatabricksAlertV2#parent_path}.
        :param query_text: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#query_text DataDatabricksAlertV2#query_text}.
        :param run_as: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#run_as DataDatabricksAlertV2#run_as}.
        :param run_as_user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#run_as_user_name DataDatabricksAlertV2#run_as_user_name}.
        :param schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#schedule DataDatabricksAlertV2#schedule}.
        :param warehouse_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#warehouse_id DataDatabricksAlertV2#warehouse_id}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#workspace_id DataDatabricksAlertV2#workspace_id}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8bd4c25e05dfb053d8df168e430b04c7d7222a2c87e80fb57f63a17b6a695733)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataDatabricksAlertV2Config(
            custom_description=custom_description,
            custom_summary=custom_summary,
            display_name=display_name,
            evaluation=evaluation,
            parent_path=parent_path,
            query_text=query_text,
            run_as=run_as,
            run_as_user_name=run_as_user_name,
            schedule=schedule,
            warehouse_id=warehouse_id,
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
        '''Generates CDKTF code for importing a DataDatabricksAlertV2 resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDatabricksAlertV2 to import.
        :param import_from_id: The id of the existing DataDatabricksAlertV2 that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDatabricksAlertV2 to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1f2deba08dee3aeb6209e16fd9aca19338528fd69504eebc726c4edfa86f0f6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putEvaluation")
    def put_evaluation(
        self,
        *,
        comparison_operator: typing.Optional[builtins.str] = None,
        empty_result_state: typing.Optional[builtins.str] = None,
        notification: typing.Optional[typing.Union["DataDatabricksAlertV2EvaluationNotification", typing.Dict[builtins.str, typing.Any]]] = None,
        source: typing.Optional[typing.Union["DataDatabricksAlertV2EvaluationSource", typing.Dict[builtins.str, typing.Any]]] = None,
        threshold: typing.Optional[typing.Union["DataDatabricksAlertV2EvaluationThreshold", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param comparison_operator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#comparison_operator DataDatabricksAlertV2#comparison_operator}.
        :param empty_result_state: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#empty_result_state DataDatabricksAlertV2#empty_result_state}.
        :param notification: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#notification DataDatabricksAlertV2#notification}.
        :param source: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#source DataDatabricksAlertV2#source}.
        :param threshold: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#threshold DataDatabricksAlertV2#threshold}.
        '''
        value = DataDatabricksAlertV2Evaluation(
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
        :param service_principal_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#service_principal_name DataDatabricksAlertV2#service_principal_name}.
        :param user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#user_name DataDatabricksAlertV2#user_name}.
        '''
        value = DataDatabricksAlertV2RunAs(
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
        :param pause_status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#pause_status DataDatabricksAlertV2#pause_status}.
        :param quartz_cron_schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#quartz_cron_schedule DataDatabricksAlertV2#quartz_cron_schedule}.
        :param timezone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#timezone_id DataDatabricksAlertV2#timezone_id}.
        '''
        value = DataDatabricksAlertV2Schedule(
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
    @jsii.member(jsii_name="createTime")
    def create_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createTime"))

    @builtins.property
    @jsii.member(jsii_name="effectiveRunAs")
    def effective_run_as(self) -> "DataDatabricksAlertV2EffectiveRunAsOutputReference":
        return typing.cast("DataDatabricksAlertV2EffectiveRunAsOutputReference", jsii.get(self, "effectiveRunAs"))

    @builtins.property
    @jsii.member(jsii_name="evaluation")
    def evaluation(self) -> "DataDatabricksAlertV2EvaluationOutputReference":
        return typing.cast("DataDatabricksAlertV2EvaluationOutputReference", jsii.get(self, "evaluation"))

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
    def run_as(self) -> "DataDatabricksAlertV2RunAsOutputReference":
        return typing.cast("DataDatabricksAlertV2RunAsOutputReference", jsii.get(self, "runAs"))

    @builtins.property
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> "DataDatabricksAlertV2ScheduleOutputReference":
        return typing.cast("DataDatabricksAlertV2ScheduleOutputReference", jsii.get(self, "schedule"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAlertV2Evaluation"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAlertV2Evaluation"]], jsii.get(self, "evaluationInput"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAlertV2RunAs"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAlertV2RunAs"]], jsii.get(self, "runAsInput"))

    @builtins.property
    @jsii.member(jsii_name="runAsUserNameInput")
    def run_as_user_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "runAsUserNameInput"))

    @builtins.property
    @jsii.member(jsii_name="scheduleInput")
    def schedule_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAlertV2Schedule"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAlertV2Schedule"]], jsii.get(self, "scheduleInput"))

    @builtins.property
    @jsii.member(jsii_name="warehouseIdInput")
    def warehouse_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "warehouseIdInput"))

    @builtins.property
    @jsii.member(jsii_name="workspaceIdInput")
    def workspace_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workspaceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="customDescription")
    def custom_description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customDescription"))

    @custom_description.setter
    def custom_description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__099566be87adbc22476ad55e5caebf8df9b0ea9fc96f8205095ad63ae33bd929)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customDescription", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="customSummary")
    def custom_summary(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customSummary"))

    @custom_summary.setter
    def custom_summary(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4b01b2ee488ee2f9b8ac380641ae391a62434286e0e3696347dddc0d818dbcd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customSummary", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "displayName"))

    @display_name.setter
    def display_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d97d49451b44932b3fada0eb1d4ede75fded7cf0b40b5e90e0656d3fa6f38f45)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "displayName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parentPath")
    def parent_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parentPath"))

    @parent_path.setter
    def parent_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39e50f3508b5d212413c552b4d28f78c2c60803ac72f330d1c89cfe3fc47fd81)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parentPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="queryText")
    def query_text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queryText"))

    @query_text.setter
    def query_text(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__248c419dbbd147de93af9f05dec4ad8cdf302df4b607940643088e02666c183f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "queryText", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runAsUserName")
    def run_as_user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runAsUserName"))

    @run_as_user_name.setter
    def run_as_user_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__294a3a428d8c0fa50aeece38a66ebe4c6d75c7578ff96146652ddef5f7af2d01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runAsUserName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="warehouseId")
    def warehouse_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "warehouseId"))

    @warehouse_id.setter
    def warehouse_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38151d6782300f06d4cb0520c3004ffc6b20d10501c3385f8ecbb261a166d3d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "warehouseId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workspaceId")
    def workspace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceId"))

    @workspace_id.setter
    def workspace_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5efe59e84e1bcd43758e90bb60b8a619d92f452ec1bd342b567e59933a5192a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workspaceId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertV2.DataDatabricksAlertV2Config",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
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
        "workspace_id": "workspaceId",
    },
)
class DataDatabricksAlertV2Config(_cdktf_9a9027ec.TerraformMetaArguments):
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
        custom_description: typing.Optional[builtins.str] = None,
        custom_summary: typing.Optional[builtins.str] = None,
        display_name: typing.Optional[builtins.str] = None,
        evaluation: typing.Optional[typing.Union["DataDatabricksAlertV2Evaluation", typing.Dict[builtins.str, typing.Any]]] = None,
        parent_path: typing.Optional[builtins.str] = None,
        query_text: typing.Optional[builtins.str] = None,
        run_as: typing.Optional[typing.Union["DataDatabricksAlertV2RunAs", typing.Dict[builtins.str, typing.Any]]] = None,
        run_as_user_name: typing.Optional[builtins.str] = None,
        schedule: typing.Optional[typing.Union["DataDatabricksAlertV2Schedule", typing.Dict[builtins.str, typing.Any]]] = None,
        warehouse_id: typing.Optional[builtins.str] = None,
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
        :param custom_description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#custom_description DataDatabricksAlertV2#custom_description}.
        :param custom_summary: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#custom_summary DataDatabricksAlertV2#custom_summary}.
        :param display_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#display_name DataDatabricksAlertV2#display_name}.
        :param evaluation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#evaluation DataDatabricksAlertV2#evaluation}.
        :param parent_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#parent_path DataDatabricksAlertV2#parent_path}.
        :param query_text: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#query_text DataDatabricksAlertV2#query_text}.
        :param run_as: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#run_as DataDatabricksAlertV2#run_as}.
        :param run_as_user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#run_as_user_name DataDatabricksAlertV2#run_as_user_name}.
        :param schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#schedule DataDatabricksAlertV2#schedule}.
        :param warehouse_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#warehouse_id DataDatabricksAlertV2#warehouse_id}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#workspace_id DataDatabricksAlertV2#workspace_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(evaluation, dict):
            evaluation = DataDatabricksAlertV2Evaluation(**evaluation)
        if isinstance(run_as, dict):
            run_as = DataDatabricksAlertV2RunAs(**run_as)
        if isinstance(schedule, dict):
            schedule = DataDatabricksAlertV2Schedule(**schedule)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2dc2c577299781afd09d460997fec81e9b09297533b05893646c6edfe90f20a1)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
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
    def custom_description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#custom_description DataDatabricksAlertV2#custom_description}.'''
        result = self._values.get("custom_description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_summary(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#custom_summary DataDatabricksAlertV2#custom_summary}.'''
        result = self._values.get("custom_summary")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def display_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#display_name DataDatabricksAlertV2#display_name}.'''
        result = self._values.get("display_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def evaluation(self) -> typing.Optional["DataDatabricksAlertV2Evaluation"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#evaluation DataDatabricksAlertV2#evaluation}.'''
        result = self._values.get("evaluation")
        return typing.cast(typing.Optional["DataDatabricksAlertV2Evaluation"], result)

    @builtins.property
    def parent_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#parent_path DataDatabricksAlertV2#parent_path}.'''
        result = self._values.get("parent_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def query_text(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#query_text DataDatabricksAlertV2#query_text}.'''
        result = self._values.get("query_text")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def run_as(self) -> typing.Optional["DataDatabricksAlertV2RunAs"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#run_as DataDatabricksAlertV2#run_as}.'''
        result = self._values.get("run_as")
        return typing.cast(typing.Optional["DataDatabricksAlertV2RunAs"], result)

    @builtins.property
    def run_as_user_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#run_as_user_name DataDatabricksAlertV2#run_as_user_name}.'''
        result = self._values.get("run_as_user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def schedule(self) -> typing.Optional["DataDatabricksAlertV2Schedule"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#schedule DataDatabricksAlertV2#schedule}.'''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional["DataDatabricksAlertV2Schedule"], result)

    @builtins.property
    def warehouse_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#warehouse_id DataDatabricksAlertV2#warehouse_id}.'''
        result = self._values.get("warehouse_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workspace_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#workspace_id DataDatabricksAlertV2#workspace_id}.'''
        result = self._values.get("workspace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAlertV2Config(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertV2.DataDatabricksAlertV2EffectiveRunAs",
    jsii_struct_bases=[],
    name_mapping={
        "service_principal_name": "servicePrincipalName",
        "user_name": "userName",
    },
)
class DataDatabricksAlertV2EffectiveRunAs:
    def __init__(
        self,
        *,
        service_principal_name: typing.Optional[builtins.str] = None,
        user_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param service_principal_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#service_principal_name DataDatabricksAlertV2#service_principal_name}.
        :param user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#user_name DataDatabricksAlertV2#user_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e820d3fa8fd82fc7027539c15478859b80daa77c2b73595478f2b77be9b35e1)
            check_type(argname="argument service_principal_name", value=service_principal_name, expected_type=type_hints["service_principal_name"])
            check_type(argname="argument user_name", value=user_name, expected_type=type_hints["user_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if service_principal_name is not None:
            self._values["service_principal_name"] = service_principal_name
        if user_name is not None:
            self._values["user_name"] = user_name

    @builtins.property
    def service_principal_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#service_principal_name DataDatabricksAlertV2#service_principal_name}.'''
        result = self._values.get("service_principal_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#user_name DataDatabricksAlertV2#user_name}.'''
        result = self._values.get("user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAlertV2EffectiveRunAs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAlertV2EffectiveRunAsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertV2.DataDatabricksAlertV2EffectiveRunAsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9190e9146c417b949a8e163f5c0a010ed25914e6d3aa1173efd982f491e286d6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2634aa4ae75b66a34d9deabc5fb30ef48dddb6c14dd8aa7d7cd8475eeaf59888)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "servicePrincipalName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userName"))

    @user_name.setter
    def user_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3ad36e3e0d363a9ec2e039c707658532c1965414847d7be181f9c22a623b7d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataDatabricksAlertV2EffectiveRunAs]:
        return typing.cast(typing.Optional[DataDatabricksAlertV2EffectiveRunAs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksAlertV2EffectiveRunAs],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06819f170a3a84a7d373ad212cb421c2ff943ae7374ef15f5cff4ad93ca68358)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertV2.DataDatabricksAlertV2Evaluation",
    jsii_struct_bases=[],
    name_mapping={
        "comparison_operator": "comparisonOperator",
        "empty_result_state": "emptyResultState",
        "notification": "notification",
        "source": "source",
        "threshold": "threshold",
    },
)
class DataDatabricksAlertV2Evaluation:
    def __init__(
        self,
        *,
        comparison_operator: typing.Optional[builtins.str] = None,
        empty_result_state: typing.Optional[builtins.str] = None,
        notification: typing.Optional[typing.Union["DataDatabricksAlertV2EvaluationNotification", typing.Dict[builtins.str, typing.Any]]] = None,
        source: typing.Optional[typing.Union["DataDatabricksAlertV2EvaluationSource", typing.Dict[builtins.str, typing.Any]]] = None,
        threshold: typing.Optional[typing.Union["DataDatabricksAlertV2EvaluationThreshold", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param comparison_operator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#comparison_operator DataDatabricksAlertV2#comparison_operator}.
        :param empty_result_state: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#empty_result_state DataDatabricksAlertV2#empty_result_state}.
        :param notification: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#notification DataDatabricksAlertV2#notification}.
        :param source: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#source DataDatabricksAlertV2#source}.
        :param threshold: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#threshold DataDatabricksAlertV2#threshold}.
        '''
        if isinstance(notification, dict):
            notification = DataDatabricksAlertV2EvaluationNotification(**notification)
        if isinstance(source, dict):
            source = DataDatabricksAlertV2EvaluationSource(**source)
        if isinstance(threshold, dict):
            threshold = DataDatabricksAlertV2EvaluationThreshold(**threshold)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86b0039790992e7e2a8c00391e3b6c630f5d4af4d6db2bd0b7dff9ad7163d1b7)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#comparison_operator DataDatabricksAlertV2#comparison_operator}.'''
        result = self._values.get("comparison_operator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def empty_result_state(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#empty_result_state DataDatabricksAlertV2#empty_result_state}.'''
        result = self._values.get("empty_result_state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notification(
        self,
    ) -> typing.Optional["DataDatabricksAlertV2EvaluationNotification"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#notification DataDatabricksAlertV2#notification}.'''
        result = self._values.get("notification")
        return typing.cast(typing.Optional["DataDatabricksAlertV2EvaluationNotification"], result)

    @builtins.property
    def source(self) -> typing.Optional["DataDatabricksAlertV2EvaluationSource"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#source DataDatabricksAlertV2#source}.'''
        result = self._values.get("source")
        return typing.cast(typing.Optional["DataDatabricksAlertV2EvaluationSource"], result)

    @builtins.property
    def threshold(self) -> typing.Optional["DataDatabricksAlertV2EvaluationThreshold"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#threshold DataDatabricksAlertV2#threshold}.'''
        result = self._values.get("threshold")
        return typing.cast(typing.Optional["DataDatabricksAlertV2EvaluationThreshold"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAlertV2Evaluation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertV2.DataDatabricksAlertV2EvaluationNotification",
    jsii_struct_bases=[],
    name_mapping={
        "notify_on_ok": "notifyOnOk",
        "retrigger_seconds": "retriggerSeconds",
        "subscriptions": "subscriptions",
    },
)
class DataDatabricksAlertV2EvaluationNotification:
    def __init__(
        self,
        *,
        notify_on_ok: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        retrigger_seconds: typing.Optional[jsii.Number] = None,
        subscriptions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksAlertV2EvaluationNotificationSubscriptions", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param notify_on_ok: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#notify_on_ok DataDatabricksAlertV2#notify_on_ok}.
        :param retrigger_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#retrigger_seconds DataDatabricksAlertV2#retrigger_seconds}.
        :param subscriptions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#subscriptions DataDatabricksAlertV2#subscriptions}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b1bbcd5ba02c1c19be884186ec72c2e4e634e222b7f56faeac3fc3f11ddc3c3)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#notify_on_ok DataDatabricksAlertV2#notify_on_ok}.'''
        result = self._values.get("notify_on_ok")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def retrigger_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#retrigger_seconds DataDatabricksAlertV2#retrigger_seconds}.'''
        result = self._values.get("retrigger_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def subscriptions(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksAlertV2EvaluationNotificationSubscriptions"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#subscriptions DataDatabricksAlertV2#subscriptions}.'''
        result = self._values.get("subscriptions")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksAlertV2EvaluationNotificationSubscriptions"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAlertV2EvaluationNotification(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAlertV2EvaluationNotificationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertV2.DataDatabricksAlertV2EvaluationNotificationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__db834bb11ba15f29fd6073311a0084880d9ff17e818da5fd4ac850df1509a2cd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putSubscriptions")
    def put_subscriptions(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksAlertV2EvaluationNotificationSubscriptions", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8dfdb2d455eebb4ae2b52580cc90e97b41d51ef2a87bd21bf1a808bc58cf66f)
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
    ) -> "DataDatabricksAlertV2EvaluationNotificationSubscriptionsList":
        return typing.cast("DataDatabricksAlertV2EvaluationNotificationSubscriptionsList", jsii.get(self, "subscriptions"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksAlertV2EvaluationNotificationSubscriptions"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksAlertV2EvaluationNotificationSubscriptions"]]], jsii.get(self, "subscriptionsInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__9b847330412353612bbb174f274731c0bfed5615397e682d54dcda0ec7fbfa03)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notifyOnOk", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retriggerSeconds")
    def retrigger_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retriggerSeconds"))

    @retrigger_seconds.setter
    def retrigger_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__287957ebdbc4c0ff7bd30155cb0fb56dfa03c2fef74b24b78942e5dbdb989068)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retriggerSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2EvaluationNotification]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2EvaluationNotification]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2EvaluationNotification]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__336bdfe86b71276e3db9288864a50f8a3a5d4b3f2a9bce19faab239273290cf8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertV2.DataDatabricksAlertV2EvaluationNotificationSubscriptions",
    jsii_struct_bases=[],
    name_mapping={"destination_id": "destinationId", "user_email": "userEmail"},
)
class DataDatabricksAlertV2EvaluationNotificationSubscriptions:
    def __init__(
        self,
        *,
        destination_id: typing.Optional[builtins.str] = None,
        user_email: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param destination_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#destination_id DataDatabricksAlertV2#destination_id}.
        :param user_email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#user_email DataDatabricksAlertV2#user_email}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41fb23e4411a754ed471c761999df7d6e8692a4b55844aafa2f5a7e1ab6a25aa)
            check_type(argname="argument destination_id", value=destination_id, expected_type=type_hints["destination_id"])
            check_type(argname="argument user_email", value=user_email, expected_type=type_hints["user_email"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if destination_id is not None:
            self._values["destination_id"] = destination_id
        if user_email is not None:
            self._values["user_email"] = user_email

    @builtins.property
    def destination_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#destination_id DataDatabricksAlertV2#destination_id}.'''
        result = self._values.get("destination_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_email(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#user_email DataDatabricksAlertV2#user_email}.'''
        result = self._values.get("user_email")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAlertV2EvaluationNotificationSubscriptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAlertV2EvaluationNotificationSubscriptionsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertV2.DataDatabricksAlertV2EvaluationNotificationSubscriptionsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ab58ae05f97b69acf45f81028fe498b74b7af1305e273db6bb43ea15db98f84b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksAlertV2EvaluationNotificationSubscriptionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8798282347b5728ee9947e6f1d681ddfcabc0bad0754199378a28d091e13dfae)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksAlertV2EvaluationNotificationSubscriptionsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0086dc9fd8c42f97055df5648933ee996df9e125aee15d7cae907a8797850d44)
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
            type_hints = typing.get_type_hints(_typecheckingstub__58e8ea546ce29e709c37c5dacce6021c61df813863c41d3ee9e859cad693c414)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9a7065059ef5757424611896c882e85566a77954d05e96cb44f6a9f6a7c87d96)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAlertV2EvaluationNotificationSubscriptions]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAlertV2EvaluationNotificationSubscriptions]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAlertV2EvaluationNotificationSubscriptions]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8bee6d687f909f25b1195f141d4f1c54df862519cc0860a48478a4173467334d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAlertV2EvaluationNotificationSubscriptionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertV2.DataDatabricksAlertV2EvaluationNotificationSubscriptionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__853d3521df1395469462e44b7aa52536ae35e6a550ba6dc674483cc967a1c996)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8b3894cb3cdabfd643472af8ccbfee4e0a2f0794263035e78aee081281ab4e11)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destinationId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userEmail")
    def user_email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userEmail"))

    @user_email.setter
    def user_email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41858276d8a0760c3633f8a34bbc89326390b99e1d54e3dc7e3a44629494acf6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userEmail", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2EvaluationNotificationSubscriptions]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2EvaluationNotificationSubscriptions]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2EvaluationNotificationSubscriptions]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7036044c7cc5a8006ae9f108cd35db94d2b0d3eac23281bb7acddbae1846488f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAlertV2EvaluationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertV2.DataDatabricksAlertV2EvaluationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c2c8ecee29368ab37c90294d58271d5f10f7739242038ff21b8de6c43ba525e6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putNotification")
    def put_notification(
        self,
        *,
        notify_on_ok: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        retrigger_seconds: typing.Optional[jsii.Number] = None,
        subscriptions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksAlertV2EvaluationNotificationSubscriptions, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param notify_on_ok: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#notify_on_ok DataDatabricksAlertV2#notify_on_ok}.
        :param retrigger_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#retrigger_seconds DataDatabricksAlertV2#retrigger_seconds}.
        :param subscriptions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#subscriptions DataDatabricksAlertV2#subscriptions}.
        '''
        value = DataDatabricksAlertV2EvaluationNotification(
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
        :param aggregation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#aggregation DataDatabricksAlertV2#aggregation}.
        :param display: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#display DataDatabricksAlertV2#display}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#name DataDatabricksAlertV2#name}.
        '''
        value = DataDatabricksAlertV2EvaluationSource(
            aggregation=aggregation, display=display, name=name
        )

        return typing.cast(None, jsii.invoke(self, "putSource", [value]))

    @jsii.member(jsii_name="putThreshold")
    def put_threshold(
        self,
        *,
        column: typing.Optional[typing.Union["DataDatabricksAlertV2EvaluationThresholdColumn", typing.Dict[builtins.str, typing.Any]]] = None,
        value: typing.Optional[typing.Union["DataDatabricksAlertV2EvaluationThresholdValue", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param column: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#column DataDatabricksAlertV2#column}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#value DataDatabricksAlertV2#value}.
        '''
        value_ = DataDatabricksAlertV2EvaluationThreshold(column=column, value=value)

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
    ) -> DataDatabricksAlertV2EvaluationNotificationOutputReference:
        return typing.cast(DataDatabricksAlertV2EvaluationNotificationOutputReference, jsii.get(self, "notification"))

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> "DataDatabricksAlertV2EvaluationSourceOutputReference":
        return typing.cast("DataDatabricksAlertV2EvaluationSourceOutputReference", jsii.get(self, "source"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> "DataDatabricksAlertV2EvaluationThresholdOutputReference":
        return typing.cast("DataDatabricksAlertV2EvaluationThresholdOutputReference", jsii.get(self, "threshold"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2EvaluationNotification]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2EvaluationNotification]], jsii.get(self, "notificationInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceInput")
    def source_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAlertV2EvaluationSource"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAlertV2EvaluationSource"]], jsii.get(self, "sourceInput"))

    @builtins.property
    @jsii.member(jsii_name="thresholdInput")
    def threshold_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAlertV2EvaluationThreshold"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAlertV2EvaluationThreshold"]], jsii.get(self, "thresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="comparisonOperator")
    def comparison_operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comparisonOperator"))

    @comparison_operator.setter
    def comparison_operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7ed1cc92dec2bab7e685166bd7701dec9953962be5e730652740563ea96af90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comparisonOperator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="emptyResultState")
    def empty_result_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emptyResultState"))

    @empty_result_state.setter
    def empty_result_state(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6f49d0f1d9132ed4334038111bd3f6f53120dd2e65bc32ad179152f8d07e470)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emptyResultState", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2Evaluation]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2Evaluation]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2Evaluation]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5cc84bb3e41df015edddad310f7cd7a7afe05db473a2387f8a7de32990bb4c2c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertV2.DataDatabricksAlertV2EvaluationSource",
    jsii_struct_bases=[],
    name_mapping={"aggregation": "aggregation", "display": "display", "name": "name"},
)
class DataDatabricksAlertV2EvaluationSource:
    def __init__(
        self,
        *,
        aggregation: typing.Optional[builtins.str] = None,
        display: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param aggregation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#aggregation DataDatabricksAlertV2#aggregation}.
        :param display: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#display DataDatabricksAlertV2#display}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#name DataDatabricksAlertV2#name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8535b4ffbaf9c0fd32a9bf4d476c8f675c1279273836b97e8cb81f66f3cff897)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#aggregation DataDatabricksAlertV2#aggregation}.'''
        result = self._values.get("aggregation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def display(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#display DataDatabricksAlertV2#display}.'''
        result = self._values.get("display")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#name DataDatabricksAlertV2#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAlertV2EvaluationSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAlertV2EvaluationSourceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertV2.DataDatabricksAlertV2EvaluationSourceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__736cca5d4558d8b739b94d87d7856684624d2d100cce8722b587afe2786e44c9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4e50e0a79cb5b78829b9cea93c173ccb2369221ec77738452b91ae9b8e25f854)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "aggregation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="display")
    def display(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "display"))

    @display.setter
    def display(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58ebc5cdd5b12c8d7a99380202632d83bc0dc7d1505a2af092090869779856e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "display", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__986187c92927104e1233010b52e026a3843ba682c61caf60c751336eb1123f4d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2EvaluationSource]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2EvaluationSource]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2EvaluationSource]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__910acb0824cda00181a79e60deeec1a309a7dc6f578b8fbc91e936ad33478d3e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertV2.DataDatabricksAlertV2EvaluationThreshold",
    jsii_struct_bases=[],
    name_mapping={"column": "column", "value": "value"},
)
class DataDatabricksAlertV2EvaluationThreshold:
    def __init__(
        self,
        *,
        column: typing.Optional[typing.Union["DataDatabricksAlertV2EvaluationThresholdColumn", typing.Dict[builtins.str, typing.Any]]] = None,
        value: typing.Optional[typing.Union["DataDatabricksAlertV2EvaluationThresholdValue", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param column: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#column DataDatabricksAlertV2#column}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#value DataDatabricksAlertV2#value}.
        '''
        if isinstance(column, dict):
            column = DataDatabricksAlertV2EvaluationThresholdColumn(**column)
        if isinstance(value, dict):
            value = DataDatabricksAlertV2EvaluationThresholdValue(**value)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b1b9220cb878da0bfd481f334071e8d3ebd4b4bc239c66f3e5e333067c3f4d4)
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
    ) -> typing.Optional["DataDatabricksAlertV2EvaluationThresholdColumn"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#column DataDatabricksAlertV2#column}.'''
        result = self._values.get("column")
        return typing.cast(typing.Optional["DataDatabricksAlertV2EvaluationThresholdColumn"], result)

    @builtins.property
    def value(self) -> typing.Optional["DataDatabricksAlertV2EvaluationThresholdValue"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#value DataDatabricksAlertV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional["DataDatabricksAlertV2EvaluationThresholdValue"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAlertV2EvaluationThreshold(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertV2.DataDatabricksAlertV2EvaluationThresholdColumn",
    jsii_struct_bases=[],
    name_mapping={"aggregation": "aggregation", "display": "display", "name": "name"},
)
class DataDatabricksAlertV2EvaluationThresholdColumn:
    def __init__(
        self,
        *,
        aggregation: typing.Optional[builtins.str] = None,
        display: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param aggregation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#aggregation DataDatabricksAlertV2#aggregation}.
        :param display: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#display DataDatabricksAlertV2#display}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#name DataDatabricksAlertV2#name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__769015db9e72575d38abfe05dfe298df2c5b3dc58abf1f61a8aeb5dbc104c96c)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#aggregation DataDatabricksAlertV2#aggregation}.'''
        result = self._values.get("aggregation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def display(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#display DataDatabricksAlertV2#display}.'''
        result = self._values.get("display")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#name DataDatabricksAlertV2#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAlertV2EvaluationThresholdColumn(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAlertV2EvaluationThresholdColumnOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertV2.DataDatabricksAlertV2EvaluationThresholdColumnOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3291eced178480eecc18ede29743b39c931b3019dfa0645da12d974727da0c55)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a734e088c2383a7783b37a59035b157c764f199843c74e2fb1c30d2e5e0b8b31)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "aggregation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="display")
    def display(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "display"))

    @display.setter
    def display(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ace5b75af3be3dba3ab4d0aea529d05de2606efc695bdc9f414481dfe3177ff0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "display", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b6a512c696650f23e2bbb1eb3e7a1e940016d8e208391cb27ed4eafda4508e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2EvaluationThresholdColumn]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2EvaluationThresholdColumn]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2EvaluationThresholdColumn]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__943ae1c1b5f7dd50f5e4aeb5780e15f128c6f6aedcaeac9a834e606bb3a638e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAlertV2EvaluationThresholdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertV2.DataDatabricksAlertV2EvaluationThresholdOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ac96e85b47c62c8ef14f4aff3d445e21faee90f5149f9da768cfc0a7ddff204c)
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
        :param aggregation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#aggregation DataDatabricksAlertV2#aggregation}.
        :param display: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#display DataDatabricksAlertV2#display}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#name DataDatabricksAlertV2#name}.
        '''
        value = DataDatabricksAlertV2EvaluationThresholdColumn(
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
        :param bool_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#bool_value DataDatabricksAlertV2#bool_value}.
        :param double_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#double_value DataDatabricksAlertV2#double_value}.
        :param string_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#string_value DataDatabricksAlertV2#string_value}.
        '''
        value = DataDatabricksAlertV2EvaluationThresholdValue(
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
    def column(self) -> DataDatabricksAlertV2EvaluationThresholdColumnOutputReference:
        return typing.cast(DataDatabricksAlertV2EvaluationThresholdColumnOutputReference, jsii.get(self, "column"))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> "DataDatabricksAlertV2EvaluationThresholdValueOutputReference":
        return typing.cast("DataDatabricksAlertV2EvaluationThresholdValueOutputReference", jsii.get(self, "value"))

    @builtins.property
    @jsii.member(jsii_name="columnInput")
    def column_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2EvaluationThresholdColumn]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2EvaluationThresholdColumn]], jsii.get(self, "columnInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAlertV2EvaluationThresholdValue"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAlertV2EvaluationThresholdValue"]], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2EvaluationThreshold]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2EvaluationThreshold]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2EvaluationThreshold]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc15223d5469a115352ebb2bb55fa7710b68103de2725a3c022fe7494e85685f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertV2.DataDatabricksAlertV2EvaluationThresholdValue",
    jsii_struct_bases=[],
    name_mapping={
        "bool_value": "boolValue",
        "double_value": "doubleValue",
        "string_value": "stringValue",
    },
)
class DataDatabricksAlertV2EvaluationThresholdValue:
    def __init__(
        self,
        *,
        bool_value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        double_value: typing.Optional[jsii.Number] = None,
        string_value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bool_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#bool_value DataDatabricksAlertV2#bool_value}.
        :param double_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#double_value DataDatabricksAlertV2#double_value}.
        :param string_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#string_value DataDatabricksAlertV2#string_value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4754eb5548a9591baeb3a64d3967571966f09b53b52ae28eb1b8a1a1858eeb6)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#bool_value DataDatabricksAlertV2#bool_value}.'''
        result = self._values.get("bool_value")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def double_value(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#double_value DataDatabricksAlertV2#double_value}.'''
        result = self._values.get("double_value")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def string_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#string_value DataDatabricksAlertV2#string_value}.'''
        result = self._values.get("string_value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAlertV2EvaluationThresholdValue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAlertV2EvaluationThresholdValueOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertV2.DataDatabricksAlertV2EvaluationThresholdValueOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__244883a3cc335594f7da0ff8f624bc3147a0ba303e33bd0b67139591144bf63b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b6a975d9600e5e7f8722b18086a1ec683725f60ded6abeec80c353a44f01c68b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boolValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="doubleValue")
    def double_value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "doubleValue"))

    @double_value.setter
    def double_value(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__963953310e3602652ba241dcd9b81093fd631aa45721bd6f6060505f7a42c1d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "doubleValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stringValue")
    def string_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stringValue"))

    @string_value.setter
    def string_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__083d73f51130c20c9813a656c0d0ebbc6651695c06fd985aa62ff95e2aa2ea44)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stringValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2EvaluationThresholdValue]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2EvaluationThresholdValue]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2EvaluationThresholdValue]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05511e89915c37f6f617f03596ce10f7848d3f3ab668e5b83c85035817fd1fa0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertV2.DataDatabricksAlertV2RunAs",
    jsii_struct_bases=[],
    name_mapping={
        "service_principal_name": "servicePrincipalName",
        "user_name": "userName",
    },
)
class DataDatabricksAlertV2RunAs:
    def __init__(
        self,
        *,
        service_principal_name: typing.Optional[builtins.str] = None,
        user_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param service_principal_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#service_principal_name DataDatabricksAlertV2#service_principal_name}.
        :param user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#user_name DataDatabricksAlertV2#user_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec61280fa77cca28c6a171ad66eddafd5b737ec9efb8f7e0761bbcdd40a9e933)
            check_type(argname="argument service_principal_name", value=service_principal_name, expected_type=type_hints["service_principal_name"])
            check_type(argname="argument user_name", value=user_name, expected_type=type_hints["user_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if service_principal_name is not None:
            self._values["service_principal_name"] = service_principal_name
        if user_name is not None:
            self._values["user_name"] = user_name

    @builtins.property
    def service_principal_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#service_principal_name DataDatabricksAlertV2#service_principal_name}.'''
        result = self._values.get("service_principal_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#user_name DataDatabricksAlertV2#user_name}.'''
        result = self._values.get("user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAlertV2RunAs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAlertV2RunAsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertV2.DataDatabricksAlertV2RunAsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8b380b58dc08e2e883899b868114080e6fdfdc2509a11a917a9fca3ee7e028ca)
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
            type_hints = typing.get_type_hints(_typecheckingstub__00995f3345466eb100ea1edd442cd983cd40fba2f22b0a8c41b9432732472423)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "servicePrincipalName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userName"))

    @user_name.setter
    def user_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6025e5b923c209b7af9173d1bb8f6809f5943b362136fecf5f668c62e51fc232)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2RunAs]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2RunAs]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2RunAs]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8989a1c63d5e5fb7494df394e49a9c3bc72b3d0a29f9b6e05db6deb8702ea0e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertV2.DataDatabricksAlertV2Schedule",
    jsii_struct_bases=[],
    name_mapping={
        "pause_status": "pauseStatus",
        "quartz_cron_schedule": "quartzCronSchedule",
        "timezone_id": "timezoneId",
    },
)
class DataDatabricksAlertV2Schedule:
    def __init__(
        self,
        *,
        pause_status: typing.Optional[builtins.str] = None,
        quartz_cron_schedule: typing.Optional[builtins.str] = None,
        timezone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param pause_status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#pause_status DataDatabricksAlertV2#pause_status}.
        :param quartz_cron_schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#quartz_cron_schedule DataDatabricksAlertV2#quartz_cron_schedule}.
        :param timezone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#timezone_id DataDatabricksAlertV2#timezone_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__996abeafe1dd2c0433a3690cbb38de5f67aac16b5182fb788e330ea52e373c84)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#pause_status DataDatabricksAlertV2#pause_status}.'''
        result = self._values.get("pause_status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def quartz_cron_schedule(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#quartz_cron_schedule DataDatabricksAlertV2#quartz_cron_schedule}.'''
        result = self._values.get("quartz_cron_schedule")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timezone_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/alert_v2#timezone_id DataDatabricksAlertV2#timezone_id}.'''
        result = self._values.get("timezone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAlertV2Schedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAlertV2ScheduleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAlertV2.DataDatabricksAlertV2ScheduleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d6bc67801ad7299f147e23237a8e669fc3e2a8e85216f51deead63f51ce24c3b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__70748a7cdfdaa2794bef4291c04165f7402b3c14f62d1439b1456d3ddd8f8630)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pauseStatus", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="quartzCronSchedule")
    def quartz_cron_schedule(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "quartzCronSchedule"))

    @quartz_cron_schedule.setter
    def quartz_cron_schedule(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__973325b57f67a1d8044a9e3dbf568d1dfaf376e715cf8467362c054bfd06db3a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "quartzCronSchedule", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timezoneId")
    def timezone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timezoneId"))

    @timezone_id.setter
    def timezone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04c49ad41f8a57ef9722973ff46082b381c468d3e26e3920b996d25fab79878c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timezoneId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2Schedule]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2Schedule]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2Schedule]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__675d8bda754d1eb2ec0207ab9bf9ca59c9a3107d4f1c6057f7e852ba135306a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataDatabricksAlertV2",
    "DataDatabricksAlertV2Config",
    "DataDatabricksAlertV2EffectiveRunAs",
    "DataDatabricksAlertV2EffectiveRunAsOutputReference",
    "DataDatabricksAlertV2Evaluation",
    "DataDatabricksAlertV2EvaluationNotification",
    "DataDatabricksAlertV2EvaluationNotificationOutputReference",
    "DataDatabricksAlertV2EvaluationNotificationSubscriptions",
    "DataDatabricksAlertV2EvaluationNotificationSubscriptionsList",
    "DataDatabricksAlertV2EvaluationNotificationSubscriptionsOutputReference",
    "DataDatabricksAlertV2EvaluationOutputReference",
    "DataDatabricksAlertV2EvaluationSource",
    "DataDatabricksAlertV2EvaluationSourceOutputReference",
    "DataDatabricksAlertV2EvaluationThreshold",
    "DataDatabricksAlertV2EvaluationThresholdColumn",
    "DataDatabricksAlertV2EvaluationThresholdColumnOutputReference",
    "DataDatabricksAlertV2EvaluationThresholdOutputReference",
    "DataDatabricksAlertV2EvaluationThresholdValue",
    "DataDatabricksAlertV2EvaluationThresholdValueOutputReference",
    "DataDatabricksAlertV2RunAs",
    "DataDatabricksAlertV2RunAsOutputReference",
    "DataDatabricksAlertV2Schedule",
    "DataDatabricksAlertV2ScheduleOutputReference",
]

publication.publish()

def _typecheckingstub__8bd4c25e05dfb053d8df168e430b04c7d7222a2c87e80fb57f63a17b6a695733(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    custom_description: typing.Optional[builtins.str] = None,
    custom_summary: typing.Optional[builtins.str] = None,
    display_name: typing.Optional[builtins.str] = None,
    evaluation: typing.Optional[typing.Union[DataDatabricksAlertV2Evaluation, typing.Dict[builtins.str, typing.Any]]] = None,
    parent_path: typing.Optional[builtins.str] = None,
    query_text: typing.Optional[builtins.str] = None,
    run_as: typing.Optional[typing.Union[DataDatabricksAlertV2RunAs, typing.Dict[builtins.str, typing.Any]]] = None,
    run_as_user_name: typing.Optional[builtins.str] = None,
    schedule: typing.Optional[typing.Union[DataDatabricksAlertV2Schedule, typing.Dict[builtins.str, typing.Any]]] = None,
    warehouse_id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__d1f2deba08dee3aeb6209e16fd9aca19338528fd69504eebc726c4edfa86f0f6(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__099566be87adbc22476ad55e5caebf8df9b0ea9fc96f8205095ad63ae33bd929(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4b01b2ee488ee2f9b8ac380641ae391a62434286e0e3696347dddc0d818dbcd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d97d49451b44932b3fada0eb1d4ede75fded7cf0b40b5e90e0656d3fa6f38f45(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39e50f3508b5d212413c552b4d28f78c2c60803ac72f330d1c89cfe3fc47fd81(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__248c419dbbd147de93af9f05dec4ad8cdf302df4b607940643088e02666c183f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__294a3a428d8c0fa50aeece38a66ebe4c6d75c7578ff96146652ddef5f7af2d01(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38151d6782300f06d4cb0520c3004ffc6b20d10501c3385f8ecbb261a166d3d0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5efe59e84e1bcd43758e90bb60b8a619d92f452ec1bd342b567e59933a5192a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2dc2c577299781afd09d460997fec81e9b09297533b05893646c6edfe90f20a1(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    custom_description: typing.Optional[builtins.str] = None,
    custom_summary: typing.Optional[builtins.str] = None,
    display_name: typing.Optional[builtins.str] = None,
    evaluation: typing.Optional[typing.Union[DataDatabricksAlertV2Evaluation, typing.Dict[builtins.str, typing.Any]]] = None,
    parent_path: typing.Optional[builtins.str] = None,
    query_text: typing.Optional[builtins.str] = None,
    run_as: typing.Optional[typing.Union[DataDatabricksAlertV2RunAs, typing.Dict[builtins.str, typing.Any]]] = None,
    run_as_user_name: typing.Optional[builtins.str] = None,
    schedule: typing.Optional[typing.Union[DataDatabricksAlertV2Schedule, typing.Dict[builtins.str, typing.Any]]] = None,
    warehouse_id: typing.Optional[builtins.str] = None,
    workspace_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e820d3fa8fd82fc7027539c15478859b80daa77c2b73595478f2b77be9b35e1(
    *,
    service_principal_name: typing.Optional[builtins.str] = None,
    user_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9190e9146c417b949a8e163f5c0a010ed25914e6d3aa1173efd982f491e286d6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2634aa4ae75b66a34d9deabc5fb30ef48dddb6c14dd8aa7d7cd8475eeaf59888(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3ad36e3e0d363a9ec2e039c707658532c1965414847d7be181f9c22a623b7d4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06819f170a3a84a7d373ad212cb421c2ff943ae7374ef15f5cff4ad93ca68358(
    value: typing.Optional[DataDatabricksAlertV2EffectiveRunAs],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86b0039790992e7e2a8c00391e3b6c630f5d4af4d6db2bd0b7dff9ad7163d1b7(
    *,
    comparison_operator: typing.Optional[builtins.str] = None,
    empty_result_state: typing.Optional[builtins.str] = None,
    notification: typing.Optional[typing.Union[DataDatabricksAlertV2EvaluationNotification, typing.Dict[builtins.str, typing.Any]]] = None,
    source: typing.Optional[typing.Union[DataDatabricksAlertV2EvaluationSource, typing.Dict[builtins.str, typing.Any]]] = None,
    threshold: typing.Optional[typing.Union[DataDatabricksAlertV2EvaluationThreshold, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b1bbcd5ba02c1c19be884186ec72c2e4e634e222b7f56faeac3fc3f11ddc3c3(
    *,
    notify_on_ok: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    retrigger_seconds: typing.Optional[jsii.Number] = None,
    subscriptions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksAlertV2EvaluationNotificationSubscriptions, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db834bb11ba15f29fd6073311a0084880d9ff17e818da5fd4ac850df1509a2cd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8dfdb2d455eebb4ae2b52580cc90e97b41d51ef2a87bd21bf1a808bc58cf66f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksAlertV2EvaluationNotificationSubscriptions, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b847330412353612bbb174f274731c0bfed5615397e682d54dcda0ec7fbfa03(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__287957ebdbc4c0ff7bd30155cb0fb56dfa03c2fef74b24b78942e5dbdb989068(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__336bdfe86b71276e3db9288864a50f8a3a5d4b3f2a9bce19faab239273290cf8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2EvaluationNotification]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41fb23e4411a754ed471c761999df7d6e8692a4b55844aafa2f5a7e1ab6a25aa(
    *,
    destination_id: typing.Optional[builtins.str] = None,
    user_email: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab58ae05f97b69acf45f81028fe498b74b7af1305e273db6bb43ea15db98f84b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8798282347b5728ee9947e6f1d681ddfcabc0bad0754199378a28d091e13dfae(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0086dc9fd8c42f97055df5648933ee996df9e125aee15d7cae907a8797850d44(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58e8ea546ce29e709c37c5dacce6021c61df813863c41d3ee9e859cad693c414(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a7065059ef5757424611896c882e85566a77954d05e96cb44f6a9f6a7c87d96(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8bee6d687f909f25b1195f141d4f1c54df862519cc0860a48478a4173467334d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAlertV2EvaluationNotificationSubscriptions]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__853d3521df1395469462e44b7aa52536ae35e6a550ba6dc674483cc967a1c996(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b3894cb3cdabfd643472af8ccbfee4e0a2f0794263035e78aee081281ab4e11(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41858276d8a0760c3633f8a34bbc89326390b99e1d54e3dc7e3a44629494acf6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7036044c7cc5a8006ae9f108cd35db94d2b0d3eac23281bb7acddbae1846488f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2EvaluationNotificationSubscriptions]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2c8ecee29368ab37c90294d58271d5f10f7739242038ff21b8de6c43ba525e6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7ed1cc92dec2bab7e685166bd7701dec9953962be5e730652740563ea96af90(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6f49d0f1d9132ed4334038111bd3f6f53120dd2e65bc32ad179152f8d07e470(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5cc84bb3e41df015edddad310f7cd7a7afe05db473a2387f8a7de32990bb4c2c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2Evaluation]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8535b4ffbaf9c0fd32a9bf4d476c8f675c1279273836b97e8cb81f66f3cff897(
    *,
    aggregation: typing.Optional[builtins.str] = None,
    display: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__736cca5d4558d8b739b94d87d7856684624d2d100cce8722b587afe2786e44c9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e50e0a79cb5b78829b9cea93c173ccb2369221ec77738452b91ae9b8e25f854(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58ebc5cdd5b12c8d7a99380202632d83bc0dc7d1505a2af092090869779856e5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__986187c92927104e1233010b52e026a3843ba682c61caf60c751336eb1123f4d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__910acb0824cda00181a79e60deeec1a309a7dc6f578b8fbc91e936ad33478d3e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2EvaluationSource]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b1b9220cb878da0bfd481f334071e8d3ebd4b4bc239c66f3e5e333067c3f4d4(
    *,
    column: typing.Optional[typing.Union[DataDatabricksAlertV2EvaluationThresholdColumn, typing.Dict[builtins.str, typing.Any]]] = None,
    value: typing.Optional[typing.Union[DataDatabricksAlertV2EvaluationThresholdValue, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__769015db9e72575d38abfe05dfe298df2c5b3dc58abf1f61a8aeb5dbc104c96c(
    *,
    aggregation: typing.Optional[builtins.str] = None,
    display: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3291eced178480eecc18ede29743b39c931b3019dfa0645da12d974727da0c55(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a734e088c2383a7783b37a59035b157c764f199843c74e2fb1c30d2e5e0b8b31(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ace5b75af3be3dba3ab4d0aea529d05de2606efc695bdc9f414481dfe3177ff0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b6a512c696650f23e2bbb1eb3e7a1e940016d8e208391cb27ed4eafda4508e6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__943ae1c1b5f7dd50f5e4aeb5780e15f128c6f6aedcaeac9a834e606bb3a638e1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2EvaluationThresholdColumn]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac96e85b47c62c8ef14f4aff3d445e21faee90f5149f9da768cfc0a7ddff204c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc15223d5469a115352ebb2bb55fa7710b68103de2725a3c022fe7494e85685f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2EvaluationThreshold]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4754eb5548a9591baeb3a64d3967571966f09b53b52ae28eb1b8a1a1858eeb6(
    *,
    bool_value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    double_value: typing.Optional[jsii.Number] = None,
    string_value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__244883a3cc335594f7da0ff8f624bc3147a0ba303e33bd0b67139591144bf63b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6a975d9600e5e7f8722b18086a1ec683725f60ded6abeec80c353a44f01c68b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__963953310e3602652ba241dcd9b81093fd631aa45721bd6f6060505f7a42c1d3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__083d73f51130c20c9813a656c0d0ebbc6651695c06fd985aa62ff95e2aa2ea44(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05511e89915c37f6f617f03596ce10f7848d3f3ab668e5b83c85035817fd1fa0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2EvaluationThresholdValue]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec61280fa77cca28c6a171ad66eddafd5b737ec9efb8f7e0761bbcdd40a9e933(
    *,
    service_principal_name: typing.Optional[builtins.str] = None,
    user_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b380b58dc08e2e883899b868114080e6fdfdc2509a11a917a9fca3ee7e028ca(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00995f3345466eb100ea1edd442cd983cd40fba2f22b0a8c41b9432732472423(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6025e5b923c209b7af9173d1bb8f6809f5943b362136fecf5f668c62e51fc232(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8989a1c63d5e5fb7494df394e49a9c3bc72b3d0a29f9b6e05db6deb8702ea0e5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2RunAs]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__996abeafe1dd2c0433a3690cbb38de5f67aac16b5182fb788e330ea52e373c84(
    *,
    pause_status: typing.Optional[builtins.str] = None,
    quartz_cron_schedule: typing.Optional[builtins.str] = None,
    timezone_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6bc67801ad7299f147e23237a8e669fc3e2a8e85216f51deead63f51ce24c3b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70748a7cdfdaa2794bef4291c04165f7402b3c14f62d1439b1456d3ddd8f8630(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__973325b57f67a1d8044a9e3dbf568d1dfaf376e715cf8467362c054bfd06db3a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04c49ad41f8a57ef9722973ff46082b381c468d3e26e3920b996d25fab79878c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__675d8bda754d1eb2ec0207ab9bf9ca59c9a3107d4f1c6057f7e852ba135306a8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAlertV2Schedule]],
) -> None:
    """Type checking stubs"""
    pass
