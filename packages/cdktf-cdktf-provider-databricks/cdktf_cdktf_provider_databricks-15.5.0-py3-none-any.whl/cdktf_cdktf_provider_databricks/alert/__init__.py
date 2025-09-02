r'''
# `databricks_alert`

Refer to the Terraform Registry for docs: [`databricks_alert`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert).
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


class Alert(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.alert.Alert",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert databricks_alert}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        condition: typing.Union["AlertCondition", typing.Dict[builtins.str, typing.Any]],
        display_name: builtins.str,
        query_id: builtins.str,
        custom_body: typing.Optional[builtins.str] = None,
        custom_subject: typing.Optional[builtins.str] = None,
        notify_on_ok: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        owner_user_name: typing.Optional[builtins.str] = None,
        parent_path: typing.Optional[builtins.str] = None,
        seconds_to_retrigger: typing.Optional[jsii.Number] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert databricks_alert} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param condition: condition block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#condition Alert#condition}
        :param display_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#display_name Alert#display_name}.
        :param query_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#query_id Alert#query_id}.
        :param custom_body: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#custom_body Alert#custom_body}.
        :param custom_subject: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#custom_subject Alert#custom_subject}.
        :param notify_on_ok: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#notify_on_ok Alert#notify_on_ok}.
        :param owner_user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#owner_user_name Alert#owner_user_name}.
        :param parent_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#parent_path Alert#parent_path}.
        :param seconds_to_retrigger: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#seconds_to_retrigger Alert#seconds_to_retrigger}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10a9f2ebc8c289606d48346aded858543421b61dc49c1343ad9654f31afd4e76)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = AlertConfig(
            condition=condition,
            display_name=display_name,
            query_id=query_id,
            custom_body=custom_body,
            custom_subject=custom_subject,
            notify_on_ok=notify_on_ok,
            owner_user_name=owner_user_name,
            parent_path=parent_path,
            seconds_to_retrigger=seconds_to_retrigger,
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
        '''Generates CDKTF code for importing a Alert resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the Alert to import.
        :param import_from_id: The id of the existing Alert that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the Alert to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__477bc1054eb40b9827841049d5350d70e28f4a9ea98e1803b9041d1285341ca0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putCondition")
    def put_condition(
        self,
        *,
        op: builtins.str,
        operand: typing.Union["AlertConditionOperand", typing.Dict[builtins.str, typing.Any]],
        empty_result_state: typing.Optional[builtins.str] = None,
        threshold: typing.Optional[typing.Union["AlertConditionThreshold", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param op: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#op Alert#op}.
        :param operand: operand block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#operand Alert#operand}
        :param empty_result_state: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#empty_result_state Alert#empty_result_state}.
        :param threshold: threshold block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#threshold Alert#threshold}
        '''
        value = AlertCondition(
            op=op,
            operand=operand,
            empty_result_state=empty_result_state,
            threshold=threshold,
        )

        return typing.cast(None, jsii.invoke(self, "putCondition", [value]))

    @jsii.member(jsii_name="resetCustomBody")
    def reset_custom_body(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomBody", []))

    @jsii.member(jsii_name="resetCustomSubject")
    def reset_custom_subject(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomSubject", []))

    @jsii.member(jsii_name="resetNotifyOnOk")
    def reset_notify_on_ok(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotifyOnOk", []))

    @jsii.member(jsii_name="resetOwnerUserName")
    def reset_owner_user_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOwnerUserName", []))

    @jsii.member(jsii_name="resetParentPath")
    def reset_parent_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParentPath", []))

    @jsii.member(jsii_name="resetSecondsToRetrigger")
    def reset_seconds_to_retrigger(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecondsToRetrigger", []))

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
    @jsii.member(jsii_name="condition")
    def condition(self) -> "AlertConditionOutputReference":
        return typing.cast("AlertConditionOutputReference", jsii.get(self, "condition"))

    @builtins.property
    @jsii.member(jsii_name="createTime")
    def create_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createTime"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="lifecycleState")
    def lifecycle_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lifecycleState"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="triggerTime")
    def trigger_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "triggerTime"))

    @builtins.property
    @jsii.member(jsii_name="updateTime")
    def update_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updateTime"))

    @builtins.property
    @jsii.member(jsii_name="conditionInput")
    def condition_input(self) -> typing.Optional["AlertCondition"]:
        return typing.cast(typing.Optional["AlertCondition"], jsii.get(self, "conditionInput"))

    @builtins.property
    @jsii.member(jsii_name="customBodyInput")
    def custom_body_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customBodyInput"))

    @builtins.property
    @jsii.member(jsii_name="customSubjectInput")
    def custom_subject_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customSubjectInput"))

    @builtins.property
    @jsii.member(jsii_name="displayNameInput")
    def display_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "displayNameInput"))

    @builtins.property
    @jsii.member(jsii_name="notifyOnOkInput")
    def notify_on_ok_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "notifyOnOkInput"))

    @builtins.property
    @jsii.member(jsii_name="ownerUserNameInput")
    def owner_user_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ownerUserNameInput"))

    @builtins.property
    @jsii.member(jsii_name="parentPathInput")
    def parent_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parentPathInput"))

    @builtins.property
    @jsii.member(jsii_name="queryIdInput")
    def query_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queryIdInput"))

    @builtins.property
    @jsii.member(jsii_name="secondsToRetriggerInput")
    def seconds_to_retrigger_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "secondsToRetriggerInput"))

    @builtins.property
    @jsii.member(jsii_name="customBody")
    def custom_body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customBody"))

    @custom_body.setter
    def custom_body(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e1f8766cee1f312e56193384e739402ddd72fb445e90dcf2cd54d153a727125)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customBody", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="customSubject")
    def custom_subject(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customSubject"))

    @custom_subject.setter
    def custom_subject(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60bf5a7283379bcef05229b7440d6feeaeed786d85c26e9d61bb8cb2f9baf5cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customSubject", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "displayName"))

    @display_name.setter
    def display_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86e237ce91fd081ad47f519ba27bbed7edccdadfc28f5a979dc1dddc39eda35e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "displayName", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__fe09e28c2b8f0055e6ae75d6d1b00e860919c45472a3b6e498dfbcc63f0946c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notifyOnOk", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ownerUserName")
    def owner_user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ownerUserName"))

    @owner_user_name.setter
    def owner_user_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4712777adf3a5a2dd66b1012ced284e4c69eb761c6f6304afaf17c913acfc6a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ownerUserName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parentPath")
    def parent_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parentPath"))

    @parent_path.setter
    def parent_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5889acd0729a3e3d4f3f4bbcfb646588e4f4df9506aff32aaa46255a170b93d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parentPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="queryId")
    def query_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queryId"))

    @query_id.setter
    def query_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f09d34e74b75cd5691eb08039cdfce7d5c78ce7c017b22fada403ce5d5592d15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "queryId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secondsToRetrigger")
    def seconds_to_retrigger(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "secondsToRetrigger"))

    @seconds_to_retrigger.setter
    def seconds_to_retrigger(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcd99e4d1005fbb42198bf780272d5aefbc0947aa6b810e6c07d49d04c467dad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secondsToRetrigger", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.alert.AlertCondition",
    jsii_struct_bases=[],
    name_mapping={
        "op": "op",
        "operand": "operand",
        "empty_result_state": "emptyResultState",
        "threshold": "threshold",
    },
)
class AlertCondition:
    def __init__(
        self,
        *,
        op: builtins.str,
        operand: typing.Union["AlertConditionOperand", typing.Dict[builtins.str, typing.Any]],
        empty_result_state: typing.Optional[builtins.str] = None,
        threshold: typing.Optional[typing.Union["AlertConditionThreshold", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param op: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#op Alert#op}.
        :param operand: operand block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#operand Alert#operand}
        :param empty_result_state: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#empty_result_state Alert#empty_result_state}.
        :param threshold: threshold block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#threshold Alert#threshold}
        '''
        if isinstance(operand, dict):
            operand = AlertConditionOperand(**operand)
        if isinstance(threshold, dict):
            threshold = AlertConditionThreshold(**threshold)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ab5a506a7afb318f3a0edddf895a1a457d61ee10e56e3f1cec247280144fa25)
            check_type(argname="argument op", value=op, expected_type=type_hints["op"])
            check_type(argname="argument operand", value=operand, expected_type=type_hints["operand"])
            check_type(argname="argument empty_result_state", value=empty_result_state, expected_type=type_hints["empty_result_state"])
            check_type(argname="argument threshold", value=threshold, expected_type=type_hints["threshold"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "op": op,
            "operand": operand,
        }
        if empty_result_state is not None:
            self._values["empty_result_state"] = empty_result_state
        if threshold is not None:
            self._values["threshold"] = threshold

    @builtins.property
    def op(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#op Alert#op}.'''
        result = self._values.get("op")
        assert result is not None, "Required property 'op' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def operand(self) -> "AlertConditionOperand":
        '''operand block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#operand Alert#operand}
        '''
        result = self._values.get("operand")
        assert result is not None, "Required property 'operand' is missing"
        return typing.cast("AlertConditionOperand", result)

    @builtins.property
    def empty_result_state(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#empty_result_state Alert#empty_result_state}.'''
        result = self._values.get("empty_result_state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def threshold(self) -> typing.Optional["AlertConditionThreshold"]:
        '''threshold block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#threshold Alert#threshold}
        '''
        result = self._values.get("threshold")
        return typing.cast(typing.Optional["AlertConditionThreshold"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertCondition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.alert.AlertConditionOperand",
    jsii_struct_bases=[],
    name_mapping={"column": "column"},
)
class AlertConditionOperand:
    def __init__(
        self,
        *,
        column: typing.Union["AlertConditionOperandColumn", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param column: column block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#column Alert#column}
        '''
        if isinstance(column, dict):
            column = AlertConditionOperandColumn(**column)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58e8447c56fa7317e369383f61eefca63ff5c4cb283fe1a962aa49ed22736eb1)
            check_type(argname="argument column", value=column, expected_type=type_hints["column"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "column": column,
        }

    @builtins.property
    def column(self) -> "AlertConditionOperandColumn":
        '''column block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#column Alert#column}
        '''
        result = self._values.get("column")
        assert result is not None, "Required property 'column' is missing"
        return typing.cast("AlertConditionOperandColumn", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertConditionOperand(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.alert.AlertConditionOperandColumn",
    jsii_struct_bases=[],
    name_mapping={"name": "name"},
)
class AlertConditionOperandColumn:
    def __init__(self, *, name: builtins.str) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#name Alert#name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__080996d85c140099d56f41061cff208d33b3a0a24a64195783c19020b4df3e21)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#name Alert#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertConditionOperandColumn(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AlertConditionOperandColumnOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.alert.AlertConditionOperandColumnOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d82e461cb7b0c946a0bc3726a55b6a7073142499430414c1bd619e4f79694323)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c03e45678434ddb9de7e74dc676cd0867ece2be8873f9bb8705730ce2fecdbf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AlertConditionOperandColumn]:
        return typing.cast(typing.Optional[AlertConditionOperandColumn], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AlertConditionOperandColumn],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2b777c40c620691a6fab3e762f93fe017a09f505462a3e29437efa8e8a15129)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class AlertConditionOperandOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.alert.AlertConditionOperandOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__918ee72b82bfb862dd7876e58b01dda2112bebdb5d6d7c54b1accd65ad9b578e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putColumn")
    def put_column(self, *, name: builtins.str) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#name Alert#name}.
        '''
        value = AlertConditionOperandColumn(name=name)

        return typing.cast(None, jsii.invoke(self, "putColumn", [value]))

    @builtins.property
    @jsii.member(jsii_name="column")
    def column(self) -> AlertConditionOperandColumnOutputReference:
        return typing.cast(AlertConditionOperandColumnOutputReference, jsii.get(self, "column"))

    @builtins.property
    @jsii.member(jsii_name="columnInput")
    def column_input(self) -> typing.Optional[AlertConditionOperandColumn]:
        return typing.cast(typing.Optional[AlertConditionOperandColumn], jsii.get(self, "columnInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AlertConditionOperand]:
        return typing.cast(typing.Optional[AlertConditionOperand], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[AlertConditionOperand]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__362777edd40373c0797eac65c4a3861e950e6c8fd6598119388c5f691dec14ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class AlertConditionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.alert.AlertConditionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c01f3b9fbf8a78c68138f97e46176702ec5308a00967556908ec755f4c857353)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putOperand")
    def put_operand(
        self,
        *,
        column: typing.Union[AlertConditionOperandColumn, typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param column: column block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#column Alert#column}
        '''
        value = AlertConditionOperand(column=column)

        return typing.cast(None, jsii.invoke(self, "putOperand", [value]))

    @jsii.member(jsii_name="putThreshold")
    def put_threshold(
        self,
        *,
        value: typing.Union["AlertConditionThresholdValue", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param value: value block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#value Alert#value}
        '''
        value_ = AlertConditionThreshold(value=value)

        return typing.cast(None, jsii.invoke(self, "putThreshold", [value_]))

    @jsii.member(jsii_name="resetEmptyResultState")
    def reset_empty_result_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmptyResultState", []))

    @jsii.member(jsii_name="resetThreshold")
    def reset_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreshold", []))

    @builtins.property
    @jsii.member(jsii_name="operand")
    def operand(self) -> AlertConditionOperandOutputReference:
        return typing.cast(AlertConditionOperandOutputReference, jsii.get(self, "operand"))

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> "AlertConditionThresholdOutputReference":
        return typing.cast("AlertConditionThresholdOutputReference", jsii.get(self, "threshold"))

    @builtins.property
    @jsii.member(jsii_name="emptyResultStateInput")
    def empty_result_state_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emptyResultStateInput"))

    @builtins.property
    @jsii.member(jsii_name="operandInput")
    def operand_input(self) -> typing.Optional[AlertConditionOperand]:
        return typing.cast(typing.Optional[AlertConditionOperand], jsii.get(self, "operandInput"))

    @builtins.property
    @jsii.member(jsii_name="opInput")
    def op_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "opInput"))

    @builtins.property
    @jsii.member(jsii_name="thresholdInput")
    def threshold_input(self) -> typing.Optional["AlertConditionThreshold"]:
        return typing.cast(typing.Optional["AlertConditionThreshold"], jsii.get(self, "thresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="emptyResultState")
    def empty_result_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emptyResultState"))

    @empty_result_state.setter
    def empty_result_state(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65b584056e56cee80ed11e7da3b9c58c2c491b58cf18b196a5ebe1c1bd851018)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emptyResultState", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="op")
    def op(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "op"))

    @op.setter
    def op(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddc5e973bea430a7d925d50c75801865d4bb4807af3a0b4ceec942e4a8b9a00d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "op", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AlertCondition]:
        return typing.cast(typing.Optional[AlertCondition], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[AlertCondition]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8984bdcfed13eccb08e2d94e90e94bebdfc0a1e0d10b732c7473990d9e7bb6be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.alert.AlertConditionThreshold",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class AlertConditionThreshold:
    def __init__(
        self,
        *,
        value: typing.Union["AlertConditionThresholdValue", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param value: value block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#value Alert#value}
        '''
        if isinstance(value, dict):
            value = AlertConditionThresholdValue(**value)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2aea09bf5e6b756884523cc102d2d7f03efd102d6e140dffe4ed95c61030880)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "value": value,
        }

    @builtins.property
    def value(self) -> "AlertConditionThresholdValue":
        '''value block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#value Alert#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast("AlertConditionThresholdValue", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertConditionThreshold(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AlertConditionThresholdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.alert.AlertConditionThresholdOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a700be8fd875d374566ead3a1ff94ce85ce3b30df3b4caa52a330ed290eb6cdf)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putValue")
    def put_value(
        self,
        *,
        bool_value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        double_value: typing.Optional[jsii.Number] = None,
        string_value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bool_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#bool_value Alert#bool_value}.
        :param double_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#double_value Alert#double_value}.
        :param string_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#string_value Alert#string_value}.
        '''
        value = AlertConditionThresholdValue(
            bool_value=bool_value, double_value=double_value, string_value=string_value
        )

        return typing.cast(None, jsii.invoke(self, "putValue", [value]))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> "AlertConditionThresholdValueOutputReference":
        return typing.cast("AlertConditionThresholdValueOutputReference", jsii.get(self, "value"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional["AlertConditionThresholdValue"]:
        return typing.cast(typing.Optional["AlertConditionThresholdValue"], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AlertConditionThreshold]:
        return typing.cast(typing.Optional[AlertConditionThreshold], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[AlertConditionThreshold]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2143014227dcad339d4416f3307f2b220c076925d8e23eb2ce65c13ef236207d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.alert.AlertConditionThresholdValue",
    jsii_struct_bases=[],
    name_mapping={
        "bool_value": "boolValue",
        "double_value": "doubleValue",
        "string_value": "stringValue",
    },
)
class AlertConditionThresholdValue:
    def __init__(
        self,
        *,
        bool_value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        double_value: typing.Optional[jsii.Number] = None,
        string_value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bool_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#bool_value Alert#bool_value}.
        :param double_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#double_value Alert#double_value}.
        :param string_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#string_value Alert#string_value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__453e7b3ae205f1817c0878a4368608d6a26a03c959d292ea38dd74287b0b71ee)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#bool_value Alert#bool_value}.'''
        result = self._values.get("bool_value")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def double_value(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#double_value Alert#double_value}.'''
        result = self._values.get("double_value")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def string_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#string_value Alert#string_value}.'''
        result = self._values.get("string_value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertConditionThresholdValue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AlertConditionThresholdValueOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.alert.AlertConditionThresholdValueOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e8d63ef3ce3ce4060a08a9ce66a5de82555ef085453f46668eec69802a29a09b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2d583d6c7ce0cc1bfd174801d7b1873a3833612db7d767e938bb100091d46488)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boolValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="doubleValue")
    def double_value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "doubleValue"))

    @double_value.setter
    def double_value(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3348711e099bda4edd3beab904da06c67cdc326a5d3fb7f6cefa0c52d63e0070)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "doubleValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stringValue")
    def string_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stringValue"))

    @string_value.setter
    def string_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee5249521b104e59d2e7331fc1a7592b7d0af1f9354eac176b24c681c8244c29)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stringValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AlertConditionThresholdValue]:
        return typing.cast(typing.Optional[AlertConditionThresholdValue], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AlertConditionThresholdValue],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__157a8592adab0e6c23dd361160a8a616e9ac40a943d357ab244fe3c79941c45f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.alert.AlertConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "condition": "condition",
        "display_name": "displayName",
        "query_id": "queryId",
        "custom_body": "customBody",
        "custom_subject": "customSubject",
        "notify_on_ok": "notifyOnOk",
        "owner_user_name": "ownerUserName",
        "parent_path": "parentPath",
        "seconds_to_retrigger": "secondsToRetrigger",
    },
)
class AlertConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        condition: typing.Union[AlertCondition, typing.Dict[builtins.str, typing.Any]],
        display_name: builtins.str,
        query_id: builtins.str,
        custom_body: typing.Optional[builtins.str] = None,
        custom_subject: typing.Optional[builtins.str] = None,
        notify_on_ok: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        owner_user_name: typing.Optional[builtins.str] = None,
        parent_path: typing.Optional[builtins.str] = None,
        seconds_to_retrigger: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param condition: condition block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#condition Alert#condition}
        :param display_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#display_name Alert#display_name}.
        :param query_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#query_id Alert#query_id}.
        :param custom_body: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#custom_body Alert#custom_body}.
        :param custom_subject: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#custom_subject Alert#custom_subject}.
        :param notify_on_ok: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#notify_on_ok Alert#notify_on_ok}.
        :param owner_user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#owner_user_name Alert#owner_user_name}.
        :param parent_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#parent_path Alert#parent_path}.
        :param seconds_to_retrigger: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#seconds_to_retrigger Alert#seconds_to_retrigger}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(condition, dict):
            condition = AlertCondition(**condition)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__236ffd4d3cecba403a12fa2b33420c958b9f345162d972f0ce1ef702a53d9aef)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument condition", value=condition, expected_type=type_hints["condition"])
            check_type(argname="argument display_name", value=display_name, expected_type=type_hints["display_name"])
            check_type(argname="argument query_id", value=query_id, expected_type=type_hints["query_id"])
            check_type(argname="argument custom_body", value=custom_body, expected_type=type_hints["custom_body"])
            check_type(argname="argument custom_subject", value=custom_subject, expected_type=type_hints["custom_subject"])
            check_type(argname="argument notify_on_ok", value=notify_on_ok, expected_type=type_hints["notify_on_ok"])
            check_type(argname="argument owner_user_name", value=owner_user_name, expected_type=type_hints["owner_user_name"])
            check_type(argname="argument parent_path", value=parent_path, expected_type=type_hints["parent_path"])
            check_type(argname="argument seconds_to_retrigger", value=seconds_to_retrigger, expected_type=type_hints["seconds_to_retrigger"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "condition": condition,
            "display_name": display_name,
            "query_id": query_id,
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
        if custom_body is not None:
            self._values["custom_body"] = custom_body
        if custom_subject is not None:
            self._values["custom_subject"] = custom_subject
        if notify_on_ok is not None:
            self._values["notify_on_ok"] = notify_on_ok
        if owner_user_name is not None:
            self._values["owner_user_name"] = owner_user_name
        if parent_path is not None:
            self._values["parent_path"] = parent_path
        if seconds_to_retrigger is not None:
            self._values["seconds_to_retrigger"] = seconds_to_retrigger

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
    def condition(self) -> AlertCondition:
        '''condition block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#condition Alert#condition}
        '''
        result = self._values.get("condition")
        assert result is not None, "Required property 'condition' is missing"
        return typing.cast(AlertCondition, result)

    @builtins.property
    def display_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#display_name Alert#display_name}.'''
        result = self._values.get("display_name")
        assert result is not None, "Required property 'display_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def query_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#query_id Alert#query_id}.'''
        result = self._values.get("query_id")
        assert result is not None, "Required property 'query_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def custom_body(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#custom_body Alert#custom_body}.'''
        result = self._values.get("custom_body")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_subject(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#custom_subject Alert#custom_subject}.'''
        result = self._values.get("custom_subject")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notify_on_ok(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#notify_on_ok Alert#notify_on_ok}.'''
        result = self._values.get("notify_on_ok")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def owner_user_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#owner_user_name Alert#owner_user_name}.'''
        result = self._values.get("owner_user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#parent_path Alert#parent_path}.'''
        result = self._values.get("parent_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def seconds_to_retrigger(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/alert#seconds_to_retrigger Alert#seconds_to_retrigger}.'''
        result = self._values.get("seconds_to_retrigger")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Alert",
    "AlertCondition",
    "AlertConditionOperand",
    "AlertConditionOperandColumn",
    "AlertConditionOperandColumnOutputReference",
    "AlertConditionOperandOutputReference",
    "AlertConditionOutputReference",
    "AlertConditionThreshold",
    "AlertConditionThresholdOutputReference",
    "AlertConditionThresholdValue",
    "AlertConditionThresholdValueOutputReference",
    "AlertConfig",
]

publication.publish()

def _typecheckingstub__10a9f2ebc8c289606d48346aded858543421b61dc49c1343ad9654f31afd4e76(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    condition: typing.Union[AlertCondition, typing.Dict[builtins.str, typing.Any]],
    display_name: builtins.str,
    query_id: builtins.str,
    custom_body: typing.Optional[builtins.str] = None,
    custom_subject: typing.Optional[builtins.str] = None,
    notify_on_ok: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    owner_user_name: typing.Optional[builtins.str] = None,
    parent_path: typing.Optional[builtins.str] = None,
    seconds_to_retrigger: typing.Optional[jsii.Number] = None,
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

def _typecheckingstub__477bc1054eb40b9827841049d5350d70e28f4a9ea98e1803b9041d1285341ca0(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e1f8766cee1f312e56193384e739402ddd72fb445e90dcf2cd54d153a727125(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60bf5a7283379bcef05229b7440d6feeaeed786d85c26e9d61bb8cb2f9baf5cd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86e237ce91fd081ad47f519ba27bbed7edccdadfc28f5a979dc1dddc39eda35e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe09e28c2b8f0055e6ae75d6d1b00e860919c45472a3b6e498dfbcc63f0946c7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4712777adf3a5a2dd66b1012ced284e4c69eb761c6f6304afaf17c913acfc6a5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5889acd0729a3e3d4f3f4bbcfb646588e4f4df9506aff32aaa46255a170b93d7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f09d34e74b75cd5691eb08039cdfce7d5c78ce7c017b22fada403ce5d5592d15(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcd99e4d1005fbb42198bf780272d5aefbc0947aa6b810e6c07d49d04c467dad(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ab5a506a7afb318f3a0edddf895a1a457d61ee10e56e3f1cec247280144fa25(
    *,
    op: builtins.str,
    operand: typing.Union[AlertConditionOperand, typing.Dict[builtins.str, typing.Any]],
    empty_result_state: typing.Optional[builtins.str] = None,
    threshold: typing.Optional[typing.Union[AlertConditionThreshold, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58e8447c56fa7317e369383f61eefca63ff5c4cb283fe1a962aa49ed22736eb1(
    *,
    column: typing.Union[AlertConditionOperandColumn, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__080996d85c140099d56f41061cff208d33b3a0a24a64195783c19020b4df3e21(
    *,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d82e461cb7b0c946a0bc3726a55b6a7073142499430414c1bd619e4f79694323(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c03e45678434ddb9de7e74dc676cd0867ece2be8873f9bb8705730ce2fecdbf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2b777c40c620691a6fab3e762f93fe017a09f505462a3e29437efa8e8a15129(
    value: typing.Optional[AlertConditionOperandColumn],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__918ee72b82bfb862dd7876e58b01dda2112bebdb5d6d7c54b1accd65ad9b578e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__362777edd40373c0797eac65c4a3861e950e6c8fd6598119388c5f691dec14ab(
    value: typing.Optional[AlertConditionOperand],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c01f3b9fbf8a78c68138f97e46176702ec5308a00967556908ec755f4c857353(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65b584056e56cee80ed11e7da3b9c58c2c491b58cf18b196a5ebe1c1bd851018(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddc5e973bea430a7d925d50c75801865d4bb4807af3a0b4ceec942e4a8b9a00d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8984bdcfed13eccb08e2d94e90e94bebdfc0a1e0d10b732c7473990d9e7bb6be(
    value: typing.Optional[AlertCondition],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2aea09bf5e6b756884523cc102d2d7f03efd102d6e140dffe4ed95c61030880(
    *,
    value: typing.Union[AlertConditionThresholdValue, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a700be8fd875d374566ead3a1ff94ce85ce3b30df3b4caa52a330ed290eb6cdf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2143014227dcad339d4416f3307f2b220c076925d8e23eb2ce65c13ef236207d(
    value: typing.Optional[AlertConditionThreshold],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__453e7b3ae205f1817c0878a4368608d6a26a03c959d292ea38dd74287b0b71ee(
    *,
    bool_value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    double_value: typing.Optional[jsii.Number] = None,
    string_value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8d63ef3ce3ce4060a08a9ce66a5de82555ef085453f46668eec69802a29a09b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d583d6c7ce0cc1bfd174801d7b1873a3833612db7d767e938bb100091d46488(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3348711e099bda4edd3beab904da06c67cdc326a5d3fb7f6cefa0c52d63e0070(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee5249521b104e59d2e7331fc1a7592b7d0af1f9354eac176b24c681c8244c29(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__157a8592adab0e6c23dd361160a8a616e9ac40a943d357ab244fe3c79941c45f(
    value: typing.Optional[AlertConditionThresholdValue],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__236ffd4d3cecba403a12fa2b33420c958b9f345162d972f0ce1ef702a53d9aef(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    condition: typing.Union[AlertCondition, typing.Dict[builtins.str, typing.Any]],
    display_name: builtins.str,
    query_id: builtins.str,
    custom_body: typing.Optional[builtins.str] = None,
    custom_subject: typing.Optional[builtins.str] = None,
    notify_on_ok: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    owner_user_name: typing.Optional[builtins.str] = None,
    parent_path: typing.Optional[builtins.str] = None,
    seconds_to_retrigger: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass
