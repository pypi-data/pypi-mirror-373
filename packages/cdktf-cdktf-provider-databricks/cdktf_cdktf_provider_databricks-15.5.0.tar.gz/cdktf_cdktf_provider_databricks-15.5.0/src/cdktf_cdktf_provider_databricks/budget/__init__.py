r'''
# `databricks_budget`

Refer to the Terraform Registry for docs: [`databricks_budget`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget).
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


class Budget(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.budget.Budget",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget databricks_budget}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        account_id: typing.Optional[builtins.str] = None,
        alert_configurations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["BudgetAlertConfigurations", typing.Dict[builtins.str, typing.Any]]]]] = None,
        budget_configuration_id: typing.Optional[builtins.str] = None,
        create_time: typing.Optional[jsii.Number] = None,
        display_name: typing.Optional[builtins.str] = None,
        filter: typing.Optional[typing.Union["BudgetFilter", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        update_time: typing.Optional[jsii.Number] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget databricks_budget} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#account_id Budget#account_id}.
        :param alert_configurations: alert_configurations block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#alert_configurations Budget#alert_configurations}
        :param budget_configuration_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#budget_configuration_id Budget#budget_configuration_id}.
        :param create_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#create_time Budget#create_time}.
        :param display_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#display_name Budget#display_name}.
        :param filter: filter block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#filter Budget#filter}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#id Budget#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param update_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#update_time Budget#update_time}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__174326d81483b00a42ac61c92f23e171206eb13f1744863d3a44385969db8459)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = BudgetConfig(
            account_id=account_id,
            alert_configurations=alert_configurations,
            budget_configuration_id=budget_configuration_id,
            create_time=create_time,
            display_name=display_name,
            filter=filter,
            id=id,
            update_time=update_time,
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
        '''Generates CDKTF code for importing a Budget resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the Budget to import.
        :param import_from_id: The id of the existing Budget that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the Budget to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f42104772a3adaab199aa31d0c269b3ebaec31cd974fa3f07f7ecccb922e88f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAlertConfigurations")
    def put_alert_configurations(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["BudgetAlertConfigurations", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56c8cb8c957a136ab0aba5d3848affdfcadcd2480d149d64ea582430940bdac1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAlertConfigurations", [value]))

    @jsii.member(jsii_name="putFilter")
    def put_filter(
        self,
        *,
        tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["BudgetFilterTags", typing.Dict[builtins.str, typing.Any]]]]] = None,
        workspace_id: typing.Optional[typing.Union["BudgetFilterWorkspaceId", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param tags: tags block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#tags Budget#tags}
        :param workspace_id: workspace_id block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#workspace_id Budget#workspace_id}
        '''
        value = BudgetFilter(tags=tags, workspace_id=workspace_id)

        return typing.cast(None, jsii.invoke(self, "putFilter", [value]))

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="resetAlertConfigurations")
    def reset_alert_configurations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlertConfigurations", []))

    @jsii.member(jsii_name="resetBudgetConfigurationId")
    def reset_budget_configuration_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBudgetConfigurationId", []))

    @jsii.member(jsii_name="resetCreateTime")
    def reset_create_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreateTime", []))

    @jsii.member(jsii_name="resetDisplayName")
    def reset_display_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisplayName", []))

    @jsii.member(jsii_name="resetFilter")
    def reset_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilter", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetUpdateTime")
    def reset_update_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdateTime", []))

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
    @jsii.member(jsii_name="alertConfigurations")
    def alert_configurations(self) -> "BudgetAlertConfigurationsList":
        return typing.cast("BudgetAlertConfigurationsList", jsii.get(self, "alertConfigurations"))

    @builtins.property
    @jsii.member(jsii_name="filter")
    def filter(self) -> "BudgetFilterOutputReference":
        return typing.cast("BudgetFilterOutputReference", jsii.get(self, "filter"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="alertConfigurationsInput")
    def alert_configurations_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["BudgetAlertConfigurations"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["BudgetAlertConfigurations"]]], jsii.get(self, "alertConfigurationsInput"))

    @builtins.property
    @jsii.member(jsii_name="budgetConfigurationIdInput")
    def budget_configuration_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "budgetConfigurationIdInput"))

    @builtins.property
    @jsii.member(jsii_name="createTimeInput")
    def create_time_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "createTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="displayNameInput")
    def display_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "displayNameInput"))

    @builtins.property
    @jsii.member(jsii_name="filterInput")
    def filter_input(self) -> typing.Optional["BudgetFilter"]:
        return typing.cast(typing.Optional["BudgetFilter"], jsii.get(self, "filterInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="updateTimeInput")
    def update_time_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "updateTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e500d6e3fa20261d3cc96aed2d8ce3a6dc260a1fd05d7ad3f295db76fc88faa8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="budgetConfigurationId")
    def budget_configuration_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "budgetConfigurationId"))

    @budget_configuration_id.setter
    def budget_configuration_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6418d632e4cf1405ad8f65ca5a9a3faff9dc3729f839b56ab592ee872b1998a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "budgetConfigurationId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="createTime")
    def create_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "createTime"))

    @create_time.setter
    def create_time(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__068261561cda897932cc08d856062ac058c294e591acd8ec9d5113028d2f669c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "displayName"))

    @display_name.setter
    def display_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8bf587af3ff268b2f3c7df1c9afc612d9f84de48b401ac5be4087c5ec8085df7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "displayName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__446097c4d9e9496c9cc921989d922ddd43499a08478af7b2634411695ef03360)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="updateTime")
    def update_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "updateTime"))

    @update_time.setter
    def update_time(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0dc0dd67d124eb9329c4e8e9233840ddfbb23b6fd6da1baba96004f142166fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "updateTime", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.budget.BudgetAlertConfigurations",
    jsii_struct_bases=[],
    name_mapping={
        "action_configurations": "actionConfigurations",
        "alert_configuration_id": "alertConfigurationId",
        "quantity_threshold": "quantityThreshold",
        "quantity_type": "quantityType",
        "time_period": "timePeriod",
        "trigger_type": "triggerType",
    },
)
class BudgetAlertConfigurations:
    def __init__(
        self,
        *,
        action_configurations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["BudgetAlertConfigurationsActionConfigurations", typing.Dict[builtins.str, typing.Any]]]]] = None,
        alert_configuration_id: typing.Optional[builtins.str] = None,
        quantity_threshold: typing.Optional[builtins.str] = None,
        quantity_type: typing.Optional[builtins.str] = None,
        time_period: typing.Optional[builtins.str] = None,
        trigger_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param action_configurations: action_configurations block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#action_configurations Budget#action_configurations}
        :param alert_configuration_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#alert_configuration_id Budget#alert_configuration_id}.
        :param quantity_threshold: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#quantity_threshold Budget#quantity_threshold}.
        :param quantity_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#quantity_type Budget#quantity_type}.
        :param time_period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#time_period Budget#time_period}.
        :param trigger_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#trigger_type Budget#trigger_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__965ae6856c7198c887f33b8148c80b7d48784c33d6143f682dd422cbeb707a26)
            check_type(argname="argument action_configurations", value=action_configurations, expected_type=type_hints["action_configurations"])
            check_type(argname="argument alert_configuration_id", value=alert_configuration_id, expected_type=type_hints["alert_configuration_id"])
            check_type(argname="argument quantity_threshold", value=quantity_threshold, expected_type=type_hints["quantity_threshold"])
            check_type(argname="argument quantity_type", value=quantity_type, expected_type=type_hints["quantity_type"])
            check_type(argname="argument time_period", value=time_period, expected_type=type_hints["time_period"])
            check_type(argname="argument trigger_type", value=trigger_type, expected_type=type_hints["trigger_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if action_configurations is not None:
            self._values["action_configurations"] = action_configurations
        if alert_configuration_id is not None:
            self._values["alert_configuration_id"] = alert_configuration_id
        if quantity_threshold is not None:
            self._values["quantity_threshold"] = quantity_threshold
        if quantity_type is not None:
            self._values["quantity_type"] = quantity_type
        if time_period is not None:
            self._values["time_period"] = time_period
        if trigger_type is not None:
            self._values["trigger_type"] = trigger_type

    @builtins.property
    def action_configurations(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["BudgetAlertConfigurationsActionConfigurations"]]]:
        '''action_configurations block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#action_configurations Budget#action_configurations}
        '''
        result = self._values.get("action_configurations")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["BudgetAlertConfigurationsActionConfigurations"]]], result)

    @builtins.property
    def alert_configuration_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#alert_configuration_id Budget#alert_configuration_id}.'''
        result = self._values.get("alert_configuration_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def quantity_threshold(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#quantity_threshold Budget#quantity_threshold}.'''
        result = self._values.get("quantity_threshold")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def quantity_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#quantity_type Budget#quantity_type}.'''
        result = self._values.get("quantity_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def time_period(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#time_period Budget#time_period}.'''
        result = self._values.get("time_period")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def trigger_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#trigger_type Budget#trigger_type}.'''
        result = self._values.get("trigger_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BudgetAlertConfigurations(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.budget.BudgetAlertConfigurationsActionConfigurations",
    jsii_struct_bases=[],
    name_mapping={
        "action_configuration_id": "actionConfigurationId",
        "action_type": "actionType",
        "target": "target",
    },
)
class BudgetAlertConfigurationsActionConfigurations:
    def __init__(
        self,
        *,
        action_configuration_id: typing.Optional[builtins.str] = None,
        action_type: typing.Optional[builtins.str] = None,
        target: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param action_configuration_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#action_configuration_id Budget#action_configuration_id}.
        :param action_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#action_type Budget#action_type}.
        :param target: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#target Budget#target}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f66fe903368694c3b0efaeba494eeb190f81a91e2c2487b8a02edf8fb7651dc1)
            check_type(argname="argument action_configuration_id", value=action_configuration_id, expected_type=type_hints["action_configuration_id"])
            check_type(argname="argument action_type", value=action_type, expected_type=type_hints["action_type"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if action_configuration_id is not None:
            self._values["action_configuration_id"] = action_configuration_id
        if action_type is not None:
            self._values["action_type"] = action_type
        if target is not None:
            self._values["target"] = target

    @builtins.property
    def action_configuration_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#action_configuration_id Budget#action_configuration_id}.'''
        result = self._values.get("action_configuration_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def action_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#action_type Budget#action_type}.'''
        result = self._values.get("action_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#target Budget#target}.'''
        result = self._values.get("target")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BudgetAlertConfigurationsActionConfigurations(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BudgetAlertConfigurationsActionConfigurationsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.budget.BudgetAlertConfigurationsActionConfigurationsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c8f50bd7c1d41dd5ba46d10ef665b19652adfdb50edea8409204a1e0c8884685)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "BudgetAlertConfigurationsActionConfigurationsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bb0b8408b3f7895ac99438a8a3a68981b762ccea2f30f3c567a97e1299eb311)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("BudgetAlertConfigurationsActionConfigurationsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da3f97d7a309ec29df8817df4b21a03c6b9d132d1e88b2d8d851d2172fedeacf)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c7a4f7d6cfa04d497078a0f25766dd31b8367b2dc40153a331603d4b6cd835d9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__85565523d5b0eb6eb25f86d9a550ab209c2a93eb664bfc5ddb84550c0ede8b43)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[BudgetAlertConfigurationsActionConfigurations]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[BudgetAlertConfigurationsActionConfigurations]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[BudgetAlertConfigurationsActionConfigurations]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ed4491b1dd8be248cc18fe52660401e094f07a1e9171b4ded5f0f2d156cb0d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class BudgetAlertConfigurationsActionConfigurationsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.budget.BudgetAlertConfigurationsActionConfigurationsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__41391e20476d017a2c6104635cfdf50a5970dcf0e35af94c18ea9f4fe02fbcf3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetActionConfigurationId")
    def reset_action_configuration_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActionConfigurationId", []))

    @jsii.member(jsii_name="resetActionType")
    def reset_action_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActionType", []))

    @jsii.member(jsii_name="resetTarget")
    def reset_target(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTarget", []))

    @builtins.property
    @jsii.member(jsii_name="actionConfigurationIdInput")
    def action_configuration_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionConfigurationIdInput"))

    @builtins.property
    @jsii.member(jsii_name="actionTypeInput")
    def action_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="targetInput")
    def target_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetInput"))

    @builtins.property
    @jsii.member(jsii_name="actionConfigurationId")
    def action_configuration_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "actionConfigurationId"))

    @action_configuration_id.setter
    def action_configuration_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__402b8218a14ad8cd567671e2fcf8bddc0549ba071ae3c2947616610224f92803)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "actionConfigurationId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="actionType")
    def action_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "actionType"))

    @action_type.setter
    def action_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81cca952c93975c2bb5d0019e06288c49a891d2eef3706bbc3e0987e96d68fae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "actionType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="target")
    def target(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "target"))

    @target.setter
    def target(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2cb850ea1d49b88f48b997814c825763e2cb1047a9eea6c7391091dab38d4b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "target", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, BudgetAlertConfigurationsActionConfigurations]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, BudgetAlertConfigurationsActionConfigurations]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, BudgetAlertConfigurationsActionConfigurations]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85d7c2908ea0c5494f204fdd6983da585262d42ee1c75b6900b3f156e0f2bdc3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class BudgetAlertConfigurationsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.budget.BudgetAlertConfigurationsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__599c1b3a9b90c6be62487a045b301445d87a7721c055d9675574d3caf30a1e92)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "BudgetAlertConfigurationsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f34a654076be5663fff10085d4cd7efb659b35d0b8545c4ea9cb1999aa6533ae)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("BudgetAlertConfigurationsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a81bd667cf2516383e76f2fe40a947417aee8ee625a3b730092f7c47c964dd41)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4b772d9ed54fd053c141468b7d2cc5dbd351c7c94987a9a99c6454b9b0025f61)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b2514dab833c3d94c53e42532fc00818952c7cb52253c35db0920b2f916cc3fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[BudgetAlertConfigurations]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[BudgetAlertConfigurations]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[BudgetAlertConfigurations]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebcc8c0c764c2e5802c5c09c20c35f3ddf213c2b0fc3fb6c0f90c5077f5ec9d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class BudgetAlertConfigurationsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.budget.BudgetAlertConfigurationsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e9461feae45bea3d6a822d5ecc5fcb8d387efcc80d19e3cad3799792330cfe46)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putActionConfigurations")
    def put_action_configurations(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[BudgetAlertConfigurationsActionConfigurations, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c64eb25cfe59c78f9b96670a10bdacfb610617cad2265b955646db554f16fb06)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putActionConfigurations", [value]))

    @jsii.member(jsii_name="resetActionConfigurations")
    def reset_action_configurations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActionConfigurations", []))

    @jsii.member(jsii_name="resetAlertConfigurationId")
    def reset_alert_configuration_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlertConfigurationId", []))

    @jsii.member(jsii_name="resetQuantityThreshold")
    def reset_quantity_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQuantityThreshold", []))

    @jsii.member(jsii_name="resetQuantityType")
    def reset_quantity_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQuantityType", []))

    @jsii.member(jsii_name="resetTimePeriod")
    def reset_time_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimePeriod", []))

    @jsii.member(jsii_name="resetTriggerType")
    def reset_trigger_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTriggerType", []))

    @builtins.property
    @jsii.member(jsii_name="actionConfigurations")
    def action_configurations(
        self,
    ) -> BudgetAlertConfigurationsActionConfigurationsList:
        return typing.cast(BudgetAlertConfigurationsActionConfigurationsList, jsii.get(self, "actionConfigurations"))

    @builtins.property
    @jsii.member(jsii_name="actionConfigurationsInput")
    def action_configurations_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[BudgetAlertConfigurationsActionConfigurations]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[BudgetAlertConfigurationsActionConfigurations]]], jsii.get(self, "actionConfigurationsInput"))

    @builtins.property
    @jsii.member(jsii_name="alertConfigurationIdInput")
    def alert_configuration_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alertConfigurationIdInput"))

    @builtins.property
    @jsii.member(jsii_name="quantityThresholdInput")
    def quantity_threshold_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "quantityThresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="quantityTypeInput")
    def quantity_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "quantityTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="timePeriodInput")
    def time_period_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timePeriodInput"))

    @builtins.property
    @jsii.member(jsii_name="triggerTypeInput")
    def trigger_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "triggerTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="alertConfigurationId")
    def alert_configuration_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alertConfigurationId"))

    @alert_configuration_id.setter
    def alert_configuration_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b32ab1115fe3832d836feb6ccfab3169a927fda231b78ed9c6ad4b016b0cc957)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alertConfigurationId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="quantityThreshold")
    def quantity_threshold(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "quantityThreshold"))

    @quantity_threshold.setter
    def quantity_threshold(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe3fd676082be8a5686a6a0008fcff11a68d5da38820bc1343527a72daeca483)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "quantityThreshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="quantityType")
    def quantity_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "quantityType"))

    @quantity_type.setter
    def quantity_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8528f7cab1db31fdd588757af0ea8554cd27667d03fd46c3aa759aa90f002033)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "quantityType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timePeriod")
    def time_period(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timePeriod"))

    @time_period.setter
    def time_period(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce5521b859d0382627612f17c12b88593ca14127eabb1dc1e96fd329e85c1275)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timePeriod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="triggerType")
    def trigger_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "triggerType"))

    @trigger_type.setter
    def trigger_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d7f13cde782b8724071142cf942935fbe399c4654b619ac46a646ed515cf6fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "triggerType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, BudgetAlertConfigurations]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, BudgetAlertConfigurations]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, BudgetAlertConfigurations]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ec3d4e3ecf4b2610cdd1a0f26eba2d60301d9a7dff0f6efe82e86d3ac896b34)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.budget.BudgetConfig",
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
        "alert_configurations": "alertConfigurations",
        "budget_configuration_id": "budgetConfigurationId",
        "create_time": "createTime",
        "display_name": "displayName",
        "filter": "filter",
        "id": "id",
        "update_time": "updateTime",
    },
)
class BudgetConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        account_id: typing.Optional[builtins.str] = None,
        alert_configurations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[BudgetAlertConfigurations, typing.Dict[builtins.str, typing.Any]]]]] = None,
        budget_configuration_id: typing.Optional[builtins.str] = None,
        create_time: typing.Optional[jsii.Number] = None,
        display_name: typing.Optional[builtins.str] = None,
        filter: typing.Optional[typing.Union["BudgetFilter", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        update_time: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#account_id Budget#account_id}.
        :param alert_configurations: alert_configurations block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#alert_configurations Budget#alert_configurations}
        :param budget_configuration_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#budget_configuration_id Budget#budget_configuration_id}.
        :param create_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#create_time Budget#create_time}.
        :param display_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#display_name Budget#display_name}.
        :param filter: filter block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#filter Budget#filter}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#id Budget#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param update_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#update_time Budget#update_time}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(filter, dict):
            filter = BudgetFilter(**filter)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a275019e19d523434d897e9d468809a65acc05a46dc089a713f89097fb74f3b)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument alert_configurations", value=alert_configurations, expected_type=type_hints["alert_configurations"])
            check_type(argname="argument budget_configuration_id", value=budget_configuration_id, expected_type=type_hints["budget_configuration_id"])
            check_type(argname="argument create_time", value=create_time, expected_type=type_hints["create_time"])
            check_type(argname="argument display_name", value=display_name, expected_type=type_hints["display_name"])
            check_type(argname="argument filter", value=filter, expected_type=type_hints["filter"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument update_time", value=update_time, expected_type=type_hints["update_time"])
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
        if account_id is not None:
            self._values["account_id"] = account_id
        if alert_configurations is not None:
            self._values["alert_configurations"] = alert_configurations
        if budget_configuration_id is not None:
            self._values["budget_configuration_id"] = budget_configuration_id
        if create_time is not None:
            self._values["create_time"] = create_time
        if display_name is not None:
            self._values["display_name"] = display_name
        if filter is not None:
            self._values["filter"] = filter
        if id is not None:
            self._values["id"] = id
        if update_time is not None:
            self._values["update_time"] = update_time

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
    def account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#account_id Budget#account_id}.'''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def alert_configurations(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[BudgetAlertConfigurations]]]:
        '''alert_configurations block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#alert_configurations Budget#alert_configurations}
        '''
        result = self._values.get("alert_configurations")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[BudgetAlertConfigurations]]], result)

    @builtins.property
    def budget_configuration_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#budget_configuration_id Budget#budget_configuration_id}.'''
        result = self._values.get("budget_configuration_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def create_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#create_time Budget#create_time}.'''
        result = self._values.get("create_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def display_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#display_name Budget#display_name}.'''
        result = self._values.get("display_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def filter(self) -> typing.Optional["BudgetFilter"]:
        '''filter block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#filter Budget#filter}
        '''
        result = self._values.get("filter")
        return typing.cast(typing.Optional["BudgetFilter"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#id Budget#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#update_time Budget#update_time}.'''
        result = self._values.get("update_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BudgetConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.budget.BudgetFilter",
    jsii_struct_bases=[],
    name_mapping={"tags": "tags", "workspace_id": "workspaceId"},
)
class BudgetFilter:
    def __init__(
        self,
        *,
        tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["BudgetFilterTags", typing.Dict[builtins.str, typing.Any]]]]] = None,
        workspace_id: typing.Optional[typing.Union["BudgetFilterWorkspaceId", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param tags: tags block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#tags Budget#tags}
        :param workspace_id: workspace_id block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#workspace_id Budget#workspace_id}
        '''
        if isinstance(workspace_id, dict):
            workspace_id = BudgetFilterWorkspaceId(**workspace_id)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4f8eeb2f6c87573dd5ce59ebe411492aec7a2a440c34c3e818b10010cc738da)
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument workspace_id", value=workspace_id, expected_type=type_hints["workspace_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if tags is not None:
            self._values["tags"] = tags
        if workspace_id is not None:
            self._values["workspace_id"] = workspace_id

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["BudgetFilterTags"]]]:
        '''tags block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#tags Budget#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["BudgetFilterTags"]]], result)

    @builtins.property
    def workspace_id(self) -> typing.Optional["BudgetFilterWorkspaceId"]:
        '''workspace_id block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#workspace_id Budget#workspace_id}
        '''
        result = self._values.get("workspace_id")
        return typing.cast(typing.Optional["BudgetFilterWorkspaceId"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BudgetFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BudgetFilterOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.budget.BudgetFilterOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__86f1b4b8a87882950939a1015d1761c5bfb25fe93b005944da5745787855b518)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putTags")
    def put_tags(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["BudgetFilterTags", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5aaebea257bae88504f4b30bd11cfb42feb54a8afb137eed73f5cd39a69397aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTags", [value]))

    @jsii.member(jsii_name="putWorkspaceId")
    def put_workspace_id(
        self,
        *,
        operator: typing.Optional[builtins.str] = None,
        values: typing.Optional[typing.Sequence[jsii.Number]] = None,
    ) -> None:
        '''
        :param operator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#operator Budget#operator}.
        :param values: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#values Budget#values}.
        '''
        value = BudgetFilterWorkspaceId(operator=operator, values=values)

        return typing.cast(None, jsii.invoke(self, "putWorkspaceId", [value]))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetWorkspaceId")
    def reset_workspace_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkspaceId", []))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> "BudgetFilterTagsList":
        return typing.cast("BudgetFilterTagsList", jsii.get(self, "tags"))

    @builtins.property
    @jsii.member(jsii_name="workspaceId")
    def workspace_id(self) -> "BudgetFilterWorkspaceIdOutputReference":
        return typing.cast("BudgetFilterWorkspaceIdOutputReference", jsii.get(self, "workspaceId"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["BudgetFilterTags"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["BudgetFilterTags"]]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="workspaceIdInput")
    def workspace_id_input(self) -> typing.Optional["BudgetFilterWorkspaceId"]:
        return typing.cast(typing.Optional["BudgetFilterWorkspaceId"], jsii.get(self, "workspaceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[BudgetFilter]:
        return typing.cast(typing.Optional[BudgetFilter], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[BudgetFilter]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d925554e404786ebadd17e56f5950edfb9b694888ea7301fa89b4af86b9eb861)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.budget.BudgetFilterTags",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class BudgetFilterTags:
    def __init__(
        self,
        *,
        key: typing.Optional[builtins.str] = None,
        value: typing.Optional[typing.Union["BudgetFilterTagsValue", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#key Budget#key}.
        :param value: value block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#value Budget#value}
        '''
        if isinstance(value, dict):
            value = BudgetFilterTagsValue(**value)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1f9f45a38192bce6e0071a974ad2c3a3c6ae63c2e0942b70a9e93328b458908)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if key is not None:
            self._values["key"] = key
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#key Budget#key}.'''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional["BudgetFilterTagsValue"]:
        '''value block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#value Budget#value}
        '''
        result = self._values.get("value")
        return typing.cast(typing.Optional["BudgetFilterTagsValue"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BudgetFilterTags(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BudgetFilterTagsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.budget.BudgetFilterTagsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2022b713e3aabe9dd3926f874cf8585d028f65fbc93cea8d03475bfa14d413e2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "BudgetFilterTagsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c12d23cf5b8a11fbb06a367ad4fd69b7bca48f3f833f5078a4ba999d4281711)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("BudgetFilterTagsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__600e7a66269099cb1b0b6c3b94ac42021f5b858f76929bf8dd24213d507f3d2d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__196a801ab0d39bc377c8e95ddeed98c00334a6bf0425c6a4b34f16db2a30bb06)
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
            type_hints = typing.get_type_hints(_typecheckingstub__22b0275252d56b05852f47829078990ebb01a6f8d332b62a9fdcff1ee21c27af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[BudgetFilterTags]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[BudgetFilterTags]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[BudgetFilterTags]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2100b9a072fe5bb162e85919efd2610b426ead03d5a95b293da8c4e8a49bc43)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class BudgetFilterTagsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.budget.BudgetFilterTagsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__abd2bbde04c84265bcc5666260ea8a2124a77ad372616f6ae0daad2e78da9392)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putValue")
    def put_value(
        self,
        *,
        operator: typing.Optional[builtins.str] = None,
        values: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param operator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#operator Budget#operator}.
        :param values: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#values Budget#values}.
        '''
        value = BudgetFilterTagsValue(operator=operator, values=values)

        return typing.cast(None, jsii.invoke(self, "putValue", [value]))

    @jsii.member(jsii_name="resetKey")
    def reset_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKey", []))

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> "BudgetFilterTagsValueOutputReference":
        return typing.cast("BudgetFilterTagsValueOutputReference", jsii.get(self, "value"))

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional["BudgetFilterTagsValue"]:
        return typing.cast(typing.Optional["BudgetFilterTagsValue"], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34e90b1d9c422a7037785c7cb769dbf299c299b94249da130f6fbeed56122a18)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, BudgetFilterTags]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, BudgetFilterTags]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, BudgetFilterTags]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed9edd82eecb5e68eedf83b5d35934d8e0bc7a773ca51bba666e78c1c7c17d94)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.budget.BudgetFilterTagsValue",
    jsii_struct_bases=[],
    name_mapping={"operator": "operator", "values": "values"},
)
class BudgetFilterTagsValue:
    def __init__(
        self,
        *,
        operator: typing.Optional[builtins.str] = None,
        values: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param operator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#operator Budget#operator}.
        :param values: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#values Budget#values}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46c2b9dfe7b04a7ab72a122bc6bb0154e8313231200206372c45293df090d336)
            check_type(argname="argument operator", value=operator, expected_type=type_hints["operator"])
            check_type(argname="argument values", value=values, expected_type=type_hints["values"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if operator is not None:
            self._values["operator"] = operator
        if values is not None:
            self._values["values"] = values

    @builtins.property
    def operator(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#operator Budget#operator}.'''
        result = self._values.get("operator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def values(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#values Budget#values}.'''
        result = self._values.get("values")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BudgetFilterTagsValue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BudgetFilterTagsValueOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.budget.BudgetFilterTagsValueOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__811e87a6166b9176cdba9192b5a57e37a18f6d7cb6be6626997460de998a275c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetOperator")
    def reset_operator(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperator", []))

    @jsii.member(jsii_name="resetValues")
    def reset_values(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValues", []))

    @builtins.property
    @jsii.member(jsii_name="operatorInput")
    def operator_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "operatorInput"))

    @builtins.property
    @jsii.member(jsii_name="valuesInput")
    def values_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "valuesInput"))

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__109b9c20f7aa6bfb0b0453b2c6bbe9b8e72ff0284d14346eda5f0e7e3b48e9a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="values")
    def values(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "values"))

    @values.setter
    def values(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac4e5174973935741f31fc901a627a5ba09ca8c125d80c19c6ba00eb5617e6cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "values", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[BudgetFilterTagsValue]:
        return typing.cast(typing.Optional[BudgetFilterTagsValue], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[BudgetFilterTagsValue]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a676fc22987d800efadcbe28ca27435718db4c14de8da47e660e51a248afbca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.budget.BudgetFilterWorkspaceId",
    jsii_struct_bases=[],
    name_mapping={"operator": "operator", "values": "values"},
)
class BudgetFilterWorkspaceId:
    def __init__(
        self,
        *,
        operator: typing.Optional[builtins.str] = None,
        values: typing.Optional[typing.Sequence[jsii.Number]] = None,
    ) -> None:
        '''
        :param operator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#operator Budget#operator}.
        :param values: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#values Budget#values}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f772beb5e14a301e626f1bdb860958d13837c535a6dc684a5f0f4f6c7b74a42)
            check_type(argname="argument operator", value=operator, expected_type=type_hints["operator"])
            check_type(argname="argument values", value=values, expected_type=type_hints["values"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if operator is not None:
            self._values["operator"] = operator
        if values is not None:
            self._values["values"] = values

    @builtins.property
    def operator(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#operator Budget#operator}.'''
        result = self._values.get("operator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def values(self) -> typing.Optional[typing.List[jsii.Number]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/budget#values Budget#values}.'''
        result = self._values.get("values")
        return typing.cast(typing.Optional[typing.List[jsii.Number]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BudgetFilterWorkspaceId(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BudgetFilterWorkspaceIdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.budget.BudgetFilterWorkspaceIdOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a8434d8499731ec8c0fbfc3030553a295b79a8ff8bf2564da382a12003b31b27)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetOperator")
    def reset_operator(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperator", []))

    @jsii.member(jsii_name="resetValues")
    def reset_values(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValues", []))

    @builtins.property
    @jsii.member(jsii_name="operatorInput")
    def operator_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "operatorInput"))

    @builtins.property
    @jsii.member(jsii_name="valuesInput")
    def values_input(self) -> typing.Optional[typing.List[jsii.Number]]:
        return typing.cast(typing.Optional[typing.List[jsii.Number]], jsii.get(self, "valuesInput"))

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7915152eb2da8a776daccb32e319910e0e6275708264ac5875617c5254f69c8e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="values")
    def values(self) -> typing.List[jsii.Number]:
        return typing.cast(typing.List[jsii.Number], jsii.get(self, "values"))

    @values.setter
    def values(self, value: typing.List[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e0297ef706cda8ff72472c82aabd628768b73bd1b0c05854a5c90e44898dc4b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "values", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[BudgetFilterWorkspaceId]:
        return typing.cast(typing.Optional[BudgetFilterWorkspaceId], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[BudgetFilterWorkspaceId]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83444295555afe074ee54bbb8cffc074a2a0d6b23d5cce7b698804248727d2eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "Budget",
    "BudgetAlertConfigurations",
    "BudgetAlertConfigurationsActionConfigurations",
    "BudgetAlertConfigurationsActionConfigurationsList",
    "BudgetAlertConfigurationsActionConfigurationsOutputReference",
    "BudgetAlertConfigurationsList",
    "BudgetAlertConfigurationsOutputReference",
    "BudgetConfig",
    "BudgetFilter",
    "BudgetFilterOutputReference",
    "BudgetFilterTags",
    "BudgetFilterTagsList",
    "BudgetFilterTagsOutputReference",
    "BudgetFilterTagsValue",
    "BudgetFilterTagsValueOutputReference",
    "BudgetFilterWorkspaceId",
    "BudgetFilterWorkspaceIdOutputReference",
]

publication.publish()

def _typecheckingstub__174326d81483b00a42ac61c92f23e171206eb13f1744863d3a44385969db8459(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    account_id: typing.Optional[builtins.str] = None,
    alert_configurations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[BudgetAlertConfigurations, typing.Dict[builtins.str, typing.Any]]]]] = None,
    budget_configuration_id: typing.Optional[builtins.str] = None,
    create_time: typing.Optional[jsii.Number] = None,
    display_name: typing.Optional[builtins.str] = None,
    filter: typing.Optional[typing.Union[BudgetFilter, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    update_time: typing.Optional[jsii.Number] = None,
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

def _typecheckingstub__0f42104772a3adaab199aa31d0c269b3ebaec31cd974fa3f07f7ecccb922e88f(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56c8cb8c957a136ab0aba5d3848affdfcadcd2480d149d64ea582430940bdac1(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[BudgetAlertConfigurations, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e500d6e3fa20261d3cc96aed2d8ce3a6dc260a1fd05d7ad3f295db76fc88faa8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6418d632e4cf1405ad8f65ca5a9a3faff9dc3729f839b56ab592ee872b1998a8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__068261561cda897932cc08d856062ac058c294e591acd8ec9d5113028d2f669c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8bf587af3ff268b2f3c7df1c9afc612d9f84de48b401ac5be4087c5ec8085df7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__446097c4d9e9496c9cc921989d922ddd43499a08478af7b2634411695ef03360(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0dc0dd67d124eb9329c4e8e9233840ddfbb23b6fd6da1baba96004f142166fe(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__965ae6856c7198c887f33b8148c80b7d48784c33d6143f682dd422cbeb707a26(
    *,
    action_configurations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[BudgetAlertConfigurationsActionConfigurations, typing.Dict[builtins.str, typing.Any]]]]] = None,
    alert_configuration_id: typing.Optional[builtins.str] = None,
    quantity_threshold: typing.Optional[builtins.str] = None,
    quantity_type: typing.Optional[builtins.str] = None,
    time_period: typing.Optional[builtins.str] = None,
    trigger_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f66fe903368694c3b0efaeba494eeb190f81a91e2c2487b8a02edf8fb7651dc1(
    *,
    action_configuration_id: typing.Optional[builtins.str] = None,
    action_type: typing.Optional[builtins.str] = None,
    target: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8f50bd7c1d41dd5ba46d10ef665b19652adfdb50edea8409204a1e0c8884685(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bb0b8408b3f7895ac99438a8a3a68981b762ccea2f30f3c567a97e1299eb311(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da3f97d7a309ec29df8817df4b21a03c6b9d132d1e88b2d8d851d2172fedeacf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7a4f7d6cfa04d497078a0f25766dd31b8367b2dc40153a331603d4b6cd835d9(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85565523d5b0eb6eb25f86d9a550ab209c2a93eb664bfc5ddb84550c0ede8b43(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ed4491b1dd8be248cc18fe52660401e094f07a1e9171b4ded5f0f2d156cb0d4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[BudgetAlertConfigurationsActionConfigurations]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41391e20476d017a2c6104635cfdf50a5970dcf0e35af94c18ea9f4fe02fbcf3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__402b8218a14ad8cd567671e2fcf8bddc0549ba071ae3c2947616610224f92803(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81cca952c93975c2bb5d0019e06288c49a891d2eef3706bbc3e0987e96d68fae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2cb850ea1d49b88f48b997814c825763e2cb1047a9eea6c7391091dab38d4b9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85d7c2908ea0c5494f204fdd6983da585262d42ee1c75b6900b3f156e0f2bdc3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, BudgetAlertConfigurationsActionConfigurations]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__599c1b3a9b90c6be62487a045b301445d87a7721c055d9675574d3caf30a1e92(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f34a654076be5663fff10085d4cd7efb659b35d0b8545c4ea9cb1999aa6533ae(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a81bd667cf2516383e76f2fe40a947417aee8ee625a3b730092f7c47c964dd41(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b772d9ed54fd053c141468b7d2cc5dbd351c7c94987a9a99c6454b9b0025f61(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2514dab833c3d94c53e42532fc00818952c7cb52253c35db0920b2f916cc3fb(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebcc8c0c764c2e5802c5c09c20c35f3ddf213c2b0fc3fb6c0f90c5077f5ec9d9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[BudgetAlertConfigurations]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9461feae45bea3d6a822d5ecc5fcb8d387efcc80d19e3cad3799792330cfe46(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c64eb25cfe59c78f9b96670a10bdacfb610617cad2265b955646db554f16fb06(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[BudgetAlertConfigurationsActionConfigurations, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b32ab1115fe3832d836feb6ccfab3169a927fda231b78ed9c6ad4b016b0cc957(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe3fd676082be8a5686a6a0008fcff11a68d5da38820bc1343527a72daeca483(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8528f7cab1db31fdd588757af0ea8554cd27667d03fd46c3aa759aa90f002033(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce5521b859d0382627612f17c12b88593ca14127eabb1dc1e96fd329e85c1275(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d7f13cde782b8724071142cf942935fbe399c4654b619ac46a646ed515cf6fd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ec3d4e3ecf4b2610cdd1a0f26eba2d60301d9a7dff0f6efe82e86d3ac896b34(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, BudgetAlertConfigurations]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a275019e19d523434d897e9d468809a65acc05a46dc089a713f89097fb74f3b(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: typing.Optional[builtins.str] = None,
    alert_configurations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[BudgetAlertConfigurations, typing.Dict[builtins.str, typing.Any]]]]] = None,
    budget_configuration_id: typing.Optional[builtins.str] = None,
    create_time: typing.Optional[jsii.Number] = None,
    display_name: typing.Optional[builtins.str] = None,
    filter: typing.Optional[typing.Union[BudgetFilter, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    update_time: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4f8eeb2f6c87573dd5ce59ebe411492aec7a2a440c34c3e818b10010cc738da(
    *,
    tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[BudgetFilterTags, typing.Dict[builtins.str, typing.Any]]]]] = None,
    workspace_id: typing.Optional[typing.Union[BudgetFilterWorkspaceId, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86f1b4b8a87882950939a1015d1761c5bfb25fe93b005944da5745787855b518(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5aaebea257bae88504f4b30bd11cfb42feb54a8afb137eed73f5cd39a69397aa(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[BudgetFilterTags, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d925554e404786ebadd17e56f5950edfb9b694888ea7301fa89b4af86b9eb861(
    value: typing.Optional[BudgetFilter],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1f9f45a38192bce6e0071a974ad2c3a3c6ae63c2e0942b70a9e93328b458908(
    *,
    key: typing.Optional[builtins.str] = None,
    value: typing.Optional[typing.Union[BudgetFilterTagsValue, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2022b713e3aabe9dd3926f874cf8585d028f65fbc93cea8d03475bfa14d413e2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c12d23cf5b8a11fbb06a367ad4fd69b7bca48f3f833f5078a4ba999d4281711(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__600e7a66269099cb1b0b6c3b94ac42021f5b858f76929bf8dd24213d507f3d2d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__196a801ab0d39bc377c8e95ddeed98c00334a6bf0425c6a4b34f16db2a30bb06(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22b0275252d56b05852f47829078990ebb01a6f8d332b62a9fdcff1ee21c27af(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2100b9a072fe5bb162e85919efd2610b426ead03d5a95b293da8c4e8a49bc43(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[BudgetFilterTags]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abd2bbde04c84265bcc5666260ea8a2124a77ad372616f6ae0daad2e78da9392(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34e90b1d9c422a7037785c7cb769dbf299c299b94249da130f6fbeed56122a18(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed9edd82eecb5e68eedf83b5d35934d8e0bc7a773ca51bba666e78c1c7c17d94(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, BudgetFilterTags]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46c2b9dfe7b04a7ab72a122bc6bb0154e8313231200206372c45293df090d336(
    *,
    operator: typing.Optional[builtins.str] = None,
    values: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__811e87a6166b9176cdba9192b5a57e37a18f6d7cb6be6626997460de998a275c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__109b9c20f7aa6bfb0b0453b2c6bbe9b8e72ff0284d14346eda5f0e7e3b48e9a1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac4e5174973935741f31fc901a627a5ba09ca8c125d80c19c6ba00eb5617e6cd(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a676fc22987d800efadcbe28ca27435718db4c14de8da47e660e51a248afbca(
    value: typing.Optional[BudgetFilterTagsValue],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f772beb5e14a301e626f1bdb860958d13837c535a6dc684a5f0f4f6c7b74a42(
    *,
    operator: typing.Optional[builtins.str] = None,
    values: typing.Optional[typing.Sequence[jsii.Number]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8434d8499731ec8c0fbfc3030553a295b79a8ff8bf2564da382a12003b31b27(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7915152eb2da8a776daccb32e319910e0e6275708264ac5875617c5254f69c8e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e0297ef706cda8ff72472c82aabd628768b73bd1b0c05854a5c90e44898dc4b(
    value: typing.List[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83444295555afe074ee54bbb8cffc074a2a0d6b23d5cce7b698804248727d2eb(
    value: typing.Optional[BudgetFilterWorkspaceId],
) -> None:
    """Type checking stubs"""
    pass
