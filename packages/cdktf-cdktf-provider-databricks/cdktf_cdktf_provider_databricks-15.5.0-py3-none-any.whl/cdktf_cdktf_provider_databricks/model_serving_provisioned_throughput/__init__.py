r'''
# `databricks_model_serving_provisioned_throughput`

Refer to the Terraform Registry for docs: [`databricks_model_serving_provisioned_throughput`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput).
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


class ModelServingProvisionedThroughput(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughput",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput databricks_model_serving_provisioned_throughput}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        config: typing.Union["ModelServingProvisionedThroughputConfigA", typing.Dict[builtins.str, typing.Any]],
        name: builtins.str,
        ai_gateway: typing.Optional[typing.Union["ModelServingProvisionedThroughputAiGateway", typing.Dict[builtins.str, typing.Any]]] = None,
        budget_policy_id: typing.Optional[builtins.str] = None,
        email_notifications: typing.Optional[typing.Union["ModelServingProvisionedThroughputEmailNotifications", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingProvisionedThroughputTags", typing.Dict[builtins.str, typing.Any]]]]] = None,
        timeouts: typing.Optional[typing.Union["ModelServingProvisionedThroughputTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput databricks_model_serving_provisioned_throughput} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param config: config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#config ModelServingProvisionedThroughput#config}
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#name ModelServingProvisionedThroughput#name}.
        :param ai_gateway: ai_gateway block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#ai_gateway ModelServingProvisionedThroughput#ai_gateway}
        :param budget_policy_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#budget_policy_id ModelServingProvisionedThroughput#budget_policy_id}.
        :param email_notifications: email_notifications block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#email_notifications ModelServingProvisionedThroughput#email_notifications}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#id ModelServingProvisionedThroughput#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: tags block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#tags ModelServingProvisionedThroughput#tags}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#timeouts ModelServingProvisionedThroughput#timeouts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__112dca9c8a5ee404308b6da0984bdb5bf6259bbdc06c5dd75c2c280a18d1bcfa)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config_ = ModelServingProvisionedThroughputConfig(
            config=config,
            name=name,
            ai_gateway=ai_gateway,
            budget_policy_id=budget_policy_id,
            email_notifications=email_notifications,
            id=id,
            tags=tags,
            timeouts=timeouts,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config_])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a ModelServingProvisionedThroughput resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ModelServingProvisionedThroughput to import.
        :param import_from_id: The id of the existing ModelServingProvisionedThroughput that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ModelServingProvisionedThroughput to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3783c812dc1e71498e65b7c7100777920a7373c92de1095dd3ce449412b82bf4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAiGateway")
    def put_ai_gateway(
        self,
        *,
        fallback_config: typing.Optional[typing.Union["ModelServingProvisionedThroughputAiGatewayFallbackConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        guardrails: typing.Optional[typing.Union["ModelServingProvisionedThroughputAiGatewayGuardrails", typing.Dict[builtins.str, typing.Any]]] = None,
        inference_table_config: typing.Optional[typing.Union["ModelServingProvisionedThroughputAiGatewayInferenceTableConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        rate_limits: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingProvisionedThroughputAiGatewayRateLimits", typing.Dict[builtins.str, typing.Any]]]]] = None,
        usage_tracking_config: typing.Optional[typing.Union["ModelServingProvisionedThroughputAiGatewayUsageTrackingConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param fallback_config: fallback_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#fallback_config ModelServingProvisionedThroughput#fallback_config}
        :param guardrails: guardrails block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#guardrails ModelServingProvisionedThroughput#guardrails}
        :param inference_table_config: inference_table_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#inference_table_config ModelServingProvisionedThroughput#inference_table_config}
        :param rate_limits: rate_limits block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#rate_limits ModelServingProvisionedThroughput#rate_limits}
        :param usage_tracking_config: usage_tracking_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#usage_tracking_config ModelServingProvisionedThroughput#usage_tracking_config}
        '''
        value = ModelServingProvisionedThroughputAiGateway(
            fallback_config=fallback_config,
            guardrails=guardrails,
            inference_table_config=inference_table_config,
            rate_limits=rate_limits,
            usage_tracking_config=usage_tracking_config,
        )

        return typing.cast(None, jsii.invoke(self, "putAiGateway", [value]))

    @jsii.member(jsii_name="putConfig")
    def put_config(
        self,
        *,
        served_entities: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingProvisionedThroughputConfigServedEntities", typing.Dict[builtins.str, typing.Any]]]]] = None,
        traffic_config: typing.Optional[typing.Union["ModelServingProvisionedThroughputConfigTrafficConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param served_entities: served_entities block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#served_entities ModelServingProvisionedThroughput#served_entities}
        :param traffic_config: traffic_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#traffic_config ModelServingProvisionedThroughput#traffic_config}
        '''
        value = ModelServingProvisionedThroughputConfigA(
            served_entities=served_entities, traffic_config=traffic_config
        )

        return typing.cast(None, jsii.invoke(self, "putConfig", [value]))

    @jsii.member(jsii_name="putEmailNotifications")
    def put_email_notifications(
        self,
        *,
        on_update_failure: typing.Optional[typing.Sequence[builtins.str]] = None,
        on_update_success: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param on_update_failure: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#on_update_failure ModelServingProvisionedThroughput#on_update_failure}.
        :param on_update_success: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#on_update_success ModelServingProvisionedThroughput#on_update_success}.
        '''
        value = ModelServingProvisionedThroughputEmailNotifications(
            on_update_failure=on_update_failure, on_update_success=on_update_success
        )

        return typing.cast(None, jsii.invoke(self, "putEmailNotifications", [value]))

    @jsii.member(jsii_name="putTags")
    def put_tags(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingProvisionedThroughputTags", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22b78850ab944ac8770090026265326bc0ab3a02a842bb2771dd07aef049c21b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTags", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#create ModelServingProvisionedThroughput#create}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#update ModelServingProvisionedThroughput#update}.
        '''
        value = ModelServingProvisionedThroughputTimeouts(create=create, update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetAiGateway")
    def reset_ai_gateway(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAiGateway", []))

    @jsii.member(jsii_name="resetBudgetPolicyId")
    def reset_budget_policy_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBudgetPolicyId", []))

    @jsii.member(jsii_name="resetEmailNotifications")
    def reset_email_notifications(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailNotifications", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

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
    @jsii.member(jsii_name="aiGateway")
    def ai_gateway(self) -> "ModelServingProvisionedThroughputAiGatewayOutputReference":
        return typing.cast("ModelServingProvisionedThroughputAiGatewayOutputReference", jsii.get(self, "aiGateway"))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> "ModelServingProvisionedThroughputConfigAOutputReference":
        return typing.cast("ModelServingProvisionedThroughputConfigAOutputReference", jsii.get(self, "config"))

    @builtins.property
    @jsii.member(jsii_name="emailNotifications")
    def email_notifications(
        self,
    ) -> "ModelServingProvisionedThroughputEmailNotificationsOutputReference":
        return typing.cast("ModelServingProvisionedThroughputEmailNotificationsOutputReference", jsii.get(self, "emailNotifications"))

    @builtins.property
    @jsii.member(jsii_name="servingEndpointId")
    def serving_endpoint_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "servingEndpointId"))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> "ModelServingProvisionedThroughputTagsList":
        return typing.cast("ModelServingProvisionedThroughputTagsList", jsii.get(self, "tags"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "ModelServingProvisionedThroughputTimeoutsOutputReference":
        return typing.cast("ModelServingProvisionedThroughputTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="aiGatewayInput")
    def ai_gateway_input(
        self,
    ) -> typing.Optional["ModelServingProvisionedThroughputAiGateway"]:
        return typing.cast(typing.Optional["ModelServingProvisionedThroughputAiGateway"], jsii.get(self, "aiGatewayInput"))

    @builtins.property
    @jsii.member(jsii_name="budgetPolicyIdInput")
    def budget_policy_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "budgetPolicyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="configInput")
    def config_input(
        self,
    ) -> typing.Optional["ModelServingProvisionedThroughputConfigA"]:
        return typing.cast(typing.Optional["ModelServingProvisionedThroughputConfigA"], jsii.get(self, "configInput"))

    @builtins.property
    @jsii.member(jsii_name="emailNotificationsInput")
    def email_notifications_input(
        self,
    ) -> typing.Optional["ModelServingProvisionedThroughputEmailNotifications"]:
        return typing.cast(typing.Optional["ModelServingProvisionedThroughputEmailNotifications"], jsii.get(self, "emailNotificationsInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingProvisionedThroughputTags"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingProvisionedThroughputTags"]]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ModelServingProvisionedThroughputTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ModelServingProvisionedThroughputTimeouts"]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="budgetPolicyId")
    def budget_policy_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "budgetPolicyId"))

    @budget_policy_id.setter
    def budget_policy_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef1d8dc57f16f03551e82268b5b506188e96055739eee77f32ad61ee3dd7cf86)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "budgetPolicyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e247134aad1103266f297c9eba06b8f9b1bb63cf81f77153bf7a580c1ae552a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8a0faf611a704639d749c142bd3f79c3f64157e33fb86d5b495a2d9e798d2a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputAiGateway",
    jsii_struct_bases=[],
    name_mapping={
        "fallback_config": "fallbackConfig",
        "guardrails": "guardrails",
        "inference_table_config": "inferenceTableConfig",
        "rate_limits": "rateLimits",
        "usage_tracking_config": "usageTrackingConfig",
    },
)
class ModelServingProvisionedThroughputAiGateway:
    def __init__(
        self,
        *,
        fallback_config: typing.Optional[typing.Union["ModelServingProvisionedThroughputAiGatewayFallbackConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        guardrails: typing.Optional[typing.Union["ModelServingProvisionedThroughputAiGatewayGuardrails", typing.Dict[builtins.str, typing.Any]]] = None,
        inference_table_config: typing.Optional[typing.Union["ModelServingProvisionedThroughputAiGatewayInferenceTableConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        rate_limits: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingProvisionedThroughputAiGatewayRateLimits", typing.Dict[builtins.str, typing.Any]]]]] = None,
        usage_tracking_config: typing.Optional[typing.Union["ModelServingProvisionedThroughputAiGatewayUsageTrackingConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param fallback_config: fallback_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#fallback_config ModelServingProvisionedThroughput#fallback_config}
        :param guardrails: guardrails block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#guardrails ModelServingProvisionedThroughput#guardrails}
        :param inference_table_config: inference_table_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#inference_table_config ModelServingProvisionedThroughput#inference_table_config}
        :param rate_limits: rate_limits block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#rate_limits ModelServingProvisionedThroughput#rate_limits}
        :param usage_tracking_config: usage_tracking_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#usage_tracking_config ModelServingProvisionedThroughput#usage_tracking_config}
        '''
        if isinstance(fallback_config, dict):
            fallback_config = ModelServingProvisionedThroughputAiGatewayFallbackConfig(**fallback_config)
        if isinstance(guardrails, dict):
            guardrails = ModelServingProvisionedThroughputAiGatewayGuardrails(**guardrails)
        if isinstance(inference_table_config, dict):
            inference_table_config = ModelServingProvisionedThroughputAiGatewayInferenceTableConfig(**inference_table_config)
        if isinstance(usage_tracking_config, dict):
            usage_tracking_config = ModelServingProvisionedThroughputAiGatewayUsageTrackingConfig(**usage_tracking_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3472bc1584d927826567d82772b591c10c727a87612bfc8f13835de910c332c8)
            check_type(argname="argument fallback_config", value=fallback_config, expected_type=type_hints["fallback_config"])
            check_type(argname="argument guardrails", value=guardrails, expected_type=type_hints["guardrails"])
            check_type(argname="argument inference_table_config", value=inference_table_config, expected_type=type_hints["inference_table_config"])
            check_type(argname="argument rate_limits", value=rate_limits, expected_type=type_hints["rate_limits"])
            check_type(argname="argument usage_tracking_config", value=usage_tracking_config, expected_type=type_hints["usage_tracking_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if fallback_config is not None:
            self._values["fallback_config"] = fallback_config
        if guardrails is not None:
            self._values["guardrails"] = guardrails
        if inference_table_config is not None:
            self._values["inference_table_config"] = inference_table_config
        if rate_limits is not None:
            self._values["rate_limits"] = rate_limits
        if usage_tracking_config is not None:
            self._values["usage_tracking_config"] = usage_tracking_config

    @builtins.property
    def fallback_config(
        self,
    ) -> typing.Optional["ModelServingProvisionedThroughputAiGatewayFallbackConfig"]:
        '''fallback_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#fallback_config ModelServingProvisionedThroughput#fallback_config}
        '''
        result = self._values.get("fallback_config")
        return typing.cast(typing.Optional["ModelServingProvisionedThroughputAiGatewayFallbackConfig"], result)

    @builtins.property
    def guardrails(
        self,
    ) -> typing.Optional["ModelServingProvisionedThroughputAiGatewayGuardrails"]:
        '''guardrails block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#guardrails ModelServingProvisionedThroughput#guardrails}
        '''
        result = self._values.get("guardrails")
        return typing.cast(typing.Optional["ModelServingProvisionedThroughputAiGatewayGuardrails"], result)

    @builtins.property
    def inference_table_config(
        self,
    ) -> typing.Optional["ModelServingProvisionedThroughputAiGatewayInferenceTableConfig"]:
        '''inference_table_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#inference_table_config ModelServingProvisionedThroughput#inference_table_config}
        '''
        result = self._values.get("inference_table_config")
        return typing.cast(typing.Optional["ModelServingProvisionedThroughputAiGatewayInferenceTableConfig"], result)

    @builtins.property
    def rate_limits(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingProvisionedThroughputAiGatewayRateLimits"]]]:
        '''rate_limits block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#rate_limits ModelServingProvisionedThroughput#rate_limits}
        '''
        result = self._values.get("rate_limits")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingProvisionedThroughputAiGatewayRateLimits"]]], result)

    @builtins.property
    def usage_tracking_config(
        self,
    ) -> typing.Optional["ModelServingProvisionedThroughputAiGatewayUsageTrackingConfig"]:
        '''usage_tracking_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#usage_tracking_config ModelServingProvisionedThroughput#usage_tracking_config}
        '''
        result = self._values.get("usage_tracking_config")
        return typing.cast(typing.Optional["ModelServingProvisionedThroughputAiGatewayUsageTrackingConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingProvisionedThroughputAiGateway(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputAiGatewayFallbackConfig",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled"},
)
class ModelServingProvisionedThroughputAiGatewayFallbackConfig:
    def __init__(
        self,
        *,
        enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#enabled ModelServingProvisionedThroughput#enabled}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eef49a07c6162f167aef128e026eccb2257f1eca34b837f17d361a5162c5955b)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "enabled": enabled,
        }

    @builtins.property
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#enabled ModelServingProvisionedThroughput#enabled}.'''
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingProvisionedThroughputAiGatewayFallbackConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingProvisionedThroughputAiGatewayFallbackConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputAiGatewayFallbackConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2be6308f5572c0e1b0d30f4c1e80bd36bae310dca4772d2030c2994e5ca99ddd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__e3ef7e624a131d3b149c530b8d071e0972b918963fa40bd39ff75ad0d7723e2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingProvisionedThroughputAiGatewayFallbackConfig]:
        return typing.cast(typing.Optional[ModelServingProvisionedThroughputAiGatewayFallbackConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingProvisionedThroughputAiGatewayFallbackConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__119321bd7f2533b70749178bcefe56ce2132f470adad70627844b9808ccb8f12)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputAiGatewayGuardrails",
    jsii_struct_bases=[],
    name_mapping={"input": "input", "output": "output"},
)
class ModelServingProvisionedThroughputAiGatewayGuardrails:
    def __init__(
        self,
        *,
        input: typing.Optional[typing.Union["ModelServingProvisionedThroughputAiGatewayGuardrailsInput", typing.Dict[builtins.str, typing.Any]]] = None,
        output: typing.Optional[typing.Union["ModelServingProvisionedThroughputAiGatewayGuardrailsOutput", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param input: input block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#input ModelServingProvisionedThroughput#input}
        :param output: output block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#output ModelServingProvisionedThroughput#output}
        '''
        if isinstance(input, dict):
            input = ModelServingProvisionedThroughputAiGatewayGuardrailsInput(**input)
        if isinstance(output, dict):
            output = ModelServingProvisionedThroughputAiGatewayGuardrailsOutput(**output)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b175c019629ad28730b52085bb2815f7be0a3bf90b1a2042c182f57fa3e192e8)
            check_type(argname="argument input", value=input, expected_type=type_hints["input"])
            check_type(argname="argument output", value=output, expected_type=type_hints["output"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if input is not None:
            self._values["input"] = input
        if output is not None:
            self._values["output"] = output

    @builtins.property
    def input(
        self,
    ) -> typing.Optional["ModelServingProvisionedThroughputAiGatewayGuardrailsInput"]:
        '''input block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#input ModelServingProvisionedThroughput#input}
        '''
        result = self._values.get("input")
        return typing.cast(typing.Optional["ModelServingProvisionedThroughputAiGatewayGuardrailsInput"], result)

    @builtins.property
    def output(
        self,
    ) -> typing.Optional["ModelServingProvisionedThroughputAiGatewayGuardrailsOutput"]:
        '''output block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#output ModelServingProvisionedThroughput#output}
        '''
        result = self._values.get("output")
        return typing.cast(typing.Optional["ModelServingProvisionedThroughputAiGatewayGuardrailsOutput"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingProvisionedThroughputAiGatewayGuardrails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputAiGatewayGuardrailsInput",
    jsii_struct_bases=[],
    name_mapping={
        "invalid_keywords": "invalidKeywords",
        "pii": "pii",
        "safety": "safety",
        "valid_topics": "validTopics",
    },
)
class ModelServingProvisionedThroughputAiGatewayGuardrailsInput:
    def __init__(
        self,
        *,
        invalid_keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        pii: typing.Optional[typing.Union["ModelServingProvisionedThroughputAiGatewayGuardrailsInputPii", typing.Dict[builtins.str, typing.Any]]] = None,
        safety: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        valid_topics: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param invalid_keywords: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#invalid_keywords ModelServingProvisionedThroughput#invalid_keywords}.
        :param pii: pii block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#pii ModelServingProvisionedThroughput#pii}
        :param safety: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#safety ModelServingProvisionedThroughput#safety}.
        :param valid_topics: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#valid_topics ModelServingProvisionedThroughput#valid_topics}.
        '''
        if isinstance(pii, dict):
            pii = ModelServingProvisionedThroughputAiGatewayGuardrailsInputPii(**pii)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c74a9be870b4a4b5abb2f2d6d02110d63b0cf9b8e9d2ebc887e5299dae241605)
            check_type(argname="argument invalid_keywords", value=invalid_keywords, expected_type=type_hints["invalid_keywords"])
            check_type(argname="argument pii", value=pii, expected_type=type_hints["pii"])
            check_type(argname="argument safety", value=safety, expected_type=type_hints["safety"])
            check_type(argname="argument valid_topics", value=valid_topics, expected_type=type_hints["valid_topics"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if invalid_keywords is not None:
            self._values["invalid_keywords"] = invalid_keywords
        if pii is not None:
            self._values["pii"] = pii
        if safety is not None:
            self._values["safety"] = safety
        if valid_topics is not None:
            self._values["valid_topics"] = valid_topics

    @builtins.property
    def invalid_keywords(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#invalid_keywords ModelServingProvisionedThroughput#invalid_keywords}.'''
        result = self._values.get("invalid_keywords")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def pii(
        self,
    ) -> typing.Optional["ModelServingProvisionedThroughputAiGatewayGuardrailsInputPii"]:
        '''pii block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#pii ModelServingProvisionedThroughput#pii}
        '''
        result = self._values.get("pii")
        return typing.cast(typing.Optional["ModelServingProvisionedThroughputAiGatewayGuardrailsInputPii"], result)

    @builtins.property
    def safety(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#safety ModelServingProvisionedThroughput#safety}.'''
        result = self._values.get("safety")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def valid_topics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#valid_topics ModelServingProvisionedThroughput#valid_topics}.'''
        result = self._values.get("valid_topics")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingProvisionedThroughputAiGatewayGuardrailsInput(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingProvisionedThroughputAiGatewayGuardrailsInputOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputAiGatewayGuardrailsInputOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__678627d51503d74e8010a809f47fe697afc68bf099aabed5ee2aa38f178afde9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putPii")
    def put_pii(self, *, behavior: typing.Optional[builtins.str] = None) -> None:
        '''
        :param behavior: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#behavior ModelServingProvisionedThroughput#behavior}.
        '''
        value = ModelServingProvisionedThroughputAiGatewayGuardrailsInputPii(
            behavior=behavior
        )

        return typing.cast(None, jsii.invoke(self, "putPii", [value]))

    @jsii.member(jsii_name="resetInvalidKeywords")
    def reset_invalid_keywords(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInvalidKeywords", []))

    @jsii.member(jsii_name="resetPii")
    def reset_pii(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPii", []))

    @jsii.member(jsii_name="resetSafety")
    def reset_safety(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSafety", []))

    @jsii.member(jsii_name="resetValidTopics")
    def reset_valid_topics(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValidTopics", []))

    @builtins.property
    @jsii.member(jsii_name="pii")
    def pii(
        self,
    ) -> "ModelServingProvisionedThroughputAiGatewayGuardrailsInputPiiOutputReference":
        return typing.cast("ModelServingProvisionedThroughputAiGatewayGuardrailsInputPiiOutputReference", jsii.get(self, "pii"))

    @builtins.property
    @jsii.member(jsii_name="invalidKeywordsInput")
    def invalid_keywords_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "invalidKeywordsInput"))

    @builtins.property
    @jsii.member(jsii_name="piiInput")
    def pii_input(
        self,
    ) -> typing.Optional["ModelServingProvisionedThroughputAiGatewayGuardrailsInputPii"]:
        return typing.cast(typing.Optional["ModelServingProvisionedThroughputAiGatewayGuardrailsInputPii"], jsii.get(self, "piiInput"))

    @builtins.property
    @jsii.member(jsii_name="safetyInput")
    def safety_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "safetyInput"))

    @builtins.property
    @jsii.member(jsii_name="validTopicsInput")
    def valid_topics_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "validTopicsInput"))

    @builtins.property
    @jsii.member(jsii_name="invalidKeywords")
    def invalid_keywords(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "invalidKeywords"))

    @invalid_keywords.setter
    def invalid_keywords(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__883cc28d2c98b874ad47d7b0a636aee9d8f16dbf66c7ef0a25742719b4ccfb01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "invalidKeywords", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="safety")
    def safety(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "safety"))

    @safety.setter
    def safety(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e7e9b0e0f5d32b6e3e00ae6330119b9b8471ce02c1995d954642b47472c2bae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "safety", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="validTopics")
    def valid_topics(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "validTopics"))

    @valid_topics.setter
    def valid_topics(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__913fb0dc0a9e813e00afdbbd5bbf5fba3ee3e3ef3c4565af6c40c5d7170182ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "validTopics", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingProvisionedThroughputAiGatewayGuardrailsInput]:
        return typing.cast(typing.Optional[ModelServingProvisionedThroughputAiGatewayGuardrailsInput], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingProvisionedThroughputAiGatewayGuardrailsInput],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3025ba60fca46216294354db3a1e2f3577fc432906d416c261262a2c72a8a918)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputAiGatewayGuardrailsInputPii",
    jsii_struct_bases=[],
    name_mapping={"behavior": "behavior"},
)
class ModelServingProvisionedThroughputAiGatewayGuardrailsInputPii:
    def __init__(self, *, behavior: typing.Optional[builtins.str] = None) -> None:
        '''
        :param behavior: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#behavior ModelServingProvisionedThroughput#behavior}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbf4523f5c16759fbe30165a97751fa11cc2773679bfae50a0fe3c414a3baad9)
            check_type(argname="argument behavior", value=behavior, expected_type=type_hints["behavior"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if behavior is not None:
            self._values["behavior"] = behavior

    @builtins.property
    def behavior(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#behavior ModelServingProvisionedThroughput#behavior}.'''
        result = self._values.get("behavior")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingProvisionedThroughputAiGatewayGuardrailsInputPii(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingProvisionedThroughputAiGatewayGuardrailsInputPiiOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputAiGatewayGuardrailsInputPiiOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3f24a990b7bccf8ae268a8347012c1a6cc8de1e92c34c856c911d54031d6b623)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetBehavior")
    def reset_behavior(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBehavior", []))

    @builtins.property
    @jsii.member(jsii_name="behaviorInput")
    def behavior_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "behaviorInput"))

    @builtins.property
    @jsii.member(jsii_name="behavior")
    def behavior(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "behavior"))

    @behavior.setter
    def behavior(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afc972c094502ea4a4700843165ff2d8d02ad06633e40002b4d25d87f0031582)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "behavior", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingProvisionedThroughputAiGatewayGuardrailsInputPii]:
        return typing.cast(typing.Optional[ModelServingProvisionedThroughputAiGatewayGuardrailsInputPii], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingProvisionedThroughputAiGatewayGuardrailsInputPii],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36be8c9f6ba4baad5ff5eee13699f8b4d9fbc7d168c9fab3d56b894fccc4ed54)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputAiGatewayGuardrailsOutput",
    jsii_struct_bases=[],
    name_mapping={
        "invalid_keywords": "invalidKeywords",
        "pii": "pii",
        "safety": "safety",
        "valid_topics": "validTopics",
    },
)
class ModelServingProvisionedThroughputAiGatewayGuardrailsOutput:
    def __init__(
        self,
        *,
        invalid_keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        pii: typing.Optional[typing.Union["ModelServingProvisionedThroughputAiGatewayGuardrailsOutputPii", typing.Dict[builtins.str, typing.Any]]] = None,
        safety: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        valid_topics: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param invalid_keywords: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#invalid_keywords ModelServingProvisionedThroughput#invalid_keywords}.
        :param pii: pii block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#pii ModelServingProvisionedThroughput#pii}
        :param safety: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#safety ModelServingProvisionedThroughput#safety}.
        :param valid_topics: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#valid_topics ModelServingProvisionedThroughput#valid_topics}.
        '''
        if isinstance(pii, dict):
            pii = ModelServingProvisionedThroughputAiGatewayGuardrailsOutputPii(**pii)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9efbda3bba53a205f1c2dfe3947a94bd44bc6d9e1e4fae0137c1492d7da832f5)
            check_type(argname="argument invalid_keywords", value=invalid_keywords, expected_type=type_hints["invalid_keywords"])
            check_type(argname="argument pii", value=pii, expected_type=type_hints["pii"])
            check_type(argname="argument safety", value=safety, expected_type=type_hints["safety"])
            check_type(argname="argument valid_topics", value=valid_topics, expected_type=type_hints["valid_topics"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if invalid_keywords is not None:
            self._values["invalid_keywords"] = invalid_keywords
        if pii is not None:
            self._values["pii"] = pii
        if safety is not None:
            self._values["safety"] = safety
        if valid_topics is not None:
            self._values["valid_topics"] = valid_topics

    @builtins.property
    def invalid_keywords(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#invalid_keywords ModelServingProvisionedThroughput#invalid_keywords}.'''
        result = self._values.get("invalid_keywords")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def pii(
        self,
    ) -> typing.Optional["ModelServingProvisionedThroughputAiGatewayGuardrailsOutputPii"]:
        '''pii block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#pii ModelServingProvisionedThroughput#pii}
        '''
        result = self._values.get("pii")
        return typing.cast(typing.Optional["ModelServingProvisionedThroughputAiGatewayGuardrailsOutputPii"], result)

    @builtins.property
    def safety(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#safety ModelServingProvisionedThroughput#safety}.'''
        result = self._values.get("safety")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def valid_topics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#valid_topics ModelServingProvisionedThroughput#valid_topics}.'''
        result = self._values.get("valid_topics")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingProvisionedThroughputAiGatewayGuardrailsOutput(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingProvisionedThroughputAiGatewayGuardrailsOutputOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputAiGatewayGuardrailsOutputOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__66dacf958f6985937c4e78f88c6de331a05184d02a578643f52540f6a622683c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putPii")
    def put_pii(self, *, behavior: typing.Optional[builtins.str] = None) -> None:
        '''
        :param behavior: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#behavior ModelServingProvisionedThroughput#behavior}.
        '''
        value = ModelServingProvisionedThroughputAiGatewayGuardrailsOutputPii(
            behavior=behavior
        )

        return typing.cast(None, jsii.invoke(self, "putPii", [value]))

    @jsii.member(jsii_name="resetInvalidKeywords")
    def reset_invalid_keywords(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInvalidKeywords", []))

    @jsii.member(jsii_name="resetPii")
    def reset_pii(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPii", []))

    @jsii.member(jsii_name="resetSafety")
    def reset_safety(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSafety", []))

    @jsii.member(jsii_name="resetValidTopics")
    def reset_valid_topics(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValidTopics", []))

    @builtins.property
    @jsii.member(jsii_name="pii")
    def pii(
        self,
    ) -> "ModelServingProvisionedThroughputAiGatewayGuardrailsOutputPiiOutputReference":
        return typing.cast("ModelServingProvisionedThroughputAiGatewayGuardrailsOutputPiiOutputReference", jsii.get(self, "pii"))

    @builtins.property
    @jsii.member(jsii_name="invalidKeywordsInput")
    def invalid_keywords_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "invalidKeywordsInput"))

    @builtins.property
    @jsii.member(jsii_name="piiInput")
    def pii_input(
        self,
    ) -> typing.Optional["ModelServingProvisionedThroughputAiGatewayGuardrailsOutputPii"]:
        return typing.cast(typing.Optional["ModelServingProvisionedThroughputAiGatewayGuardrailsOutputPii"], jsii.get(self, "piiInput"))

    @builtins.property
    @jsii.member(jsii_name="safetyInput")
    def safety_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "safetyInput"))

    @builtins.property
    @jsii.member(jsii_name="validTopicsInput")
    def valid_topics_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "validTopicsInput"))

    @builtins.property
    @jsii.member(jsii_name="invalidKeywords")
    def invalid_keywords(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "invalidKeywords"))

    @invalid_keywords.setter
    def invalid_keywords(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8612ecc53c7136048dd23b5e7e16a98ab61b7f6f042d69663e5253720cab2f4c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "invalidKeywords", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="safety")
    def safety(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "safety"))

    @safety.setter
    def safety(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e21c54eaff145763f8f9bd29ed35afe8bc411e7c1cb4ffb9242233c0a81c5fe8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "safety", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="validTopics")
    def valid_topics(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "validTopics"))

    @valid_topics.setter
    def valid_topics(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c1e736eedd5b71a9c6b7f701a0dd11ea70e1737c048535b91df2e5ba3c8489a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "validTopics", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingProvisionedThroughputAiGatewayGuardrailsOutput]:
        return typing.cast(typing.Optional[ModelServingProvisionedThroughputAiGatewayGuardrailsOutput], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingProvisionedThroughputAiGatewayGuardrailsOutput],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f13b4db6467954d4dc511acb317e0f2583c1c3209b4dd01efd72517a6c2459f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputAiGatewayGuardrailsOutputPii",
    jsii_struct_bases=[],
    name_mapping={"behavior": "behavior"},
)
class ModelServingProvisionedThroughputAiGatewayGuardrailsOutputPii:
    def __init__(self, *, behavior: typing.Optional[builtins.str] = None) -> None:
        '''
        :param behavior: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#behavior ModelServingProvisionedThroughput#behavior}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c651aa5d572d1a984dec51d9eaf1d4f9856eb9b362c6982bcc375568159a14f7)
            check_type(argname="argument behavior", value=behavior, expected_type=type_hints["behavior"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if behavior is not None:
            self._values["behavior"] = behavior

    @builtins.property
    def behavior(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#behavior ModelServingProvisionedThroughput#behavior}.'''
        result = self._values.get("behavior")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingProvisionedThroughputAiGatewayGuardrailsOutputPii(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingProvisionedThroughputAiGatewayGuardrailsOutputPiiOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputAiGatewayGuardrailsOutputPiiOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__55386120ac6bc16269cc72b17d0fc878622067c4acbde3947474501bc5c1412c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetBehavior")
    def reset_behavior(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBehavior", []))

    @builtins.property
    @jsii.member(jsii_name="behaviorInput")
    def behavior_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "behaviorInput"))

    @builtins.property
    @jsii.member(jsii_name="behavior")
    def behavior(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "behavior"))

    @behavior.setter
    def behavior(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b8482105600c77f643d2de617d9051363d5657f244bb34589fd77d86b61eecf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "behavior", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingProvisionedThroughputAiGatewayGuardrailsOutputPii]:
        return typing.cast(typing.Optional[ModelServingProvisionedThroughputAiGatewayGuardrailsOutputPii], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingProvisionedThroughputAiGatewayGuardrailsOutputPii],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93250e2d87acb703b631a3e45d19b0cd543f02bc309e67039a472ad61981fd78)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ModelServingProvisionedThroughputAiGatewayGuardrailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputAiGatewayGuardrailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__95e0b494d82ea1b6856b33d74c0897f4c0804bfe6750bccebfbd16ec109c12bd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putInput")
    def put_input(
        self,
        *,
        invalid_keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        pii: typing.Optional[typing.Union[ModelServingProvisionedThroughputAiGatewayGuardrailsInputPii, typing.Dict[builtins.str, typing.Any]]] = None,
        safety: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        valid_topics: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param invalid_keywords: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#invalid_keywords ModelServingProvisionedThroughput#invalid_keywords}.
        :param pii: pii block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#pii ModelServingProvisionedThroughput#pii}
        :param safety: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#safety ModelServingProvisionedThroughput#safety}.
        :param valid_topics: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#valid_topics ModelServingProvisionedThroughput#valid_topics}.
        '''
        value = ModelServingProvisionedThroughputAiGatewayGuardrailsInput(
            invalid_keywords=invalid_keywords,
            pii=pii,
            safety=safety,
            valid_topics=valid_topics,
        )

        return typing.cast(None, jsii.invoke(self, "putInput", [value]))

    @jsii.member(jsii_name="putOutput")
    def put_output(
        self,
        *,
        invalid_keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        pii: typing.Optional[typing.Union[ModelServingProvisionedThroughputAiGatewayGuardrailsOutputPii, typing.Dict[builtins.str, typing.Any]]] = None,
        safety: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        valid_topics: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param invalid_keywords: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#invalid_keywords ModelServingProvisionedThroughput#invalid_keywords}.
        :param pii: pii block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#pii ModelServingProvisionedThroughput#pii}
        :param safety: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#safety ModelServingProvisionedThroughput#safety}.
        :param valid_topics: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#valid_topics ModelServingProvisionedThroughput#valid_topics}.
        '''
        value = ModelServingProvisionedThroughputAiGatewayGuardrailsOutput(
            invalid_keywords=invalid_keywords,
            pii=pii,
            safety=safety,
            valid_topics=valid_topics,
        )

        return typing.cast(None, jsii.invoke(self, "putOutput", [value]))

    @jsii.member(jsii_name="resetInput")
    def reset_input(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInput", []))

    @jsii.member(jsii_name="resetOutput")
    def reset_output(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOutput", []))

    @builtins.property
    @jsii.member(jsii_name="input")
    def input(
        self,
    ) -> ModelServingProvisionedThroughputAiGatewayGuardrailsInputOutputReference:
        return typing.cast(ModelServingProvisionedThroughputAiGatewayGuardrailsInputOutputReference, jsii.get(self, "input"))

    @builtins.property
    @jsii.member(jsii_name="output")
    def output(
        self,
    ) -> ModelServingProvisionedThroughputAiGatewayGuardrailsOutputOutputReference:
        return typing.cast(ModelServingProvisionedThroughputAiGatewayGuardrailsOutputOutputReference, jsii.get(self, "output"))

    @builtins.property
    @jsii.member(jsii_name="inputInput")
    def input_input(
        self,
    ) -> typing.Optional[ModelServingProvisionedThroughputAiGatewayGuardrailsInput]:
        return typing.cast(typing.Optional[ModelServingProvisionedThroughputAiGatewayGuardrailsInput], jsii.get(self, "inputInput"))

    @builtins.property
    @jsii.member(jsii_name="outputInput")
    def output_input(
        self,
    ) -> typing.Optional[ModelServingProvisionedThroughputAiGatewayGuardrailsOutput]:
        return typing.cast(typing.Optional[ModelServingProvisionedThroughputAiGatewayGuardrailsOutput], jsii.get(self, "outputInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingProvisionedThroughputAiGatewayGuardrails]:
        return typing.cast(typing.Optional[ModelServingProvisionedThroughputAiGatewayGuardrails], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingProvisionedThroughputAiGatewayGuardrails],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31ee10b8ace32136ea4a9022e7ce15bada11fc2ae78221a806078a298117bafc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputAiGatewayInferenceTableConfig",
    jsii_struct_bases=[],
    name_mapping={
        "catalog_name": "catalogName",
        "enabled": "enabled",
        "schema_name": "schemaName",
        "table_name_prefix": "tableNamePrefix",
    },
)
class ModelServingProvisionedThroughputAiGatewayInferenceTableConfig:
    def __init__(
        self,
        *,
        catalog_name: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        schema_name: typing.Optional[builtins.str] = None,
        table_name_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param catalog_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#catalog_name ModelServingProvisionedThroughput#catalog_name}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#enabled ModelServingProvisionedThroughput#enabled}.
        :param schema_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#schema_name ModelServingProvisionedThroughput#schema_name}.
        :param table_name_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#table_name_prefix ModelServingProvisionedThroughput#table_name_prefix}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfcb764f756555c70ef53a076a07828a3ab78f2ecb001b66597c8ce5e87cdcef)
            check_type(argname="argument catalog_name", value=catalog_name, expected_type=type_hints["catalog_name"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument schema_name", value=schema_name, expected_type=type_hints["schema_name"])
            check_type(argname="argument table_name_prefix", value=table_name_prefix, expected_type=type_hints["table_name_prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if catalog_name is not None:
            self._values["catalog_name"] = catalog_name
        if enabled is not None:
            self._values["enabled"] = enabled
        if schema_name is not None:
            self._values["schema_name"] = schema_name
        if table_name_prefix is not None:
            self._values["table_name_prefix"] = table_name_prefix

    @builtins.property
    def catalog_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#catalog_name ModelServingProvisionedThroughput#catalog_name}.'''
        result = self._values.get("catalog_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#enabled ModelServingProvisionedThroughput#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def schema_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#schema_name ModelServingProvisionedThroughput#schema_name}.'''
        result = self._values.get("schema_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def table_name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#table_name_prefix ModelServingProvisionedThroughput#table_name_prefix}.'''
        result = self._values.get("table_name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingProvisionedThroughputAiGatewayInferenceTableConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingProvisionedThroughputAiGatewayInferenceTableConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputAiGatewayInferenceTableConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__056354db4ede85f34d8c7148ede89fec9784feece25f279d99a283142eb3edf7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCatalogName")
    def reset_catalog_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCatalogName", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetSchemaName")
    def reset_schema_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchemaName", []))

    @jsii.member(jsii_name="resetTableNamePrefix")
    def reset_table_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTableNamePrefix", []))

    @builtins.property
    @jsii.member(jsii_name="catalogNameInput")
    def catalog_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "catalogNameInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="schemaNameInput")
    def schema_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schemaNameInput"))

    @builtins.property
    @jsii.member(jsii_name="tableNamePrefixInput")
    def table_name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tableNamePrefixInput"))

    @builtins.property
    @jsii.member(jsii_name="catalogName")
    def catalog_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "catalogName"))

    @catalog_name.setter
    def catalog_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f171967a9a57f04e34da42063151f3275d44f35f23c5ab56b365ba116f2e21d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "catalogName", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__728e38b0fe291f325ada2319bf24b3127adec6239c34b9250486572d3cbd982b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="schemaName")
    def schema_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schemaName"))

    @schema_name.setter
    def schema_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ab77d4ac8e744e54d127900481e838393d342ae82a502fcbfef8e4edfa8caa4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "schemaName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tableNamePrefix")
    def table_name_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tableNamePrefix"))

    @table_name_prefix.setter
    def table_name_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4492cce97ae8f169d3162a423f09791b5ca5d4fbcf54d579deb01b7261b9cf26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tableNamePrefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingProvisionedThroughputAiGatewayInferenceTableConfig]:
        return typing.cast(typing.Optional[ModelServingProvisionedThroughputAiGatewayInferenceTableConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingProvisionedThroughputAiGatewayInferenceTableConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcc16043366883ace9a512c51f0d2c3dcc6350f58217d442a6ff151bc003b434)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ModelServingProvisionedThroughputAiGatewayOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputAiGatewayOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0d8cc3a0f7f4513a1b6339024dc20e4ffb56b7247ef3b053f03a32ed9f7a99c6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putFallbackConfig")
    def put_fallback_config(
        self,
        *,
        enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#enabled ModelServingProvisionedThroughput#enabled}.
        '''
        value = ModelServingProvisionedThroughputAiGatewayFallbackConfig(
            enabled=enabled
        )

        return typing.cast(None, jsii.invoke(self, "putFallbackConfig", [value]))

    @jsii.member(jsii_name="putGuardrails")
    def put_guardrails(
        self,
        *,
        input: typing.Optional[typing.Union[ModelServingProvisionedThroughputAiGatewayGuardrailsInput, typing.Dict[builtins.str, typing.Any]]] = None,
        output: typing.Optional[typing.Union[ModelServingProvisionedThroughputAiGatewayGuardrailsOutput, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param input: input block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#input ModelServingProvisionedThroughput#input}
        :param output: output block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#output ModelServingProvisionedThroughput#output}
        '''
        value = ModelServingProvisionedThroughputAiGatewayGuardrails(
            input=input, output=output
        )

        return typing.cast(None, jsii.invoke(self, "putGuardrails", [value]))

    @jsii.member(jsii_name="putInferenceTableConfig")
    def put_inference_table_config(
        self,
        *,
        catalog_name: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        schema_name: typing.Optional[builtins.str] = None,
        table_name_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param catalog_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#catalog_name ModelServingProvisionedThroughput#catalog_name}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#enabled ModelServingProvisionedThroughput#enabled}.
        :param schema_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#schema_name ModelServingProvisionedThroughput#schema_name}.
        :param table_name_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#table_name_prefix ModelServingProvisionedThroughput#table_name_prefix}.
        '''
        value = ModelServingProvisionedThroughputAiGatewayInferenceTableConfig(
            catalog_name=catalog_name,
            enabled=enabled,
            schema_name=schema_name,
            table_name_prefix=table_name_prefix,
        )

        return typing.cast(None, jsii.invoke(self, "putInferenceTableConfig", [value]))

    @jsii.member(jsii_name="putRateLimits")
    def put_rate_limits(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingProvisionedThroughputAiGatewayRateLimits", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9bb2a72ad01e65c9b9effa4f8dc8de5d7e02ae895a3eb236de3fdaac219fa0d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRateLimits", [value]))

    @jsii.member(jsii_name="putUsageTrackingConfig")
    def put_usage_tracking_config(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#enabled ModelServingProvisionedThroughput#enabled}.
        '''
        value = ModelServingProvisionedThroughputAiGatewayUsageTrackingConfig(
            enabled=enabled
        )

        return typing.cast(None, jsii.invoke(self, "putUsageTrackingConfig", [value]))

    @jsii.member(jsii_name="resetFallbackConfig")
    def reset_fallback_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFallbackConfig", []))

    @jsii.member(jsii_name="resetGuardrails")
    def reset_guardrails(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGuardrails", []))

    @jsii.member(jsii_name="resetInferenceTableConfig")
    def reset_inference_table_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInferenceTableConfig", []))

    @jsii.member(jsii_name="resetRateLimits")
    def reset_rate_limits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRateLimits", []))

    @jsii.member(jsii_name="resetUsageTrackingConfig")
    def reset_usage_tracking_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsageTrackingConfig", []))

    @builtins.property
    @jsii.member(jsii_name="fallbackConfig")
    def fallback_config(
        self,
    ) -> ModelServingProvisionedThroughputAiGatewayFallbackConfigOutputReference:
        return typing.cast(ModelServingProvisionedThroughputAiGatewayFallbackConfigOutputReference, jsii.get(self, "fallbackConfig"))

    @builtins.property
    @jsii.member(jsii_name="guardrails")
    def guardrails(
        self,
    ) -> ModelServingProvisionedThroughputAiGatewayGuardrailsOutputReference:
        return typing.cast(ModelServingProvisionedThroughputAiGatewayGuardrailsOutputReference, jsii.get(self, "guardrails"))

    @builtins.property
    @jsii.member(jsii_name="inferenceTableConfig")
    def inference_table_config(
        self,
    ) -> ModelServingProvisionedThroughputAiGatewayInferenceTableConfigOutputReference:
        return typing.cast(ModelServingProvisionedThroughputAiGatewayInferenceTableConfigOutputReference, jsii.get(self, "inferenceTableConfig"))

    @builtins.property
    @jsii.member(jsii_name="rateLimits")
    def rate_limits(self) -> "ModelServingProvisionedThroughputAiGatewayRateLimitsList":
        return typing.cast("ModelServingProvisionedThroughputAiGatewayRateLimitsList", jsii.get(self, "rateLimits"))

    @builtins.property
    @jsii.member(jsii_name="usageTrackingConfig")
    def usage_tracking_config(
        self,
    ) -> "ModelServingProvisionedThroughputAiGatewayUsageTrackingConfigOutputReference":
        return typing.cast("ModelServingProvisionedThroughputAiGatewayUsageTrackingConfigOutputReference", jsii.get(self, "usageTrackingConfig"))

    @builtins.property
    @jsii.member(jsii_name="fallbackConfigInput")
    def fallback_config_input(
        self,
    ) -> typing.Optional[ModelServingProvisionedThroughputAiGatewayFallbackConfig]:
        return typing.cast(typing.Optional[ModelServingProvisionedThroughputAiGatewayFallbackConfig], jsii.get(self, "fallbackConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="guardrailsInput")
    def guardrails_input(
        self,
    ) -> typing.Optional[ModelServingProvisionedThroughputAiGatewayGuardrails]:
        return typing.cast(typing.Optional[ModelServingProvisionedThroughputAiGatewayGuardrails], jsii.get(self, "guardrailsInput"))

    @builtins.property
    @jsii.member(jsii_name="inferenceTableConfigInput")
    def inference_table_config_input(
        self,
    ) -> typing.Optional[ModelServingProvisionedThroughputAiGatewayInferenceTableConfig]:
        return typing.cast(typing.Optional[ModelServingProvisionedThroughputAiGatewayInferenceTableConfig], jsii.get(self, "inferenceTableConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="rateLimitsInput")
    def rate_limits_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingProvisionedThroughputAiGatewayRateLimits"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingProvisionedThroughputAiGatewayRateLimits"]]], jsii.get(self, "rateLimitsInput"))

    @builtins.property
    @jsii.member(jsii_name="usageTrackingConfigInput")
    def usage_tracking_config_input(
        self,
    ) -> typing.Optional["ModelServingProvisionedThroughputAiGatewayUsageTrackingConfig"]:
        return typing.cast(typing.Optional["ModelServingProvisionedThroughputAiGatewayUsageTrackingConfig"], jsii.get(self, "usageTrackingConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingProvisionedThroughputAiGateway]:
        return typing.cast(typing.Optional[ModelServingProvisionedThroughputAiGateway], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingProvisionedThroughputAiGateway],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3cd29adb040f2763877a6625c4411c25787f5e1c07104abd56e10add9df6def)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputAiGatewayRateLimits",
    jsii_struct_bases=[],
    name_mapping={
        "renewal_period": "renewalPeriod",
        "calls": "calls",
        "key": "key",
        "principal": "principal",
        "tokens": "tokens",
    },
)
class ModelServingProvisionedThroughputAiGatewayRateLimits:
    def __init__(
        self,
        *,
        renewal_period: builtins.str,
        calls: typing.Optional[jsii.Number] = None,
        key: typing.Optional[builtins.str] = None,
        principal: typing.Optional[builtins.str] = None,
        tokens: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param renewal_period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#renewal_period ModelServingProvisionedThroughput#renewal_period}.
        :param calls: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#calls ModelServingProvisionedThroughput#calls}.
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#key ModelServingProvisionedThroughput#key}.
        :param principal: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#principal ModelServingProvisionedThroughput#principal}.
        :param tokens: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#tokens ModelServingProvisionedThroughput#tokens}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2756476e14a22a6371ecce8619e59b2716b91e838a442a4d92e536b15adb534c)
            check_type(argname="argument renewal_period", value=renewal_period, expected_type=type_hints["renewal_period"])
            check_type(argname="argument calls", value=calls, expected_type=type_hints["calls"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument principal", value=principal, expected_type=type_hints["principal"])
            check_type(argname="argument tokens", value=tokens, expected_type=type_hints["tokens"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "renewal_period": renewal_period,
        }
        if calls is not None:
            self._values["calls"] = calls
        if key is not None:
            self._values["key"] = key
        if principal is not None:
            self._values["principal"] = principal
        if tokens is not None:
            self._values["tokens"] = tokens

    @builtins.property
    def renewal_period(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#renewal_period ModelServingProvisionedThroughput#renewal_period}.'''
        result = self._values.get("renewal_period")
        assert result is not None, "Required property 'renewal_period' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def calls(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#calls ModelServingProvisionedThroughput#calls}.'''
        result = self._values.get("calls")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#key ModelServingProvisionedThroughput#key}.'''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def principal(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#principal ModelServingProvisionedThroughput#principal}.'''
        result = self._values.get("principal")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tokens(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#tokens ModelServingProvisionedThroughput#tokens}.'''
        result = self._values.get("tokens")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingProvisionedThroughputAiGatewayRateLimits(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingProvisionedThroughputAiGatewayRateLimitsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputAiGatewayRateLimitsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9ddd49328e744f3bed48cb0c26bd86386608b8dd35d97e52acb6676a61a8323e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ModelServingProvisionedThroughputAiGatewayRateLimitsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b2a10f6eaa450651b05a1b097fbf2b5555ce402bd8c003593530dcb703138b0)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ModelServingProvisionedThroughputAiGatewayRateLimitsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13c508725bcc50186a33388144851b4b3271ea4f2557f22e07dabc4bf606d265)
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
            type_hints = typing.get_type_hints(_typecheckingstub__aa9b7e380f2c4b0fc1662b8c2dc88909b82fcba482756b2c0d4a366309a87481)
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
            type_hints = typing.get_type_hints(_typecheckingstub__065630854dc20859d93bb263a95eae4402f887e6f38a3c60211cda0ee4849c18)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingProvisionedThroughputAiGatewayRateLimits]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingProvisionedThroughputAiGatewayRateLimits]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingProvisionedThroughputAiGatewayRateLimits]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b7d4520eb2abb2b9258a68dcf956fd1b141d6336ac4c25bb0adae673aa8b002)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ModelServingProvisionedThroughputAiGatewayRateLimitsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputAiGatewayRateLimitsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b311d194a26ebe882bc8067f6617001075194600f86b966f9b2b304063f46d08)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetCalls")
    def reset_calls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCalls", []))

    @jsii.member(jsii_name="resetKey")
    def reset_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKey", []))

    @jsii.member(jsii_name="resetPrincipal")
    def reset_principal(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrincipal", []))

    @jsii.member(jsii_name="resetTokens")
    def reset_tokens(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokens", []))

    @builtins.property
    @jsii.member(jsii_name="callsInput")
    def calls_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "callsInput"))

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="principalInput")
    def principal_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "principalInput"))

    @builtins.property
    @jsii.member(jsii_name="renewalPeriodInput")
    def renewal_period_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "renewalPeriodInput"))

    @builtins.property
    @jsii.member(jsii_name="tokensInput")
    def tokens_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "tokensInput"))

    @builtins.property
    @jsii.member(jsii_name="calls")
    def calls(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "calls"))

    @calls.setter
    def calls(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5124cd70a8e1b221060f467ae5644edf6af4c31738bf574045ade7eb6dacb256)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "calls", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03f53ce4212a778690f264da5ef6e482fa55a5b8fa5cb714785f3ebfb0671f47)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="principal")
    def principal(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "principal"))

    @principal.setter
    def principal(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00d3226ea359ae01a46172167787b51c16a83f1bc3d9797a2249ef2e6c3bc5ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "principal", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="renewalPeriod")
    def renewal_period(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "renewalPeriod"))

    @renewal_period.setter
    def renewal_period(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2cf0f4fbd1f53a528b5a26da5328d72d7b87d7c855c55c6078fbf601df8ca241)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "renewalPeriod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokens")
    def tokens(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokens"))

    @tokens.setter
    def tokens(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0624ff9d20f7dbbbc00309f14d448dae58701f97ae9ab606a31eaf0071f2bc04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokens", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingProvisionedThroughputAiGatewayRateLimits]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingProvisionedThroughputAiGatewayRateLimits]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingProvisionedThroughputAiGatewayRateLimits]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8380a434f4dbfa8f6ef73de9cac727c3ac28abbb0f25c69f201ce9aa8dd2ae7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputAiGatewayUsageTrackingConfig",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled"},
)
class ModelServingProvisionedThroughputAiGatewayUsageTrackingConfig:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#enabled ModelServingProvisionedThroughput#enabled}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36954b179830ac10c83b8990174f021dad0f0267f7be18c3b43f4768890f1b2b)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#enabled ModelServingProvisionedThroughput#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingProvisionedThroughputAiGatewayUsageTrackingConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingProvisionedThroughputAiGatewayUsageTrackingConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputAiGatewayUsageTrackingConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3374ad46a5fd6eaa5baf7adf9a41300f6ab7bee2c376434ff6c5e5b846d29b2b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__e02712d487a054eb45334ceb2ccf72e475961042c2f253fd7069819198fabb20)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingProvisionedThroughputAiGatewayUsageTrackingConfig]:
        return typing.cast(typing.Optional[ModelServingProvisionedThroughputAiGatewayUsageTrackingConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingProvisionedThroughputAiGatewayUsageTrackingConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e494bb61dd810dfe310475ba5a73047f7b0f5aad131723f298402b8f0a26f952)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "config": "config",
        "name": "name",
        "ai_gateway": "aiGateway",
        "budget_policy_id": "budgetPolicyId",
        "email_notifications": "emailNotifications",
        "id": "id",
        "tags": "tags",
        "timeouts": "timeouts",
    },
)
class ModelServingProvisionedThroughputConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        config: typing.Union["ModelServingProvisionedThroughputConfigA", typing.Dict[builtins.str, typing.Any]],
        name: builtins.str,
        ai_gateway: typing.Optional[typing.Union[ModelServingProvisionedThroughputAiGateway, typing.Dict[builtins.str, typing.Any]]] = None,
        budget_policy_id: typing.Optional[builtins.str] = None,
        email_notifications: typing.Optional[typing.Union["ModelServingProvisionedThroughputEmailNotifications", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingProvisionedThroughputTags", typing.Dict[builtins.str, typing.Any]]]]] = None,
        timeouts: typing.Optional[typing.Union["ModelServingProvisionedThroughputTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param config: config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#config ModelServingProvisionedThroughput#config}
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#name ModelServingProvisionedThroughput#name}.
        :param ai_gateway: ai_gateway block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#ai_gateway ModelServingProvisionedThroughput#ai_gateway}
        :param budget_policy_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#budget_policy_id ModelServingProvisionedThroughput#budget_policy_id}.
        :param email_notifications: email_notifications block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#email_notifications ModelServingProvisionedThroughput#email_notifications}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#id ModelServingProvisionedThroughput#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: tags block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#tags ModelServingProvisionedThroughput#tags}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#timeouts ModelServingProvisionedThroughput#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(config, dict):
            config = ModelServingProvisionedThroughputConfigA(**config)
        if isinstance(ai_gateway, dict):
            ai_gateway = ModelServingProvisionedThroughputAiGateway(**ai_gateway)
        if isinstance(email_notifications, dict):
            email_notifications = ModelServingProvisionedThroughputEmailNotifications(**email_notifications)
        if isinstance(timeouts, dict):
            timeouts = ModelServingProvisionedThroughputTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb5a0ca550c7cc11c2fc55dac1fc51c9d2bcf317bd40c5fce052cd4f94fe241a)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument config", value=config, expected_type=type_hints["config"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument ai_gateway", value=ai_gateway, expected_type=type_hints["ai_gateway"])
            check_type(argname="argument budget_policy_id", value=budget_policy_id, expected_type=type_hints["budget_policy_id"])
            check_type(argname="argument email_notifications", value=email_notifications, expected_type=type_hints["email_notifications"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "config": config,
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
        if ai_gateway is not None:
            self._values["ai_gateway"] = ai_gateway
        if budget_policy_id is not None:
            self._values["budget_policy_id"] = budget_policy_id
        if email_notifications is not None:
            self._values["email_notifications"] = email_notifications
        if id is not None:
            self._values["id"] = id
        if tags is not None:
            self._values["tags"] = tags
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
    def config(self) -> "ModelServingProvisionedThroughputConfigA":
        '''config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#config ModelServingProvisionedThroughput#config}
        '''
        result = self._values.get("config")
        assert result is not None, "Required property 'config' is missing"
        return typing.cast("ModelServingProvisionedThroughputConfigA", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#name ModelServingProvisionedThroughput#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ai_gateway(self) -> typing.Optional[ModelServingProvisionedThroughputAiGateway]:
        '''ai_gateway block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#ai_gateway ModelServingProvisionedThroughput#ai_gateway}
        '''
        result = self._values.get("ai_gateway")
        return typing.cast(typing.Optional[ModelServingProvisionedThroughputAiGateway], result)

    @builtins.property
    def budget_policy_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#budget_policy_id ModelServingProvisionedThroughput#budget_policy_id}.'''
        result = self._values.get("budget_policy_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_notifications(
        self,
    ) -> typing.Optional["ModelServingProvisionedThroughputEmailNotifications"]:
        '''email_notifications block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#email_notifications ModelServingProvisionedThroughput#email_notifications}
        '''
        result = self._values.get("email_notifications")
        return typing.cast(typing.Optional["ModelServingProvisionedThroughputEmailNotifications"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#id ModelServingProvisionedThroughput#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingProvisionedThroughputTags"]]]:
        '''tags block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#tags ModelServingProvisionedThroughput#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingProvisionedThroughputTags"]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["ModelServingProvisionedThroughputTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#timeouts ModelServingProvisionedThroughput#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["ModelServingProvisionedThroughputTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingProvisionedThroughputConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputConfigA",
    jsii_struct_bases=[],
    name_mapping={
        "served_entities": "servedEntities",
        "traffic_config": "trafficConfig",
    },
)
class ModelServingProvisionedThroughputConfigA:
    def __init__(
        self,
        *,
        served_entities: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingProvisionedThroughputConfigServedEntities", typing.Dict[builtins.str, typing.Any]]]]] = None,
        traffic_config: typing.Optional[typing.Union["ModelServingProvisionedThroughputConfigTrafficConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param served_entities: served_entities block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#served_entities ModelServingProvisionedThroughput#served_entities}
        :param traffic_config: traffic_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#traffic_config ModelServingProvisionedThroughput#traffic_config}
        '''
        if isinstance(traffic_config, dict):
            traffic_config = ModelServingProvisionedThroughputConfigTrafficConfig(**traffic_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe30232b9ae3d20bc23b44bdec2f68557bdb0ceeeaab5e4d8a07724fb5443421)
            check_type(argname="argument served_entities", value=served_entities, expected_type=type_hints["served_entities"])
            check_type(argname="argument traffic_config", value=traffic_config, expected_type=type_hints["traffic_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if served_entities is not None:
            self._values["served_entities"] = served_entities
        if traffic_config is not None:
            self._values["traffic_config"] = traffic_config

    @builtins.property
    def served_entities(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingProvisionedThroughputConfigServedEntities"]]]:
        '''served_entities block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#served_entities ModelServingProvisionedThroughput#served_entities}
        '''
        result = self._values.get("served_entities")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingProvisionedThroughputConfigServedEntities"]]], result)

    @builtins.property
    def traffic_config(
        self,
    ) -> typing.Optional["ModelServingProvisionedThroughputConfigTrafficConfig"]:
        '''traffic_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#traffic_config ModelServingProvisionedThroughput#traffic_config}
        '''
        result = self._values.get("traffic_config")
        return typing.cast(typing.Optional["ModelServingProvisionedThroughputConfigTrafficConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingProvisionedThroughputConfigA(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingProvisionedThroughputConfigAOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputConfigAOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__af5f32ef5bc6b463e7170ee4991eb8a6a1dc258b56e626cccad29221747384ba)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putServedEntities")
    def put_served_entities(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingProvisionedThroughputConfigServedEntities", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd56f3a45d13388574f0d030791bcbf6e5373e02199bbf0b7e1034c510c743ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putServedEntities", [value]))

    @jsii.member(jsii_name="putTrafficConfig")
    def put_traffic_config(
        self,
        *,
        routes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingProvisionedThroughputConfigTrafficConfigRoutes", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param routes: routes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#routes ModelServingProvisionedThroughput#routes}
        '''
        value = ModelServingProvisionedThroughputConfigTrafficConfig(routes=routes)

        return typing.cast(None, jsii.invoke(self, "putTrafficConfig", [value]))

    @jsii.member(jsii_name="resetServedEntities")
    def reset_served_entities(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServedEntities", []))

    @jsii.member(jsii_name="resetTrafficConfig")
    def reset_traffic_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTrafficConfig", []))

    @builtins.property
    @jsii.member(jsii_name="servedEntities")
    def served_entities(
        self,
    ) -> "ModelServingProvisionedThroughputConfigServedEntitiesList":
        return typing.cast("ModelServingProvisionedThroughputConfigServedEntitiesList", jsii.get(self, "servedEntities"))

    @builtins.property
    @jsii.member(jsii_name="trafficConfig")
    def traffic_config(
        self,
    ) -> "ModelServingProvisionedThroughputConfigTrafficConfigOutputReference":
        return typing.cast("ModelServingProvisionedThroughputConfigTrafficConfigOutputReference", jsii.get(self, "trafficConfig"))

    @builtins.property
    @jsii.member(jsii_name="servedEntitiesInput")
    def served_entities_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingProvisionedThroughputConfigServedEntities"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingProvisionedThroughputConfigServedEntities"]]], jsii.get(self, "servedEntitiesInput"))

    @builtins.property
    @jsii.member(jsii_name="trafficConfigInput")
    def traffic_config_input(
        self,
    ) -> typing.Optional["ModelServingProvisionedThroughputConfigTrafficConfig"]:
        return typing.cast(typing.Optional["ModelServingProvisionedThroughputConfigTrafficConfig"], jsii.get(self, "trafficConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingProvisionedThroughputConfigA]:
        return typing.cast(typing.Optional[ModelServingProvisionedThroughputConfigA], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingProvisionedThroughputConfigA],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbce8f46c4559e3e0c400a2dc78ef88644699d012753ee396bb12d4c208fac4c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputConfigServedEntities",
    jsii_struct_bases=[],
    name_mapping={
        "entity_name": "entityName",
        "entity_version": "entityVersion",
        "provisioned_model_units": "provisionedModelUnits",
        "name": "name",
    },
)
class ModelServingProvisionedThroughputConfigServedEntities:
    def __init__(
        self,
        *,
        entity_name: builtins.str,
        entity_version: builtins.str,
        provisioned_model_units: jsii.Number,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param entity_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#entity_name ModelServingProvisionedThroughput#entity_name}.
        :param entity_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#entity_version ModelServingProvisionedThroughput#entity_version}.
        :param provisioned_model_units: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#provisioned_model_units ModelServingProvisionedThroughput#provisioned_model_units}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#name ModelServingProvisionedThroughput#name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__245fb0ce67430590ea7ffa416e51461fb03fc9523b0a65e542a90369290209a4)
            check_type(argname="argument entity_name", value=entity_name, expected_type=type_hints["entity_name"])
            check_type(argname="argument entity_version", value=entity_version, expected_type=type_hints["entity_version"])
            check_type(argname="argument provisioned_model_units", value=provisioned_model_units, expected_type=type_hints["provisioned_model_units"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "entity_name": entity_name,
            "entity_version": entity_version,
            "provisioned_model_units": provisioned_model_units,
        }
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def entity_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#entity_name ModelServingProvisionedThroughput#entity_name}.'''
        result = self._values.get("entity_name")
        assert result is not None, "Required property 'entity_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def entity_version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#entity_version ModelServingProvisionedThroughput#entity_version}.'''
        result = self._values.get("entity_version")
        assert result is not None, "Required property 'entity_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def provisioned_model_units(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#provisioned_model_units ModelServingProvisionedThroughput#provisioned_model_units}.'''
        result = self._values.get("provisioned_model_units")
        assert result is not None, "Required property 'provisioned_model_units' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#name ModelServingProvisionedThroughput#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingProvisionedThroughputConfigServedEntities(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingProvisionedThroughputConfigServedEntitiesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputConfigServedEntitiesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__010bd3861333dfd8c69ece840911f2a54c31b8bd194838cba885fcef38a6037e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ModelServingProvisionedThroughputConfigServedEntitiesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8b98b22956ef8b04323b6ed99f42c45cc0a1369a469b3cc0e9db3103ef0b15f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ModelServingProvisionedThroughputConfigServedEntitiesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55c522a74b488cf8d4658f568bd8304a97980f7efe048a1cfa4960ba95457d58)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7dc4970d45167b70bf1693905cc9285d9e9b8fecf69955e40016b50c4d111ca6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7dc0593a79645aee2f5b4381f046cd1ea9eef39191d5bc28acd9a9614a09b820)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingProvisionedThroughputConfigServedEntities]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingProvisionedThroughputConfigServedEntities]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingProvisionedThroughputConfigServedEntities]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9be129c9d0a674d924a49c59a494024cdc5a75c22be60ad287d6b0ef0e19212e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ModelServingProvisionedThroughputConfigServedEntitiesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputConfigServedEntitiesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7ebbc72841c4bf9327c7914d2276076a6109d402720d9070331b03a60ad9d5e2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @builtins.property
    @jsii.member(jsii_name="entityNameInput")
    def entity_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "entityNameInput"))

    @builtins.property
    @jsii.member(jsii_name="entityVersionInput")
    def entity_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "entityVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="provisionedModelUnitsInput")
    def provisioned_model_units_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "provisionedModelUnitsInput"))

    @builtins.property
    @jsii.member(jsii_name="entityName")
    def entity_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "entityName"))

    @entity_name.setter
    def entity_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17326be681995b21969129fb68af1352b121a60d688fda4f74e514c794bcfbab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "entityName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="entityVersion")
    def entity_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "entityVersion"))

    @entity_version.setter
    def entity_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dec412b8d99a642679c46c5e8a799569fa89245ac1009f473f368ef7ce1082bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "entityVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a43b0c93918935a4c9a89af21c571394094e01d85221e9da812ac89b68ccf35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="provisionedModelUnits")
    def provisioned_model_units(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "provisionedModelUnits"))

    @provisioned_model_units.setter
    def provisioned_model_units(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4059c3b969dc0e13e1dcee05811f8059f95df961c920d94ad78bca7a09c8eea9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "provisionedModelUnits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingProvisionedThroughputConfigServedEntities]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingProvisionedThroughputConfigServedEntities]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingProvisionedThroughputConfigServedEntities]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95945133d0fdcae60045c84555952700861d3c7df5bb4ce0d844d90f511511d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputConfigTrafficConfig",
    jsii_struct_bases=[],
    name_mapping={"routes": "routes"},
)
class ModelServingProvisionedThroughputConfigTrafficConfig:
    def __init__(
        self,
        *,
        routes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingProvisionedThroughputConfigTrafficConfigRoutes", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param routes: routes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#routes ModelServingProvisionedThroughput#routes}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21a038814a143819bfd6e0b790b0cc2afb73a3f6152b9630e11bdecedddc1d04)
            check_type(argname="argument routes", value=routes, expected_type=type_hints["routes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if routes is not None:
            self._values["routes"] = routes

    @builtins.property
    def routes(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingProvisionedThroughputConfigTrafficConfigRoutes"]]]:
        '''routes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#routes ModelServingProvisionedThroughput#routes}
        '''
        result = self._values.get("routes")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingProvisionedThroughputConfigTrafficConfigRoutes"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingProvisionedThroughputConfigTrafficConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingProvisionedThroughputConfigTrafficConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputConfigTrafficConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__38399d0c293304edb136bd318932f130db7eaf9975ab82a35e5da37fe939c193)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putRoutes")
    def put_routes(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingProvisionedThroughputConfigTrafficConfigRoutes", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__552b6d545349e39a4cf28b3c4b042eab262cce1b6a7e5666cb215a62e269ba63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRoutes", [value]))

    @jsii.member(jsii_name="resetRoutes")
    def reset_routes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoutes", []))

    @builtins.property
    @jsii.member(jsii_name="routes")
    def routes(
        self,
    ) -> "ModelServingProvisionedThroughputConfigTrafficConfigRoutesList":
        return typing.cast("ModelServingProvisionedThroughputConfigTrafficConfigRoutesList", jsii.get(self, "routes"))

    @builtins.property
    @jsii.member(jsii_name="routesInput")
    def routes_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingProvisionedThroughputConfigTrafficConfigRoutes"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingProvisionedThroughputConfigTrafficConfigRoutes"]]], jsii.get(self, "routesInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingProvisionedThroughputConfigTrafficConfig]:
        return typing.cast(typing.Optional[ModelServingProvisionedThroughputConfigTrafficConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingProvisionedThroughputConfigTrafficConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6751039f8620377e63b05c5cd009754c16385bf4302e1e7067d6aa09aef79730)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputConfigTrafficConfigRoutes",
    jsii_struct_bases=[],
    name_mapping={
        "traffic_percentage": "trafficPercentage",
        "served_entity_name": "servedEntityName",
        "served_model_name": "servedModelName",
    },
)
class ModelServingProvisionedThroughputConfigTrafficConfigRoutes:
    def __init__(
        self,
        *,
        traffic_percentage: jsii.Number,
        served_entity_name: typing.Optional[builtins.str] = None,
        served_model_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param traffic_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#traffic_percentage ModelServingProvisionedThroughput#traffic_percentage}.
        :param served_entity_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#served_entity_name ModelServingProvisionedThroughput#served_entity_name}.
        :param served_model_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#served_model_name ModelServingProvisionedThroughput#served_model_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c7b1c9fab3de032527d812a6fdef2688ddff8d9abb0b03dca3aa6635b74a7e1)
            check_type(argname="argument traffic_percentage", value=traffic_percentage, expected_type=type_hints["traffic_percentage"])
            check_type(argname="argument served_entity_name", value=served_entity_name, expected_type=type_hints["served_entity_name"])
            check_type(argname="argument served_model_name", value=served_model_name, expected_type=type_hints["served_model_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "traffic_percentage": traffic_percentage,
        }
        if served_entity_name is not None:
            self._values["served_entity_name"] = served_entity_name
        if served_model_name is not None:
            self._values["served_model_name"] = served_model_name

    @builtins.property
    def traffic_percentage(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#traffic_percentage ModelServingProvisionedThroughput#traffic_percentage}.'''
        result = self._values.get("traffic_percentage")
        assert result is not None, "Required property 'traffic_percentage' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def served_entity_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#served_entity_name ModelServingProvisionedThroughput#served_entity_name}.'''
        result = self._values.get("served_entity_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def served_model_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#served_model_name ModelServingProvisionedThroughput#served_model_name}.'''
        result = self._values.get("served_model_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingProvisionedThroughputConfigTrafficConfigRoutes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingProvisionedThroughputConfigTrafficConfigRoutesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputConfigTrafficConfigRoutesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b34830bce44e9836c24e12a83f71e26f02bd43c695ba21fb972e9d9ba8b8d63a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ModelServingProvisionedThroughputConfigTrafficConfigRoutesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88c0fcb339252152f7b6ff62339ef5ab984f56169247e9897f97fc87954bc589)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ModelServingProvisionedThroughputConfigTrafficConfigRoutesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbe976b34a31852a7bf356c948d2664f86b1712929a60c253fdfbcc87e98f404)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4733ea8767c1c9489c0cefe2d59e8e4bef25f2dd7950442ec657f1333746e74e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__53d935a55457f26eb38ee450d6255a7181ce7a38309ed753b64d10c7b4f85ab4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingProvisionedThroughputConfigTrafficConfigRoutes]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingProvisionedThroughputConfigTrafficConfigRoutes]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingProvisionedThroughputConfigTrafficConfigRoutes]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0b03a782c4c8b4204bfca06a638adfb58b3cd760c5e30e2aed1ce245ba42aeb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ModelServingProvisionedThroughputConfigTrafficConfigRoutesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputConfigTrafficConfigRoutesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__35ca3ad7f47a8198454223f5de5ef703ca0432998718f59cc7f5b2c78895104b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetServedEntityName")
    def reset_served_entity_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServedEntityName", []))

    @jsii.member(jsii_name="resetServedModelName")
    def reset_served_model_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServedModelName", []))

    @builtins.property
    @jsii.member(jsii_name="servedEntityNameInput")
    def served_entity_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "servedEntityNameInput"))

    @builtins.property
    @jsii.member(jsii_name="servedModelNameInput")
    def served_model_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "servedModelNameInput"))

    @builtins.property
    @jsii.member(jsii_name="trafficPercentageInput")
    def traffic_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "trafficPercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="servedEntityName")
    def served_entity_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "servedEntityName"))

    @served_entity_name.setter
    def served_entity_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e57419c6d26eef8c6d564f941dd8ac6171620683392884b35d2514770d83bcbd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "servedEntityName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="servedModelName")
    def served_model_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "servedModelName"))

    @served_model_name.setter
    def served_model_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5c3329bc73b41fe2cb280b980323d2e9ad679a841d65e44c437b519d9d0f1be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "servedModelName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="trafficPercentage")
    def traffic_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "trafficPercentage"))

    @traffic_percentage.setter
    def traffic_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b4df19610fc3a29c54500b1427afb082f9b049131e9fa6c507354ddfa0a64ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "trafficPercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingProvisionedThroughputConfigTrafficConfigRoutes]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingProvisionedThroughputConfigTrafficConfigRoutes]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingProvisionedThroughputConfigTrafficConfigRoutes]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7778335f3c3afc5b1334c9d2384497d8a376d872b67dc6bb6e53ca693341b9ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputEmailNotifications",
    jsii_struct_bases=[],
    name_mapping={
        "on_update_failure": "onUpdateFailure",
        "on_update_success": "onUpdateSuccess",
    },
)
class ModelServingProvisionedThroughputEmailNotifications:
    def __init__(
        self,
        *,
        on_update_failure: typing.Optional[typing.Sequence[builtins.str]] = None,
        on_update_success: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param on_update_failure: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#on_update_failure ModelServingProvisionedThroughput#on_update_failure}.
        :param on_update_success: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#on_update_success ModelServingProvisionedThroughput#on_update_success}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8f97b4b969843ac1da1abcafa24706923091f81731b21e08f569c571614e7d1)
            check_type(argname="argument on_update_failure", value=on_update_failure, expected_type=type_hints["on_update_failure"])
            check_type(argname="argument on_update_success", value=on_update_success, expected_type=type_hints["on_update_success"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if on_update_failure is not None:
            self._values["on_update_failure"] = on_update_failure
        if on_update_success is not None:
            self._values["on_update_success"] = on_update_success

    @builtins.property
    def on_update_failure(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#on_update_failure ModelServingProvisionedThroughput#on_update_failure}.'''
        result = self._values.get("on_update_failure")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def on_update_success(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#on_update_success ModelServingProvisionedThroughput#on_update_success}.'''
        result = self._values.get("on_update_success")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingProvisionedThroughputEmailNotifications(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingProvisionedThroughputEmailNotificationsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputEmailNotificationsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c1c9aa325158307b64db7aaaced8369badd769b16b10a5445c78f00de176507a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetOnUpdateFailure")
    def reset_on_update_failure(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnUpdateFailure", []))

    @jsii.member(jsii_name="resetOnUpdateSuccess")
    def reset_on_update_success(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnUpdateSuccess", []))

    @builtins.property
    @jsii.member(jsii_name="onUpdateFailureInput")
    def on_update_failure_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "onUpdateFailureInput"))

    @builtins.property
    @jsii.member(jsii_name="onUpdateSuccessInput")
    def on_update_success_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "onUpdateSuccessInput"))

    @builtins.property
    @jsii.member(jsii_name="onUpdateFailure")
    def on_update_failure(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "onUpdateFailure"))

    @on_update_failure.setter
    def on_update_failure(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d8acfd88f129fa4fe6fb930a5c730c84748ddc76915c274b59a0a60629c6bb3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onUpdateFailure", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="onUpdateSuccess")
    def on_update_success(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "onUpdateSuccess"))

    @on_update_success.setter
    def on_update_success(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ae521720b4853406805759597ad8f8cd2932cf90b19f3ca5a3c08fa4504d2c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onUpdateSuccess", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingProvisionedThroughputEmailNotifications]:
        return typing.cast(typing.Optional[ModelServingProvisionedThroughputEmailNotifications], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingProvisionedThroughputEmailNotifications],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94c664bf47aa7d51880695166aa140ff0288b346fc23431e5958783f8810553f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputTags",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class ModelServingProvisionedThroughputTags:
    def __init__(
        self,
        *,
        key: builtins.str,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#key ModelServingProvisionedThroughput#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#value ModelServingProvisionedThroughput#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__115f09f316262ee893f8d03df96eb866bcf7e6ae3b92f0c118bf6802591eebef)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
        }
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#key ModelServingProvisionedThroughput#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#value ModelServingProvisionedThroughput#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingProvisionedThroughputTags(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingProvisionedThroughputTagsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputTagsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0775c2288d607e8e5972c51bd4e85a156fefd9128c584cc36fed473c60327d4f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ModelServingProvisionedThroughputTagsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6534e6b67bf2ed2e5cb9847fbd8fb3aba6436c568483172676e118c531aa3205)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ModelServingProvisionedThroughputTagsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d40e911b039d06d0cc8b93ba10e320e3216c43d4848bea8951a6df5c2722d22)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b2d084c6cae8a509f499acd198aa2b010b6a02f6576d3e1d7e10495363a62a44)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8490887bcf4e42d60d3902994aa537ecbe53e289b2f9db7b3f49b7f9135a59cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingProvisionedThroughputTags]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingProvisionedThroughputTags]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingProvisionedThroughputTags]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24bd6e0ca426f2e6b276e69f3a97278f126be77924e4a356eaa6bcb4b4113201)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ModelServingProvisionedThroughputTagsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputTagsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__02c922556682b7c1f63cbb79d81b8920042ab417544d350c76b4b9d806f81b8f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f45f93ff3a89b68a6cd07df66dad8f27233a5675a116632054407150088fffa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10af19d7e933830361b36745829dd04115566510ab2a8d5fc5a781bb3dd1f97d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingProvisionedThroughputTags]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingProvisionedThroughputTags]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingProvisionedThroughputTags]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5e1f9714d13c762a8eb880bbde71c01f0341581a4ffd510952bad63402d01c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "update": "update"},
)
class ModelServingProvisionedThroughputTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#create ModelServingProvisionedThroughput#create}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#update ModelServingProvisionedThroughput#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7438ec9c625f571f7ef6d704dd0c6811dc14b713f34b9237d4dc13293aec825)
            check_type(argname="argument create", value=create, expected_type=type_hints["create"])
            check_type(argname="argument update", value=update, expected_type=type_hints["update"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#create ModelServingProvisionedThroughput#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving_provisioned_throughput#update ModelServingProvisionedThroughput#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingProvisionedThroughputTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingProvisionedThroughputTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServingProvisionedThroughput.ModelServingProvisionedThroughputTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7f0e118b76371a92d3a8ab91254b71a10c7b82d2764d605ceb637723e2a755f0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc0ce933eec038464352ff36e56c5db89a4eb817bedd2a7fa5d7b716478446d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3646c66e0617ec57eab48ceb2f502cc575028a6d0e7e0d241907597db9970ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingProvisionedThroughputTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingProvisionedThroughputTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingProvisionedThroughputTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5eecb588f81bd51f05c617bcfb76d0c6aa8e5b5e0a36c8d1097951dfb044e61)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ModelServingProvisionedThroughput",
    "ModelServingProvisionedThroughputAiGateway",
    "ModelServingProvisionedThroughputAiGatewayFallbackConfig",
    "ModelServingProvisionedThroughputAiGatewayFallbackConfigOutputReference",
    "ModelServingProvisionedThroughputAiGatewayGuardrails",
    "ModelServingProvisionedThroughputAiGatewayGuardrailsInput",
    "ModelServingProvisionedThroughputAiGatewayGuardrailsInputOutputReference",
    "ModelServingProvisionedThroughputAiGatewayGuardrailsInputPii",
    "ModelServingProvisionedThroughputAiGatewayGuardrailsInputPiiOutputReference",
    "ModelServingProvisionedThroughputAiGatewayGuardrailsOutput",
    "ModelServingProvisionedThroughputAiGatewayGuardrailsOutputOutputReference",
    "ModelServingProvisionedThroughputAiGatewayGuardrailsOutputPii",
    "ModelServingProvisionedThroughputAiGatewayGuardrailsOutputPiiOutputReference",
    "ModelServingProvisionedThroughputAiGatewayGuardrailsOutputReference",
    "ModelServingProvisionedThroughputAiGatewayInferenceTableConfig",
    "ModelServingProvisionedThroughputAiGatewayInferenceTableConfigOutputReference",
    "ModelServingProvisionedThroughputAiGatewayOutputReference",
    "ModelServingProvisionedThroughputAiGatewayRateLimits",
    "ModelServingProvisionedThroughputAiGatewayRateLimitsList",
    "ModelServingProvisionedThroughputAiGatewayRateLimitsOutputReference",
    "ModelServingProvisionedThroughputAiGatewayUsageTrackingConfig",
    "ModelServingProvisionedThroughputAiGatewayUsageTrackingConfigOutputReference",
    "ModelServingProvisionedThroughputConfig",
    "ModelServingProvisionedThroughputConfigA",
    "ModelServingProvisionedThroughputConfigAOutputReference",
    "ModelServingProvisionedThroughputConfigServedEntities",
    "ModelServingProvisionedThroughputConfigServedEntitiesList",
    "ModelServingProvisionedThroughputConfigServedEntitiesOutputReference",
    "ModelServingProvisionedThroughputConfigTrafficConfig",
    "ModelServingProvisionedThroughputConfigTrafficConfigOutputReference",
    "ModelServingProvisionedThroughputConfigTrafficConfigRoutes",
    "ModelServingProvisionedThroughputConfigTrafficConfigRoutesList",
    "ModelServingProvisionedThroughputConfigTrafficConfigRoutesOutputReference",
    "ModelServingProvisionedThroughputEmailNotifications",
    "ModelServingProvisionedThroughputEmailNotificationsOutputReference",
    "ModelServingProvisionedThroughputTags",
    "ModelServingProvisionedThroughputTagsList",
    "ModelServingProvisionedThroughputTagsOutputReference",
    "ModelServingProvisionedThroughputTimeouts",
    "ModelServingProvisionedThroughputTimeoutsOutputReference",
]

publication.publish()

def _typecheckingstub__112dca9c8a5ee404308b6da0984bdb5bf6259bbdc06c5dd75c2c280a18d1bcfa(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    config: typing.Union[ModelServingProvisionedThroughputConfigA, typing.Dict[builtins.str, typing.Any]],
    name: builtins.str,
    ai_gateway: typing.Optional[typing.Union[ModelServingProvisionedThroughputAiGateway, typing.Dict[builtins.str, typing.Any]]] = None,
    budget_policy_id: typing.Optional[builtins.str] = None,
    email_notifications: typing.Optional[typing.Union[ModelServingProvisionedThroughputEmailNotifications, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingProvisionedThroughputTags, typing.Dict[builtins.str, typing.Any]]]]] = None,
    timeouts: typing.Optional[typing.Union[ModelServingProvisionedThroughputTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__3783c812dc1e71498e65b7c7100777920a7373c92de1095dd3ce449412b82bf4(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22b78850ab944ac8770090026265326bc0ab3a02a842bb2771dd07aef049c21b(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingProvisionedThroughputTags, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef1d8dc57f16f03551e82268b5b506188e96055739eee77f32ad61ee3dd7cf86(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e247134aad1103266f297c9eba06b8f9b1bb63cf81f77153bf7a580c1ae552a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8a0faf611a704639d749c142bd3f79c3f64157e33fb86d5b495a2d9e798d2a8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3472bc1584d927826567d82772b591c10c727a87612bfc8f13835de910c332c8(
    *,
    fallback_config: typing.Optional[typing.Union[ModelServingProvisionedThroughputAiGatewayFallbackConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    guardrails: typing.Optional[typing.Union[ModelServingProvisionedThroughputAiGatewayGuardrails, typing.Dict[builtins.str, typing.Any]]] = None,
    inference_table_config: typing.Optional[typing.Union[ModelServingProvisionedThroughputAiGatewayInferenceTableConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    rate_limits: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingProvisionedThroughputAiGatewayRateLimits, typing.Dict[builtins.str, typing.Any]]]]] = None,
    usage_tracking_config: typing.Optional[typing.Union[ModelServingProvisionedThroughputAiGatewayUsageTrackingConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eef49a07c6162f167aef128e026eccb2257f1eca34b837f17d361a5162c5955b(
    *,
    enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2be6308f5572c0e1b0d30f4c1e80bd36bae310dca4772d2030c2994e5ca99ddd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3ef7e624a131d3b149c530b8d071e0972b918963fa40bd39ff75ad0d7723e2a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__119321bd7f2533b70749178bcefe56ce2132f470adad70627844b9808ccb8f12(
    value: typing.Optional[ModelServingProvisionedThroughputAiGatewayFallbackConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b175c019629ad28730b52085bb2815f7be0a3bf90b1a2042c182f57fa3e192e8(
    *,
    input: typing.Optional[typing.Union[ModelServingProvisionedThroughputAiGatewayGuardrailsInput, typing.Dict[builtins.str, typing.Any]]] = None,
    output: typing.Optional[typing.Union[ModelServingProvisionedThroughputAiGatewayGuardrailsOutput, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c74a9be870b4a4b5abb2f2d6d02110d63b0cf9b8e9d2ebc887e5299dae241605(
    *,
    invalid_keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
    pii: typing.Optional[typing.Union[ModelServingProvisionedThroughputAiGatewayGuardrailsInputPii, typing.Dict[builtins.str, typing.Any]]] = None,
    safety: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    valid_topics: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__678627d51503d74e8010a809f47fe697afc68bf099aabed5ee2aa38f178afde9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__883cc28d2c98b874ad47d7b0a636aee9d8f16dbf66c7ef0a25742719b4ccfb01(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e7e9b0e0f5d32b6e3e00ae6330119b9b8471ce02c1995d954642b47472c2bae(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__913fb0dc0a9e813e00afdbbd5bbf5fba3ee3e3ef3c4565af6c40c5d7170182ab(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3025ba60fca46216294354db3a1e2f3577fc432906d416c261262a2c72a8a918(
    value: typing.Optional[ModelServingProvisionedThroughputAiGatewayGuardrailsInput],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbf4523f5c16759fbe30165a97751fa11cc2773679bfae50a0fe3c414a3baad9(
    *,
    behavior: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f24a990b7bccf8ae268a8347012c1a6cc8de1e92c34c856c911d54031d6b623(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afc972c094502ea4a4700843165ff2d8d02ad06633e40002b4d25d87f0031582(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36be8c9f6ba4baad5ff5eee13699f8b4d9fbc7d168c9fab3d56b894fccc4ed54(
    value: typing.Optional[ModelServingProvisionedThroughputAiGatewayGuardrailsInputPii],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9efbda3bba53a205f1c2dfe3947a94bd44bc6d9e1e4fae0137c1492d7da832f5(
    *,
    invalid_keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
    pii: typing.Optional[typing.Union[ModelServingProvisionedThroughputAiGatewayGuardrailsOutputPii, typing.Dict[builtins.str, typing.Any]]] = None,
    safety: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    valid_topics: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66dacf958f6985937c4e78f88c6de331a05184d02a578643f52540f6a622683c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8612ecc53c7136048dd23b5e7e16a98ab61b7f6f042d69663e5253720cab2f4c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e21c54eaff145763f8f9bd29ed35afe8bc411e7c1cb4ffb9242233c0a81c5fe8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c1e736eedd5b71a9c6b7f701a0dd11ea70e1737c048535b91df2e5ba3c8489a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f13b4db6467954d4dc511acb317e0f2583c1c3209b4dd01efd72517a6c2459f5(
    value: typing.Optional[ModelServingProvisionedThroughputAiGatewayGuardrailsOutput],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c651aa5d572d1a984dec51d9eaf1d4f9856eb9b362c6982bcc375568159a14f7(
    *,
    behavior: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55386120ac6bc16269cc72b17d0fc878622067c4acbde3947474501bc5c1412c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b8482105600c77f643d2de617d9051363d5657f244bb34589fd77d86b61eecf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93250e2d87acb703b631a3e45d19b0cd543f02bc309e67039a472ad61981fd78(
    value: typing.Optional[ModelServingProvisionedThroughputAiGatewayGuardrailsOutputPii],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95e0b494d82ea1b6856b33d74c0897f4c0804bfe6750bccebfbd16ec109c12bd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31ee10b8ace32136ea4a9022e7ce15bada11fc2ae78221a806078a298117bafc(
    value: typing.Optional[ModelServingProvisionedThroughputAiGatewayGuardrails],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfcb764f756555c70ef53a076a07828a3ab78f2ecb001b66597c8ce5e87cdcef(
    *,
    catalog_name: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    schema_name: typing.Optional[builtins.str] = None,
    table_name_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__056354db4ede85f34d8c7148ede89fec9784feece25f279d99a283142eb3edf7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f171967a9a57f04e34da42063151f3275d44f35f23c5ab56b365ba116f2e21d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__728e38b0fe291f325ada2319bf24b3127adec6239c34b9250486572d3cbd982b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ab77d4ac8e744e54d127900481e838393d342ae82a502fcbfef8e4edfa8caa4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4492cce97ae8f169d3162a423f09791b5ca5d4fbcf54d579deb01b7261b9cf26(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcc16043366883ace9a512c51f0d2c3dcc6350f58217d442a6ff151bc003b434(
    value: typing.Optional[ModelServingProvisionedThroughputAiGatewayInferenceTableConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d8cc3a0f7f4513a1b6339024dc20e4ffb56b7247ef3b053f03a32ed9f7a99c6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9bb2a72ad01e65c9b9effa4f8dc8de5d7e02ae895a3eb236de3fdaac219fa0d(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingProvisionedThroughputAiGatewayRateLimits, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3cd29adb040f2763877a6625c4411c25787f5e1c07104abd56e10add9df6def(
    value: typing.Optional[ModelServingProvisionedThroughputAiGateway],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2756476e14a22a6371ecce8619e59b2716b91e838a442a4d92e536b15adb534c(
    *,
    renewal_period: builtins.str,
    calls: typing.Optional[jsii.Number] = None,
    key: typing.Optional[builtins.str] = None,
    principal: typing.Optional[builtins.str] = None,
    tokens: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ddd49328e744f3bed48cb0c26bd86386608b8dd35d97e52acb6676a61a8323e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b2a10f6eaa450651b05a1b097fbf2b5555ce402bd8c003593530dcb703138b0(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13c508725bcc50186a33388144851b4b3271ea4f2557f22e07dabc4bf606d265(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa9b7e380f2c4b0fc1662b8c2dc88909b82fcba482756b2c0d4a366309a87481(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__065630854dc20859d93bb263a95eae4402f887e6f38a3c60211cda0ee4849c18(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b7d4520eb2abb2b9258a68dcf956fd1b141d6336ac4c25bb0adae673aa8b002(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingProvisionedThroughputAiGatewayRateLimits]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b311d194a26ebe882bc8067f6617001075194600f86b966f9b2b304063f46d08(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5124cd70a8e1b221060f467ae5644edf6af4c31738bf574045ade7eb6dacb256(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03f53ce4212a778690f264da5ef6e482fa55a5b8fa5cb714785f3ebfb0671f47(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00d3226ea359ae01a46172167787b51c16a83f1bc3d9797a2249ef2e6c3bc5ae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cf0f4fbd1f53a528b5a26da5328d72d7b87d7c855c55c6078fbf601df8ca241(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0624ff9d20f7dbbbc00309f14d448dae58701f97ae9ab606a31eaf0071f2bc04(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8380a434f4dbfa8f6ef73de9cac727c3ac28abbb0f25c69f201ce9aa8dd2ae7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingProvisionedThroughputAiGatewayRateLimits]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36954b179830ac10c83b8990174f021dad0f0267f7be18c3b43f4768890f1b2b(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3374ad46a5fd6eaa5baf7adf9a41300f6ab7bee2c376434ff6c5e5b846d29b2b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e02712d487a054eb45334ceb2ccf72e475961042c2f253fd7069819198fabb20(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e494bb61dd810dfe310475ba5a73047f7b0f5aad131723f298402b8f0a26f952(
    value: typing.Optional[ModelServingProvisionedThroughputAiGatewayUsageTrackingConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb5a0ca550c7cc11c2fc55dac1fc51c9d2bcf317bd40c5fce052cd4f94fe241a(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    config: typing.Union[ModelServingProvisionedThroughputConfigA, typing.Dict[builtins.str, typing.Any]],
    name: builtins.str,
    ai_gateway: typing.Optional[typing.Union[ModelServingProvisionedThroughputAiGateway, typing.Dict[builtins.str, typing.Any]]] = None,
    budget_policy_id: typing.Optional[builtins.str] = None,
    email_notifications: typing.Optional[typing.Union[ModelServingProvisionedThroughputEmailNotifications, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingProvisionedThroughputTags, typing.Dict[builtins.str, typing.Any]]]]] = None,
    timeouts: typing.Optional[typing.Union[ModelServingProvisionedThroughputTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe30232b9ae3d20bc23b44bdec2f68557bdb0ceeeaab5e4d8a07724fb5443421(
    *,
    served_entities: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingProvisionedThroughputConfigServedEntities, typing.Dict[builtins.str, typing.Any]]]]] = None,
    traffic_config: typing.Optional[typing.Union[ModelServingProvisionedThroughputConfigTrafficConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af5f32ef5bc6b463e7170ee4991eb8a6a1dc258b56e626cccad29221747384ba(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd56f3a45d13388574f0d030791bcbf6e5373e02199bbf0b7e1034c510c743ff(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingProvisionedThroughputConfigServedEntities, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbce8f46c4559e3e0c400a2dc78ef88644699d012753ee396bb12d4c208fac4c(
    value: typing.Optional[ModelServingProvisionedThroughputConfigA],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__245fb0ce67430590ea7ffa416e51461fb03fc9523b0a65e542a90369290209a4(
    *,
    entity_name: builtins.str,
    entity_version: builtins.str,
    provisioned_model_units: jsii.Number,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__010bd3861333dfd8c69ece840911f2a54c31b8bd194838cba885fcef38a6037e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8b98b22956ef8b04323b6ed99f42c45cc0a1369a469b3cc0e9db3103ef0b15f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55c522a74b488cf8d4658f568bd8304a97980f7efe048a1cfa4960ba95457d58(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7dc4970d45167b70bf1693905cc9285d9e9b8fecf69955e40016b50c4d111ca6(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7dc0593a79645aee2f5b4381f046cd1ea9eef39191d5bc28acd9a9614a09b820(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9be129c9d0a674d924a49c59a494024cdc5a75c22be60ad287d6b0ef0e19212e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingProvisionedThroughputConfigServedEntities]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ebbc72841c4bf9327c7914d2276076a6109d402720d9070331b03a60ad9d5e2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17326be681995b21969129fb68af1352b121a60d688fda4f74e514c794bcfbab(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dec412b8d99a642679c46c5e8a799569fa89245ac1009f473f368ef7ce1082bd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a43b0c93918935a4c9a89af21c571394094e01d85221e9da812ac89b68ccf35(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4059c3b969dc0e13e1dcee05811f8059f95df961c920d94ad78bca7a09c8eea9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95945133d0fdcae60045c84555952700861d3c7df5bb4ce0d844d90f511511d8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingProvisionedThroughputConfigServedEntities]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21a038814a143819bfd6e0b790b0cc2afb73a3f6152b9630e11bdecedddc1d04(
    *,
    routes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingProvisionedThroughputConfigTrafficConfigRoutes, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38399d0c293304edb136bd318932f130db7eaf9975ab82a35e5da37fe939c193(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__552b6d545349e39a4cf28b3c4b042eab262cce1b6a7e5666cb215a62e269ba63(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingProvisionedThroughputConfigTrafficConfigRoutes, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6751039f8620377e63b05c5cd009754c16385bf4302e1e7067d6aa09aef79730(
    value: typing.Optional[ModelServingProvisionedThroughputConfigTrafficConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c7b1c9fab3de032527d812a6fdef2688ddff8d9abb0b03dca3aa6635b74a7e1(
    *,
    traffic_percentage: jsii.Number,
    served_entity_name: typing.Optional[builtins.str] = None,
    served_model_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b34830bce44e9836c24e12a83f71e26f02bd43c695ba21fb972e9d9ba8b8d63a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88c0fcb339252152f7b6ff62339ef5ab984f56169247e9897f97fc87954bc589(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbe976b34a31852a7bf356c948d2664f86b1712929a60c253fdfbcc87e98f404(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4733ea8767c1c9489c0cefe2d59e8e4bef25f2dd7950442ec657f1333746e74e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53d935a55457f26eb38ee450d6255a7181ce7a38309ed753b64d10c7b4f85ab4(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0b03a782c4c8b4204bfca06a638adfb58b3cd760c5e30e2aed1ce245ba42aeb(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingProvisionedThroughputConfigTrafficConfigRoutes]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35ca3ad7f47a8198454223f5de5ef703ca0432998718f59cc7f5b2c78895104b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e57419c6d26eef8c6d564f941dd8ac6171620683392884b35d2514770d83bcbd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5c3329bc73b41fe2cb280b980323d2e9ad679a841d65e44c437b519d9d0f1be(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b4df19610fc3a29c54500b1427afb082f9b049131e9fa6c507354ddfa0a64ad(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7778335f3c3afc5b1334c9d2384497d8a376d872b67dc6bb6e53ca693341b9ac(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingProvisionedThroughputConfigTrafficConfigRoutes]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8f97b4b969843ac1da1abcafa24706923091f81731b21e08f569c571614e7d1(
    *,
    on_update_failure: typing.Optional[typing.Sequence[builtins.str]] = None,
    on_update_success: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1c9aa325158307b64db7aaaced8369badd769b16b10a5445c78f00de176507a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d8acfd88f129fa4fe6fb930a5c730c84748ddc76915c274b59a0a60629c6bb3(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ae521720b4853406805759597ad8f8cd2932cf90b19f3ca5a3c08fa4504d2c2(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94c664bf47aa7d51880695166aa140ff0288b346fc23431e5958783f8810553f(
    value: typing.Optional[ModelServingProvisionedThroughputEmailNotifications],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__115f09f316262ee893f8d03df96eb866bcf7e6ae3b92f0c118bf6802591eebef(
    *,
    key: builtins.str,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0775c2288d607e8e5972c51bd4e85a156fefd9128c584cc36fed473c60327d4f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6534e6b67bf2ed2e5cb9847fbd8fb3aba6436c568483172676e118c531aa3205(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d40e911b039d06d0cc8b93ba10e320e3216c43d4848bea8951a6df5c2722d22(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2d084c6cae8a509f499acd198aa2b010b6a02f6576d3e1d7e10495363a62a44(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8490887bcf4e42d60d3902994aa537ecbe53e289b2f9db7b3f49b7f9135a59cd(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24bd6e0ca426f2e6b276e69f3a97278f126be77924e4a356eaa6bcb4b4113201(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingProvisionedThroughputTags]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02c922556682b7c1f63cbb79d81b8920042ab417544d350c76b4b9d806f81b8f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f45f93ff3a89b68a6cd07df66dad8f27233a5675a116632054407150088fffa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10af19d7e933830361b36745829dd04115566510ab2a8d5fc5a781bb3dd1f97d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5e1f9714d13c762a8eb880bbde71c01f0341581a4ffd510952bad63402d01c5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingProvisionedThroughputTags]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7438ec9c625f571f7ef6d704dd0c6811dc14b713f34b9237d4dc13293aec825(
    *,
    create: typing.Optional[builtins.str] = None,
    update: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f0e118b76371a92d3a8ab91254b71a10c7b82d2764d605ceb637723e2a755f0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc0ce933eec038464352ff36e56c5db89a4eb817bedd2a7fa5d7b716478446d0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3646c66e0617ec57eab48ceb2f502cc575028a6d0e7e0d241907597db9970ee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5eecb588f81bd51f05c617bcfb76d0c6aa8e5b5e0a36c8d1097951dfb044e61(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingProvisionedThroughputTimeouts]],
) -> None:
    """Type checking stubs"""
    pass
