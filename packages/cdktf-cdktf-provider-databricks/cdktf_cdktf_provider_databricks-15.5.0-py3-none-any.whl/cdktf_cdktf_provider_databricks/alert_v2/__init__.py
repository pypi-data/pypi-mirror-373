r'''
# `databricks_alert_v2`

Refer to the Terraform Registry for docs: [`databricks_alert_v2`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2).
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


class AlertV2(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.alertV2.AlertV2",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2 databricks_alert_v2}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        custom_description: typing.Optional[builtins.str] = None,
        custom_summary: typing.Optional[builtins.str] = None,
        display_name: typing.Optional[builtins.str] = None,
        evaluation: typing.Optional[typing.Union["AlertV2Evaluation", typing.Dict[builtins.str, typing.Any]]] = None,
        parent_path: typing.Optional[builtins.str] = None,
        query_text: typing.Optional[builtins.str] = None,
        run_as: typing.Optional[typing.Union["AlertV2RunAs", typing.Dict[builtins.str, typing.Any]]] = None,
        run_as_user_name: typing.Optional[builtins.str] = None,
        schedule: typing.Optional[typing.Union["AlertV2Schedule", typing.Dict[builtins.str, typing.Any]]] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2 databricks_alert_v2} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param custom_description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#custom_description AlertV2#custom_description}.
        :param custom_summary: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#custom_summary AlertV2#custom_summary}.
        :param display_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#display_name AlertV2#display_name}.
        :param evaluation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#evaluation AlertV2#evaluation}.
        :param parent_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#parent_path AlertV2#parent_path}.
        :param query_text: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#query_text AlertV2#query_text}.
        :param run_as: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#run_as AlertV2#run_as}.
        :param run_as_user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#run_as_user_name AlertV2#run_as_user_name}.
        :param schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#schedule AlertV2#schedule}.
        :param warehouse_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#warehouse_id AlertV2#warehouse_id}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#workspace_id AlertV2#workspace_id}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dca0b185eb5c03093428da7efbdaf124a32abb6740d00836e21bb53ad001b428)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = AlertV2Config(
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
        '''Generates CDKTF code for importing a AlertV2 resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AlertV2 to import.
        :param import_from_id: The id of the existing AlertV2 that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AlertV2 to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57728441fa3750fa73b25165bb4265a235c17448c0b5eac0a14abf182b9b40ad)
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
        notification: typing.Optional[typing.Union["AlertV2EvaluationNotification", typing.Dict[builtins.str, typing.Any]]] = None,
        source: typing.Optional[typing.Union["AlertV2EvaluationSource", typing.Dict[builtins.str, typing.Any]]] = None,
        threshold: typing.Optional[typing.Union["AlertV2EvaluationThreshold", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param comparison_operator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#comparison_operator AlertV2#comparison_operator}.
        :param empty_result_state: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#empty_result_state AlertV2#empty_result_state}.
        :param notification: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#notification AlertV2#notification}.
        :param source: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#source AlertV2#source}.
        :param threshold: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#threshold AlertV2#threshold}.
        '''
        value = AlertV2Evaluation(
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
        :param service_principal_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#service_principal_name AlertV2#service_principal_name}.
        :param user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#user_name AlertV2#user_name}.
        '''
        value = AlertV2RunAs(
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
        :param pause_status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#pause_status AlertV2#pause_status}.
        :param quartz_cron_schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#quartz_cron_schedule AlertV2#quartz_cron_schedule}.
        :param timezone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#timezone_id AlertV2#timezone_id}.
        '''
        value = AlertV2Schedule(
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
    def effective_run_as(self) -> "AlertV2EffectiveRunAsOutputReference":
        return typing.cast("AlertV2EffectiveRunAsOutputReference", jsii.get(self, "effectiveRunAs"))

    @builtins.property
    @jsii.member(jsii_name="evaluation")
    def evaluation(self) -> "AlertV2EvaluationOutputReference":
        return typing.cast("AlertV2EvaluationOutputReference", jsii.get(self, "evaluation"))

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
    def run_as(self) -> "AlertV2RunAsOutputReference":
        return typing.cast("AlertV2RunAsOutputReference", jsii.get(self, "runAs"))

    @builtins.property
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> "AlertV2ScheduleOutputReference":
        return typing.cast("AlertV2ScheduleOutputReference", jsii.get(self, "schedule"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AlertV2Evaluation"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AlertV2Evaluation"]], jsii.get(self, "evaluationInput"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AlertV2RunAs"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AlertV2RunAs"]], jsii.get(self, "runAsInput"))

    @builtins.property
    @jsii.member(jsii_name="runAsUserNameInput")
    def run_as_user_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "runAsUserNameInput"))

    @builtins.property
    @jsii.member(jsii_name="scheduleInput")
    def schedule_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AlertV2Schedule"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AlertV2Schedule"]], jsii.get(self, "scheduleInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__bc51b4ac5c76dbe7cf6e687f3c372918b93383096adc8df423bfba6fcac32d5d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customDescription", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="customSummary")
    def custom_summary(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customSummary"))

    @custom_summary.setter
    def custom_summary(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a029115ecd50506cb54f8f7e52578acd5b165a7639a7ea22cdc4b7fa043ec1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customSummary", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "displayName"))

    @display_name.setter
    def display_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__778461c7c40cf9114b95a3f1401ccdd5f1f67bf43766fd2de5aef2828a6e0798)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "displayName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parentPath")
    def parent_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parentPath"))

    @parent_path.setter
    def parent_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f416aa6b70f3a74c4edca467928e56f2cd9fcd9bdbd98747999fe3bb27b24e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parentPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="queryText")
    def query_text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queryText"))

    @query_text.setter
    def query_text(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb93dced366c7dfe7a329c3e0d072694436dc464dd40110da3b200fa064d2ac3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "queryText", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runAsUserName")
    def run_as_user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runAsUserName"))

    @run_as_user_name.setter
    def run_as_user_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0fa16e99392c431cc422f8fc27173aed141e40df7a0d4f71974afb82436f25d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runAsUserName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="warehouseId")
    def warehouse_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "warehouseId"))

    @warehouse_id.setter
    def warehouse_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d6bf72065d995df6b314c3d02eda736ceafd5e51df7683ff1be82a0d6b5e557)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "warehouseId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workspaceId")
    def workspace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceId"))

    @workspace_id.setter
    def workspace_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__282b11b793858057378b0aa1caeead804b22550286b67bda978ded695b9225d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workspaceId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.alertV2.AlertV2Config",
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
class AlertV2Config(_cdktf_9a9027ec.TerraformMetaArguments):
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
        evaluation: typing.Optional[typing.Union["AlertV2Evaluation", typing.Dict[builtins.str, typing.Any]]] = None,
        parent_path: typing.Optional[builtins.str] = None,
        query_text: typing.Optional[builtins.str] = None,
        run_as: typing.Optional[typing.Union["AlertV2RunAs", typing.Dict[builtins.str, typing.Any]]] = None,
        run_as_user_name: typing.Optional[builtins.str] = None,
        schedule: typing.Optional[typing.Union["AlertV2Schedule", typing.Dict[builtins.str, typing.Any]]] = None,
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
        :param custom_description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#custom_description AlertV2#custom_description}.
        :param custom_summary: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#custom_summary AlertV2#custom_summary}.
        :param display_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#display_name AlertV2#display_name}.
        :param evaluation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#evaluation AlertV2#evaluation}.
        :param parent_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#parent_path AlertV2#parent_path}.
        :param query_text: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#query_text AlertV2#query_text}.
        :param run_as: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#run_as AlertV2#run_as}.
        :param run_as_user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#run_as_user_name AlertV2#run_as_user_name}.
        :param schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#schedule AlertV2#schedule}.
        :param warehouse_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#warehouse_id AlertV2#warehouse_id}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#workspace_id AlertV2#workspace_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(evaluation, dict):
            evaluation = AlertV2Evaluation(**evaluation)
        if isinstance(run_as, dict):
            run_as = AlertV2RunAs(**run_as)
        if isinstance(schedule, dict):
            schedule = AlertV2Schedule(**schedule)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__319dff9251546b17600eaf0dda8a9a75355833a381129123ee110d524c989db2)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#custom_description AlertV2#custom_description}.'''
        result = self._values.get("custom_description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_summary(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#custom_summary AlertV2#custom_summary}.'''
        result = self._values.get("custom_summary")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def display_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#display_name AlertV2#display_name}.'''
        result = self._values.get("display_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def evaluation(self) -> typing.Optional["AlertV2Evaluation"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#evaluation AlertV2#evaluation}.'''
        result = self._values.get("evaluation")
        return typing.cast(typing.Optional["AlertV2Evaluation"], result)

    @builtins.property
    def parent_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#parent_path AlertV2#parent_path}.'''
        result = self._values.get("parent_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def query_text(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#query_text AlertV2#query_text}.'''
        result = self._values.get("query_text")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def run_as(self) -> typing.Optional["AlertV2RunAs"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#run_as AlertV2#run_as}.'''
        result = self._values.get("run_as")
        return typing.cast(typing.Optional["AlertV2RunAs"], result)

    @builtins.property
    def run_as_user_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#run_as_user_name AlertV2#run_as_user_name}.'''
        result = self._values.get("run_as_user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def schedule(self) -> typing.Optional["AlertV2Schedule"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#schedule AlertV2#schedule}.'''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional["AlertV2Schedule"], result)

    @builtins.property
    def warehouse_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#warehouse_id AlertV2#warehouse_id}.'''
        result = self._values.get("warehouse_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workspace_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#workspace_id AlertV2#workspace_id}.'''
        result = self._values.get("workspace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertV2Config(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.alertV2.AlertV2EffectiveRunAs",
    jsii_struct_bases=[],
    name_mapping={
        "service_principal_name": "servicePrincipalName",
        "user_name": "userName",
    },
)
class AlertV2EffectiveRunAs:
    def __init__(
        self,
        *,
        service_principal_name: typing.Optional[builtins.str] = None,
        user_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param service_principal_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#service_principal_name AlertV2#service_principal_name}.
        :param user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#user_name AlertV2#user_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c89a573908de5c6fb3e43bbbdb46a79219abd7cac0227e8f5b89a85b065050c3)
            check_type(argname="argument service_principal_name", value=service_principal_name, expected_type=type_hints["service_principal_name"])
            check_type(argname="argument user_name", value=user_name, expected_type=type_hints["user_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if service_principal_name is not None:
            self._values["service_principal_name"] = service_principal_name
        if user_name is not None:
            self._values["user_name"] = user_name

    @builtins.property
    def service_principal_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#service_principal_name AlertV2#service_principal_name}.'''
        result = self._values.get("service_principal_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#user_name AlertV2#user_name}.'''
        result = self._values.get("user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertV2EffectiveRunAs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AlertV2EffectiveRunAsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.alertV2.AlertV2EffectiveRunAsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f45b941fa0b88d054ab0a4a52c7fbbd3a9956f7bedb6822d75e91991f5525548)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5415a9cf9a9a8dc79ed047e08e778af27b9961eb4d0478320834477d9f9be65b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "servicePrincipalName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userName"))

    @user_name.setter
    def user_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4e5ef1a5a0c69ae66938ccfc6e97a5bd39a24817014882adb39fef3bad3d6ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AlertV2EffectiveRunAs]:
        return typing.cast(typing.Optional[AlertV2EffectiveRunAs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[AlertV2EffectiveRunAs]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0821fd53aa3d4853f2a20a74786a60c3872198debacfe6ccc6e6c13c48e169c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.alertV2.AlertV2Evaluation",
    jsii_struct_bases=[],
    name_mapping={
        "comparison_operator": "comparisonOperator",
        "empty_result_state": "emptyResultState",
        "notification": "notification",
        "source": "source",
        "threshold": "threshold",
    },
)
class AlertV2Evaluation:
    def __init__(
        self,
        *,
        comparison_operator: typing.Optional[builtins.str] = None,
        empty_result_state: typing.Optional[builtins.str] = None,
        notification: typing.Optional[typing.Union["AlertV2EvaluationNotification", typing.Dict[builtins.str, typing.Any]]] = None,
        source: typing.Optional[typing.Union["AlertV2EvaluationSource", typing.Dict[builtins.str, typing.Any]]] = None,
        threshold: typing.Optional[typing.Union["AlertV2EvaluationThreshold", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param comparison_operator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#comparison_operator AlertV2#comparison_operator}.
        :param empty_result_state: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#empty_result_state AlertV2#empty_result_state}.
        :param notification: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#notification AlertV2#notification}.
        :param source: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#source AlertV2#source}.
        :param threshold: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#threshold AlertV2#threshold}.
        '''
        if isinstance(notification, dict):
            notification = AlertV2EvaluationNotification(**notification)
        if isinstance(source, dict):
            source = AlertV2EvaluationSource(**source)
        if isinstance(threshold, dict):
            threshold = AlertV2EvaluationThreshold(**threshold)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f126c08539abb1bdce394ddedf2407710fdbddbbcd74dd3215b961eb26c60985)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#comparison_operator AlertV2#comparison_operator}.'''
        result = self._values.get("comparison_operator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def empty_result_state(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#empty_result_state AlertV2#empty_result_state}.'''
        result = self._values.get("empty_result_state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notification(self) -> typing.Optional["AlertV2EvaluationNotification"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#notification AlertV2#notification}.'''
        result = self._values.get("notification")
        return typing.cast(typing.Optional["AlertV2EvaluationNotification"], result)

    @builtins.property
    def source(self) -> typing.Optional["AlertV2EvaluationSource"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#source AlertV2#source}.'''
        result = self._values.get("source")
        return typing.cast(typing.Optional["AlertV2EvaluationSource"], result)

    @builtins.property
    def threshold(self) -> typing.Optional["AlertV2EvaluationThreshold"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#threshold AlertV2#threshold}.'''
        result = self._values.get("threshold")
        return typing.cast(typing.Optional["AlertV2EvaluationThreshold"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertV2Evaluation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.alertV2.AlertV2EvaluationNotification",
    jsii_struct_bases=[],
    name_mapping={
        "notify_on_ok": "notifyOnOk",
        "retrigger_seconds": "retriggerSeconds",
        "subscriptions": "subscriptions",
    },
)
class AlertV2EvaluationNotification:
    def __init__(
        self,
        *,
        notify_on_ok: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        retrigger_seconds: typing.Optional[jsii.Number] = None,
        subscriptions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AlertV2EvaluationNotificationSubscriptions", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param notify_on_ok: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#notify_on_ok AlertV2#notify_on_ok}.
        :param retrigger_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#retrigger_seconds AlertV2#retrigger_seconds}.
        :param subscriptions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#subscriptions AlertV2#subscriptions}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e053e00d702a289db0d7073a6aa6d5b7bfee5b48767250db397509b549bf4be4)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#notify_on_ok AlertV2#notify_on_ok}.'''
        result = self._values.get("notify_on_ok")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def retrigger_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#retrigger_seconds AlertV2#retrigger_seconds}.'''
        result = self._values.get("retrigger_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def subscriptions(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AlertV2EvaluationNotificationSubscriptions"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#subscriptions AlertV2#subscriptions}.'''
        result = self._values.get("subscriptions")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AlertV2EvaluationNotificationSubscriptions"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertV2EvaluationNotification(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AlertV2EvaluationNotificationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.alertV2.AlertV2EvaluationNotificationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0c28fe2e078e6b710d58d4e86d8cd353f22e77c9d2dffdba4e5c69802d16f789)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putSubscriptions")
    def put_subscriptions(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AlertV2EvaluationNotificationSubscriptions", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aaea6c7212a3f924a65460bf205bc5f7e8c4c4df66227bb7732e20059643739a)
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
    def subscriptions(self) -> "AlertV2EvaluationNotificationSubscriptionsList":
        return typing.cast("AlertV2EvaluationNotificationSubscriptionsList", jsii.get(self, "subscriptions"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AlertV2EvaluationNotificationSubscriptions"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AlertV2EvaluationNotificationSubscriptions"]]], jsii.get(self, "subscriptionsInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__f448cb136bffa3d0d75de2e5592f748d5369ad308c618d7c789553812ad199d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notifyOnOk", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retriggerSeconds")
    def retrigger_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retriggerSeconds"))

    @retrigger_seconds.setter
    def retrigger_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__050dfc6fd74e14ffaf68b1563e4134a67db91e4d4fc97d2b3c9676824849c849)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retriggerSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2EvaluationNotification]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2EvaluationNotification]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2EvaluationNotification]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8ae0695eeac6d7cc2fcbd6b4f6d57fbfc48aad8060f40a4ca20c289669298b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.alertV2.AlertV2EvaluationNotificationSubscriptions",
    jsii_struct_bases=[],
    name_mapping={"destination_id": "destinationId", "user_email": "userEmail"},
)
class AlertV2EvaluationNotificationSubscriptions:
    def __init__(
        self,
        *,
        destination_id: typing.Optional[builtins.str] = None,
        user_email: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param destination_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#destination_id AlertV2#destination_id}.
        :param user_email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#user_email AlertV2#user_email}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a51c547eecc33e2bb6be1266e9c35abd456e7e3ce98cc6fb60ebcea39f526e2)
            check_type(argname="argument destination_id", value=destination_id, expected_type=type_hints["destination_id"])
            check_type(argname="argument user_email", value=user_email, expected_type=type_hints["user_email"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if destination_id is not None:
            self._values["destination_id"] = destination_id
        if user_email is not None:
            self._values["user_email"] = user_email

    @builtins.property
    def destination_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#destination_id AlertV2#destination_id}.'''
        result = self._values.get("destination_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_email(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#user_email AlertV2#user_email}.'''
        result = self._values.get("user_email")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertV2EvaluationNotificationSubscriptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AlertV2EvaluationNotificationSubscriptionsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.alertV2.AlertV2EvaluationNotificationSubscriptionsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__38da6da595b43152c796b70fd119c5f16dc32af74802c1e1d795f24784b12d4e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "AlertV2EvaluationNotificationSubscriptionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b38c951e1fbb70cd0fe3e85ec061db7e247c3fd52959c96ea6d1454dd772f1ba)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("AlertV2EvaluationNotificationSubscriptionsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68bdcd8984e8ebff0548af0e49af8ecda60c4817cc7b65fab508694bef820c14)
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
            type_hints = typing.get_type_hints(_typecheckingstub__49beaa9e29158df530507313bdf1f4e02467fd0a29b98b5b3538a1d11fc0f1e3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__972f3bbc6d23b8c8f724787ef2770148e55db9d95926b4d1169329f343f6e87a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AlertV2EvaluationNotificationSubscriptions]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AlertV2EvaluationNotificationSubscriptions]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AlertV2EvaluationNotificationSubscriptions]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d0e96b0411ae20cda1883af6c9583b320043da09454202d418a4149f73835f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class AlertV2EvaluationNotificationSubscriptionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.alertV2.AlertV2EvaluationNotificationSubscriptionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ce379297d5ea022b9f0877603b07476f007ffa81c1cbb8e866556c4fd17b4e91)
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
            type_hints = typing.get_type_hints(_typecheckingstub__997f60c935f6f0032a973e85f537e8fcc51aa79669b8a89de2566103c5101dc4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destinationId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userEmail")
    def user_email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userEmail"))

    @user_email.setter
    def user_email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__558fb01f4b7d093e341c84c97ca18fa429bf9c3587fd4adc61db1292aa1c929e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userEmail", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2EvaluationNotificationSubscriptions]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2EvaluationNotificationSubscriptions]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2EvaluationNotificationSubscriptions]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49ea9d75c6c89f24a4e37272fe7ad7729d9a5ef66c908f94b0ff1cf2ecd53c6a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class AlertV2EvaluationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.alertV2.AlertV2EvaluationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ea2390385c8f7999de0ade48acde2795e78e3714c9f45d70551908dc186b00c7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putNotification")
    def put_notification(
        self,
        *,
        notify_on_ok: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        retrigger_seconds: typing.Optional[jsii.Number] = None,
        subscriptions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AlertV2EvaluationNotificationSubscriptions, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param notify_on_ok: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#notify_on_ok AlertV2#notify_on_ok}.
        :param retrigger_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#retrigger_seconds AlertV2#retrigger_seconds}.
        :param subscriptions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#subscriptions AlertV2#subscriptions}.
        '''
        value = AlertV2EvaluationNotification(
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
        :param aggregation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#aggregation AlertV2#aggregation}.
        :param display: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#display AlertV2#display}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#name AlertV2#name}.
        '''
        value = AlertV2EvaluationSource(
            aggregation=aggregation, display=display, name=name
        )

        return typing.cast(None, jsii.invoke(self, "putSource", [value]))

    @jsii.member(jsii_name="putThreshold")
    def put_threshold(
        self,
        *,
        column: typing.Optional[typing.Union["AlertV2EvaluationThresholdColumn", typing.Dict[builtins.str, typing.Any]]] = None,
        value: typing.Optional[typing.Union["AlertV2EvaluationThresholdValue", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param column: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#column AlertV2#column}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#value AlertV2#value}.
        '''
        value_ = AlertV2EvaluationThreshold(column=column, value=value)

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
    def notification(self) -> AlertV2EvaluationNotificationOutputReference:
        return typing.cast(AlertV2EvaluationNotificationOutputReference, jsii.get(self, "notification"))

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> "AlertV2EvaluationSourceOutputReference":
        return typing.cast("AlertV2EvaluationSourceOutputReference", jsii.get(self, "source"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> "AlertV2EvaluationThresholdOutputReference":
        return typing.cast("AlertV2EvaluationThresholdOutputReference", jsii.get(self, "threshold"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2EvaluationNotification]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2EvaluationNotification]], jsii.get(self, "notificationInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceInput")
    def source_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AlertV2EvaluationSource"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AlertV2EvaluationSource"]], jsii.get(self, "sourceInput"))

    @builtins.property
    @jsii.member(jsii_name="thresholdInput")
    def threshold_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AlertV2EvaluationThreshold"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AlertV2EvaluationThreshold"]], jsii.get(self, "thresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="comparisonOperator")
    def comparison_operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comparisonOperator"))

    @comparison_operator.setter
    def comparison_operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f6f11d8074136a2acdfddb35a8b56221d5ffa57bfc18dc34153d77f22208bc4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comparisonOperator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="emptyResultState")
    def empty_result_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emptyResultState"))

    @empty_result_state.setter
    def empty_result_state(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8e33f69cab214498e36a2c57f65705e679a16212692d7f0a7aae8e37f917c23)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emptyResultState", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2Evaluation]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2Evaluation]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2Evaluation]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8f60c2dbc6a8a4cf45c0cd2e4679d8e008596f9f3144b38c2f58a348f9a00ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.alertV2.AlertV2EvaluationSource",
    jsii_struct_bases=[],
    name_mapping={"aggregation": "aggregation", "display": "display", "name": "name"},
)
class AlertV2EvaluationSource:
    def __init__(
        self,
        *,
        aggregation: typing.Optional[builtins.str] = None,
        display: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param aggregation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#aggregation AlertV2#aggregation}.
        :param display: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#display AlertV2#display}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#name AlertV2#name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2377ee215a9e808c2a390629731b43c9a5058dc0978b7258c034a1f80e6eb096)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#aggregation AlertV2#aggregation}.'''
        result = self._values.get("aggregation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def display(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#display AlertV2#display}.'''
        result = self._values.get("display")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#name AlertV2#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertV2EvaluationSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AlertV2EvaluationSourceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.alertV2.AlertV2EvaluationSourceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__31317f8d8b15d74bba2f81f496866f6a711a5938f61618e4b1359d67af681d7b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__57540e122c11bb8270f587c58c028fc9b7358a6addcb31894a08206d3fa517b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "aggregation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="display")
    def display(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "display"))

    @display.setter
    def display(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__210ba79ab0fae7bd4d94f8828e3a349d2b0f7b80a46cdbd481c9d3fcb4d2ba4f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "display", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c834d4eaa50e0a6a2352558c19a3497943387af6cf623cf5723668606bdf6624)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2EvaluationSource]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2EvaluationSource]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2EvaluationSource]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f0d54fba35e4e869bd20295846a14c03b996f8e15383460be742941421a83a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.alertV2.AlertV2EvaluationThreshold",
    jsii_struct_bases=[],
    name_mapping={"column": "column", "value": "value"},
)
class AlertV2EvaluationThreshold:
    def __init__(
        self,
        *,
        column: typing.Optional[typing.Union["AlertV2EvaluationThresholdColumn", typing.Dict[builtins.str, typing.Any]]] = None,
        value: typing.Optional[typing.Union["AlertV2EvaluationThresholdValue", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param column: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#column AlertV2#column}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#value AlertV2#value}.
        '''
        if isinstance(column, dict):
            column = AlertV2EvaluationThresholdColumn(**column)
        if isinstance(value, dict):
            value = AlertV2EvaluationThresholdValue(**value)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97ef580485ce59ea427e7ba42fa8e38d0705c36c6fd9c1da8b7142e23fd71076)
            check_type(argname="argument column", value=column, expected_type=type_hints["column"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if column is not None:
            self._values["column"] = column
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def column(self) -> typing.Optional["AlertV2EvaluationThresholdColumn"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#column AlertV2#column}.'''
        result = self._values.get("column")
        return typing.cast(typing.Optional["AlertV2EvaluationThresholdColumn"], result)

    @builtins.property
    def value(self) -> typing.Optional["AlertV2EvaluationThresholdValue"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#value AlertV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional["AlertV2EvaluationThresholdValue"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertV2EvaluationThreshold(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.alertV2.AlertV2EvaluationThresholdColumn",
    jsii_struct_bases=[],
    name_mapping={"aggregation": "aggregation", "display": "display", "name": "name"},
)
class AlertV2EvaluationThresholdColumn:
    def __init__(
        self,
        *,
        aggregation: typing.Optional[builtins.str] = None,
        display: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param aggregation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#aggregation AlertV2#aggregation}.
        :param display: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#display AlertV2#display}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#name AlertV2#name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__159bf496e7f5f60576750ab266d77e9e49259ad61f4d64572a3d791f7d9d7f56)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#aggregation AlertV2#aggregation}.'''
        result = self._values.get("aggregation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def display(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#display AlertV2#display}.'''
        result = self._values.get("display")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#name AlertV2#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertV2EvaluationThresholdColumn(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AlertV2EvaluationThresholdColumnOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.alertV2.AlertV2EvaluationThresholdColumnOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d222826aecb24533b39fd1cb25cb6e39cd16091b4098dd55569cde54f24fb7b0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__182632011748707983ff7967f2cbfeec509335219fdee1771d8ac9de3424ec9d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "aggregation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="display")
    def display(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "display"))

    @display.setter
    def display(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1819d591338f48c9904a15c533ff1c42728587eb46421b6e4d271bbb04892e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "display", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58c8fa59320c280734a244a60df7325df6c7ec4173e25a6a96a8c5000f293ec9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2EvaluationThresholdColumn]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2EvaluationThresholdColumn]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2EvaluationThresholdColumn]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f126486f9e0daf207f45398a2ff9421d4af9a00be4fdbaccfee2abfa2b597db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class AlertV2EvaluationThresholdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.alertV2.AlertV2EvaluationThresholdOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__eac733ee1021082f03478f37a0bf54a0c814293decc21df503ed2cf21499c6ed)
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
        :param aggregation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#aggregation AlertV2#aggregation}.
        :param display: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#display AlertV2#display}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#name AlertV2#name}.
        '''
        value = AlertV2EvaluationThresholdColumn(
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
        :param bool_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#bool_value AlertV2#bool_value}.
        :param double_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#double_value AlertV2#double_value}.
        :param string_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#string_value AlertV2#string_value}.
        '''
        value = AlertV2EvaluationThresholdValue(
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
    def column(self) -> AlertV2EvaluationThresholdColumnOutputReference:
        return typing.cast(AlertV2EvaluationThresholdColumnOutputReference, jsii.get(self, "column"))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> "AlertV2EvaluationThresholdValueOutputReference":
        return typing.cast("AlertV2EvaluationThresholdValueOutputReference", jsii.get(self, "value"))

    @builtins.property
    @jsii.member(jsii_name="columnInput")
    def column_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2EvaluationThresholdColumn]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2EvaluationThresholdColumn]], jsii.get(self, "columnInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AlertV2EvaluationThresholdValue"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AlertV2EvaluationThresholdValue"]], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2EvaluationThreshold]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2EvaluationThreshold]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2EvaluationThreshold]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94abcb434e0091a65a9d56f1d80dd1d58089a6b5cc1d73e4e513b8d8b526e27d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.alertV2.AlertV2EvaluationThresholdValue",
    jsii_struct_bases=[],
    name_mapping={
        "bool_value": "boolValue",
        "double_value": "doubleValue",
        "string_value": "stringValue",
    },
)
class AlertV2EvaluationThresholdValue:
    def __init__(
        self,
        *,
        bool_value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        double_value: typing.Optional[jsii.Number] = None,
        string_value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bool_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#bool_value AlertV2#bool_value}.
        :param double_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#double_value AlertV2#double_value}.
        :param string_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#string_value AlertV2#string_value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a922d00345b77236ea699f16b50e6ed6f3add90b6fdd7f512bb3a722ab359db3)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#bool_value AlertV2#bool_value}.'''
        result = self._values.get("bool_value")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def double_value(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#double_value AlertV2#double_value}.'''
        result = self._values.get("double_value")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def string_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#string_value AlertV2#string_value}.'''
        result = self._values.get("string_value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertV2EvaluationThresholdValue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AlertV2EvaluationThresholdValueOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.alertV2.AlertV2EvaluationThresholdValueOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__32c9d75dc889ef5a156912e9bfdee972b4831340883e02b772dfa3bdfc49176a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6513c1e247002a2b8e82ae2e1cfacc1a7bea0897deb1d3f7b075e799a99e8bf6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boolValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="doubleValue")
    def double_value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "doubleValue"))

    @double_value.setter
    def double_value(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ba5a17d23b8c553a9afcce50d7e1b902c2a3ec452b0f48eb90391c7b1de64ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "doubleValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stringValue")
    def string_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stringValue"))

    @string_value.setter
    def string_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__682aa512169c822d7c43f11adba5a7e5a65a9be8ccc8c1f473d51aac7470dde1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stringValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2EvaluationThresholdValue]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2EvaluationThresholdValue]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2EvaluationThresholdValue]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f2e00f81962d36031befcc289021f7e65f9673692d80fe691e7ad80de598fde)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.alertV2.AlertV2RunAs",
    jsii_struct_bases=[],
    name_mapping={
        "service_principal_name": "servicePrincipalName",
        "user_name": "userName",
    },
)
class AlertV2RunAs:
    def __init__(
        self,
        *,
        service_principal_name: typing.Optional[builtins.str] = None,
        user_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param service_principal_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#service_principal_name AlertV2#service_principal_name}.
        :param user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#user_name AlertV2#user_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff45c72469e4360972d641f9d23cf448fb87ab47b3fda677df55b581c47b04e0)
            check_type(argname="argument service_principal_name", value=service_principal_name, expected_type=type_hints["service_principal_name"])
            check_type(argname="argument user_name", value=user_name, expected_type=type_hints["user_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if service_principal_name is not None:
            self._values["service_principal_name"] = service_principal_name
        if user_name is not None:
            self._values["user_name"] = user_name

    @builtins.property
    def service_principal_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#service_principal_name AlertV2#service_principal_name}.'''
        result = self._values.get("service_principal_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#user_name AlertV2#user_name}.'''
        result = self._values.get("user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertV2RunAs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AlertV2RunAsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.alertV2.AlertV2RunAsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ede214c2b42b3dc7964909425666d1e7dea50e22dbfd01fd0d48da6c97059e98)
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
            type_hints = typing.get_type_hints(_typecheckingstub__714b4380762ac80cdbb30d0f6871988f86bc2cad4f0124bf3932e7e5c9e9a4ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "servicePrincipalName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userName"))

    @user_name.setter
    def user_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce1640702440c9594cc011b13c48cc2652e20f90b4b6f8d0d65313d10a0f4f67)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2RunAs]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2RunAs]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2RunAs]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e17a85b4d0b4f1af07f362c317678f510be1fc8a380f30e92da26729b8ac2b92)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.alertV2.AlertV2Schedule",
    jsii_struct_bases=[],
    name_mapping={
        "pause_status": "pauseStatus",
        "quartz_cron_schedule": "quartzCronSchedule",
        "timezone_id": "timezoneId",
    },
)
class AlertV2Schedule:
    def __init__(
        self,
        *,
        pause_status: typing.Optional[builtins.str] = None,
        quartz_cron_schedule: typing.Optional[builtins.str] = None,
        timezone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param pause_status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#pause_status AlertV2#pause_status}.
        :param quartz_cron_schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#quartz_cron_schedule AlertV2#quartz_cron_schedule}.
        :param timezone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#timezone_id AlertV2#timezone_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c794896635dd36bd022d6bce5396f6775c7efa4640c52d35cd5bef9ca09f148)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#pause_status AlertV2#pause_status}.'''
        result = self._values.get("pause_status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def quartz_cron_schedule(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#quartz_cron_schedule AlertV2#quartz_cron_schedule}.'''
        result = self._values.get("quartz_cron_schedule")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timezone_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert_v2#timezone_id AlertV2#timezone_id}.'''
        result = self._values.get("timezone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertV2Schedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AlertV2ScheduleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.alertV2.AlertV2ScheduleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ea42dfade7ef03589d234779850a332af5758e79334147f35f2be5126196cc7f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f692fdd6dcfd448685d468147943ed1537cc45a06ec863b0a77776066620f904)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pauseStatus", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="quartzCronSchedule")
    def quartz_cron_schedule(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "quartzCronSchedule"))

    @quartz_cron_schedule.setter
    def quartz_cron_schedule(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__712fc2e3480a290be8be35b65aa88eceee5f642e4823057bd0c6414a63c1dbb4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "quartzCronSchedule", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timezoneId")
    def timezone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timezoneId"))

    @timezone_id.setter
    def timezone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26752a9f13ba605e16edea062772af5ec1494693db2f5df21d74daf51b704dbe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timezoneId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2Schedule]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2Schedule]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2Schedule]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8796aa99166698588e5eb74587065829f6143d10e8c11557e408de54defc2903)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "AlertV2",
    "AlertV2Config",
    "AlertV2EffectiveRunAs",
    "AlertV2EffectiveRunAsOutputReference",
    "AlertV2Evaluation",
    "AlertV2EvaluationNotification",
    "AlertV2EvaluationNotificationOutputReference",
    "AlertV2EvaluationNotificationSubscriptions",
    "AlertV2EvaluationNotificationSubscriptionsList",
    "AlertV2EvaluationNotificationSubscriptionsOutputReference",
    "AlertV2EvaluationOutputReference",
    "AlertV2EvaluationSource",
    "AlertV2EvaluationSourceOutputReference",
    "AlertV2EvaluationThreshold",
    "AlertV2EvaluationThresholdColumn",
    "AlertV2EvaluationThresholdColumnOutputReference",
    "AlertV2EvaluationThresholdOutputReference",
    "AlertV2EvaluationThresholdValue",
    "AlertV2EvaluationThresholdValueOutputReference",
    "AlertV2RunAs",
    "AlertV2RunAsOutputReference",
    "AlertV2Schedule",
    "AlertV2ScheduleOutputReference",
]

publication.publish()

def _typecheckingstub__dca0b185eb5c03093428da7efbdaf124a32abb6740d00836e21bb53ad001b428(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    custom_description: typing.Optional[builtins.str] = None,
    custom_summary: typing.Optional[builtins.str] = None,
    display_name: typing.Optional[builtins.str] = None,
    evaluation: typing.Optional[typing.Union[AlertV2Evaluation, typing.Dict[builtins.str, typing.Any]]] = None,
    parent_path: typing.Optional[builtins.str] = None,
    query_text: typing.Optional[builtins.str] = None,
    run_as: typing.Optional[typing.Union[AlertV2RunAs, typing.Dict[builtins.str, typing.Any]]] = None,
    run_as_user_name: typing.Optional[builtins.str] = None,
    schedule: typing.Optional[typing.Union[AlertV2Schedule, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__57728441fa3750fa73b25165bb4265a235c17448c0b5eac0a14abf182b9b40ad(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc51b4ac5c76dbe7cf6e687f3c372918b93383096adc8df423bfba6fcac32d5d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a029115ecd50506cb54f8f7e52578acd5b165a7639a7ea22cdc4b7fa043ec1d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__778461c7c40cf9114b95a3f1401ccdd5f1f67bf43766fd2de5aef2828a6e0798(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f416aa6b70f3a74c4edca467928e56f2cd9fcd9bdbd98747999fe3bb27b24e1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb93dced366c7dfe7a329c3e0d072694436dc464dd40110da3b200fa064d2ac3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0fa16e99392c431cc422f8fc27173aed141e40df7a0d4f71974afb82436f25d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d6bf72065d995df6b314c3d02eda736ceafd5e51df7683ff1be82a0d6b5e557(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__282b11b793858057378b0aa1caeead804b22550286b67bda978ded695b9225d9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__319dff9251546b17600eaf0dda8a9a75355833a381129123ee110d524c989db2(
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
    evaluation: typing.Optional[typing.Union[AlertV2Evaluation, typing.Dict[builtins.str, typing.Any]]] = None,
    parent_path: typing.Optional[builtins.str] = None,
    query_text: typing.Optional[builtins.str] = None,
    run_as: typing.Optional[typing.Union[AlertV2RunAs, typing.Dict[builtins.str, typing.Any]]] = None,
    run_as_user_name: typing.Optional[builtins.str] = None,
    schedule: typing.Optional[typing.Union[AlertV2Schedule, typing.Dict[builtins.str, typing.Any]]] = None,
    warehouse_id: typing.Optional[builtins.str] = None,
    workspace_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c89a573908de5c6fb3e43bbbdb46a79219abd7cac0227e8f5b89a85b065050c3(
    *,
    service_principal_name: typing.Optional[builtins.str] = None,
    user_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f45b941fa0b88d054ab0a4a52c7fbbd3a9956f7bedb6822d75e91991f5525548(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5415a9cf9a9a8dc79ed047e08e778af27b9961eb4d0478320834477d9f9be65b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4e5ef1a5a0c69ae66938ccfc6e97a5bd39a24817014882adb39fef3bad3d6ab(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0821fd53aa3d4853f2a20a74786a60c3872198debacfe6ccc6e6c13c48e169c9(
    value: typing.Optional[AlertV2EffectiveRunAs],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f126c08539abb1bdce394ddedf2407710fdbddbbcd74dd3215b961eb26c60985(
    *,
    comparison_operator: typing.Optional[builtins.str] = None,
    empty_result_state: typing.Optional[builtins.str] = None,
    notification: typing.Optional[typing.Union[AlertV2EvaluationNotification, typing.Dict[builtins.str, typing.Any]]] = None,
    source: typing.Optional[typing.Union[AlertV2EvaluationSource, typing.Dict[builtins.str, typing.Any]]] = None,
    threshold: typing.Optional[typing.Union[AlertV2EvaluationThreshold, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e053e00d702a289db0d7073a6aa6d5b7bfee5b48767250db397509b549bf4be4(
    *,
    notify_on_ok: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    retrigger_seconds: typing.Optional[jsii.Number] = None,
    subscriptions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AlertV2EvaluationNotificationSubscriptions, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c28fe2e078e6b710d58d4e86d8cd353f22e77c9d2dffdba4e5c69802d16f789(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aaea6c7212a3f924a65460bf205bc5f7e8c4c4df66227bb7732e20059643739a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AlertV2EvaluationNotificationSubscriptions, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f448cb136bffa3d0d75de2e5592f748d5369ad308c618d7c789553812ad199d5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__050dfc6fd74e14ffaf68b1563e4134a67db91e4d4fc97d2b3c9676824849c849(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8ae0695eeac6d7cc2fcbd6b4f6d57fbfc48aad8060f40a4ca20c289669298b3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2EvaluationNotification]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a51c547eecc33e2bb6be1266e9c35abd456e7e3ce98cc6fb60ebcea39f526e2(
    *,
    destination_id: typing.Optional[builtins.str] = None,
    user_email: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38da6da595b43152c796b70fd119c5f16dc32af74802c1e1d795f24784b12d4e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b38c951e1fbb70cd0fe3e85ec061db7e247c3fd52959c96ea6d1454dd772f1ba(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68bdcd8984e8ebff0548af0e49af8ecda60c4817cc7b65fab508694bef820c14(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49beaa9e29158df530507313bdf1f4e02467fd0a29b98b5b3538a1d11fc0f1e3(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__972f3bbc6d23b8c8f724787ef2770148e55db9d95926b4d1169329f343f6e87a(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d0e96b0411ae20cda1883af6c9583b320043da09454202d418a4149f73835f2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AlertV2EvaluationNotificationSubscriptions]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce379297d5ea022b9f0877603b07476f007ffa81c1cbb8e866556c4fd17b4e91(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__997f60c935f6f0032a973e85f537e8fcc51aa79669b8a89de2566103c5101dc4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__558fb01f4b7d093e341c84c97ca18fa429bf9c3587fd4adc61db1292aa1c929e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49ea9d75c6c89f24a4e37272fe7ad7729d9a5ef66c908f94b0ff1cf2ecd53c6a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2EvaluationNotificationSubscriptions]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea2390385c8f7999de0ade48acde2795e78e3714c9f45d70551908dc186b00c7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f6f11d8074136a2acdfddb35a8b56221d5ffa57bfc18dc34153d77f22208bc4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8e33f69cab214498e36a2c57f65705e679a16212692d7f0a7aae8e37f917c23(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8f60c2dbc6a8a4cf45c0cd2e4679d8e008596f9f3144b38c2f58a348f9a00ca(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2Evaluation]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2377ee215a9e808c2a390629731b43c9a5058dc0978b7258c034a1f80e6eb096(
    *,
    aggregation: typing.Optional[builtins.str] = None,
    display: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31317f8d8b15d74bba2f81f496866f6a711a5938f61618e4b1359d67af681d7b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57540e122c11bb8270f587c58c028fc9b7358a6addcb31894a08206d3fa517b7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__210ba79ab0fae7bd4d94f8828e3a349d2b0f7b80a46cdbd481c9d3fcb4d2ba4f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c834d4eaa50e0a6a2352558c19a3497943387af6cf623cf5723668606bdf6624(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f0d54fba35e4e869bd20295846a14c03b996f8e15383460be742941421a83a1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2EvaluationSource]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97ef580485ce59ea427e7ba42fa8e38d0705c36c6fd9c1da8b7142e23fd71076(
    *,
    column: typing.Optional[typing.Union[AlertV2EvaluationThresholdColumn, typing.Dict[builtins.str, typing.Any]]] = None,
    value: typing.Optional[typing.Union[AlertV2EvaluationThresholdValue, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__159bf496e7f5f60576750ab266d77e9e49259ad61f4d64572a3d791f7d9d7f56(
    *,
    aggregation: typing.Optional[builtins.str] = None,
    display: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d222826aecb24533b39fd1cb25cb6e39cd16091b4098dd55569cde54f24fb7b0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__182632011748707983ff7967f2cbfeec509335219fdee1771d8ac9de3424ec9d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1819d591338f48c9904a15c533ff1c42728587eb46421b6e4d271bbb04892e7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58c8fa59320c280734a244a60df7325df6c7ec4173e25a6a96a8c5000f293ec9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f126486f9e0daf207f45398a2ff9421d4af9a00be4fdbaccfee2abfa2b597db(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2EvaluationThresholdColumn]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eac733ee1021082f03478f37a0bf54a0c814293decc21df503ed2cf21499c6ed(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94abcb434e0091a65a9d56f1d80dd1d58089a6b5cc1d73e4e513b8d8b526e27d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2EvaluationThreshold]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a922d00345b77236ea699f16b50e6ed6f3add90b6fdd7f512bb3a722ab359db3(
    *,
    bool_value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    double_value: typing.Optional[jsii.Number] = None,
    string_value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32c9d75dc889ef5a156912e9bfdee972b4831340883e02b772dfa3bdfc49176a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6513c1e247002a2b8e82ae2e1cfacc1a7bea0897deb1d3f7b075e799a99e8bf6(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ba5a17d23b8c553a9afcce50d7e1b902c2a3ec452b0f48eb90391c7b1de64ff(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__682aa512169c822d7c43f11adba5a7e5a65a9be8ccc8c1f473d51aac7470dde1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f2e00f81962d36031befcc289021f7e65f9673692d80fe691e7ad80de598fde(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2EvaluationThresholdValue]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff45c72469e4360972d641f9d23cf448fb87ab47b3fda677df55b581c47b04e0(
    *,
    service_principal_name: typing.Optional[builtins.str] = None,
    user_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ede214c2b42b3dc7964909425666d1e7dea50e22dbfd01fd0d48da6c97059e98(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__714b4380762ac80cdbb30d0f6871988f86bc2cad4f0124bf3932e7e5c9e9a4ef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce1640702440c9594cc011b13c48cc2652e20f90b4b6f8d0d65313d10a0f4f67(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e17a85b4d0b4f1af07f362c317678f510be1fc8a380f30e92da26729b8ac2b92(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2RunAs]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c794896635dd36bd022d6bce5396f6775c7efa4640c52d35cd5bef9ca09f148(
    *,
    pause_status: typing.Optional[builtins.str] = None,
    quartz_cron_schedule: typing.Optional[builtins.str] = None,
    timezone_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea42dfade7ef03589d234779850a332af5758e79334147f35f2be5126196cc7f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f692fdd6dcfd448685d468147943ed1537cc45a06ec863b0a77776066620f904(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__712fc2e3480a290be8be35b65aa88eceee5f642e4823057bd0c6414a63c1dbb4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26752a9f13ba605e16edea062772af5ec1494693db2f5df21d74daf51b704dbe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8796aa99166698588e5eb74587065829f6143d10e8c11557e408de54defc2903(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertV2Schedule]],
) -> None:
    """Type checking stubs"""
    pass
