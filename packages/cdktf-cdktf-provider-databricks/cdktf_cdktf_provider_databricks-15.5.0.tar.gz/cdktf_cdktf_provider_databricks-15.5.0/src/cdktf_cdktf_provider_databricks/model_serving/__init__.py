r'''
# `databricks_model_serving`

Refer to the Terraform Registry for docs: [`databricks_model_serving`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving).
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


class ModelServing(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServing",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving databricks_model_serving}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        ai_gateway: typing.Optional[typing.Union["ModelServingAiGateway", typing.Dict[builtins.str, typing.Any]]] = None,
        budget_policy_id: typing.Optional[builtins.str] = None,
        config: typing.Optional[typing.Union["ModelServingConfigA", typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        email_notifications: typing.Optional[typing.Union["ModelServingEmailNotifications", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        rate_limits: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingRateLimits", typing.Dict[builtins.str, typing.Any]]]]] = None,
        route_optimized: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingTags", typing.Dict[builtins.str, typing.Any]]]]] = None,
        timeouts: typing.Optional[typing.Union["ModelServingTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving databricks_model_serving} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#name ModelServing#name}.
        :param ai_gateway: ai_gateway block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#ai_gateway ModelServing#ai_gateway}
        :param budget_policy_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#budget_policy_id ModelServing#budget_policy_id}.
        :param config: config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#config ModelServing#config}
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#description ModelServing#description}.
        :param email_notifications: email_notifications block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#email_notifications ModelServing#email_notifications}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#id ModelServing#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param rate_limits: rate_limits block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#rate_limits ModelServing#rate_limits}
        :param route_optimized: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#route_optimized ModelServing#route_optimized}.
        :param tags: tags block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#tags ModelServing#tags}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#timeouts ModelServing#timeouts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcdceab54e050923170b39eff538055f8b76b660bb8732c203c9c67261d31d37)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config_ = ModelServingConfig(
            name=name,
            ai_gateway=ai_gateway,
            budget_policy_id=budget_policy_id,
            config=config,
            description=description,
            email_notifications=email_notifications,
            id=id,
            rate_limits=rate_limits,
            route_optimized=route_optimized,
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
        '''Generates CDKTF code for importing a ModelServing resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ModelServing to import.
        :param import_from_id: The id of the existing ModelServing that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ModelServing to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee1bb539ded3a1716a5800f3c306bd3bf91c26ca2eb1bd182e8248cdbaff5430)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAiGateway")
    def put_ai_gateway(
        self,
        *,
        fallback_config: typing.Optional[typing.Union["ModelServingAiGatewayFallbackConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        guardrails: typing.Optional[typing.Union["ModelServingAiGatewayGuardrails", typing.Dict[builtins.str, typing.Any]]] = None,
        inference_table_config: typing.Optional[typing.Union["ModelServingAiGatewayInferenceTableConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        rate_limits: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingAiGatewayRateLimits", typing.Dict[builtins.str, typing.Any]]]]] = None,
        usage_tracking_config: typing.Optional[typing.Union["ModelServingAiGatewayUsageTrackingConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param fallback_config: fallback_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#fallback_config ModelServing#fallback_config}
        :param guardrails: guardrails block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#guardrails ModelServing#guardrails}
        :param inference_table_config: inference_table_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#inference_table_config ModelServing#inference_table_config}
        :param rate_limits: rate_limits block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#rate_limits ModelServing#rate_limits}
        :param usage_tracking_config: usage_tracking_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#usage_tracking_config ModelServing#usage_tracking_config}
        '''
        value = ModelServingAiGateway(
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
        auto_capture_config: typing.Optional[typing.Union["ModelServingConfigAutoCaptureConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        served_entities: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingConfigServedEntities", typing.Dict[builtins.str, typing.Any]]]]] = None,
        served_models: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingConfigServedModels", typing.Dict[builtins.str, typing.Any]]]]] = None,
        traffic_config: typing.Optional[typing.Union["ModelServingConfigTrafficConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param auto_capture_config: auto_capture_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#auto_capture_config ModelServing#auto_capture_config}
        :param served_entities: served_entities block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#served_entities ModelServing#served_entities}
        :param served_models: served_models block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#served_models ModelServing#served_models}
        :param traffic_config: traffic_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#traffic_config ModelServing#traffic_config}
        '''
        value = ModelServingConfigA(
            auto_capture_config=auto_capture_config,
            served_entities=served_entities,
            served_models=served_models,
            traffic_config=traffic_config,
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
        :param on_update_failure: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#on_update_failure ModelServing#on_update_failure}.
        :param on_update_success: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#on_update_success ModelServing#on_update_success}.
        '''
        value = ModelServingEmailNotifications(
            on_update_failure=on_update_failure, on_update_success=on_update_success
        )

        return typing.cast(None, jsii.invoke(self, "putEmailNotifications", [value]))

    @jsii.member(jsii_name="putRateLimits")
    def put_rate_limits(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingRateLimits", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80a275a6bfdceace553e2be007a16e27fa4711760199dc7e1aa3df554d09920e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRateLimits", [value]))

    @jsii.member(jsii_name="putTags")
    def put_tags(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingTags", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9a326d60c6d2388605269123ef001af7186ca3f81f93ddf683edaaa2863033b)
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
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#create ModelServing#create}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#update ModelServing#update}.
        '''
        value = ModelServingTimeouts(create=create, update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetAiGateway")
    def reset_ai_gateway(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAiGateway", []))

    @jsii.member(jsii_name="resetBudgetPolicyId")
    def reset_budget_policy_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBudgetPolicyId", []))

    @jsii.member(jsii_name="resetConfig")
    def reset_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfig", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetEmailNotifications")
    def reset_email_notifications(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailNotifications", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetRateLimits")
    def reset_rate_limits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRateLimits", []))

    @jsii.member(jsii_name="resetRouteOptimized")
    def reset_route_optimized(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRouteOptimized", []))

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
    def ai_gateway(self) -> "ModelServingAiGatewayOutputReference":
        return typing.cast("ModelServingAiGatewayOutputReference", jsii.get(self, "aiGateway"))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> "ModelServingConfigAOutputReference":
        return typing.cast("ModelServingConfigAOutputReference", jsii.get(self, "config"))

    @builtins.property
    @jsii.member(jsii_name="emailNotifications")
    def email_notifications(self) -> "ModelServingEmailNotificationsOutputReference":
        return typing.cast("ModelServingEmailNotificationsOutputReference", jsii.get(self, "emailNotifications"))

    @builtins.property
    @jsii.member(jsii_name="endpointUrl")
    def endpoint_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpointUrl"))

    @builtins.property
    @jsii.member(jsii_name="rateLimits")
    def rate_limits(self) -> "ModelServingRateLimitsList":
        return typing.cast("ModelServingRateLimitsList", jsii.get(self, "rateLimits"))

    @builtins.property
    @jsii.member(jsii_name="servingEndpointId")
    def serving_endpoint_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "servingEndpointId"))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> "ModelServingTagsList":
        return typing.cast("ModelServingTagsList", jsii.get(self, "tags"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "ModelServingTimeoutsOutputReference":
        return typing.cast("ModelServingTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="aiGatewayInput")
    def ai_gateway_input(self) -> typing.Optional["ModelServingAiGateway"]:
        return typing.cast(typing.Optional["ModelServingAiGateway"], jsii.get(self, "aiGatewayInput"))

    @builtins.property
    @jsii.member(jsii_name="budgetPolicyIdInput")
    def budget_policy_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "budgetPolicyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="configInput")
    def config_input(self) -> typing.Optional["ModelServingConfigA"]:
        return typing.cast(typing.Optional["ModelServingConfigA"], jsii.get(self, "configInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="emailNotificationsInput")
    def email_notifications_input(
        self,
    ) -> typing.Optional["ModelServingEmailNotifications"]:
        return typing.cast(typing.Optional["ModelServingEmailNotifications"], jsii.get(self, "emailNotificationsInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="rateLimitsInput")
    def rate_limits_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingRateLimits"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingRateLimits"]]], jsii.get(self, "rateLimitsInput"))

    @builtins.property
    @jsii.member(jsii_name="routeOptimizedInput")
    def route_optimized_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "routeOptimizedInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingTags"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingTags"]]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ModelServingTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ModelServingTimeouts"]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="budgetPolicyId")
    def budget_policy_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "budgetPolicyId"))

    @budget_policy_id.setter
    def budget_policy_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0d566a8ca84f82808361be591117475b17c993ad26a78d9b2a1a9dc810f962b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "budgetPolicyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d495d7859885ddded479363c83b86f87c932a597926d0b2528792025cc752a11)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__754d4971dd64df250d28b3640fa44fa399b715301fc0dd43ff8d8304e9ef8d25)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eeb43c6ec513eda5c793054e174b6c273a821c9b323b20667ced44837696142c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="routeOptimized")
    def route_optimized(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "routeOptimized"))

    @route_optimized.setter
    def route_optimized(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d34de5d9b9fed3c9898fd854fd3464a901fd46e11ea543b532dd7d7a7df273a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "routeOptimized", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingAiGateway",
    jsii_struct_bases=[],
    name_mapping={
        "fallback_config": "fallbackConfig",
        "guardrails": "guardrails",
        "inference_table_config": "inferenceTableConfig",
        "rate_limits": "rateLimits",
        "usage_tracking_config": "usageTrackingConfig",
    },
)
class ModelServingAiGateway:
    def __init__(
        self,
        *,
        fallback_config: typing.Optional[typing.Union["ModelServingAiGatewayFallbackConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        guardrails: typing.Optional[typing.Union["ModelServingAiGatewayGuardrails", typing.Dict[builtins.str, typing.Any]]] = None,
        inference_table_config: typing.Optional[typing.Union["ModelServingAiGatewayInferenceTableConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        rate_limits: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingAiGatewayRateLimits", typing.Dict[builtins.str, typing.Any]]]]] = None,
        usage_tracking_config: typing.Optional[typing.Union["ModelServingAiGatewayUsageTrackingConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param fallback_config: fallback_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#fallback_config ModelServing#fallback_config}
        :param guardrails: guardrails block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#guardrails ModelServing#guardrails}
        :param inference_table_config: inference_table_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#inference_table_config ModelServing#inference_table_config}
        :param rate_limits: rate_limits block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#rate_limits ModelServing#rate_limits}
        :param usage_tracking_config: usage_tracking_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#usage_tracking_config ModelServing#usage_tracking_config}
        '''
        if isinstance(fallback_config, dict):
            fallback_config = ModelServingAiGatewayFallbackConfig(**fallback_config)
        if isinstance(guardrails, dict):
            guardrails = ModelServingAiGatewayGuardrails(**guardrails)
        if isinstance(inference_table_config, dict):
            inference_table_config = ModelServingAiGatewayInferenceTableConfig(**inference_table_config)
        if isinstance(usage_tracking_config, dict):
            usage_tracking_config = ModelServingAiGatewayUsageTrackingConfig(**usage_tracking_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d20f2c3755219d11514382f35601665878bc89f904a8e9fc1b0446c1b5275c4a)
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
    def fallback_config(self) -> typing.Optional["ModelServingAiGatewayFallbackConfig"]:
        '''fallback_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#fallback_config ModelServing#fallback_config}
        '''
        result = self._values.get("fallback_config")
        return typing.cast(typing.Optional["ModelServingAiGatewayFallbackConfig"], result)

    @builtins.property
    def guardrails(self) -> typing.Optional["ModelServingAiGatewayGuardrails"]:
        '''guardrails block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#guardrails ModelServing#guardrails}
        '''
        result = self._values.get("guardrails")
        return typing.cast(typing.Optional["ModelServingAiGatewayGuardrails"], result)

    @builtins.property
    def inference_table_config(
        self,
    ) -> typing.Optional["ModelServingAiGatewayInferenceTableConfig"]:
        '''inference_table_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#inference_table_config ModelServing#inference_table_config}
        '''
        result = self._values.get("inference_table_config")
        return typing.cast(typing.Optional["ModelServingAiGatewayInferenceTableConfig"], result)

    @builtins.property
    def rate_limits(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingAiGatewayRateLimits"]]]:
        '''rate_limits block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#rate_limits ModelServing#rate_limits}
        '''
        result = self._values.get("rate_limits")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingAiGatewayRateLimits"]]], result)

    @builtins.property
    def usage_tracking_config(
        self,
    ) -> typing.Optional["ModelServingAiGatewayUsageTrackingConfig"]:
        '''usage_tracking_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#usage_tracking_config ModelServing#usage_tracking_config}
        '''
        result = self._values.get("usage_tracking_config")
        return typing.cast(typing.Optional["ModelServingAiGatewayUsageTrackingConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingAiGateway(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingAiGatewayFallbackConfig",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled"},
)
class ModelServingAiGatewayFallbackConfig:
    def __init__(
        self,
        *,
        enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#enabled ModelServing#enabled}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__701ce7f0a5acfcb5954469ee619c8f0fd11b46d959d772d902d0f6d9110d3248)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "enabled": enabled,
        }

    @builtins.property
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#enabled ModelServing#enabled}.'''
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingAiGatewayFallbackConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingAiGatewayFallbackConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingAiGatewayFallbackConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c5a6a471bbba8ab4a6d22b275622b1950ddc30e8d2e9db4c7fa07ec539696d59)
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
            type_hints = typing.get_type_hints(_typecheckingstub__074be50bae8c643f6ce3a55b4d11c9158fddb491281bd69d4dca7814a922b329)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ModelServingAiGatewayFallbackConfig]:
        return typing.cast(typing.Optional[ModelServingAiGatewayFallbackConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingAiGatewayFallbackConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d071b0a987a3a07349f67db236fefc8608f4b9b2240dd2162e265936cca9e9da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingAiGatewayGuardrails",
    jsii_struct_bases=[],
    name_mapping={"input": "input", "output": "output"},
)
class ModelServingAiGatewayGuardrails:
    def __init__(
        self,
        *,
        input: typing.Optional[typing.Union["ModelServingAiGatewayGuardrailsInput", typing.Dict[builtins.str, typing.Any]]] = None,
        output: typing.Optional[typing.Union["ModelServingAiGatewayGuardrailsOutput", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param input: input block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#input ModelServing#input}
        :param output: output block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#output ModelServing#output}
        '''
        if isinstance(input, dict):
            input = ModelServingAiGatewayGuardrailsInput(**input)
        if isinstance(output, dict):
            output = ModelServingAiGatewayGuardrailsOutput(**output)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23233978ac7c7afa851e013c35b65df372202665674c78531b22b51134444acf)
            check_type(argname="argument input", value=input, expected_type=type_hints["input"])
            check_type(argname="argument output", value=output, expected_type=type_hints["output"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if input is not None:
            self._values["input"] = input
        if output is not None:
            self._values["output"] = output

    @builtins.property
    def input(self) -> typing.Optional["ModelServingAiGatewayGuardrailsInput"]:
        '''input block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#input ModelServing#input}
        '''
        result = self._values.get("input")
        return typing.cast(typing.Optional["ModelServingAiGatewayGuardrailsInput"], result)

    @builtins.property
    def output(self) -> typing.Optional["ModelServingAiGatewayGuardrailsOutput"]:
        '''output block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#output ModelServing#output}
        '''
        result = self._values.get("output")
        return typing.cast(typing.Optional["ModelServingAiGatewayGuardrailsOutput"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingAiGatewayGuardrails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingAiGatewayGuardrailsInput",
    jsii_struct_bases=[],
    name_mapping={
        "invalid_keywords": "invalidKeywords",
        "pii": "pii",
        "safety": "safety",
        "valid_topics": "validTopics",
    },
)
class ModelServingAiGatewayGuardrailsInput:
    def __init__(
        self,
        *,
        invalid_keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        pii: typing.Optional[typing.Union["ModelServingAiGatewayGuardrailsInputPii", typing.Dict[builtins.str, typing.Any]]] = None,
        safety: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        valid_topics: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param invalid_keywords: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#invalid_keywords ModelServing#invalid_keywords}.
        :param pii: pii block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#pii ModelServing#pii}
        :param safety: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#safety ModelServing#safety}.
        :param valid_topics: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#valid_topics ModelServing#valid_topics}.
        '''
        if isinstance(pii, dict):
            pii = ModelServingAiGatewayGuardrailsInputPii(**pii)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10bc8fe1b1ad77c3449c862fcf632beecfee459f26e8e3ef19e2cf3f9c87ffb9)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#invalid_keywords ModelServing#invalid_keywords}.'''
        result = self._values.get("invalid_keywords")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def pii(self) -> typing.Optional["ModelServingAiGatewayGuardrailsInputPii"]:
        '''pii block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#pii ModelServing#pii}
        '''
        result = self._values.get("pii")
        return typing.cast(typing.Optional["ModelServingAiGatewayGuardrailsInputPii"], result)

    @builtins.property
    def safety(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#safety ModelServing#safety}.'''
        result = self._values.get("safety")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def valid_topics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#valid_topics ModelServing#valid_topics}.'''
        result = self._values.get("valid_topics")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingAiGatewayGuardrailsInput(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingAiGatewayGuardrailsInputOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingAiGatewayGuardrailsInputOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__be40d438526fc7c4b26bcd8fb1966decb78a477aa24c5f743cbd6876afbedc3e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putPii")
    def put_pii(self, *, behavior: typing.Optional[builtins.str] = None) -> None:
        '''
        :param behavior: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#behavior ModelServing#behavior}.
        '''
        value = ModelServingAiGatewayGuardrailsInputPii(behavior=behavior)

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
    def pii(self) -> "ModelServingAiGatewayGuardrailsInputPiiOutputReference":
        return typing.cast("ModelServingAiGatewayGuardrailsInputPiiOutputReference", jsii.get(self, "pii"))

    @builtins.property
    @jsii.member(jsii_name="invalidKeywordsInput")
    def invalid_keywords_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "invalidKeywordsInput"))

    @builtins.property
    @jsii.member(jsii_name="piiInput")
    def pii_input(self) -> typing.Optional["ModelServingAiGatewayGuardrailsInputPii"]:
        return typing.cast(typing.Optional["ModelServingAiGatewayGuardrailsInputPii"], jsii.get(self, "piiInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__be30c47b9f8392c82005c4714d69afd927a2e4128d0234daec48bc7bbcc22aa4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9485bbe25a285d3fd2004b13f974eb8cccaf919d8c7732617d78ccf9e10118a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "safety", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="validTopics")
    def valid_topics(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "validTopics"))

    @valid_topics.setter
    def valid_topics(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a055d52f914b07e48516fb13fcec3049afcc8bac029935185bb954225f9e3f15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "validTopics", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ModelServingAiGatewayGuardrailsInput]:
        return typing.cast(typing.Optional[ModelServingAiGatewayGuardrailsInput], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingAiGatewayGuardrailsInput],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d895f86afa6af4b36f3233794187324bcd3cf51b50eb9ecfedba0347f9ec7678)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingAiGatewayGuardrailsInputPii",
    jsii_struct_bases=[],
    name_mapping={"behavior": "behavior"},
)
class ModelServingAiGatewayGuardrailsInputPii:
    def __init__(self, *, behavior: typing.Optional[builtins.str] = None) -> None:
        '''
        :param behavior: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#behavior ModelServing#behavior}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b475277a01edd50645fee8ea196ec320ff8d6ba0dbd6269e67f2f6664b1df5c)
            check_type(argname="argument behavior", value=behavior, expected_type=type_hints["behavior"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if behavior is not None:
            self._values["behavior"] = behavior

    @builtins.property
    def behavior(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#behavior ModelServing#behavior}.'''
        result = self._values.get("behavior")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingAiGatewayGuardrailsInputPii(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingAiGatewayGuardrailsInputPiiOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingAiGatewayGuardrailsInputPiiOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__837abf08fbcd192a365dbd00321873606d2e16266ed7a87dfe5b43a331d28e67)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6cc65d3ed87238263d4772d63f8d5128c5e89b63d160553ba956b09199d9d1ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "behavior", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingAiGatewayGuardrailsInputPii]:
        return typing.cast(typing.Optional[ModelServingAiGatewayGuardrailsInputPii], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingAiGatewayGuardrailsInputPii],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1cbb1b76a767619df9ecfe60dde9c3063c79370b5e969959f299b3360edabec2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingAiGatewayGuardrailsOutput",
    jsii_struct_bases=[],
    name_mapping={
        "invalid_keywords": "invalidKeywords",
        "pii": "pii",
        "safety": "safety",
        "valid_topics": "validTopics",
    },
)
class ModelServingAiGatewayGuardrailsOutput:
    def __init__(
        self,
        *,
        invalid_keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        pii: typing.Optional[typing.Union["ModelServingAiGatewayGuardrailsOutputPii", typing.Dict[builtins.str, typing.Any]]] = None,
        safety: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        valid_topics: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param invalid_keywords: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#invalid_keywords ModelServing#invalid_keywords}.
        :param pii: pii block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#pii ModelServing#pii}
        :param safety: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#safety ModelServing#safety}.
        :param valid_topics: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#valid_topics ModelServing#valid_topics}.
        '''
        if isinstance(pii, dict):
            pii = ModelServingAiGatewayGuardrailsOutputPii(**pii)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f548d69157b58cd8398d69145143beb1e4e54267cb1b8b77e1e54810bc49a6c2)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#invalid_keywords ModelServing#invalid_keywords}.'''
        result = self._values.get("invalid_keywords")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def pii(self) -> typing.Optional["ModelServingAiGatewayGuardrailsOutputPii"]:
        '''pii block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#pii ModelServing#pii}
        '''
        result = self._values.get("pii")
        return typing.cast(typing.Optional["ModelServingAiGatewayGuardrailsOutputPii"], result)

    @builtins.property
    def safety(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#safety ModelServing#safety}.'''
        result = self._values.get("safety")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def valid_topics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#valid_topics ModelServing#valid_topics}.'''
        result = self._values.get("valid_topics")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingAiGatewayGuardrailsOutput(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingAiGatewayGuardrailsOutputOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingAiGatewayGuardrailsOutputOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__83c9a450cdd4103e3510d73a3a94e3325c71495114d0ed0cd7e3dfe37ccc79a3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putPii")
    def put_pii(self, *, behavior: typing.Optional[builtins.str] = None) -> None:
        '''
        :param behavior: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#behavior ModelServing#behavior}.
        '''
        value = ModelServingAiGatewayGuardrailsOutputPii(behavior=behavior)

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
    def pii(self) -> "ModelServingAiGatewayGuardrailsOutputPiiOutputReference":
        return typing.cast("ModelServingAiGatewayGuardrailsOutputPiiOutputReference", jsii.get(self, "pii"))

    @builtins.property
    @jsii.member(jsii_name="invalidKeywordsInput")
    def invalid_keywords_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "invalidKeywordsInput"))

    @builtins.property
    @jsii.member(jsii_name="piiInput")
    def pii_input(self) -> typing.Optional["ModelServingAiGatewayGuardrailsOutputPii"]:
        return typing.cast(typing.Optional["ModelServingAiGatewayGuardrailsOutputPii"], jsii.get(self, "piiInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__fa1df921fbf5468202c64dd1e744d00224c96b9710c1e9f65efd8eeb9af3ef71)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6ae7488d99494b8d7389b62eaa7d89aed5902d20dfcbdaa1a17db3ecc221d710)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "safety", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="validTopics")
    def valid_topics(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "validTopics"))

    @valid_topics.setter
    def valid_topics(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5c18bb9d454083451fe947050a254c66190c3c00471e9069d1822022a498d10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "validTopics", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ModelServingAiGatewayGuardrailsOutput]:
        return typing.cast(typing.Optional[ModelServingAiGatewayGuardrailsOutput], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingAiGatewayGuardrailsOutput],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56db0ba3f16db8c24b5b9f5087e36a46901312ca22c8fb139e9c53265da47d67)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingAiGatewayGuardrailsOutputPii",
    jsii_struct_bases=[],
    name_mapping={"behavior": "behavior"},
)
class ModelServingAiGatewayGuardrailsOutputPii:
    def __init__(self, *, behavior: typing.Optional[builtins.str] = None) -> None:
        '''
        :param behavior: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#behavior ModelServing#behavior}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00608cb2e6ca08f41cc56ff2f0e178699afe3069582719b56f637d25334fa9c7)
            check_type(argname="argument behavior", value=behavior, expected_type=type_hints["behavior"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if behavior is not None:
            self._values["behavior"] = behavior

    @builtins.property
    def behavior(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#behavior ModelServing#behavior}.'''
        result = self._values.get("behavior")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingAiGatewayGuardrailsOutputPii(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingAiGatewayGuardrailsOutputPiiOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingAiGatewayGuardrailsOutputPiiOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__db7e2b1dcffa2324c950b536e99c5414662556c9913c71baa1dd330123d7a65e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__018617612ef39f76acece0236edba7cb453409a10b3051f4908fd503b47a8481)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "behavior", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingAiGatewayGuardrailsOutputPii]:
        return typing.cast(typing.Optional[ModelServingAiGatewayGuardrailsOutputPii], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingAiGatewayGuardrailsOutputPii],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__611d0640b1a5e15838f158da92ac1b3c765a09bd27e5656ba420714f428ec5c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ModelServingAiGatewayGuardrailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingAiGatewayGuardrailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__65a3cc711979faac9e1a4719183e502d256fe6392a49065e54d7a7a7de4973ca)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putInput")
    def put_input(
        self,
        *,
        invalid_keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        pii: typing.Optional[typing.Union[ModelServingAiGatewayGuardrailsInputPii, typing.Dict[builtins.str, typing.Any]]] = None,
        safety: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        valid_topics: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param invalid_keywords: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#invalid_keywords ModelServing#invalid_keywords}.
        :param pii: pii block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#pii ModelServing#pii}
        :param safety: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#safety ModelServing#safety}.
        :param valid_topics: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#valid_topics ModelServing#valid_topics}.
        '''
        value = ModelServingAiGatewayGuardrailsInput(
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
        pii: typing.Optional[typing.Union[ModelServingAiGatewayGuardrailsOutputPii, typing.Dict[builtins.str, typing.Any]]] = None,
        safety: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        valid_topics: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param invalid_keywords: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#invalid_keywords ModelServing#invalid_keywords}.
        :param pii: pii block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#pii ModelServing#pii}
        :param safety: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#safety ModelServing#safety}.
        :param valid_topics: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#valid_topics ModelServing#valid_topics}.
        '''
        value = ModelServingAiGatewayGuardrailsOutput(
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
    def input(self) -> ModelServingAiGatewayGuardrailsInputOutputReference:
        return typing.cast(ModelServingAiGatewayGuardrailsInputOutputReference, jsii.get(self, "input"))

    @builtins.property
    @jsii.member(jsii_name="output")
    def output(self) -> ModelServingAiGatewayGuardrailsOutputOutputReference:
        return typing.cast(ModelServingAiGatewayGuardrailsOutputOutputReference, jsii.get(self, "output"))

    @builtins.property
    @jsii.member(jsii_name="inputInput")
    def input_input(self) -> typing.Optional[ModelServingAiGatewayGuardrailsInput]:
        return typing.cast(typing.Optional[ModelServingAiGatewayGuardrailsInput], jsii.get(self, "inputInput"))

    @builtins.property
    @jsii.member(jsii_name="outputInput")
    def output_input(self) -> typing.Optional[ModelServingAiGatewayGuardrailsOutput]:
        return typing.cast(typing.Optional[ModelServingAiGatewayGuardrailsOutput], jsii.get(self, "outputInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ModelServingAiGatewayGuardrails]:
        return typing.cast(typing.Optional[ModelServingAiGatewayGuardrails], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingAiGatewayGuardrails],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce1158a951e30d4eefb3d24cbacfc622a59fb2d19bbec8557c5545379264475f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingAiGatewayInferenceTableConfig",
    jsii_struct_bases=[],
    name_mapping={
        "catalog_name": "catalogName",
        "enabled": "enabled",
        "schema_name": "schemaName",
        "table_name_prefix": "tableNamePrefix",
    },
)
class ModelServingAiGatewayInferenceTableConfig:
    def __init__(
        self,
        *,
        catalog_name: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        schema_name: typing.Optional[builtins.str] = None,
        table_name_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param catalog_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#catalog_name ModelServing#catalog_name}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#enabled ModelServing#enabled}.
        :param schema_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#schema_name ModelServing#schema_name}.
        :param table_name_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#table_name_prefix ModelServing#table_name_prefix}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e4d5020d942b7ae2d9bd5bdfec5762919d692d98129acec818c004a64a3696d)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#catalog_name ModelServing#catalog_name}.'''
        result = self._values.get("catalog_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#enabled ModelServing#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def schema_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#schema_name ModelServing#schema_name}.'''
        result = self._values.get("schema_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def table_name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#table_name_prefix ModelServing#table_name_prefix}.'''
        result = self._values.get("table_name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingAiGatewayInferenceTableConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingAiGatewayInferenceTableConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingAiGatewayInferenceTableConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1a2563785aba3de18a87612f2207d74496620fa324689f9b5121216c64559f80)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5a22eca4744ccae8295b824a610b4724c3d4a3abbfce2d7bad8991db11de07ff)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3e8f02ee39da1baccf024791fe4197f41eff4269ad6d40b893b4f631306cac12)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="schemaName")
    def schema_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schemaName"))

    @schema_name.setter
    def schema_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d34d429fc29e9504a4becb7cc1c1b8214a1aab5654d6a14ec403e143513d66ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "schemaName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tableNamePrefix")
    def table_name_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tableNamePrefix"))

    @table_name_prefix.setter
    def table_name_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d2ce41ee52b23838dc8599d17f07aa841381a76f33896742ed95079840d74fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tableNamePrefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingAiGatewayInferenceTableConfig]:
        return typing.cast(typing.Optional[ModelServingAiGatewayInferenceTableConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingAiGatewayInferenceTableConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17b1de74f932cd4b1ad6b25e355aec94b5a4207bdb7025155c9c22f41b5b3878)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ModelServingAiGatewayOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingAiGatewayOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0bfd3922a36ac9daf43294348f7c12373f1ed7d0a1ad431ee6f9a96209e227ca)
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
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#enabled ModelServing#enabled}.
        '''
        value = ModelServingAiGatewayFallbackConfig(enabled=enabled)

        return typing.cast(None, jsii.invoke(self, "putFallbackConfig", [value]))

    @jsii.member(jsii_name="putGuardrails")
    def put_guardrails(
        self,
        *,
        input: typing.Optional[typing.Union[ModelServingAiGatewayGuardrailsInput, typing.Dict[builtins.str, typing.Any]]] = None,
        output: typing.Optional[typing.Union[ModelServingAiGatewayGuardrailsOutput, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param input: input block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#input ModelServing#input}
        :param output: output block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#output ModelServing#output}
        '''
        value = ModelServingAiGatewayGuardrails(input=input, output=output)

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
        :param catalog_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#catalog_name ModelServing#catalog_name}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#enabled ModelServing#enabled}.
        :param schema_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#schema_name ModelServing#schema_name}.
        :param table_name_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#table_name_prefix ModelServing#table_name_prefix}.
        '''
        value = ModelServingAiGatewayInferenceTableConfig(
            catalog_name=catalog_name,
            enabled=enabled,
            schema_name=schema_name,
            table_name_prefix=table_name_prefix,
        )

        return typing.cast(None, jsii.invoke(self, "putInferenceTableConfig", [value]))

    @jsii.member(jsii_name="putRateLimits")
    def put_rate_limits(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingAiGatewayRateLimits", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0bd70d0eaee59805f45831c75d3ea42514dde50993cef8e25adac744aab6605)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRateLimits", [value]))

    @jsii.member(jsii_name="putUsageTrackingConfig")
    def put_usage_tracking_config(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#enabled ModelServing#enabled}.
        '''
        value = ModelServingAiGatewayUsageTrackingConfig(enabled=enabled)

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
    def fallback_config(self) -> ModelServingAiGatewayFallbackConfigOutputReference:
        return typing.cast(ModelServingAiGatewayFallbackConfigOutputReference, jsii.get(self, "fallbackConfig"))

    @builtins.property
    @jsii.member(jsii_name="guardrails")
    def guardrails(self) -> ModelServingAiGatewayGuardrailsOutputReference:
        return typing.cast(ModelServingAiGatewayGuardrailsOutputReference, jsii.get(self, "guardrails"))

    @builtins.property
    @jsii.member(jsii_name="inferenceTableConfig")
    def inference_table_config(
        self,
    ) -> ModelServingAiGatewayInferenceTableConfigOutputReference:
        return typing.cast(ModelServingAiGatewayInferenceTableConfigOutputReference, jsii.get(self, "inferenceTableConfig"))

    @builtins.property
    @jsii.member(jsii_name="rateLimits")
    def rate_limits(self) -> "ModelServingAiGatewayRateLimitsList":
        return typing.cast("ModelServingAiGatewayRateLimitsList", jsii.get(self, "rateLimits"))

    @builtins.property
    @jsii.member(jsii_name="usageTrackingConfig")
    def usage_tracking_config(
        self,
    ) -> "ModelServingAiGatewayUsageTrackingConfigOutputReference":
        return typing.cast("ModelServingAiGatewayUsageTrackingConfigOutputReference", jsii.get(self, "usageTrackingConfig"))

    @builtins.property
    @jsii.member(jsii_name="fallbackConfigInput")
    def fallback_config_input(
        self,
    ) -> typing.Optional[ModelServingAiGatewayFallbackConfig]:
        return typing.cast(typing.Optional[ModelServingAiGatewayFallbackConfig], jsii.get(self, "fallbackConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="guardrailsInput")
    def guardrails_input(self) -> typing.Optional[ModelServingAiGatewayGuardrails]:
        return typing.cast(typing.Optional[ModelServingAiGatewayGuardrails], jsii.get(self, "guardrailsInput"))

    @builtins.property
    @jsii.member(jsii_name="inferenceTableConfigInput")
    def inference_table_config_input(
        self,
    ) -> typing.Optional[ModelServingAiGatewayInferenceTableConfig]:
        return typing.cast(typing.Optional[ModelServingAiGatewayInferenceTableConfig], jsii.get(self, "inferenceTableConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="rateLimitsInput")
    def rate_limits_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingAiGatewayRateLimits"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingAiGatewayRateLimits"]]], jsii.get(self, "rateLimitsInput"))

    @builtins.property
    @jsii.member(jsii_name="usageTrackingConfigInput")
    def usage_tracking_config_input(
        self,
    ) -> typing.Optional["ModelServingAiGatewayUsageTrackingConfig"]:
        return typing.cast(typing.Optional["ModelServingAiGatewayUsageTrackingConfig"], jsii.get(self, "usageTrackingConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ModelServingAiGateway]:
        return typing.cast(typing.Optional[ModelServingAiGateway], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ModelServingAiGateway]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4eaf0079c4bbc7d152c2fd01885d79403434d9d10c9783925c4d1c613c37e692)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingAiGatewayRateLimits",
    jsii_struct_bases=[],
    name_mapping={
        "renewal_period": "renewalPeriod",
        "calls": "calls",
        "key": "key",
        "principal": "principal",
        "tokens": "tokens",
    },
)
class ModelServingAiGatewayRateLimits:
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
        :param renewal_period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#renewal_period ModelServing#renewal_period}.
        :param calls: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#calls ModelServing#calls}.
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#key ModelServing#key}.
        :param principal: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#principal ModelServing#principal}.
        :param tokens: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#tokens ModelServing#tokens}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__471cdd7770b9ecb8fc419aaea437acccb2895584dd766e6bf6bdc137c5314da3)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#renewal_period ModelServing#renewal_period}.'''
        result = self._values.get("renewal_period")
        assert result is not None, "Required property 'renewal_period' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def calls(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#calls ModelServing#calls}.'''
        result = self._values.get("calls")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#key ModelServing#key}.'''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def principal(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#principal ModelServing#principal}.'''
        result = self._values.get("principal")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tokens(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#tokens ModelServing#tokens}.'''
        result = self._values.get("tokens")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingAiGatewayRateLimits(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingAiGatewayRateLimitsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingAiGatewayRateLimitsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4749a9ca863d33734b709bd597f7485df7293e5d5981955fcb1977020062066e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ModelServingAiGatewayRateLimitsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7424ad869d07817c30ec5fcf326ccf5da3b7f7c1aa921e63879b01123c9f8b54)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ModelServingAiGatewayRateLimitsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c5827006339f47e87e6fb62e606fb9c84be888814813cf860d74a72ee5be9a4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a8d2d3ae01789ce480148b558549a9547b11ca3dcd745f187cc644ad2cfe698c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2aedbb37dcb3e56327b8081eb7e329e8ccd74aed5340773b38f88214f8ed3f11)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingAiGatewayRateLimits]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingAiGatewayRateLimits]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingAiGatewayRateLimits]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30118c0679131c53c0d490aea759da7d1964983bc0c8014e1b7be561bd6a7ce0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ModelServingAiGatewayRateLimitsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingAiGatewayRateLimitsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0ce27ce8c2b9f9ef764afc5f4924c8ea1de9acae8fa87dd88ae61079a89c69d7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d46d976942a0f8dea0a817f302c8a71f595a6c1e082ee96ff8766efa64e715df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "calls", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6050176ffba86707067e8d02087818cbb7ee25760a8b6552a1bfe314f854627f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="principal")
    def principal(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "principal"))

    @principal.setter
    def principal(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__971740f22d738c496278b6ac6a91889f1a79c65661cf1a039a800f4f8f45fc5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "principal", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="renewalPeriod")
    def renewal_period(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "renewalPeriod"))

    @renewal_period.setter
    def renewal_period(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8141d81487fbdf3d7c2591674ab7c2b6d553f349e06b75a9e1fc2c9908df526b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "renewalPeriod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokens")
    def tokens(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokens"))

    @tokens.setter
    def tokens(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ce89c379fde7986eac963cc2175c9f1865f6223fb5cd9d71e900aa6df99b558)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokens", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingAiGatewayRateLimits]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingAiGatewayRateLimits]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingAiGatewayRateLimits]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16b2b5e052b4b1b7dc8eeb46f717739a6b61dd7a325b3583d5c8cbac76669d5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingAiGatewayUsageTrackingConfig",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled"},
)
class ModelServingAiGatewayUsageTrackingConfig:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#enabled ModelServing#enabled}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a71ae3be5012117ecde8e7927d576ee33a763b98088180dc610a7648bb55f223)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#enabled ModelServing#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingAiGatewayUsageTrackingConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingAiGatewayUsageTrackingConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingAiGatewayUsageTrackingConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__195aaebdd8ff9aec3cacabf86a33cfd347169cce1a81858c2fb36a3b1218d020)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a956c9ef5a76e0935a37fc69655b0041e686dee9524415aec599f0dd2e5ec88d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingAiGatewayUsageTrackingConfig]:
        return typing.cast(typing.Optional[ModelServingAiGatewayUsageTrackingConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingAiGatewayUsageTrackingConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4bd82eb47a29e7876d59f60112fe47ffe3e56fc6347d6139313d4cad0d80d581)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfig",
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
        "ai_gateway": "aiGateway",
        "budget_policy_id": "budgetPolicyId",
        "config": "config",
        "description": "description",
        "email_notifications": "emailNotifications",
        "id": "id",
        "rate_limits": "rateLimits",
        "route_optimized": "routeOptimized",
        "tags": "tags",
        "timeouts": "timeouts",
    },
)
class ModelServingConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        ai_gateway: typing.Optional[typing.Union[ModelServingAiGateway, typing.Dict[builtins.str, typing.Any]]] = None,
        budget_policy_id: typing.Optional[builtins.str] = None,
        config: typing.Optional[typing.Union["ModelServingConfigA", typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        email_notifications: typing.Optional[typing.Union["ModelServingEmailNotifications", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        rate_limits: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingRateLimits", typing.Dict[builtins.str, typing.Any]]]]] = None,
        route_optimized: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingTags", typing.Dict[builtins.str, typing.Any]]]]] = None,
        timeouts: typing.Optional[typing.Union["ModelServingTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#name ModelServing#name}.
        :param ai_gateway: ai_gateway block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#ai_gateway ModelServing#ai_gateway}
        :param budget_policy_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#budget_policy_id ModelServing#budget_policy_id}.
        :param config: config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#config ModelServing#config}
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#description ModelServing#description}.
        :param email_notifications: email_notifications block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#email_notifications ModelServing#email_notifications}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#id ModelServing#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param rate_limits: rate_limits block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#rate_limits ModelServing#rate_limits}
        :param route_optimized: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#route_optimized ModelServing#route_optimized}.
        :param tags: tags block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#tags ModelServing#tags}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#timeouts ModelServing#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(ai_gateway, dict):
            ai_gateway = ModelServingAiGateway(**ai_gateway)
        if isinstance(config, dict):
            config = ModelServingConfigA(**config)
        if isinstance(email_notifications, dict):
            email_notifications = ModelServingEmailNotifications(**email_notifications)
        if isinstance(timeouts, dict):
            timeouts = ModelServingTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6ab99c61d3a667a89d9f5f2278213a6b075df770286584a1c864bfffbe20082)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument ai_gateway", value=ai_gateway, expected_type=type_hints["ai_gateway"])
            check_type(argname="argument budget_policy_id", value=budget_policy_id, expected_type=type_hints["budget_policy_id"])
            check_type(argname="argument config", value=config, expected_type=type_hints["config"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument email_notifications", value=email_notifications, expected_type=type_hints["email_notifications"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument rate_limits", value=rate_limits, expected_type=type_hints["rate_limits"])
            check_type(argname="argument route_optimized", value=route_optimized, expected_type=type_hints["route_optimized"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
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
        if ai_gateway is not None:
            self._values["ai_gateway"] = ai_gateway
        if budget_policy_id is not None:
            self._values["budget_policy_id"] = budget_policy_id
        if config is not None:
            self._values["config"] = config
        if description is not None:
            self._values["description"] = description
        if email_notifications is not None:
            self._values["email_notifications"] = email_notifications
        if id is not None:
            self._values["id"] = id
        if rate_limits is not None:
            self._values["rate_limits"] = rate_limits
        if route_optimized is not None:
            self._values["route_optimized"] = route_optimized
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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#name ModelServing#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ai_gateway(self) -> typing.Optional[ModelServingAiGateway]:
        '''ai_gateway block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#ai_gateway ModelServing#ai_gateway}
        '''
        result = self._values.get("ai_gateway")
        return typing.cast(typing.Optional[ModelServingAiGateway], result)

    @builtins.property
    def budget_policy_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#budget_policy_id ModelServing#budget_policy_id}.'''
        result = self._values.get("budget_policy_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def config(self) -> typing.Optional["ModelServingConfigA"]:
        '''config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#config ModelServing#config}
        '''
        result = self._values.get("config")
        return typing.cast(typing.Optional["ModelServingConfigA"], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#description ModelServing#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_notifications(self) -> typing.Optional["ModelServingEmailNotifications"]:
        '''email_notifications block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#email_notifications ModelServing#email_notifications}
        '''
        result = self._values.get("email_notifications")
        return typing.cast(typing.Optional["ModelServingEmailNotifications"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#id ModelServing#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rate_limits(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingRateLimits"]]]:
        '''rate_limits block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#rate_limits ModelServing#rate_limits}
        '''
        result = self._values.get("rate_limits")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingRateLimits"]]], result)

    @builtins.property
    def route_optimized(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#route_optimized ModelServing#route_optimized}.'''
        result = self._values.get("route_optimized")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingTags"]]]:
        '''tags block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#tags ModelServing#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingTags"]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["ModelServingTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#timeouts ModelServing#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["ModelServingTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigA",
    jsii_struct_bases=[],
    name_mapping={
        "auto_capture_config": "autoCaptureConfig",
        "served_entities": "servedEntities",
        "served_models": "servedModels",
        "traffic_config": "trafficConfig",
    },
)
class ModelServingConfigA:
    def __init__(
        self,
        *,
        auto_capture_config: typing.Optional[typing.Union["ModelServingConfigAutoCaptureConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        served_entities: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingConfigServedEntities", typing.Dict[builtins.str, typing.Any]]]]] = None,
        served_models: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingConfigServedModels", typing.Dict[builtins.str, typing.Any]]]]] = None,
        traffic_config: typing.Optional[typing.Union["ModelServingConfigTrafficConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param auto_capture_config: auto_capture_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#auto_capture_config ModelServing#auto_capture_config}
        :param served_entities: served_entities block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#served_entities ModelServing#served_entities}
        :param served_models: served_models block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#served_models ModelServing#served_models}
        :param traffic_config: traffic_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#traffic_config ModelServing#traffic_config}
        '''
        if isinstance(auto_capture_config, dict):
            auto_capture_config = ModelServingConfigAutoCaptureConfig(**auto_capture_config)
        if isinstance(traffic_config, dict):
            traffic_config = ModelServingConfigTrafficConfig(**traffic_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f209635c93e31eb79747b450ef07f331215993fe3c611af60329c1181395d96)
            check_type(argname="argument auto_capture_config", value=auto_capture_config, expected_type=type_hints["auto_capture_config"])
            check_type(argname="argument served_entities", value=served_entities, expected_type=type_hints["served_entities"])
            check_type(argname="argument served_models", value=served_models, expected_type=type_hints["served_models"])
            check_type(argname="argument traffic_config", value=traffic_config, expected_type=type_hints["traffic_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if auto_capture_config is not None:
            self._values["auto_capture_config"] = auto_capture_config
        if served_entities is not None:
            self._values["served_entities"] = served_entities
        if served_models is not None:
            self._values["served_models"] = served_models
        if traffic_config is not None:
            self._values["traffic_config"] = traffic_config

    @builtins.property
    def auto_capture_config(
        self,
    ) -> typing.Optional["ModelServingConfigAutoCaptureConfig"]:
        '''auto_capture_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#auto_capture_config ModelServing#auto_capture_config}
        '''
        result = self._values.get("auto_capture_config")
        return typing.cast(typing.Optional["ModelServingConfigAutoCaptureConfig"], result)

    @builtins.property
    def served_entities(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingConfigServedEntities"]]]:
        '''served_entities block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#served_entities ModelServing#served_entities}
        '''
        result = self._values.get("served_entities")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingConfigServedEntities"]]], result)

    @builtins.property
    def served_models(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingConfigServedModels"]]]:
        '''served_models block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#served_models ModelServing#served_models}
        '''
        result = self._values.get("served_models")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingConfigServedModels"]]], result)

    @builtins.property
    def traffic_config(self) -> typing.Optional["ModelServingConfigTrafficConfig"]:
        '''traffic_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#traffic_config ModelServing#traffic_config}
        '''
        result = self._values.get("traffic_config")
        return typing.cast(typing.Optional["ModelServingConfigTrafficConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigA(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingConfigAOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigAOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__39de19fd4e2e3b391a36cec3ae6b58c26f839e9b7717318f9c83712d464b8240)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAutoCaptureConfig")
    def put_auto_capture_config(
        self,
        *,
        catalog_name: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        schema_name: typing.Optional[builtins.str] = None,
        table_name_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param catalog_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#catalog_name ModelServing#catalog_name}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#enabled ModelServing#enabled}.
        :param schema_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#schema_name ModelServing#schema_name}.
        :param table_name_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#table_name_prefix ModelServing#table_name_prefix}.
        '''
        value = ModelServingConfigAutoCaptureConfig(
            catalog_name=catalog_name,
            enabled=enabled,
            schema_name=schema_name,
            table_name_prefix=table_name_prefix,
        )

        return typing.cast(None, jsii.invoke(self, "putAutoCaptureConfig", [value]))

    @jsii.member(jsii_name="putServedEntities")
    def put_served_entities(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingConfigServedEntities", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9147fd79fb2787c00f1d1d5fcb304fbacd554791d29739786eb47f169656f6f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putServedEntities", [value]))

    @jsii.member(jsii_name="putServedModels")
    def put_served_models(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingConfigServedModels", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64ca446d7fd23d5b8a13db8091cb8d50a52da9d34dc0d71f3453cc4df48cef58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putServedModels", [value]))

    @jsii.member(jsii_name="putTrafficConfig")
    def put_traffic_config(
        self,
        *,
        routes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingConfigTrafficConfigRoutes", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param routes: routes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#routes ModelServing#routes}
        '''
        value = ModelServingConfigTrafficConfig(routes=routes)

        return typing.cast(None, jsii.invoke(self, "putTrafficConfig", [value]))

    @jsii.member(jsii_name="resetAutoCaptureConfig")
    def reset_auto_capture_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoCaptureConfig", []))

    @jsii.member(jsii_name="resetServedEntities")
    def reset_served_entities(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServedEntities", []))

    @jsii.member(jsii_name="resetServedModels")
    def reset_served_models(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServedModels", []))

    @jsii.member(jsii_name="resetTrafficConfig")
    def reset_traffic_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTrafficConfig", []))

    @builtins.property
    @jsii.member(jsii_name="autoCaptureConfig")
    def auto_capture_config(
        self,
    ) -> "ModelServingConfigAutoCaptureConfigOutputReference":
        return typing.cast("ModelServingConfigAutoCaptureConfigOutputReference", jsii.get(self, "autoCaptureConfig"))

    @builtins.property
    @jsii.member(jsii_name="servedEntities")
    def served_entities(self) -> "ModelServingConfigServedEntitiesList":
        return typing.cast("ModelServingConfigServedEntitiesList", jsii.get(self, "servedEntities"))

    @builtins.property
    @jsii.member(jsii_name="servedModels")
    def served_models(self) -> "ModelServingConfigServedModelsList":
        return typing.cast("ModelServingConfigServedModelsList", jsii.get(self, "servedModels"))

    @builtins.property
    @jsii.member(jsii_name="trafficConfig")
    def traffic_config(self) -> "ModelServingConfigTrafficConfigOutputReference":
        return typing.cast("ModelServingConfigTrafficConfigOutputReference", jsii.get(self, "trafficConfig"))

    @builtins.property
    @jsii.member(jsii_name="autoCaptureConfigInput")
    def auto_capture_config_input(
        self,
    ) -> typing.Optional["ModelServingConfigAutoCaptureConfig"]:
        return typing.cast(typing.Optional["ModelServingConfigAutoCaptureConfig"], jsii.get(self, "autoCaptureConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="servedEntitiesInput")
    def served_entities_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingConfigServedEntities"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingConfigServedEntities"]]], jsii.get(self, "servedEntitiesInput"))

    @builtins.property
    @jsii.member(jsii_name="servedModelsInput")
    def served_models_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingConfigServedModels"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingConfigServedModels"]]], jsii.get(self, "servedModelsInput"))

    @builtins.property
    @jsii.member(jsii_name="trafficConfigInput")
    def traffic_config_input(
        self,
    ) -> typing.Optional["ModelServingConfigTrafficConfig"]:
        return typing.cast(typing.Optional["ModelServingConfigTrafficConfig"], jsii.get(self, "trafficConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ModelServingConfigA]:
        return typing.cast(typing.Optional[ModelServingConfigA], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ModelServingConfigA]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea9ca6d2b3625d2fe9064559e5ae3834b4a7d876e85a62ac1aedf940272c521b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigAutoCaptureConfig",
    jsii_struct_bases=[],
    name_mapping={
        "catalog_name": "catalogName",
        "enabled": "enabled",
        "schema_name": "schemaName",
        "table_name_prefix": "tableNamePrefix",
    },
)
class ModelServingConfigAutoCaptureConfig:
    def __init__(
        self,
        *,
        catalog_name: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        schema_name: typing.Optional[builtins.str] = None,
        table_name_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param catalog_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#catalog_name ModelServing#catalog_name}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#enabled ModelServing#enabled}.
        :param schema_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#schema_name ModelServing#schema_name}.
        :param table_name_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#table_name_prefix ModelServing#table_name_prefix}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebf8b2cb451924e6518496f1ef57ccd7f223277cadafa3d24b53b01883eebebe)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#catalog_name ModelServing#catalog_name}.'''
        result = self._values.get("catalog_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#enabled ModelServing#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def schema_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#schema_name ModelServing#schema_name}.'''
        result = self._values.get("schema_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def table_name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#table_name_prefix ModelServing#table_name_prefix}.'''
        result = self._values.get("table_name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigAutoCaptureConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingConfigAutoCaptureConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigAutoCaptureConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__67b5a32de74ec757f3fd7506a723ede01a5cbb72fe8a9e8f7f55a463e336efb9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d853ac5156bce5e1133f54bfb86fe697d8ede486fe731bfa34903faa9f25753c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f88136c1faf06edab8a7bc50c6c0024a15189007716a85bd8e4bdf7614acadd6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="schemaName")
    def schema_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schemaName"))

    @schema_name.setter
    def schema_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7efdad892ab787aa5957098c51102ad9ba0b8cbd0427823bc099599637c9475)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "schemaName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tableNamePrefix")
    def table_name_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tableNamePrefix"))

    @table_name_prefix.setter
    def table_name_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8067336e1bc5f02cec3e8f5ba3e25eee6475ed8fb875a21dee0d49ed8a33c796)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tableNamePrefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ModelServingConfigAutoCaptureConfig]:
        return typing.cast(typing.Optional[ModelServingConfigAutoCaptureConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingConfigAutoCaptureConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db8d7706dcbc2a14ef38e7145ac608ca0bbc7781baea610fd87821dbd601e6f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntities",
    jsii_struct_bases=[],
    name_mapping={
        "entity_name": "entityName",
        "entity_version": "entityVersion",
        "environment_vars": "environmentVars",
        "external_model": "externalModel",
        "instance_profile_arn": "instanceProfileArn",
        "max_provisioned_concurrency": "maxProvisionedConcurrency",
        "max_provisioned_throughput": "maxProvisionedThroughput",
        "min_provisioned_concurrency": "minProvisionedConcurrency",
        "min_provisioned_throughput": "minProvisionedThroughput",
        "name": "name",
        "provisioned_model_units": "provisionedModelUnits",
        "scale_to_zero_enabled": "scaleToZeroEnabled",
        "workload_size": "workloadSize",
        "workload_type": "workloadType",
    },
)
class ModelServingConfigServedEntities:
    def __init__(
        self,
        *,
        entity_name: typing.Optional[builtins.str] = None,
        entity_version: typing.Optional[builtins.str] = None,
        environment_vars: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        external_model: typing.Optional[typing.Union["ModelServingConfigServedEntitiesExternalModel", typing.Dict[builtins.str, typing.Any]]] = None,
        instance_profile_arn: typing.Optional[builtins.str] = None,
        max_provisioned_concurrency: typing.Optional[jsii.Number] = None,
        max_provisioned_throughput: typing.Optional[jsii.Number] = None,
        min_provisioned_concurrency: typing.Optional[jsii.Number] = None,
        min_provisioned_throughput: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        provisioned_model_units: typing.Optional[jsii.Number] = None,
        scale_to_zero_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        workload_size: typing.Optional[builtins.str] = None,
        workload_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param entity_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#entity_name ModelServing#entity_name}.
        :param entity_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#entity_version ModelServing#entity_version}.
        :param environment_vars: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#environment_vars ModelServing#environment_vars}.
        :param external_model: external_model block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#external_model ModelServing#external_model}
        :param instance_profile_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#instance_profile_arn ModelServing#instance_profile_arn}.
        :param max_provisioned_concurrency: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#max_provisioned_concurrency ModelServing#max_provisioned_concurrency}.
        :param max_provisioned_throughput: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#max_provisioned_throughput ModelServing#max_provisioned_throughput}.
        :param min_provisioned_concurrency: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#min_provisioned_concurrency ModelServing#min_provisioned_concurrency}.
        :param min_provisioned_throughput: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#min_provisioned_throughput ModelServing#min_provisioned_throughput}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#name ModelServing#name}.
        :param provisioned_model_units: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#provisioned_model_units ModelServing#provisioned_model_units}.
        :param scale_to_zero_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#scale_to_zero_enabled ModelServing#scale_to_zero_enabled}.
        :param workload_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#workload_size ModelServing#workload_size}.
        :param workload_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#workload_type ModelServing#workload_type}.
        '''
        if isinstance(external_model, dict):
            external_model = ModelServingConfigServedEntitiesExternalModel(**external_model)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9403ea38a33e4adf7cbe8b181e16d03e70709409f2f5b3cd020360a19e5995d8)
            check_type(argname="argument entity_name", value=entity_name, expected_type=type_hints["entity_name"])
            check_type(argname="argument entity_version", value=entity_version, expected_type=type_hints["entity_version"])
            check_type(argname="argument environment_vars", value=environment_vars, expected_type=type_hints["environment_vars"])
            check_type(argname="argument external_model", value=external_model, expected_type=type_hints["external_model"])
            check_type(argname="argument instance_profile_arn", value=instance_profile_arn, expected_type=type_hints["instance_profile_arn"])
            check_type(argname="argument max_provisioned_concurrency", value=max_provisioned_concurrency, expected_type=type_hints["max_provisioned_concurrency"])
            check_type(argname="argument max_provisioned_throughput", value=max_provisioned_throughput, expected_type=type_hints["max_provisioned_throughput"])
            check_type(argname="argument min_provisioned_concurrency", value=min_provisioned_concurrency, expected_type=type_hints["min_provisioned_concurrency"])
            check_type(argname="argument min_provisioned_throughput", value=min_provisioned_throughput, expected_type=type_hints["min_provisioned_throughput"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument provisioned_model_units", value=provisioned_model_units, expected_type=type_hints["provisioned_model_units"])
            check_type(argname="argument scale_to_zero_enabled", value=scale_to_zero_enabled, expected_type=type_hints["scale_to_zero_enabled"])
            check_type(argname="argument workload_size", value=workload_size, expected_type=type_hints["workload_size"])
            check_type(argname="argument workload_type", value=workload_type, expected_type=type_hints["workload_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if entity_name is not None:
            self._values["entity_name"] = entity_name
        if entity_version is not None:
            self._values["entity_version"] = entity_version
        if environment_vars is not None:
            self._values["environment_vars"] = environment_vars
        if external_model is not None:
            self._values["external_model"] = external_model
        if instance_profile_arn is not None:
            self._values["instance_profile_arn"] = instance_profile_arn
        if max_provisioned_concurrency is not None:
            self._values["max_provisioned_concurrency"] = max_provisioned_concurrency
        if max_provisioned_throughput is not None:
            self._values["max_provisioned_throughput"] = max_provisioned_throughput
        if min_provisioned_concurrency is not None:
            self._values["min_provisioned_concurrency"] = min_provisioned_concurrency
        if min_provisioned_throughput is not None:
            self._values["min_provisioned_throughput"] = min_provisioned_throughput
        if name is not None:
            self._values["name"] = name
        if provisioned_model_units is not None:
            self._values["provisioned_model_units"] = provisioned_model_units
        if scale_to_zero_enabled is not None:
            self._values["scale_to_zero_enabled"] = scale_to_zero_enabled
        if workload_size is not None:
            self._values["workload_size"] = workload_size
        if workload_type is not None:
            self._values["workload_type"] = workload_type

    @builtins.property
    def entity_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#entity_name ModelServing#entity_name}.'''
        result = self._values.get("entity_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def entity_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#entity_version ModelServing#entity_version}.'''
        result = self._values.get("entity_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment_vars(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#environment_vars ModelServing#environment_vars}.'''
        result = self._values.get("environment_vars")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def external_model(
        self,
    ) -> typing.Optional["ModelServingConfigServedEntitiesExternalModel"]:
        '''external_model block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#external_model ModelServing#external_model}
        '''
        result = self._values.get("external_model")
        return typing.cast(typing.Optional["ModelServingConfigServedEntitiesExternalModel"], result)

    @builtins.property
    def instance_profile_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#instance_profile_arn ModelServing#instance_profile_arn}.'''
        result = self._values.get("instance_profile_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_provisioned_concurrency(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#max_provisioned_concurrency ModelServing#max_provisioned_concurrency}.'''
        result = self._values.get("max_provisioned_concurrency")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_provisioned_throughput(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#max_provisioned_throughput ModelServing#max_provisioned_throughput}.'''
        result = self._values.get("max_provisioned_throughput")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_provisioned_concurrency(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#min_provisioned_concurrency ModelServing#min_provisioned_concurrency}.'''
        result = self._values.get("min_provisioned_concurrency")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_provisioned_throughput(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#min_provisioned_throughput ModelServing#min_provisioned_throughput}.'''
        result = self._values.get("min_provisioned_throughput")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#name ModelServing#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def provisioned_model_units(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#provisioned_model_units ModelServing#provisioned_model_units}.'''
        result = self._values.get("provisioned_model_units")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def scale_to_zero_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#scale_to_zero_enabled ModelServing#scale_to_zero_enabled}.'''
        result = self._values.get("scale_to_zero_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def workload_size(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#workload_size ModelServing#workload_size}.'''
        result = self._values.get("workload_size")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workload_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#workload_type ModelServing#workload_type}.'''
        result = self._values.get("workload_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigServedEntities(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModel",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "provider": "provider",
        "task": "task",
        "ai21_labs_config": "ai21LabsConfig",
        "amazon_bedrock_config": "amazonBedrockConfig",
        "anthropic_config": "anthropicConfig",
        "cohere_config": "cohereConfig",
        "custom_provider_config": "customProviderConfig",
        "databricks_model_serving_config": "databricksModelServingConfig",
        "google_cloud_vertex_ai_config": "googleCloudVertexAiConfig",
        "openai_config": "openaiConfig",
        "palm_config": "palmConfig",
    },
)
class ModelServingConfigServedEntitiesExternalModel:
    def __init__(
        self,
        *,
        name: builtins.str,
        provider: builtins.str,
        task: builtins.str,
        ai21_labs_config: typing.Optional[typing.Union["ModelServingConfigServedEntitiesExternalModelAi21LabsConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        amazon_bedrock_config: typing.Optional[typing.Union["ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        anthropic_config: typing.Optional[typing.Union["ModelServingConfigServedEntitiesExternalModelAnthropicConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        cohere_config: typing.Optional[typing.Union["ModelServingConfigServedEntitiesExternalModelCohereConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        custom_provider_config: typing.Optional[typing.Union["ModelServingConfigServedEntitiesExternalModelCustomProviderConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        databricks_model_serving_config: typing.Optional[typing.Union["ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        google_cloud_vertex_ai_config: typing.Optional[typing.Union["ModelServingConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        openai_config: typing.Optional[typing.Union["ModelServingConfigServedEntitiesExternalModelOpenaiConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        palm_config: typing.Optional[typing.Union["ModelServingConfigServedEntitiesExternalModelPalmConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#name ModelServing#name}.
        :param provider: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#provider ModelServing#provider}.
        :param task: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#task ModelServing#task}.
        :param ai21_labs_config: ai21labs_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#ai21labs_config ModelServing#ai21labs_config}
        :param amazon_bedrock_config: amazon_bedrock_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#amazon_bedrock_config ModelServing#amazon_bedrock_config}
        :param anthropic_config: anthropic_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#anthropic_config ModelServing#anthropic_config}
        :param cohere_config: cohere_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#cohere_config ModelServing#cohere_config}
        :param custom_provider_config: custom_provider_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#custom_provider_config ModelServing#custom_provider_config}
        :param databricks_model_serving_config: databricks_model_serving_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#databricks_model_serving_config ModelServing#databricks_model_serving_config}
        :param google_cloud_vertex_ai_config: google_cloud_vertex_ai_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#google_cloud_vertex_ai_config ModelServing#google_cloud_vertex_ai_config}
        :param openai_config: openai_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#openai_config ModelServing#openai_config}
        :param palm_config: palm_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#palm_config ModelServing#palm_config}
        '''
        if isinstance(ai21_labs_config, dict):
            ai21_labs_config = ModelServingConfigServedEntitiesExternalModelAi21LabsConfig(**ai21_labs_config)
        if isinstance(amazon_bedrock_config, dict):
            amazon_bedrock_config = ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig(**amazon_bedrock_config)
        if isinstance(anthropic_config, dict):
            anthropic_config = ModelServingConfigServedEntitiesExternalModelAnthropicConfig(**anthropic_config)
        if isinstance(cohere_config, dict):
            cohere_config = ModelServingConfigServedEntitiesExternalModelCohereConfig(**cohere_config)
        if isinstance(custom_provider_config, dict):
            custom_provider_config = ModelServingConfigServedEntitiesExternalModelCustomProviderConfig(**custom_provider_config)
        if isinstance(databricks_model_serving_config, dict):
            databricks_model_serving_config = ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig(**databricks_model_serving_config)
        if isinstance(google_cloud_vertex_ai_config, dict):
            google_cloud_vertex_ai_config = ModelServingConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig(**google_cloud_vertex_ai_config)
        if isinstance(openai_config, dict):
            openai_config = ModelServingConfigServedEntitiesExternalModelOpenaiConfig(**openai_config)
        if isinstance(palm_config, dict):
            palm_config = ModelServingConfigServedEntitiesExternalModelPalmConfig(**palm_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83b566f9c1a169a08e2dd41b8ad9ddbe16d86060bfdb3621f6f0b19ed393bf4b)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument task", value=task, expected_type=type_hints["task"])
            check_type(argname="argument ai21_labs_config", value=ai21_labs_config, expected_type=type_hints["ai21_labs_config"])
            check_type(argname="argument amazon_bedrock_config", value=amazon_bedrock_config, expected_type=type_hints["amazon_bedrock_config"])
            check_type(argname="argument anthropic_config", value=anthropic_config, expected_type=type_hints["anthropic_config"])
            check_type(argname="argument cohere_config", value=cohere_config, expected_type=type_hints["cohere_config"])
            check_type(argname="argument custom_provider_config", value=custom_provider_config, expected_type=type_hints["custom_provider_config"])
            check_type(argname="argument databricks_model_serving_config", value=databricks_model_serving_config, expected_type=type_hints["databricks_model_serving_config"])
            check_type(argname="argument google_cloud_vertex_ai_config", value=google_cloud_vertex_ai_config, expected_type=type_hints["google_cloud_vertex_ai_config"])
            check_type(argname="argument openai_config", value=openai_config, expected_type=type_hints["openai_config"])
            check_type(argname="argument palm_config", value=palm_config, expected_type=type_hints["palm_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "provider": provider,
            "task": task,
        }
        if ai21_labs_config is not None:
            self._values["ai21_labs_config"] = ai21_labs_config
        if amazon_bedrock_config is not None:
            self._values["amazon_bedrock_config"] = amazon_bedrock_config
        if anthropic_config is not None:
            self._values["anthropic_config"] = anthropic_config
        if cohere_config is not None:
            self._values["cohere_config"] = cohere_config
        if custom_provider_config is not None:
            self._values["custom_provider_config"] = custom_provider_config
        if databricks_model_serving_config is not None:
            self._values["databricks_model_serving_config"] = databricks_model_serving_config
        if google_cloud_vertex_ai_config is not None:
            self._values["google_cloud_vertex_ai_config"] = google_cloud_vertex_ai_config
        if openai_config is not None:
            self._values["openai_config"] = openai_config
        if palm_config is not None:
            self._values["palm_config"] = palm_config

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#name ModelServing#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def provider(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#provider ModelServing#provider}.'''
        result = self._values.get("provider")
        assert result is not None, "Required property 'provider' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def task(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#task ModelServing#task}.'''
        result = self._values.get("task")
        assert result is not None, "Required property 'task' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ai21_labs_config(
        self,
    ) -> typing.Optional["ModelServingConfigServedEntitiesExternalModelAi21LabsConfig"]:
        '''ai21labs_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#ai21labs_config ModelServing#ai21labs_config}
        '''
        result = self._values.get("ai21_labs_config")
        return typing.cast(typing.Optional["ModelServingConfigServedEntitiesExternalModelAi21LabsConfig"], result)

    @builtins.property
    def amazon_bedrock_config(
        self,
    ) -> typing.Optional["ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig"]:
        '''amazon_bedrock_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#amazon_bedrock_config ModelServing#amazon_bedrock_config}
        '''
        result = self._values.get("amazon_bedrock_config")
        return typing.cast(typing.Optional["ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig"], result)

    @builtins.property
    def anthropic_config(
        self,
    ) -> typing.Optional["ModelServingConfigServedEntitiesExternalModelAnthropicConfig"]:
        '''anthropic_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#anthropic_config ModelServing#anthropic_config}
        '''
        result = self._values.get("anthropic_config")
        return typing.cast(typing.Optional["ModelServingConfigServedEntitiesExternalModelAnthropicConfig"], result)

    @builtins.property
    def cohere_config(
        self,
    ) -> typing.Optional["ModelServingConfigServedEntitiesExternalModelCohereConfig"]:
        '''cohere_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#cohere_config ModelServing#cohere_config}
        '''
        result = self._values.get("cohere_config")
        return typing.cast(typing.Optional["ModelServingConfigServedEntitiesExternalModelCohereConfig"], result)

    @builtins.property
    def custom_provider_config(
        self,
    ) -> typing.Optional["ModelServingConfigServedEntitiesExternalModelCustomProviderConfig"]:
        '''custom_provider_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#custom_provider_config ModelServing#custom_provider_config}
        '''
        result = self._values.get("custom_provider_config")
        return typing.cast(typing.Optional["ModelServingConfigServedEntitiesExternalModelCustomProviderConfig"], result)

    @builtins.property
    def databricks_model_serving_config(
        self,
    ) -> typing.Optional["ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig"]:
        '''databricks_model_serving_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#databricks_model_serving_config ModelServing#databricks_model_serving_config}
        '''
        result = self._values.get("databricks_model_serving_config")
        return typing.cast(typing.Optional["ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig"], result)

    @builtins.property
    def google_cloud_vertex_ai_config(
        self,
    ) -> typing.Optional["ModelServingConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig"]:
        '''google_cloud_vertex_ai_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#google_cloud_vertex_ai_config ModelServing#google_cloud_vertex_ai_config}
        '''
        result = self._values.get("google_cloud_vertex_ai_config")
        return typing.cast(typing.Optional["ModelServingConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig"], result)

    @builtins.property
    def openai_config(
        self,
    ) -> typing.Optional["ModelServingConfigServedEntitiesExternalModelOpenaiConfig"]:
        '''openai_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#openai_config ModelServing#openai_config}
        '''
        result = self._values.get("openai_config")
        return typing.cast(typing.Optional["ModelServingConfigServedEntitiesExternalModelOpenaiConfig"], result)

    @builtins.property
    def palm_config(
        self,
    ) -> typing.Optional["ModelServingConfigServedEntitiesExternalModelPalmConfig"]:
        '''palm_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#palm_config ModelServing#palm_config}
        '''
        result = self._values.get("palm_config")
        return typing.cast(typing.Optional["ModelServingConfigServedEntitiesExternalModelPalmConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigServedEntitiesExternalModel(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelAi21LabsConfig",
    jsii_struct_bases=[],
    name_mapping={
        "ai21_labs_api_key": "ai21LabsApiKey",
        "ai21_labs_api_key_plaintext": "ai21LabsApiKeyPlaintext",
    },
)
class ModelServingConfigServedEntitiesExternalModelAi21LabsConfig:
    def __init__(
        self,
        *,
        ai21_labs_api_key: typing.Optional[builtins.str] = None,
        ai21_labs_api_key_plaintext: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param ai21_labs_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#ai21labs_api_key ModelServing#ai21labs_api_key}.
        :param ai21_labs_api_key_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#ai21labs_api_key_plaintext ModelServing#ai21labs_api_key_plaintext}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c0ee9dc2d1327236ae97d5c3fe5c5338c3794a40d2d88c02560c83925676710)
            check_type(argname="argument ai21_labs_api_key", value=ai21_labs_api_key, expected_type=type_hints["ai21_labs_api_key"])
            check_type(argname="argument ai21_labs_api_key_plaintext", value=ai21_labs_api_key_plaintext, expected_type=type_hints["ai21_labs_api_key_plaintext"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if ai21_labs_api_key is not None:
            self._values["ai21_labs_api_key"] = ai21_labs_api_key
        if ai21_labs_api_key_plaintext is not None:
            self._values["ai21_labs_api_key_plaintext"] = ai21_labs_api_key_plaintext

    @builtins.property
    def ai21_labs_api_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#ai21labs_api_key ModelServing#ai21labs_api_key}.'''
        result = self._values.get("ai21_labs_api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ai21_labs_api_key_plaintext(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#ai21labs_api_key_plaintext ModelServing#ai21labs_api_key_plaintext}.'''
        result = self._values.get("ai21_labs_api_key_plaintext")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigServedEntitiesExternalModelAi21LabsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingConfigServedEntitiesExternalModelAi21LabsConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelAi21LabsConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ec48b6283533d5b4c9aeb09b046668b46db9832fe3be06b87645bbc1fe6b77af)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAi21LabsApiKey")
    def reset_ai21_labs_api_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAi21LabsApiKey", []))

    @jsii.member(jsii_name="resetAi21LabsApiKeyPlaintext")
    def reset_ai21_labs_api_key_plaintext(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAi21LabsApiKeyPlaintext", []))

    @builtins.property
    @jsii.member(jsii_name="ai21LabsApiKeyInput")
    def ai21_labs_api_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ai21LabsApiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="ai21LabsApiKeyPlaintextInput")
    def ai21_labs_api_key_plaintext_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ai21LabsApiKeyPlaintextInput"))

    @builtins.property
    @jsii.member(jsii_name="ai21LabsApiKey")
    def ai21_labs_api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ai21LabsApiKey"))

    @ai21_labs_api_key.setter
    def ai21_labs_api_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__edd2ee0da33d9d6eea9698dda6843afedb835973ae8037fa09e4c0271c49a7d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ai21LabsApiKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ai21LabsApiKeyPlaintext")
    def ai21_labs_api_key_plaintext(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ai21LabsApiKeyPlaintext"))

    @ai21_labs_api_key_plaintext.setter
    def ai21_labs_api_key_plaintext(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d282adb0fc60caaab7e97d6b4dad4ad40925553dddb52a97b4ff71574fcc04b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ai21LabsApiKeyPlaintext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelAi21LabsConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelAi21LabsConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingConfigServedEntitiesExternalModelAi21LabsConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b145ea06e1bd8516ff0cc11cbf9fd2f0e536da81a5b9c4cbc7ff9c0165bb85a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig",
    jsii_struct_bases=[],
    name_mapping={
        "aws_region": "awsRegion",
        "bedrock_provider": "bedrockProvider",
        "aws_access_key_id": "awsAccessKeyId",
        "aws_access_key_id_plaintext": "awsAccessKeyIdPlaintext",
        "aws_secret_access_key": "awsSecretAccessKey",
        "aws_secret_access_key_plaintext": "awsSecretAccessKeyPlaintext",
        "instance_profile_arn": "instanceProfileArn",
    },
)
class ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig:
    def __init__(
        self,
        *,
        aws_region: builtins.str,
        bedrock_provider: builtins.str,
        aws_access_key_id: typing.Optional[builtins.str] = None,
        aws_access_key_id_plaintext: typing.Optional[builtins.str] = None,
        aws_secret_access_key: typing.Optional[builtins.str] = None,
        aws_secret_access_key_plaintext: typing.Optional[builtins.str] = None,
        instance_profile_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param aws_region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#aws_region ModelServing#aws_region}.
        :param bedrock_provider: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#bedrock_provider ModelServing#bedrock_provider}.
        :param aws_access_key_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#aws_access_key_id ModelServing#aws_access_key_id}.
        :param aws_access_key_id_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#aws_access_key_id_plaintext ModelServing#aws_access_key_id_plaintext}.
        :param aws_secret_access_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#aws_secret_access_key ModelServing#aws_secret_access_key}.
        :param aws_secret_access_key_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#aws_secret_access_key_plaintext ModelServing#aws_secret_access_key_plaintext}.
        :param instance_profile_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#instance_profile_arn ModelServing#instance_profile_arn}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90dd82469e7808adf0a9158c33b32ac196f631841b5b828af93d7f461ae108ca)
            check_type(argname="argument aws_region", value=aws_region, expected_type=type_hints["aws_region"])
            check_type(argname="argument bedrock_provider", value=bedrock_provider, expected_type=type_hints["bedrock_provider"])
            check_type(argname="argument aws_access_key_id", value=aws_access_key_id, expected_type=type_hints["aws_access_key_id"])
            check_type(argname="argument aws_access_key_id_plaintext", value=aws_access_key_id_plaintext, expected_type=type_hints["aws_access_key_id_plaintext"])
            check_type(argname="argument aws_secret_access_key", value=aws_secret_access_key, expected_type=type_hints["aws_secret_access_key"])
            check_type(argname="argument aws_secret_access_key_plaintext", value=aws_secret_access_key_plaintext, expected_type=type_hints["aws_secret_access_key_plaintext"])
            check_type(argname="argument instance_profile_arn", value=instance_profile_arn, expected_type=type_hints["instance_profile_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "aws_region": aws_region,
            "bedrock_provider": bedrock_provider,
        }
        if aws_access_key_id is not None:
            self._values["aws_access_key_id"] = aws_access_key_id
        if aws_access_key_id_plaintext is not None:
            self._values["aws_access_key_id_plaintext"] = aws_access_key_id_plaintext
        if aws_secret_access_key is not None:
            self._values["aws_secret_access_key"] = aws_secret_access_key
        if aws_secret_access_key_plaintext is not None:
            self._values["aws_secret_access_key_plaintext"] = aws_secret_access_key_plaintext
        if instance_profile_arn is not None:
            self._values["instance_profile_arn"] = instance_profile_arn

    @builtins.property
    def aws_region(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#aws_region ModelServing#aws_region}.'''
        result = self._values.get("aws_region")
        assert result is not None, "Required property 'aws_region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bedrock_provider(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#bedrock_provider ModelServing#bedrock_provider}.'''
        result = self._values.get("bedrock_provider")
        assert result is not None, "Required property 'bedrock_provider' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def aws_access_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#aws_access_key_id ModelServing#aws_access_key_id}.'''
        result = self._values.get("aws_access_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_access_key_id_plaintext(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#aws_access_key_id_plaintext ModelServing#aws_access_key_id_plaintext}.'''
        result = self._values.get("aws_access_key_id_plaintext")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_secret_access_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#aws_secret_access_key ModelServing#aws_secret_access_key}.'''
        result = self._values.get("aws_secret_access_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_secret_access_key_plaintext(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#aws_secret_access_key_plaintext ModelServing#aws_secret_access_key_plaintext}.'''
        result = self._values.get("aws_secret_access_key_plaintext")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_profile_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#instance_profile_arn ModelServing#instance_profile_arn}.'''
        result = self._values.get("instance_profile_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3f80d852ac84bb277b80e781606f1e4dd2b8f0b03f4b4f4ce3d3d3f4f752061e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAwsAccessKeyId")
    def reset_aws_access_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsAccessKeyId", []))

    @jsii.member(jsii_name="resetAwsAccessKeyIdPlaintext")
    def reset_aws_access_key_id_plaintext(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsAccessKeyIdPlaintext", []))

    @jsii.member(jsii_name="resetAwsSecretAccessKey")
    def reset_aws_secret_access_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsSecretAccessKey", []))

    @jsii.member(jsii_name="resetAwsSecretAccessKeyPlaintext")
    def reset_aws_secret_access_key_plaintext(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsSecretAccessKeyPlaintext", []))

    @jsii.member(jsii_name="resetInstanceProfileArn")
    def reset_instance_profile_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceProfileArn", []))

    @builtins.property
    @jsii.member(jsii_name="awsAccessKeyIdInput")
    def aws_access_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsAccessKeyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="awsAccessKeyIdPlaintextInput")
    def aws_access_key_id_plaintext_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsAccessKeyIdPlaintextInput"))

    @builtins.property
    @jsii.member(jsii_name="awsRegionInput")
    def aws_region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsRegionInput"))

    @builtins.property
    @jsii.member(jsii_name="awsSecretAccessKeyInput")
    def aws_secret_access_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsSecretAccessKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="awsSecretAccessKeyPlaintextInput")
    def aws_secret_access_key_plaintext_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsSecretAccessKeyPlaintextInput"))

    @builtins.property
    @jsii.member(jsii_name="bedrockProviderInput")
    def bedrock_provider_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bedrockProviderInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceProfileArnInput")
    def instance_profile_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceProfileArnInput"))

    @builtins.property
    @jsii.member(jsii_name="awsAccessKeyId")
    def aws_access_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsAccessKeyId"))

    @aws_access_key_id.setter
    def aws_access_key_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a72a91085af2cd622a5c4761f65046e6b7f2a78c1bd2cb36a4dcac5671bdb1f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsAccessKeyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="awsAccessKeyIdPlaintext")
    def aws_access_key_id_plaintext(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsAccessKeyIdPlaintext"))

    @aws_access_key_id_plaintext.setter
    def aws_access_key_id_plaintext(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8133bf37f3c85f19bce5abc03f20201edaf6fc8221ffe5df7777c5c8c1ac6c12)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsAccessKeyIdPlaintext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="awsRegion")
    def aws_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsRegion"))

    @aws_region.setter
    def aws_region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d32624b5e375ebc73dc077d306d42c18f51d38659a7f1881d39b43af1a5693cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsRegion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="awsSecretAccessKey")
    def aws_secret_access_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsSecretAccessKey"))

    @aws_secret_access_key.setter
    def aws_secret_access_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8628231e26f171719205ff1342000dc222ab9ce51be0e6d9ad62573609694543)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsSecretAccessKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="awsSecretAccessKeyPlaintext")
    def aws_secret_access_key_plaintext(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsSecretAccessKeyPlaintext"))

    @aws_secret_access_key_plaintext.setter
    def aws_secret_access_key_plaintext(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ab49af62430f7573f7b0d6955752f7f9cc4beb701051d0a3942de42d042983f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsSecretAccessKeyPlaintext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bedrockProvider")
    def bedrock_provider(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bedrockProvider"))

    @bedrock_provider.setter
    def bedrock_provider(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c269a46ec95800bb1f6e9e676994c75ad9c42fc985f8a721b147636f09ea1add)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bedrockProvider", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instanceProfileArn")
    def instance_profile_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceProfileArn"))

    @instance_profile_arn.setter
    def instance_profile_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff440325774f103952ce806a49c369c83ffba7c7a8f32abfb9bab976196c78b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceProfileArn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ee68940f0acb9b42fcf03a36fc4c76724008a5a5bd4d0a07014abf027865cf5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelAnthropicConfig",
    jsii_struct_bases=[],
    name_mapping={
        "anthropic_api_key": "anthropicApiKey",
        "anthropic_api_key_plaintext": "anthropicApiKeyPlaintext",
    },
)
class ModelServingConfigServedEntitiesExternalModelAnthropicConfig:
    def __init__(
        self,
        *,
        anthropic_api_key: typing.Optional[builtins.str] = None,
        anthropic_api_key_plaintext: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param anthropic_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#anthropic_api_key ModelServing#anthropic_api_key}.
        :param anthropic_api_key_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#anthropic_api_key_plaintext ModelServing#anthropic_api_key_plaintext}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__218f5a41e3d93d07362768598313f8b6139fdb7702b337199d420fb89c368361)
            check_type(argname="argument anthropic_api_key", value=anthropic_api_key, expected_type=type_hints["anthropic_api_key"])
            check_type(argname="argument anthropic_api_key_plaintext", value=anthropic_api_key_plaintext, expected_type=type_hints["anthropic_api_key_plaintext"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if anthropic_api_key is not None:
            self._values["anthropic_api_key"] = anthropic_api_key
        if anthropic_api_key_plaintext is not None:
            self._values["anthropic_api_key_plaintext"] = anthropic_api_key_plaintext

    @builtins.property
    def anthropic_api_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#anthropic_api_key ModelServing#anthropic_api_key}.'''
        result = self._values.get("anthropic_api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def anthropic_api_key_plaintext(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#anthropic_api_key_plaintext ModelServing#anthropic_api_key_plaintext}.'''
        result = self._values.get("anthropic_api_key_plaintext")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigServedEntitiesExternalModelAnthropicConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingConfigServedEntitiesExternalModelAnthropicConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelAnthropicConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fd5800a1e5ff7cbebc7e2b6b8a7272a5844a5b75fcb4202bafab87d419f8cb2f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAnthropicApiKey")
    def reset_anthropic_api_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAnthropicApiKey", []))

    @jsii.member(jsii_name="resetAnthropicApiKeyPlaintext")
    def reset_anthropic_api_key_plaintext(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAnthropicApiKeyPlaintext", []))

    @builtins.property
    @jsii.member(jsii_name="anthropicApiKeyInput")
    def anthropic_api_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "anthropicApiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="anthropicApiKeyPlaintextInput")
    def anthropic_api_key_plaintext_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "anthropicApiKeyPlaintextInput"))

    @builtins.property
    @jsii.member(jsii_name="anthropicApiKey")
    def anthropic_api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "anthropicApiKey"))

    @anthropic_api_key.setter
    def anthropic_api_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b023fe17c98d566c8fac5e33cf5eab2d6ab8b5f2aac678aab6bc169b3745228)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "anthropicApiKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="anthropicApiKeyPlaintext")
    def anthropic_api_key_plaintext(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "anthropicApiKeyPlaintext"))

    @anthropic_api_key_plaintext.setter
    def anthropic_api_key_plaintext(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5848ba1341bb9431c45b0b69f1dac978fd02a025321db02af075278c3f843a68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "anthropicApiKeyPlaintext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelAnthropicConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelAnthropicConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingConfigServedEntitiesExternalModelAnthropicConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a64d693f11d3435c35e4ed3c8d0458aadee5227005cf5947d024560f5846c673)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelCohereConfig",
    jsii_struct_bases=[],
    name_mapping={
        "cohere_api_base": "cohereApiBase",
        "cohere_api_key": "cohereApiKey",
        "cohere_api_key_plaintext": "cohereApiKeyPlaintext",
    },
)
class ModelServingConfigServedEntitiesExternalModelCohereConfig:
    def __init__(
        self,
        *,
        cohere_api_base: typing.Optional[builtins.str] = None,
        cohere_api_key: typing.Optional[builtins.str] = None,
        cohere_api_key_plaintext: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cohere_api_base: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#cohere_api_base ModelServing#cohere_api_base}.
        :param cohere_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#cohere_api_key ModelServing#cohere_api_key}.
        :param cohere_api_key_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#cohere_api_key_plaintext ModelServing#cohere_api_key_plaintext}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0dcb9995c75742d273441f3c12353f2a8a2afcd41c6de6865efd4504723a0455)
            check_type(argname="argument cohere_api_base", value=cohere_api_base, expected_type=type_hints["cohere_api_base"])
            check_type(argname="argument cohere_api_key", value=cohere_api_key, expected_type=type_hints["cohere_api_key"])
            check_type(argname="argument cohere_api_key_plaintext", value=cohere_api_key_plaintext, expected_type=type_hints["cohere_api_key_plaintext"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cohere_api_base is not None:
            self._values["cohere_api_base"] = cohere_api_base
        if cohere_api_key is not None:
            self._values["cohere_api_key"] = cohere_api_key
        if cohere_api_key_plaintext is not None:
            self._values["cohere_api_key_plaintext"] = cohere_api_key_plaintext

    @builtins.property
    def cohere_api_base(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#cohere_api_base ModelServing#cohere_api_base}.'''
        result = self._values.get("cohere_api_base")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cohere_api_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#cohere_api_key ModelServing#cohere_api_key}.'''
        result = self._values.get("cohere_api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cohere_api_key_plaintext(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#cohere_api_key_plaintext ModelServing#cohere_api_key_plaintext}.'''
        result = self._values.get("cohere_api_key_plaintext")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigServedEntitiesExternalModelCohereConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingConfigServedEntitiesExternalModelCohereConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelCohereConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__49817b6641b2bf6dfba75fda89240974cad2adba5d155e98e85da7ac13731ecb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCohereApiBase")
    def reset_cohere_api_base(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCohereApiBase", []))

    @jsii.member(jsii_name="resetCohereApiKey")
    def reset_cohere_api_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCohereApiKey", []))

    @jsii.member(jsii_name="resetCohereApiKeyPlaintext")
    def reset_cohere_api_key_plaintext(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCohereApiKeyPlaintext", []))

    @builtins.property
    @jsii.member(jsii_name="cohereApiBaseInput")
    def cohere_api_base_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cohereApiBaseInput"))

    @builtins.property
    @jsii.member(jsii_name="cohereApiKeyInput")
    def cohere_api_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cohereApiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="cohereApiKeyPlaintextInput")
    def cohere_api_key_plaintext_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cohereApiKeyPlaintextInput"))

    @builtins.property
    @jsii.member(jsii_name="cohereApiBase")
    def cohere_api_base(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cohereApiBase"))

    @cohere_api_base.setter
    def cohere_api_base(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8016e448b70640ac1993c1def32afbb4bfa764c9638be4feb6b7c884c6ea246a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cohereApiBase", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cohereApiKey")
    def cohere_api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cohereApiKey"))

    @cohere_api_key.setter
    def cohere_api_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75b46b4f09d11ea820e7e30599eccb4dc33c186404ec5c41a642550f3c870525)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cohereApiKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cohereApiKeyPlaintext")
    def cohere_api_key_plaintext(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cohereApiKeyPlaintext"))

    @cohere_api_key_plaintext.setter
    def cohere_api_key_plaintext(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a6130a96a14102da4be21524f02627b913c1cc764316e95851a5760493b2a35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cohereApiKeyPlaintext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelCohereConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelCohereConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingConfigServedEntitiesExternalModelCohereConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a60f8a840727e7cd3ce21617d1ae19459196adef749e8e5126eb54fd90b745a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelCustomProviderConfig",
    jsii_struct_bases=[],
    name_mapping={
        "custom_provider_url": "customProviderUrl",
        "api_key_auth": "apiKeyAuth",
        "bearer_token_auth": "bearerTokenAuth",
    },
)
class ModelServingConfigServedEntitiesExternalModelCustomProviderConfig:
    def __init__(
        self,
        *,
        custom_provider_url: builtins.str,
        api_key_auth: typing.Optional[typing.Union["ModelServingConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth", typing.Dict[builtins.str, typing.Any]]] = None,
        bearer_token_auth: typing.Optional[typing.Union["ModelServingConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param custom_provider_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#custom_provider_url ModelServing#custom_provider_url}.
        :param api_key_auth: api_key_auth block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#api_key_auth ModelServing#api_key_auth}
        :param bearer_token_auth: bearer_token_auth block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#bearer_token_auth ModelServing#bearer_token_auth}
        '''
        if isinstance(api_key_auth, dict):
            api_key_auth = ModelServingConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth(**api_key_auth)
        if isinstance(bearer_token_auth, dict):
            bearer_token_auth = ModelServingConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth(**bearer_token_auth)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__acefb3c90fd5fa5a76c875c3edd9195f1cd31e1134ec47148b34f99ba4061ef3)
            check_type(argname="argument custom_provider_url", value=custom_provider_url, expected_type=type_hints["custom_provider_url"])
            check_type(argname="argument api_key_auth", value=api_key_auth, expected_type=type_hints["api_key_auth"])
            check_type(argname="argument bearer_token_auth", value=bearer_token_auth, expected_type=type_hints["bearer_token_auth"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "custom_provider_url": custom_provider_url,
        }
        if api_key_auth is not None:
            self._values["api_key_auth"] = api_key_auth
        if bearer_token_auth is not None:
            self._values["bearer_token_auth"] = bearer_token_auth

    @builtins.property
    def custom_provider_url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#custom_provider_url ModelServing#custom_provider_url}.'''
        result = self._values.get("custom_provider_url")
        assert result is not None, "Required property 'custom_provider_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def api_key_auth(
        self,
    ) -> typing.Optional["ModelServingConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth"]:
        '''api_key_auth block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#api_key_auth ModelServing#api_key_auth}
        '''
        result = self._values.get("api_key_auth")
        return typing.cast(typing.Optional["ModelServingConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth"], result)

    @builtins.property
    def bearer_token_auth(
        self,
    ) -> typing.Optional["ModelServingConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth"]:
        '''bearer_token_auth block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#bearer_token_auth ModelServing#bearer_token_auth}
        '''
        result = self._values.get("bearer_token_auth")
        return typing.cast(typing.Optional["ModelServingConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigServedEntitiesExternalModelCustomProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value", "value_plaintext": "valuePlaintext"},
)
class ModelServingConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth:
    def __init__(
        self,
        *,
        key: builtins.str,
        value: typing.Optional[builtins.str] = None,
        value_plaintext: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#key ModelServing#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#value ModelServing#value}.
        :param value_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#value_plaintext ModelServing#value_plaintext}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ea403d6efff0b91c769a3d4cea1936ff5b2b203ec568a52461627aeedec6e00)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
            check_type(argname="argument value_plaintext", value=value_plaintext, expected_type=type_hints["value_plaintext"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
        }
        if value is not None:
            self._values["value"] = value
        if value_plaintext is not None:
            self._values["value_plaintext"] = value_plaintext

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#key ModelServing#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#value ModelServing#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value_plaintext(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#value_plaintext ModelServing#value_plaintext}.'''
        result = self._values.get("value_plaintext")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuthOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuthOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__eb360f86787ac25d68a33293ff2c056a6b2faa2487661cca7478588ebea83025)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @jsii.member(jsii_name="resetValuePlaintext")
    def reset_value_plaintext(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValuePlaintext", []))

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="valuePlaintextInput")
    def value_plaintext_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valuePlaintextInput"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6bc6d6c742e118629349376f8d1bb985bd4b7303c79ed1a78c4dcb66d48cdec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f7c1ba7d61da2693c8d6ea2ea2ea903f5d998978a45aebefaad253f32aa1ca9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="valuePlaintext")
    def value_plaintext(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "valuePlaintext"))

    @value_plaintext.setter
    def value_plaintext(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28be31ba7f11dd44b5caca28fedf2aed1c80dbef628d53facf1a5cb77745fb5c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "valuePlaintext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d46c545b237432a8ed3467497d409a2717ed45b59bedd0c1b670b50c7f7b6edc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth",
    jsii_struct_bases=[],
    name_mapping={"token": "token", "token_plaintext": "tokenPlaintext"},
)
class ModelServingConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth:
    def __init__(
        self,
        *,
        token: typing.Optional[builtins.str] = None,
        token_plaintext: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#token ModelServing#token}.
        :param token_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#token_plaintext ModelServing#token_plaintext}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ea00f39f8811accc2ea3a396d131a387872021812c42728c8bd01be5c259c45)
            check_type(argname="argument token", value=token, expected_type=type_hints["token"])
            check_type(argname="argument token_plaintext", value=token_plaintext, expected_type=type_hints["token_plaintext"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if token is not None:
            self._values["token"] = token
        if token_plaintext is not None:
            self._values["token_plaintext"] = token_plaintext

    @builtins.property
    def token(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#token ModelServing#token}.'''
        result = self._values.get("token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def token_plaintext(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#token_plaintext ModelServing#token_plaintext}.'''
        result = self._values.get("token_plaintext")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuthOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuthOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__97342de35125738cd1c3cbc111f9b1c2ba76ed4c8aa3cc9275528ae1734519f5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetToken")
    def reset_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetToken", []))

    @jsii.member(jsii_name="resetTokenPlaintext")
    def reset_token_plaintext(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokenPlaintext", []))

    @builtins.property
    @jsii.member(jsii_name="tokenInput")
    def token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenPlaintextInput")
    def token_plaintext_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenPlaintextInput"))

    @builtins.property
    @jsii.member(jsii_name="token")
    def token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "token"))

    @token.setter
    def token(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf74d09ad8e05e915922ff0858d4ee052a6377dd46fc3b4c4c1b87c4eb5bbf86)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "token", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenPlaintext")
    def token_plaintext(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tokenPlaintext"))

    @token_plaintext.setter
    def token_plaintext(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7108bcd113e8183cf6d0da55f0c9684e2d52c129d2dcde5782045005aa2b94cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenPlaintext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04f8b7006e2f5c6e0736f875b49ebccb885528af2fca63a61ed59f37fb7802a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ModelServingConfigServedEntitiesExternalModelCustomProviderConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelCustomProviderConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__880bdcf1ed230d530d3ae04098e219309eb2abc4f4202744bc573219507d067b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putApiKeyAuth")
    def put_api_key_auth(
        self,
        *,
        key: builtins.str,
        value: typing.Optional[builtins.str] = None,
        value_plaintext: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#key ModelServing#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#value ModelServing#value}.
        :param value_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#value_plaintext ModelServing#value_plaintext}.
        '''
        value_ = ModelServingConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth(
            key=key, value=value, value_plaintext=value_plaintext
        )

        return typing.cast(None, jsii.invoke(self, "putApiKeyAuth", [value_]))

    @jsii.member(jsii_name="putBearerTokenAuth")
    def put_bearer_token_auth(
        self,
        *,
        token: typing.Optional[builtins.str] = None,
        token_plaintext: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#token ModelServing#token}.
        :param token_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#token_plaintext ModelServing#token_plaintext}.
        '''
        value = ModelServingConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth(
            token=token, token_plaintext=token_plaintext
        )

        return typing.cast(None, jsii.invoke(self, "putBearerTokenAuth", [value]))

    @jsii.member(jsii_name="resetApiKeyAuth")
    def reset_api_key_auth(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiKeyAuth", []))

    @jsii.member(jsii_name="resetBearerTokenAuth")
    def reset_bearer_token_auth(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBearerTokenAuth", []))

    @builtins.property
    @jsii.member(jsii_name="apiKeyAuth")
    def api_key_auth(
        self,
    ) -> ModelServingConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuthOutputReference:
        return typing.cast(ModelServingConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuthOutputReference, jsii.get(self, "apiKeyAuth"))

    @builtins.property
    @jsii.member(jsii_name="bearerTokenAuth")
    def bearer_token_auth(
        self,
    ) -> ModelServingConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuthOutputReference:
        return typing.cast(ModelServingConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuthOutputReference, jsii.get(self, "bearerTokenAuth"))

    @builtins.property
    @jsii.member(jsii_name="apiKeyAuthInput")
    def api_key_auth_input(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth], jsii.get(self, "apiKeyAuthInput"))

    @builtins.property
    @jsii.member(jsii_name="bearerTokenAuthInput")
    def bearer_token_auth_input(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth], jsii.get(self, "bearerTokenAuthInput"))

    @builtins.property
    @jsii.member(jsii_name="customProviderUrlInput")
    def custom_provider_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customProviderUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="customProviderUrl")
    def custom_provider_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customProviderUrl"))

    @custom_provider_url.setter
    def custom_provider_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01a15497db1e35c1dd1d02b3b151d7aed2ff8c599d1a8b26c31431387a3801d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customProviderUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelCustomProviderConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelCustomProviderConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingConfigServedEntitiesExternalModelCustomProviderConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1bb9571a3126b8b0f119d9c6b50472a9499d0203230f0faa4f4a15a562554bba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig",
    jsii_struct_bases=[],
    name_mapping={
        "databricks_workspace_url": "databricksWorkspaceUrl",
        "databricks_api_token": "databricksApiToken",
        "databricks_api_token_plaintext": "databricksApiTokenPlaintext",
    },
)
class ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig:
    def __init__(
        self,
        *,
        databricks_workspace_url: builtins.str,
        databricks_api_token: typing.Optional[builtins.str] = None,
        databricks_api_token_plaintext: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param databricks_workspace_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#databricks_workspace_url ModelServing#databricks_workspace_url}.
        :param databricks_api_token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#databricks_api_token ModelServing#databricks_api_token}.
        :param databricks_api_token_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#databricks_api_token_plaintext ModelServing#databricks_api_token_plaintext}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc7d014e30705b1d364c1fdbb4051d5a7521e5c6874f14751d9b24ade962ccae)
            check_type(argname="argument databricks_workspace_url", value=databricks_workspace_url, expected_type=type_hints["databricks_workspace_url"])
            check_type(argname="argument databricks_api_token", value=databricks_api_token, expected_type=type_hints["databricks_api_token"])
            check_type(argname="argument databricks_api_token_plaintext", value=databricks_api_token_plaintext, expected_type=type_hints["databricks_api_token_plaintext"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "databricks_workspace_url": databricks_workspace_url,
        }
        if databricks_api_token is not None:
            self._values["databricks_api_token"] = databricks_api_token
        if databricks_api_token_plaintext is not None:
            self._values["databricks_api_token_plaintext"] = databricks_api_token_plaintext

    @builtins.property
    def databricks_workspace_url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#databricks_workspace_url ModelServing#databricks_workspace_url}.'''
        result = self._values.get("databricks_workspace_url")
        assert result is not None, "Required property 'databricks_workspace_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def databricks_api_token(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#databricks_api_token ModelServing#databricks_api_token}.'''
        result = self._values.get("databricks_api_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def databricks_api_token_plaintext(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#databricks_api_token_plaintext ModelServing#databricks_api_token_plaintext}.'''
        result = self._values.get("databricks_api_token_plaintext")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6cda49ad248f1b0eb4e12f1d86fc09682a280a677deaf69662836e58db84f468)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDatabricksApiToken")
    def reset_databricks_api_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatabricksApiToken", []))

    @jsii.member(jsii_name="resetDatabricksApiTokenPlaintext")
    def reset_databricks_api_token_plaintext(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatabricksApiTokenPlaintext", []))

    @builtins.property
    @jsii.member(jsii_name="databricksApiTokenInput")
    def databricks_api_token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databricksApiTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="databricksApiTokenPlaintextInput")
    def databricks_api_token_plaintext_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databricksApiTokenPlaintextInput"))

    @builtins.property
    @jsii.member(jsii_name="databricksWorkspaceUrlInput")
    def databricks_workspace_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databricksWorkspaceUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="databricksApiToken")
    def databricks_api_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "databricksApiToken"))

    @databricks_api_token.setter
    def databricks_api_token(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a09b862ceaf8807cca67fb6c462f92e28e9578762c5c262d8bfba2228fd0f6d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "databricksApiToken", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="databricksApiTokenPlaintext")
    def databricks_api_token_plaintext(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "databricksApiTokenPlaintext"))

    @databricks_api_token_plaintext.setter
    def databricks_api_token_plaintext(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd49280cf439abf571a338fc6412e818068c025e0d77cc72100dac32f0b9b6a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "databricksApiTokenPlaintext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="databricksWorkspaceUrl")
    def databricks_workspace_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "databricksWorkspaceUrl"))

    @databricks_workspace_url.setter
    def databricks_workspace_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__764fd45b87e6fd1d6cc9ef7428ca7893495c45311e54982f5cf24b55fe956143)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "databricksWorkspaceUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37a2eeb97c7e347fa469adfa492f6e516d30265f9a57baa620b6237d20f748bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig",
    jsii_struct_bases=[],
    name_mapping={
        "project_id": "projectId",
        "region": "region",
        "private_key": "privateKey",
        "private_key_plaintext": "privateKeyPlaintext",
    },
)
class ModelServingConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig:
    def __init__(
        self,
        *,
        project_id: builtins.str,
        region: builtins.str,
        private_key: typing.Optional[builtins.str] = None,
        private_key_plaintext: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#project_id ModelServing#project_id}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#region ModelServing#region}.
        :param private_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#private_key ModelServing#private_key}.
        :param private_key_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#private_key_plaintext ModelServing#private_key_plaintext}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92b6954ec6aa6882654c6ac61585c2b6514fa0a385b32c0c69b8458ab9cbae9b)
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument private_key", value=private_key, expected_type=type_hints["private_key"])
            check_type(argname="argument private_key_plaintext", value=private_key_plaintext, expected_type=type_hints["private_key_plaintext"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "project_id": project_id,
            "region": region,
        }
        if private_key is not None:
            self._values["private_key"] = private_key
        if private_key_plaintext is not None:
            self._values["private_key_plaintext"] = private_key_plaintext

    @builtins.property
    def project_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#project_id ModelServing#project_id}.'''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#region ModelServing#region}.'''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def private_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#private_key ModelServing#private_key}.'''
        result = self._values.get("private_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def private_key_plaintext(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#private_key_plaintext ModelServing#private_key_plaintext}.'''
        result = self._values.get("private_key_plaintext")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingConfigServedEntitiesExternalModelGoogleCloudVertexAiConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelGoogleCloudVertexAiConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c7339c5e558b4e74c52f833742137d4bbcea4f72e83f86975eaee71599e7d600)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetPrivateKey")
    def reset_private_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivateKey", []))

    @jsii.member(jsii_name="resetPrivateKeyPlaintext")
    def reset_private_key_plaintext(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivateKeyPlaintext", []))

    @builtins.property
    @jsii.member(jsii_name="privateKeyInput")
    def private_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="privateKeyPlaintextInput")
    def private_key_plaintext_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateKeyPlaintextInput"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="privateKey")
    def private_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKey"))

    @private_key.setter
    def private_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c09736953a1f4dc842c5ddfca94c10c1f2b54910f370d2882c93200b8e0b7d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="privateKeyPlaintext")
    def private_key_plaintext(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKeyPlaintext"))

    @private_key_plaintext.setter
    def private_key_plaintext(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf6b5cb56b65f6edcf0b2595beb0d51e55d36de58c7e1ba783991d46acb6fb69)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateKeyPlaintext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4e43bac08a36bb8e92f526829ea8694cb6feaae67f7b6c76cfcbe99784cb350)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2fe18e54667c0b3b1ebf598df1007db79ba721ae23ad34eb9f2b455235075ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__747458b582fdd786c5304b877f202e0d3bcc95124106a5e21746c03e185d5db3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelOpenaiConfig",
    jsii_struct_bases=[],
    name_mapping={
        "microsoft_entra_client_id": "microsoftEntraClientId",
        "microsoft_entra_client_secret": "microsoftEntraClientSecret",
        "microsoft_entra_client_secret_plaintext": "microsoftEntraClientSecretPlaintext",
        "microsoft_entra_tenant_id": "microsoftEntraTenantId",
        "openai_api_base": "openaiApiBase",
        "openai_api_key": "openaiApiKey",
        "openai_api_key_plaintext": "openaiApiKeyPlaintext",
        "openai_api_type": "openaiApiType",
        "openai_api_version": "openaiApiVersion",
        "openai_deployment_name": "openaiDeploymentName",
        "openai_organization": "openaiOrganization",
    },
)
class ModelServingConfigServedEntitiesExternalModelOpenaiConfig:
    def __init__(
        self,
        *,
        microsoft_entra_client_id: typing.Optional[builtins.str] = None,
        microsoft_entra_client_secret: typing.Optional[builtins.str] = None,
        microsoft_entra_client_secret_plaintext: typing.Optional[builtins.str] = None,
        microsoft_entra_tenant_id: typing.Optional[builtins.str] = None,
        openai_api_base: typing.Optional[builtins.str] = None,
        openai_api_key: typing.Optional[builtins.str] = None,
        openai_api_key_plaintext: typing.Optional[builtins.str] = None,
        openai_api_type: typing.Optional[builtins.str] = None,
        openai_api_version: typing.Optional[builtins.str] = None,
        openai_deployment_name: typing.Optional[builtins.str] = None,
        openai_organization: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param microsoft_entra_client_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#microsoft_entra_client_id ModelServing#microsoft_entra_client_id}.
        :param microsoft_entra_client_secret: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#microsoft_entra_client_secret ModelServing#microsoft_entra_client_secret}.
        :param microsoft_entra_client_secret_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#microsoft_entra_client_secret_plaintext ModelServing#microsoft_entra_client_secret_plaintext}.
        :param microsoft_entra_tenant_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#microsoft_entra_tenant_id ModelServing#microsoft_entra_tenant_id}.
        :param openai_api_base: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#openai_api_base ModelServing#openai_api_base}.
        :param openai_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#openai_api_key ModelServing#openai_api_key}.
        :param openai_api_key_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#openai_api_key_plaintext ModelServing#openai_api_key_plaintext}.
        :param openai_api_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#openai_api_type ModelServing#openai_api_type}.
        :param openai_api_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#openai_api_version ModelServing#openai_api_version}.
        :param openai_deployment_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#openai_deployment_name ModelServing#openai_deployment_name}.
        :param openai_organization: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#openai_organization ModelServing#openai_organization}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8f3651cd444a6a03a04e10e5b69221f40bf7182b94e27a3f39209873e1a2293)
            check_type(argname="argument microsoft_entra_client_id", value=microsoft_entra_client_id, expected_type=type_hints["microsoft_entra_client_id"])
            check_type(argname="argument microsoft_entra_client_secret", value=microsoft_entra_client_secret, expected_type=type_hints["microsoft_entra_client_secret"])
            check_type(argname="argument microsoft_entra_client_secret_plaintext", value=microsoft_entra_client_secret_plaintext, expected_type=type_hints["microsoft_entra_client_secret_plaintext"])
            check_type(argname="argument microsoft_entra_tenant_id", value=microsoft_entra_tenant_id, expected_type=type_hints["microsoft_entra_tenant_id"])
            check_type(argname="argument openai_api_base", value=openai_api_base, expected_type=type_hints["openai_api_base"])
            check_type(argname="argument openai_api_key", value=openai_api_key, expected_type=type_hints["openai_api_key"])
            check_type(argname="argument openai_api_key_plaintext", value=openai_api_key_plaintext, expected_type=type_hints["openai_api_key_plaintext"])
            check_type(argname="argument openai_api_type", value=openai_api_type, expected_type=type_hints["openai_api_type"])
            check_type(argname="argument openai_api_version", value=openai_api_version, expected_type=type_hints["openai_api_version"])
            check_type(argname="argument openai_deployment_name", value=openai_deployment_name, expected_type=type_hints["openai_deployment_name"])
            check_type(argname="argument openai_organization", value=openai_organization, expected_type=type_hints["openai_organization"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if microsoft_entra_client_id is not None:
            self._values["microsoft_entra_client_id"] = microsoft_entra_client_id
        if microsoft_entra_client_secret is not None:
            self._values["microsoft_entra_client_secret"] = microsoft_entra_client_secret
        if microsoft_entra_client_secret_plaintext is not None:
            self._values["microsoft_entra_client_secret_plaintext"] = microsoft_entra_client_secret_plaintext
        if microsoft_entra_tenant_id is not None:
            self._values["microsoft_entra_tenant_id"] = microsoft_entra_tenant_id
        if openai_api_base is not None:
            self._values["openai_api_base"] = openai_api_base
        if openai_api_key is not None:
            self._values["openai_api_key"] = openai_api_key
        if openai_api_key_plaintext is not None:
            self._values["openai_api_key_plaintext"] = openai_api_key_plaintext
        if openai_api_type is not None:
            self._values["openai_api_type"] = openai_api_type
        if openai_api_version is not None:
            self._values["openai_api_version"] = openai_api_version
        if openai_deployment_name is not None:
            self._values["openai_deployment_name"] = openai_deployment_name
        if openai_organization is not None:
            self._values["openai_organization"] = openai_organization

    @builtins.property
    def microsoft_entra_client_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#microsoft_entra_client_id ModelServing#microsoft_entra_client_id}.'''
        result = self._values.get("microsoft_entra_client_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def microsoft_entra_client_secret(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#microsoft_entra_client_secret ModelServing#microsoft_entra_client_secret}.'''
        result = self._values.get("microsoft_entra_client_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def microsoft_entra_client_secret_plaintext(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#microsoft_entra_client_secret_plaintext ModelServing#microsoft_entra_client_secret_plaintext}.'''
        result = self._values.get("microsoft_entra_client_secret_plaintext")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def microsoft_entra_tenant_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#microsoft_entra_tenant_id ModelServing#microsoft_entra_tenant_id}.'''
        result = self._values.get("microsoft_entra_tenant_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def openai_api_base(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#openai_api_base ModelServing#openai_api_base}.'''
        result = self._values.get("openai_api_base")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def openai_api_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#openai_api_key ModelServing#openai_api_key}.'''
        result = self._values.get("openai_api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def openai_api_key_plaintext(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#openai_api_key_plaintext ModelServing#openai_api_key_plaintext}.'''
        result = self._values.get("openai_api_key_plaintext")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def openai_api_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#openai_api_type ModelServing#openai_api_type}.'''
        result = self._values.get("openai_api_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def openai_api_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#openai_api_version ModelServing#openai_api_version}.'''
        result = self._values.get("openai_api_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def openai_deployment_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#openai_deployment_name ModelServing#openai_deployment_name}.'''
        result = self._values.get("openai_deployment_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def openai_organization(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#openai_organization ModelServing#openai_organization}.'''
        result = self._values.get("openai_organization")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigServedEntitiesExternalModelOpenaiConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingConfigServedEntitiesExternalModelOpenaiConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelOpenaiConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__96eca2227ca1f6fbe25592666bfb974076efa4c4f49bad0f227b4a2e3eb17f28)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMicrosoftEntraClientId")
    def reset_microsoft_entra_client_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMicrosoftEntraClientId", []))

    @jsii.member(jsii_name="resetMicrosoftEntraClientSecret")
    def reset_microsoft_entra_client_secret(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMicrosoftEntraClientSecret", []))

    @jsii.member(jsii_name="resetMicrosoftEntraClientSecretPlaintext")
    def reset_microsoft_entra_client_secret_plaintext(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMicrosoftEntraClientSecretPlaintext", []))

    @jsii.member(jsii_name="resetMicrosoftEntraTenantId")
    def reset_microsoft_entra_tenant_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMicrosoftEntraTenantId", []))

    @jsii.member(jsii_name="resetOpenaiApiBase")
    def reset_openai_api_base(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpenaiApiBase", []))

    @jsii.member(jsii_name="resetOpenaiApiKey")
    def reset_openai_api_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpenaiApiKey", []))

    @jsii.member(jsii_name="resetOpenaiApiKeyPlaintext")
    def reset_openai_api_key_plaintext(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpenaiApiKeyPlaintext", []))

    @jsii.member(jsii_name="resetOpenaiApiType")
    def reset_openai_api_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpenaiApiType", []))

    @jsii.member(jsii_name="resetOpenaiApiVersion")
    def reset_openai_api_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpenaiApiVersion", []))

    @jsii.member(jsii_name="resetOpenaiDeploymentName")
    def reset_openai_deployment_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpenaiDeploymentName", []))

    @jsii.member(jsii_name="resetOpenaiOrganization")
    def reset_openai_organization(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpenaiOrganization", []))

    @builtins.property
    @jsii.member(jsii_name="microsoftEntraClientIdInput")
    def microsoft_entra_client_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "microsoftEntraClientIdInput"))

    @builtins.property
    @jsii.member(jsii_name="microsoftEntraClientSecretInput")
    def microsoft_entra_client_secret_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "microsoftEntraClientSecretInput"))

    @builtins.property
    @jsii.member(jsii_name="microsoftEntraClientSecretPlaintextInput")
    def microsoft_entra_client_secret_plaintext_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "microsoftEntraClientSecretPlaintextInput"))

    @builtins.property
    @jsii.member(jsii_name="microsoftEntraTenantIdInput")
    def microsoft_entra_tenant_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "microsoftEntraTenantIdInput"))

    @builtins.property
    @jsii.member(jsii_name="openaiApiBaseInput")
    def openai_api_base_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "openaiApiBaseInput"))

    @builtins.property
    @jsii.member(jsii_name="openaiApiKeyInput")
    def openai_api_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "openaiApiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="openaiApiKeyPlaintextInput")
    def openai_api_key_plaintext_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "openaiApiKeyPlaintextInput"))

    @builtins.property
    @jsii.member(jsii_name="openaiApiTypeInput")
    def openai_api_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "openaiApiTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="openaiApiVersionInput")
    def openai_api_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "openaiApiVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="openaiDeploymentNameInput")
    def openai_deployment_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "openaiDeploymentNameInput"))

    @builtins.property
    @jsii.member(jsii_name="openaiOrganizationInput")
    def openai_organization_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "openaiOrganizationInput"))

    @builtins.property
    @jsii.member(jsii_name="microsoftEntraClientId")
    def microsoft_entra_client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "microsoftEntraClientId"))

    @microsoft_entra_client_id.setter
    def microsoft_entra_client_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b01bce6ae02663c936859b6fdd65bf9c0787e0a2cbca469a27e0254691e4f99e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "microsoftEntraClientId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="microsoftEntraClientSecret")
    def microsoft_entra_client_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "microsoftEntraClientSecret"))

    @microsoft_entra_client_secret.setter
    def microsoft_entra_client_secret(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8acf6fc23afd1ec6f16b8d814ba0c5fd3202eb75dc88075e6fa2e70bf74e1a24)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "microsoftEntraClientSecret", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="microsoftEntraClientSecretPlaintext")
    def microsoft_entra_client_secret_plaintext(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "microsoftEntraClientSecretPlaintext"))

    @microsoft_entra_client_secret_plaintext.setter
    def microsoft_entra_client_secret_plaintext(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__865c1cb72d08e3d90ac1f9581178c2014bb16d1a6af7900c9d40d558a483eca2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "microsoftEntraClientSecretPlaintext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="microsoftEntraTenantId")
    def microsoft_entra_tenant_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "microsoftEntraTenantId"))

    @microsoft_entra_tenant_id.setter
    def microsoft_entra_tenant_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__810652b88b687685a4925c644374a2c91f370a298407a4299026d674b5c21875)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "microsoftEntraTenantId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="openaiApiBase")
    def openai_api_base(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "openaiApiBase"))

    @openai_api_base.setter
    def openai_api_base(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d910ae46138165d13f96fcad38ba4d03ea99b4f6398de8d21648bf91c47f812)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "openaiApiBase", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="openaiApiKey")
    def openai_api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "openaiApiKey"))

    @openai_api_key.setter
    def openai_api_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2942665469b2d114c5b1da0a35801aba473b6fd397a92822aba7a01d3bdb6a1e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "openaiApiKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="openaiApiKeyPlaintext")
    def openai_api_key_plaintext(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "openaiApiKeyPlaintext"))

    @openai_api_key_plaintext.setter
    def openai_api_key_plaintext(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c296616bcb2f780f9324a0d82e7f45784dfb1ce26cdb86d00ead5c681b6e9aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "openaiApiKeyPlaintext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="openaiApiType")
    def openai_api_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "openaiApiType"))

    @openai_api_type.setter
    def openai_api_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffa62ef264416b3877aac41273f2288de305f9b5513e98b5feda0976afb36e2d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "openaiApiType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="openaiApiVersion")
    def openai_api_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "openaiApiVersion"))

    @openai_api_version.setter
    def openai_api_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c39917ad5aa16b52b380336edcb2f53961c8750fdc6125952517ccc54b6a951)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "openaiApiVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="openaiDeploymentName")
    def openai_deployment_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "openaiDeploymentName"))

    @openai_deployment_name.setter
    def openai_deployment_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__139733bf0f71f12b8e4408aa3bb941024091eb852488a633b731789178eda8c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "openaiDeploymentName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="openaiOrganization")
    def openai_organization(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "openaiOrganization"))

    @openai_organization.setter
    def openai_organization(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6bd90ea04878cc2aeedd21c4ab7495629f3d00b634d97096aff7e311c7d9b72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "openaiOrganization", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelOpenaiConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelOpenaiConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingConfigServedEntitiesExternalModelOpenaiConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0833c7b0577230e49679060b337fdaee600a3cc50d57218dab1a5fcc76ee558f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ModelServingConfigServedEntitiesExternalModelOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__286957a797d7d3795901e718c685222247720c7959b31372363ced1053c8349c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAi21LabsConfig")
    def put_ai21_labs_config(
        self,
        *,
        ai21_labs_api_key: typing.Optional[builtins.str] = None,
        ai21_labs_api_key_plaintext: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param ai21_labs_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#ai21labs_api_key ModelServing#ai21labs_api_key}.
        :param ai21_labs_api_key_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#ai21labs_api_key_plaintext ModelServing#ai21labs_api_key_plaintext}.
        '''
        value = ModelServingConfigServedEntitiesExternalModelAi21LabsConfig(
            ai21_labs_api_key=ai21_labs_api_key,
            ai21_labs_api_key_plaintext=ai21_labs_api_key_plaintext,
        )

        return typing.cast(None, jsii.invoke(self, "putAi21LabsConfig", [value]))

    @jsii.member(jsii_name="putAmazonBedrockConfig")
    def put_amazon_bedrock_config(
        self,
        *,
        aws_region: builtins.str,
        bedrock_provider: builtins.str,
        aws_access_key_id: typing.Optional[builtins.str] = None,
        aws_access_key_id_plaintext: typing.Optional[builtins.str] = None,
        aws_secret_access_key: typing.Optional[builtins.str] = None,
        aws_secret_access_key_plaintext: typing.Optional[builtins.str] = None,
        instance_profile_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param aws_region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#aws_region ModelServing#aws_region}.
        :param bedrock_provider: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#bedrock_provider ModelServing#bedrock_provider}.
        :param aws_access_key_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#aws_access_key_id ModelServing#aws_access_key_id}.
        :param aws_access_key_id_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#aws_access_key_id_plaintext ModelServing#aws_access_key_id_plaintext}.
        :param aws_secret_access_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#aws_secret_access_key ModelServing#aws_secret_access_key}.
        :param aws_secret_access_key_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#aws_secret_access_key_plaintext ModelServing#aws_secret_access_key_plaintext}.
        :param instance_profile_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#instance_profile_arn ModelServing#instance_profile_arn}.
        '''
        value = ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig(
            aws_region=aws_region,
            bedrock_provider=bedrock_provider,
            aws_access_key_id=aws_access_key_id,
            aws_access_key_id_plaintext=aws_access_key_id_plaintext,
            aws_secret_access_key=aws_secret_access_key,
            aws_secret_access_key_plaintext=aws_secret_access_key_plaintext,
            instance_profile_arn=instance_profile_arn,
        )

        return typing.cast(None, jsii.invoke(self, "putAmazonBedrockConfig", [value]))

    @jsii.member(jsii_name="putAnthropicConfig")
    def put_anthropic_config(
        self,
        *,
        anthropic_api_key: typing.Optional[builtins.str] = None,
        anthropic_api_key_plaintext: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param anthropic_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#anthropic_api_key ModelServing#anthropic_api_key}.
        :param anthropic_api_key_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#anthropic_api_key_plaintext ModelServing#anthropic_api_key_plaintext}.
        '''
        value = ModelServingConfigServedEntitiesExternalModelAnthropicConfig(
            anthropic_api_key=anthropic_api_key,
            anthropic_api_key_plaintext=anthropic_api_key_plaintext,
        )

        return typing.cast(None, jsii.invoke(self, "putAnthropicConfig", [value]))

    @jsii.member(jsii_name="putCohereConfig")
    def put_cohere_config(
        self,
        *,
        cohere_api_base: typing.Optional[builtins.str] = None,
        cohere_api_key: typing.Optional[builtins.str] = None,
        cohere_api_key_plaintext: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cohere_api_base: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#cohere_api_base ModelServing#cohere_api_base}.
        :param cohere_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#cohere_api_key ModelServing#cohere_api_key}.
        :param cohere_api_key_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#cohere_api_key_plaintext ModelServing#cohere_api_key_plaintext}.
        '''
        value = ModelServingConfigServedEntitiesExternalModelCohereConfig(
            cohere_api_base=cohere_api_base,
            cohere_api_key=cohere_api_key,
            cohere_api_key_plaintext=cohere_api_key_plaintext,
        )

        return typing.cast(None, jsii.invoke(self, "putCohereConfig", [value]))

    @jsii.member(jsii_name="putCustomProviderConfig")
    def put_custom_provider_config(
        self,
        *,
        custom_provider_url: builtins.str,
        api_key_auth: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth, typing.Dict[builtins.str, typing.Any]]] = None,
        bearer_token_auth: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param custom_provider_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#custom_provider_url ModelServing#custom_provider_url}.
        :param api_key_auth: api_key_auth block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#api_key_auth ModelServing#api_key_auth}
        :param bearer_token_auth: bearer_token_auth block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#bearer_token_auth ModelServing#bearer_token_auth}
        '''
        value = ModelServingConfigServedEntitiesExternalModelCustomProviderConfig(
            custom_provider_url=custom_provider_url,
            api_key_auth=api_key_auth,
            bearer_token_auth=bearer_token_auth,
        )

        return typing.cast(None, jsii.invoke(self, "putCustomProviderConfig", [value]))

    @jsii.member(jsii_name="putDatabricksModelServingConfig")
    def put_databricks_model_serving_config(
        self,
        *,
        databricks_workspace_url: builtins.str,
        databricks_api_token: typing.Optional[builtins.str] = None,
        databricks_api_token_plaintext: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param databricks_workspace_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#databricks_workspace_url ModelServing#databricks_workspace_url}.
        :param databricks_api_token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#databricks_api_token ModelServing#databricks_api_token}.
        :param databricks_api_token_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#databricks_api_token_plaintext ModelServing#databricks_api_token_plaintext}.
        '''
        value = ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig(
            databricks_workspace_url=databricks_workspace_url,
            databricks_api_token=databricks_api_token,
            databricks_api_token_plaintext=databricks_api_token_plaintext,
        )

        return typing.cast(None, jsii.invoke(self, "putDatabricksModelServingConfig", [value]))

    @jsii.member(jsii_name="putGoogleCloudVertexAiConfig")
    def put_google_cloud_vertex_ai_config(
        self,
        *,
        project_id: builtins.str,
        region: builtins.str,
        private_key: typing.Optional[builtins.str] = None,
        private_key_plaintext: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#project_id ModelServing#project_id}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#region ModelServing#region}.
        :param private_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#private_key ModelServing#private_key}.
        :param private_key_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#private_key_plaintext ModelServing#private_key_plaintext}.
        '''
        value = ModelServingConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig(
            project_id=project_id,
            region=region,
            private_key=private_key,
            private_key_plaintext=private_key_plaintext,
        )

        return typing.cast(None, jsii.invoke(self, "putGoogleCloudVertexAiConfig", [value]))

    @jsii.member(jsii_name="putOpenaiConfig")
    def put_openai_config(
        self,
        *,
        microsoft_entra_client_id: typing.Optional[builtins.str] = None,
        microsoft_entra_client_secret: typing.Optional[builtins.str] = None,
        microsoft_entra_client_secret_plaintext: typing.Optional[builtins.str] = None,
        microsoft_entra_tenant_id: typing.Optional[builtins.str] = None,
        openai_api_base: typing.Optional[builtins.str] = None,
        openai_api_key: typing.Optional[builtins.str] = None,
        openai_api_key_plaintext: typing.Optional[builtins.str] = None,
        openai_api_type: typing.Optional[builtins.str] = None,
        openai_api_version: typing.Optional[builtins.str] = None,
        openai_deployment_name: typing.Optional[builtins.str] = None,
        openai_organization: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param microsoft_entra_client_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#microsoft_entra_client_id ModelServing#microsoft_entra_client_id}.
        :param microsoft_entra_client_secret: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#microsoft_entra_client_secret ModelServing#microsoft_entra_client_secret}.
        :param microsoft_entra_client_secret_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#microsoft_entra_client_secret_plaintext ModelServing#microsoft_entra_client_secret_plaintext}.
        :param microsoft_entra_tenant_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#microsoft_entra_tenant_id ModelServing#microsoft_entra_tenant_id}.
        :param openai_api_base: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#openai_api_base ModelServing#openai_api_base}.
        :param openai_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#openai_api_key ModelServing#openai_api_key}.
        :param openai_api_key_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#openai_api_key_plaintext ModelServing#openai_api_key_plaintext}.
        :param openai_api_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#openai_api_type ModelServing#openai_api_type}.
        :param openai_api_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#openai_api_version ModelServing#openai_api_version}.
        :param openai_deployment_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#openai_deployment_name ModelServing#openai_deployment_name}.
        :param openai_organization: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#openai_organization ModelServing#openai_organization}.
        '''
        value = ModelServingConfigServedEntitiesExternalModelOpenaiConfig(
            microsoft_entra_client_id=microsoft_entra_client_id,
            microsoft_entra_client_secret=microsoft_entra_client_secret,
            microsoft_entra_client_secret_plaintext=microsoft_entra_client_secret_plaintext,
            microsoft_entra_tenant_id=microsoft_entra_tenant_id,
            openai_api_base=openai_api_base,
            openai_api_key=openai_api_key,
            openai_api_key_plaintext=openai_api_key_plaintext,
            openai_api_type=openai_api_type,
            openai_api_version=openai_api_version,
            openai_deployment_name=openai_deployment_name,
            openai_organization=openai_organization,
        )

        return typing.cast(None, jsii.invoke(self, "putOpenaiConfig", [value]))

    @jsii.member(jsii_name="putPalmConfig")
    def put_palm_config(
        self,
        *,
        palm_api_key: typing.Optional[builtins.str] = None,
        palm_api_key_plaintext: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param palm_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#palm_api_key ModelServing#palm_api_key}.
        :param palm_api_key_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#palm_api_key_plaintext ModelServing#palm_api_key_plaintext}.
        '''
        value = ModelServingConfigServedEntitiesExternalModelPalmConfig(
            palm_api_key=palm_api_key, palm_api_key_plaintext=palm_api_key_plaintext
        )

        return typing.cast(None, jsii.invoke(self, "putPalmConfig", [value]))

    @jsii.member(jsii_name="resetAi21LabsConfig")
    def reset_ai21_labs_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAi21LabsConfig", []))

    @jsii.member(jsii_name="resetAmazonBedrockConfig")
    def reset_amazon_bedrock_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAmazonBedrockConfig", []))

    @jsii.member(jsii_name="resetAnthropicConfig")
    def reset_anthropic_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAnthropicConfig", []))

    @jsii.member(jsii_name="resetCohereConfig")
    def reset_cohere_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCohereConfig", []))

    @jsii.member(jsii_name="resetCustomProviderConfig")
    def reset_custom_provider_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomProviderConfig", []))

    @jsii.member(jsii_name="resetDatabricksModelServingConfig")
    def reset_databricks_model_serving_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatabricksModelServingConfig", []))

    @jsii.member(jsii_name="resetGoogleCloudVertexAiConfig")
    def reset_google_cloud_vertex_ai_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGoogleCloudVertexAiConfig", []))

    @jsii.member(jsii_name="resetOpenaiConfig")
    def reset_openai_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpenaiConfig", []))

    @jsii.member(jsii_name="resetPalmConfig")
    def reset_palm_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPalmConfig", []))

    @builtins.property
    @jsii.member(jsii_name="ai21LabsConfig")
    def ai21_labs_config(
        self,
    ) -> ModelServingConfigServedEntitiesExternalModelAi21LabsConfigOutputReference:
        return typing.cast(ModelServingConfigServedEntitiesExternalModelAi21LabsConfigOutputReference, jsii.get(self, "ai21LabsConfig"))

    @builtins.property
    @jsii.member(jsii_name="amazonBedrockConfig")
    def amazon_bedrock_config(
        self,
    ) -> ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfigOutputReference:
        return typing.cast(ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfigOutputReference, jsii.get(self, "amazonBedrockConfig"))

    @builtins.property
    @jsii.member(jsii_name="anthropicConfig")
    def anthropic_config(
        self,
    ) -> ModelServingConfigServedEntitiesExternalModelAnthropicConfigOutputReference:
        return typing.cast(ModelServingConfigServedEntitiesExternalModelAnthropicConfigOutputReference, jsii.get(self, "anthropicConfig"))

    @builtins.property
    @jsii.member(jsii_name="cohereConfig")
    def cohere_config(
        self,
    ) -> ModelServingConfigServedEntitiesExternalModelCohereConfigOutputReference:
        return typing.cast(ModelServingConfigServedEntitiesExternalModelCohereConfigOutputReference, jsii.get(self, "cohereConfig"))

    @builtins.property
    @jsii.member(jsii_name="customProviderConfig")
    def custom_provider_config(
        self,
    ) -> ModelServingConfigServedEntitiesExternalModelCustomProviderConfigOutputReference:
        return typing.cast(ModelServingConfigServedEntitiesExternalModelCustomProviderConfigOutputReference, jsii.get(self, "customProviderConfig"))

    @builtins.property
    @jsii.member(jsii_name="databricksModelServingConfig")
    def databricks_model_serving_config(
        self,
    ) -> ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfigOutputReference:
        return typing.cast(ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfigOutputReference, jsii.get(self, "databricksModelServingConfig"))

    @builtins.property
    @jsii.member(jsii_name="googleCloudVertexAiConfig")
    def google_cloud_vertex_ai_config(
        self,
    ) -> ModelServingConfigServedEntitiesExternalModelGoogleCloudVertexAiConfigOutputReference:
        return typing.cast(ModelServingConfigServedEntitiesExternalModelGoogleCloudVertexAiConfigOutputReference, jsii.get(self, "googleCloudVertexAiConfig"))

    @builtins.property
    @jsii.member(jsii_name="openaiConfig")
    def openai_config(
        self,
    ) -> ModelServingConfigServedEntitiesExternalModelOpenaiConfigOutputReference:
        return typing.cast(ModelServingConfigServedEntitiesExternalModelOpenaiConfigOutputReference, jsii.get(self, "openaiConfig"))

    @builtins.property
    @jsii.member(jsii_name="palmConfig")
    def palm_config(
        self,
    ) -> "ModelServingConfigServedEntitiesExternalModelPalmConfigOutputReference":
        return typing.cast("ModelServingConfigServedEntitiesExternalModelPalmConfigOutputReference", jsii.get(self, "palmConfig"))

    @builtins.property
    @jsii.member(jsii_name="ai21LabsConfigInput")
    def ai21_labs_config_input(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelAi21LabsConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelAi21LabsConfig], jsii.get(self, "ai21LabsConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="amazonBedrockConfigInput")
    def amazon_bedrock_config_input(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig], jsii.get(self, "amazonBedrockConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="anthropicConfigInput")
    def anthropic_config_input(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelAnthropicConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelAnthropicConfig], jsii.get(self, "anthropicConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="cohereConfigInput")
    def cohere_config_input(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelCohereConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelCohereConfig], jsii.get(self, "cohereConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="customProviderConfigInput")
    def custom_provider_config_input(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelCustomProviderConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelCustomProviderConfig], jsii.get(self, "customProviderConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="databricksModelServingConfigInput")
    def databricks_model_serving_config_input(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig], jsii.get(self, "databricksModelServingConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="googleCloudVertexAiConfigInput")
    def google_cloud_vertex_ai_config_input(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig], jsii.get(self, "googleCloudVertexAiConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="openaiConfigInput")
    def openai_config_input(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelOpenaiConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelOpenaiConfig], jsii.get(self, "openaiConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="palmConfigInput")
    def palm_config_input(
        self,
    ) -> typing.Optional["ModelServingConfigServedEntitiesExternalModelPalmConfig"]:
        return typing.cast(typing.Optional["ModelServingConfigServedEntitiesExternalModelPalmConfig"], jsii.get(self, "palmConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="providerInput")
    def provider_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "providerInput"))

    @builtins.property
    @jsii.member(jsii_name="taskInput")
    def task_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "taskInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__186cb5665bc59aaa9ce409cb8208fb7dd40871e7acf79134bf4c7cdc5c10a2c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="provider")
    def provider(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "provider"))

    @provider.setter
    def provider(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12796f48f59357a3d01909964205037a61611468763c992eaf3a5e51a410b9d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "provider", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="task")
    def task(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "task"))

    @task.setter
    def task(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55764731d175dec17e4fc1dd16886f842c2d8074da5de0878b95679f89c7a6d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "task", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModel]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModel], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingConfigServedEntitiesExternalModel],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23c418f265754be146809c589f248006a2e823e8931bce27139b60be00a944fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelPalmConfig",
    jsii_struct_bases=[],
    name_mapping={
        "palm_api_key": "palmApiKey",
        "palm_api_key_plaintext": "palmApiKeyPlaintext",
    },
)
class ModelServingConfigServedEntitiesExternalModelPalmConfig:
    def __init__(
        self,
        *,
        palm_api_key: typing.Optional[builtins.str] = None,
        palm_api_key_plaintext: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param palm_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#palm_api_key ModelServing#palm_api_key}.
        :param palm_api_key_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#palm_api_key_plaintext ModelServing#palm_api_key_plaintext}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d7f69696e468cd3ad5ffddae6add89fbf9597eef2db2a900972795882f84260)
            check_type(argname="argument palm_api_key", value=palm_api_key, expected_type=type_hints["palm_api_key"])
            check_type(argname="argument palm_api_key_plaintext", value=palm_api_key_plaintext, expected_type=type_hints["palm_api_key_plaintext"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if palm_api_key is not None:
            self._values["palm_api_key"] = palm_api_key
        if palm_api_key_plaintext is not None:
            self._values["palm_api_key_plaintext"] = palm_api_key_plaintext

    @builtins.property
    def palm_api_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#palm_api_key ModelServing#palm_api_key}.'''
        result = self._values.get("palm_api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def palm_api_key_plaintext(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#palm_api_key_plaintext ModelServing#palm_api_key_plaintext}.'''
        result = self._values.get("palm_api_key_plaintext")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigServedEntitiesExternalModelPalmConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingConfigServedEntitiesExternalModelPalmConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelPalmConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e2415e41a2d65031da7ad03ff288304364d2a75d69e744f5986dbebe1cd84314)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetPalmApiKey")
    def reset_palm_api_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPalmApiKey", []))

    @jsii.member(jsii_name="resetPalmApiKeyPlaintext")
    def reset_palm_api_key_plaintext(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPalmApiKeyPlaintext", []))

    @builtins.property
    @jsii.member(jsii_name="palmApiKeyInput")
    def palm_api_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "palmApiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="palmApiKeyPlaintextInput")
    def palm_api_key_plaintext_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "palmApiKeyPlaintextInput"))

    @builtins.property
    @jsii.member(jsii_name="palmApiKey")
    def palm_api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "palmApiKey"))

    @palm_api_key.setter
    def palm_api_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d267a559f3a647aa1bad3826b5c511002c6e84c231d14e688498f3452c1edc93)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "palmApiKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="palmApiKeyPlaintext")
    def palm_api_key_plaintext(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "palmApiKeyPlaintext"))

    @palm_api_key_plaintext.setter
    def palm_api_key_plaintext(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a33122e6d04560c85f0d5112921621afc718b8a834763d918cd1908d3bf7a9cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "palmApiKeyPlaintext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelPalmConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelPalmConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingConfigServedEntitiesExternalModelPalmConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c92e50429bcc356c4a64039fd323e25eec3aac1617b8e44b20de759640c3439)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ModelServingConfigServedEntitiesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c5b118db3d06fdd140973d3aa4cc3a885623a42ff336d2eba7d45380b7f73959)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ModelServingConfigServedEntitiesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77acb6ce6c67f79a9b0d1314c0324692cb1fa6f244647ce53272762d81da2526)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ModelServingConfigServedEntitiesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a14f5528daebd60ea2786187c3c5a4423f153db7ab0e49a07d1ebac0cae40d3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3b2a27fd791322888d58ee916ba218a9018446d6ac345466008049d6bd107087)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ee9cad630026f7541c897b5d7427a66841f3a7b37ea702e67476de9e4e66337f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingConfigServedEntities]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingConfigServedEntities]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingConfigServedEntities]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db21c169a62214a095fb313b873f0316c06668343c8a393d69f0adf180eee16d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ModelServingConfigServedEntitiesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bce219b1818dd301c72b49d3cd1ee61649975cbfc261e27ce547ecf3c22dd279)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putExternalModel")
    def put_external_model(
        self,
        *,
        name: builtins.str,
        provider: builtins.str,
        task: builtins.str,
        ai21_labs_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelAi21LabsConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        amazon_bedrock_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        anthropic_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelAnthropicConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        cohere_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelCohereConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        custom_provider_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelCustomProviderConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        databricks_model_serving_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        google_cloud_vertex_ai_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        openai_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelOpenaiConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        palm_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelPalmConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#name ModelServing#name}.
        :param provider: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#provider ModelServing#provider}.
        :param task: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#task ModelServing#task}.
        :param ai21_labs_config: ai21labs_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#ai21labs_config ModelServing#ai21labs_config}
        :param amazon_bedrock_config: amazon_bedrock_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#amazon_bedrock_config ModelServing#amazon_bedrock_config}
        :param anthropic_config: anthropic_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#anthropic_config ModelServing#anthropic_config}
        :param cohere_config: cohere_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#cohere_config ModelServing#cohere_config}
        :param custom_provider_config: custom_provider_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#custom_provider_config ModelServing#custom_provider_config}
        :param databricks_model_serving_config: databricks_model_serving_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#databricks_model_serving_config ModelServing#databricks_model_serving_config}
        :param google_cloud_vertex_ai_config: google_cloud_vertex_ai_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#google_cloud_vertex_ai_config ModelServing#google_cloud_vertex_ai_config}
        :param openai_config: openai_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#openai_config ModelServing#openai_config}
        :param palm_config: palm_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#palm_config ModelServing#palm_config}
        '''
        value = ModelServingConfigServedEntitiesExternalModel(
            name=name,
            provider=provider,
            task=task,
            ai21_labs_config=ai21_labs_config,
            amazon_bedrock_config=amazon_bedrock_config,
            anthropic_config=anthropic_config,
            cohere_config=cohere_config,
            custom_provider_config=custom_provider_config,
            databricks_model_serving_config=databricks_model_serving_config,
            google_cloud_vertex_ai_config=google_cloud_vertex_ai_config,
            openai_config=openai_config,
            palm_config=palm_config,
        )

        return typing.cast(None, jsii.invoke(self, "putExternalModel", [value]))

    @jsii.member(jsii_name="resetEntityName")
    def reset_entity_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEntityName", []))

    @jsii.member(jsii_name="resetEntityVersion")
    def reset_entity_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEntityVersion", []))

    @jsii.member(jsii_name="resetEnvironmentVars")
    def reset_environment_vars(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnvironmentVars", []))

    @jsii.member(jsii_name="resetExternalModel")
    def reset_external_model(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExternalModel", []))

    @jsii.member(jsii_name="resetInstanceProfileArn")
    def reset_instance_profile_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceProfileArn", []))

    @jsii.member(jsii_name="resetMaxProvisionedConcurrency")
    def reset_max_provisioned_concurrency(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxProvisionedConcurrency", []))

    @jsii.member(jsii_name="resetMaxProvisionedThroughput")
    def reset_max_provisioned_throughput(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxProvisionedThroughput", []))

    @jsii.member(jsii_name="resetMinProvisionedConcurrency")
    def reset_min_provisioned_concurrency(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinProvisionedConcurrency", []))

    @jsii.member(jsii_name="resetMinProvisionedThroughput")
    def reset_min_provisioned_throughput(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinProvisionedThroughput", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetProvisionedModelUnits")
    def reset_provisioned_model_units(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProvisionedModelUnits", []))

    @jsii.member(jsii_name="resetScaleToZeroEnabled")
    def reset_scale_to_zero_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScaleToZeroEnabled", []))

    @jsii.member(jsii_name="resetWorkloadSize")
    def reset_workload_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkloadSize", []))

    @jsii.member(jsii_name="resetWorkloadType")
    def reset_workload_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkloadType", []))

    @builtins.property
    @jsii.member(jsii_name="externalModel")
    def external_model(
        self,
    ) -> ModelServingConfigServedEntitiesExternalModelOutputReference:
        return typing.cast(ModelServingConfigServedEntitiesExternalModelOutputReference, jsii.get(self, "externalModel"))

    @builtins.property
    @jsii.member(jsii_name="entityNameInput")
    def entity_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "entityNameInput"))

    @builtins.property
    @jsii.member(jsii_name="entityVersionInput")
    def entity_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "entityVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="environmentVarsInput")
    def environment_vars_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "environmentVarsInput"))

    @builtins.property
    @jsii.member(jsii_name="externalModelInput")
    def external_model_input(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModel]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModel], jsii.get(self, "externalModelInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceProfileArnInput")
    def instance_profile_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceProfileArnInput"))

    @builtins.property
    @jsii.member(jsii_name="maxProvisionedConcurrencyInput")
    def max_provisioned_concurrency_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxProvisionedConcurrencyInput"))

    @builtins.property
    @jsii.member(jsii_name="maxProvisionedThroughputInput")
    def max_provisioned_throughput_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxProvisionedThroughputInput"))

    @builtins.property
    @jsii.member(jsii_name="minProvisionedConcurrencyInput")
    def min_provisioned_concurrency_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minProvisionedConcurrencyInput"))

    @builtins.property
    @jsii.member(jsii_name="minProvisionedThroughputInput")
    def min_provisioned_throughput_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minProvisionedThroughputInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="provisionedModelUnitsInput")
    def provisioned_model_units_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "provisionedModelUnitsInput"))

    @builtins.property
    @jsii.member(jsii_name="scaleToZeroEnabledInput")
    def scale_to_zero_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "scaleToZeroEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="workloadSizeInput")
    def workload_size_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workloadSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="workloadTypeInput")
    def workload_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workloadTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="entityName")
    def entity_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "entityName"))

    @entity_name.setter
    def entity_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae5115ac461b91328a1e6dc01d00fc56cc73127601942a8e2bfdf61a81faef83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "entityName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="entityVersion")
    def entity_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "entityVersion"))

    @entity_version.setter
    def entity_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a95a0cf2db47ff6a22b93698ae18fd680c16bfffea288ef207e3f6d3b19b3ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "entityVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="environmentVars")
    def environment_vars(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "environmentVars"))

    @environment_vars.setter
    def environment_vars(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e0ee29c76865b6a9038e2d80fdd880b5452ddf1d26a05c17b26c5a5c21de86e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "environmentVars", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instanceProfileArn")
    def instance_profile_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceProfileArn"))

    @instance_profile_arn.setter
    def instance_profile_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00de5f6a64e69f35f91ab15d64763aa2dcf66850be1d320dd964dc82d83d16db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceProfileArn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxProvisionedConcurrency")
    def max_provisioned_concurrency(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxProvisionedConcurrency"))

    @max_provisioned_concurrency.setter
    def max_provisioned_concurrency(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d50aa3719691b7a1493d8cbb7cafda8fb4902113822b2a31a9a43f0ecb4b95cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxProvisionedConcurrency", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxProvisionedThroughput")
    def max_provisioned_throughput(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxProvisionedThroughput"))

    @max_provisioned_throughput.setter
    def max_provisioned_throughput(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a225a3719b5f9c5ed1f2f06d7da50f6edaa8750290b4de359c01f3e40a080563)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxProvisionedThroughput", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minProvisionedConcurrency")
    def min_provisioned_concurrency(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minProvisionedConcurrency"))

    @min_provisioned_concurrency.setter
    def min_provisioned_concurrency(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de79c00c6f7b84582b448cb3d4202514d7fa7a8789b5b27fec93d1ed835ee369)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minProvisionedConcurrency", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minProvisionedThroughput")
    def min_provisioned_throughput(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minProvisionedThroughput"))

    @min_provisioned_throughput.setter
    def min_provisioned_throughput(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1f52003d4a91bc7d946132069fb47cefe31a03c327e8f02aa9ab78527fda020)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minProvisionedThroughput", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__433fc1fe0c4f22dff549f3df966f4772b6f051027df685b4697db5f8188cf8b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="provisionedModelUnits")
    def provisioned_model_units(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "provisionedModelUnits"))

    @provisioned_model_units.setter
    def provisioned_model_units(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b5652e3b9b3b2c1fbdda7fbd4a65bedf91f7780761c45270916e00ca4b69144)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "provisionedModelUnits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scaleToZeroEnabled")
    def scale_to_zero_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "scaleToZeroEnabled"))

    @scale_to_zero_enabled.setter
    def scale_to_zero_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__599c4926eb4037b5468d52469b0e74e25a1761e72aa97bfb197e66bd64775c50)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scaleToZeroEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workloadSize")
    def workload_size(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workloadSize"))

    @workload_size.setter
    def workload_size(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e75d8d050a460878e877a289cf925e1c7f4a6801b15a82d76bab5bca968748b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workloadSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workloadType")
    def workload_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workloadType"))

    @workload_type.setter
    def workload_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78afd2dd0ca10f2743b78f75b3e0ad3d2dae0e40f1c360b06b9dc9e867dce67d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workloadType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingConfigServedEntities]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingConfigServedEntities]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingConfigServedEntities]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4174906e58d55e3fcba05db5a4e8a4dd65ca404b2f456b42386ab0fd1cdb28a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedModels",
    jsii_struct_bases=[],
    name_mapping={
        "model_name": "modelName",
        "model_version": "modelVersion",
        "environment_vars": "environmentVars",
        "instance_profile_arn": "instanceProfileArn",
        "max_provisioned_concurrency": "maxProvisionedConcurrency",
        "max_provisioned_throughput": "maxProvisionedThroughput",
        "min_provisioned_concurrency": "minProvisionedConcurrency",
        "min_provisioned_throughput": "minProvisionedThroughput",
        "name": "name",
        "provisioned_model_units": "provisionedModelUnits",
        "scale_to_zero_enabled": "scaleToZeroEnabled",
        "workload_size": "workloadSize",
        "workload_type": "workloadType",
    },
)
class ModelServingConfigServedModels:
    def __init__(
        self,
        *,
        model_name: builtins.str,
        model_version: builtins.str,
        environment_vars: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        instance_profile_arn: typing.Optional[builtins.str] = None,
        max_provisioned_concurrency: typing.Optional[jsii.Number] = None,
        max_provisioned_throughput: typing.Optional[jsii.Number] = None,
        min_provisioned_concurrency: typing.Optional[jsii.Number] = None,
        min_provisioned_throughput: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        provisioned_model_units: typing.Optional[jsii.Number] = None,
        scale_to_zero_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        workload_size: typing.Optional[builtins.str] = None,
        workload_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param model_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#model_name ModelServing#model_name}.
        :param model_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#model_version ModelServing#model_version}.
        :param environment_vars: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#environment_vars ModelServing#environment_vars}.
        :param instance_profile_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#instance_profile_arn ModelServing#instance_profile_arn}.
        :param max_provisioned_concurrency: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#max_provisioned_concurrency ModelServing#max_provisioned_concurrency}.
        :param max_provisioned_throughput: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#max_provisioned_throughput ModelServing#max_provisioned_throughput}.
        :param min_provisioned_concurrency: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#min_provisioned_concurrency ModelServing#min_provisioned_concurrency}.
        :param min_provisioned_throughput: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#min_provisioned_throughput ModelServing#min_provisioned_throughput}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#name ModelServing#name}.
        :param provisioned_model_units: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#provisioned_model_units ModelServing#provisioned_model_units}.
        :param scale_to_zero_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#scale_to_zero_enabled ModelServing#scale_to_zero_enabled}.
        :param workload_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#workload_size ModelServing#workload_size}.
        :param workload_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#workload_type ModelServing#workload_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bec3cb547e17150f62247591fe28ea70f0c54212835f4df101f3b4570944be47)
            check_type(argname="argument model_name", value=model_name, expected_type=type_hints["model_name"])
            check_type(argname="argument model_version", value=model_version, expected_type=type_hints["model_version"])
            check_type(argname="argument environment_vars", value=environment_vars, expected_type=type_hints["environment_vars"])
            check_type(argname="argument instance_profile_arn", value=instance_profile_arn, expected_type=type_hints["instance_profile_arn"])
            check_type(argname="argument max_provisioned_concurrency", value=max_provisioned_concurrency, expected_type=type_hints["max_provisioned_concurrency"])
            check_type(argname="argument max_provisioned_throughput", value=max_provisioned_throughput, expected_type=type_hints["max_provisioned_throughput"])
            check_type(argname="argument min_provisioned_concurrency", value=min_provisioned_concurrency, expected_type=type_hints["min_provisioned_concurrency"])
            check_type(argname="argument min_provisioned_throughput", value=min_provisioned_throughput, expected_type=type_hints["min_provisioned_throughput"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument provisioned_model_units", value=provisioned_model_units, expected_type=type_hints["provisioned_model_units"])
            check_type(argname="argument scale_to_zero_enabled", value=scale_to_zero_enabled, expected_type=type_hints["scale_to_zero_enabled"])
            check_type(argname="argument workload_size", value=workload_size, expected_type=type_hints["workload_size"])
            check_type(argname="argument workload_type", value=workload_type, expected_type=type_hints["workload_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "model_name": model_name,
            "model_version": model_version,
        }
        if environment_vars is not None:
            self._values["environment_vars"] = environment_vars
        if instance_profile_arn is not None:
            self._values["instance_profile_arn"] = instance_profile_arn
        if max_provisioned_concurrency is not None:
            self._values["max_provisioned_concurrency"] = max_provisioned_concurrency
        if max_provisioned_throughput is not None:
            self._values["max_provisioned_throughput"] = max_provisioned_throughput
        if min_provisioned_concurrency is not None:
            self._values["min_provisioned_concurrency"] = min_provisioned_concurrency
        if min_provisioned_throughput is not None:
            self._values["min_provisioned_throughput"] = min_provisioned_throughput
        if name is not None:
            self._values["name"] = name
        if provisioned_model_units is not None:
            self._values["provisioned_model_units"] = provisioned_model_units
        if scale_to_zero_enabled is not None:
            self._values["scale_to_zero_enabled"] = scale_to_zero_enabled
        if workload_size is not None:
            self._values["workload_size"] = workload_size
        if workload_type is not None:
            self._values["workload_type"] = workload_type

    @builtins.property
    def model_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#model_name ModelServing#model_name}.'''
        result = self._values.get("model_name")
        assert result is not None, "Required property 'model_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def model_version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#model_version ModelServing#model_version}.'''
        result = self._values.get("model_version")
        assert result is not None, "Required property 'model_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def environment_vars(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#environment_vars ModelServing#environment_vars}.'''
        result = self._values.get("environment_vars")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def instance_profile_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#instance_profile_arn ModelServing#instance_profile_arn}.'''
        result = self._values.get("instance_profile_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_provisioned_concurrency(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#max_provisioned_concurrency ModelServing#max_provisioned_concurrency}.'''
        result = self._values.get("max_provisioned_concurrency")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_provisioned_throughput(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#max_provisioned_throughput ModelServing#max_provisioned_throughput}.'''
        result = self._values.get("max_provisioned_throughput")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_provisioned_concurrency(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#min_provisioned_concurrency ModelServing#min_provisioned_concurrency}.'''
        result = self._values.get("min_provisioned_concurrency")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_provisioned_throughput(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#min_provisioned_throughput ModelServing#min_provisioned_throughput}.'''
        result = self._values.get("min_provisioned_throughput")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#name ModelServing#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def provisioned_model_units(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#provisioned_model_units ModelServing#provisioned_model_units}.'''
        result = self._values.get("provisioned_model_units")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def scale_to_zero_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#scale_to_zero_enabled ModelServing#scale_to_zero_enabled}.'''
        result = self._values.get("scale_to_zero_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def workload_size(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#workload_size ModelServing#workload_size}.'''
        result = self._values.get("workload_size")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workload_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#workload_type ModelServing#workload_type}.'''
        result = self._values.get("workload_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigServedModels(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingConfigServedModelsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedModelsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ff05e578ae924655a4766db44c640492b6da80d47a4d397d162294686bb36e28)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ModelServingConfigServedModelsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84178d8320aa70e5900bbea218aeecdfbe05a2428b168395a9aa09448d97dbbe)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ModelServingConfigServedModelsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77aa0d1b2688e799e89ca07474343e53c443abeaf05a0c5156a33508d59fd95a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c8f1442c8f42d7e7012d749108f7abb52f31f2b526ec10327597cf72e34b592a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7bd25af1f756a83a5d27b03efa85ec9bacb1572a074c8d1cb601c2981ae8b2ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingConfigServedModels]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingConfigServedModels]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingConfigServedModels]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ada08f44b74200500d8225f02a86080e59672509df4a491bf0c862b7d6f82931)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ModelServingConfigServedModelsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedModelsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a5e5fee82cb78ad16f4c3ce5d5b29f795f4c7e2b4d4ccb36068062744dd45bba)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetEnvironmentVars")
    def reset_environment_vars(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnvironmentVars", []))

    @jsii.member(jsii_name="resetInstanceProfileArn")
    def reset_instance_profile_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceProfileArn", []))

    @jsii.member(jsii_name="resetMaxProvisionedConcurrency")
    def reset_max_provisioned_concurrency(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxProvisionedConcurrency", []))

    @jsii.member(jsii_name="resetMaxProvisionedThroughput")
    def reset_max_provisioned_throughput(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxProvisionedThroughput", []))

    @jsii.member(jsii_name="resetMinProvisionedConcurrency")
    def reset_min_provisioned_concurrency(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinProvisionedConcurrency", []))

    @jsii.member(jsii_name="resetMinProvisionedThroughput")
    def reset_min_provisioned_throughput(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinProvisionedThroughput", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetProvisionedModelUnits")
    def reset_provisioned_model_units(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProvisionedModelUnits", []))

    @jsii.member(jsii_name="resetScaleToZeroEnabled")
    def reset_scale_to_zero_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScaleToZeroEnabled", []))

    @jsii.member(jsii_name="resetWorkloadSize")
    def reset_workload_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkloadSize", []))

    @jsii.member(jsii_name="resetWorkloadType")
    def reset_workload_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkloadType", []))

    @builtins.property
    @jsii.member(jsii_name="environmentVarsInput")
    def environment_vars_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "environmentVarsInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceProfileArnInput")
    def instance_profile_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceProfileArnInput"))

    @builtins.property
    @jsii.member(jsii_name="maxProvisionedConcurrencyInput")
    def max_provisioned_concurrency_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxProvisionedConcurrencyInput"))

    @builtins.property
    @jsii.member(jsii_name="maxProvisionedThroughputInput")
    def max_provisioned_throughput_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxProvisionedThroughputInput"))

    @builtins.property
    @jsii.member(jsii_name="minProvisionedConcurrencyInput")
    def min_provisioned_concurrency_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minProvisionedConcurrencyInput"))

    @builtins.property
    @jsii.member(jsii_name="minProvisionedThroughputInput")
    def min_provisioned_throughput_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minProvisionedThroughputInput"))

    @builtins.property
    @jsii.member(jsii_name="modelNameInput")
    def model_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modelNameInput"))

    @builtins.property
    @jsii.member(jsii_name="modelVersionInput")
    def model_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modelVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="provisionedModelUnitsInput")
    def provisioned_model_units_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "provisionedModelUnitsInput"))

    @builtins.property
    @jsii.member(jsii_name="scaleToZeroEnabledInput")
    def scale_to_zero_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "scaleToZeroEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="workloadSizeInput")
    def workload_size_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workloadSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="workloadTypeInput")
    def workload_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workloadTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="environmentVars")
    def environment_vars(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "environmentVars"))

    @environment_vars.setter
    def environment_vars(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c94b7c74795cba572f02b2d4bbeceffa53726338e6d644eea2330d1d67e2ab4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "environmentVars", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instanceProfileArn")
    def instance_profile_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceProfileArn"))

    @instance_profile_arn.setter
    def instance_profile_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__600c13055a167361ee8c1b924c85d37f4aed1c0dc1adcbde9c77bf70323c88a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceProfileArn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxProvisionedConcurrency")
    def max_provisioned_concurrency(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxProvisionedConcurrency"))

    @max_provisioned_concurrency.setter
    def max_provisioned_concurrency(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20f9b03a76829ba0f7a7044a4b3c493d25acb1ddea99af4c01fb72385a146ae3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxProvisionedConcurrency", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxProvisionedThroughput")
    def max_provisioned_throughput(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxProvisionedThroughput"))

    @max_provisioned_throughput.setter
    def max_provisioned_throughput(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fedb34b662eb91cf45e210d789ad69f7517ec0f36564f697e07a982785c3d72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxProvisionedThroughput", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minProvisionedConcurrency")
    def min_provisioned_concurrency(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minProvisionedConcurrency"))

    @min_provisioned_concurrency.setter
    def min_provisioned_concurrency(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5aacea179332c7eab288223120cba027c0c7ac76a2dde1e6a910642a10f2c7e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minProvisionedConcurrency", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minProvisionedThroughput")
    def min_provisioned_throughput(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minProvisionedThroughput"))

    @min_provisioned_throughput.setter
    def min_provisioned_throughput(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7209372cee7eb8021380d11654f8779390d77e8fa5034e208baa206edb8422f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minProvisionedThroughput", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="modelName")
    def model_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modelName"))

    @model_name.setter
    def model_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__246db0f2e3c2794ec642ff5589afcd225d22aeeef0173856cd1b8a19e3be72f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "modelName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="modelVersion")
    def model_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modelVersion"))

    @model_version.setter
    def model_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8faa5d39a1c50c0937e9ada650301611ebdbcbb2c72a533d76d7a13350b7d4bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "modelVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d85df55ade7de8d5146a1a1809561baadddfe8c2162f49382f9749aca4a35517)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="provisionedModelUnits")
    def provisioned_model_units(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "provisionedModelUnits"))

    @provisioned_model_units.setter
    def provisioned_model_units(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0afb2bdc6342bde8996d4341bbada5171208c933bac91cec2e70e4c3ebcb4af2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "provisionedModelUnits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scaleToZeroEnabled")
    def scale_to_zero_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "scaleToZeroEnabled"))

    @scale_to_zero_enabled.setter
    def scale_to_zero_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f13f0668cd4c89869f5cdd22f46f6bd6faed171f0a66453ab8cd82788afa283)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scaleToZeroEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workloadSize")
    def workload_size(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workloadSize"))

    @workload_size.setter
    def workload_size(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__310a1ec81c55dc2863fe2f526e0675e18185afcb588ed135018894a496895da5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workloadSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workloadType")
    def workload_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workloadType"))

    @workload_type.setter
    def workload_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92590622baa0c6b330e9ed5bbf461036c23f78b0a6fa109df1fa80da7b963ee6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workloadType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingConfigServedModels]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingConfigServedModels]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingConfigServedModels]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2d23a7f41385d0449902edb78963b500da63de3a8166b4db1d089812f4e547f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigTrafficConfig",
    jsii_struct_bases=[],
    name_mapping={"routes": "routes"},
)
class ModelServingConfigTrafficConfig:
    def __init__(
        self,
        *,
        routes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingConfigTrafficConfigRoutes", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param routes: routes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#routes ModelServing#routes}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26c7c05757d593b8a0348c6024c652a7d84c6460ca0619c9d6bf44268a2e6a30)
            check_type(argname="argument routes", value=routes, expected_type=type_hints["routes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if routes is not None:
            self._values["routes"] = routes

    @builtins.property
    def routes(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingConfigTrafficConfigRoutes"]]]:
        '''routes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#routes ModelServing#routes}
        '''
        result = self._values.get("routes")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingConfigTrafficConfigRoutes"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigTrafficConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingConfigTrafficConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigTrafficConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a27c3dbafebf718cda970a54eb8a52a6feffd4ebdb9c01c773b771ed47506e52)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putRoutes")
    def put_routes(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingConfigTrafficConfigRoutes", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__753bbf141b0f2bf6e6d75290fc838f96cb1be6fbe13fa1104c5ff64d7b8af24c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRoutes", [value]))

    @jsii.member(jsii_name="resetRoutes")
    def reset_routes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoutes", []))

    @builtins.property
    @jsii.member(jsii_name="routes")
    def routes(self) -> "ModelServingConfigTrafficConfigRoutesList":
        return typing.cast("ModelServingConfigTrafficConfigRoutesList", jsii.get(self, "routes"))

    @builtins.property
    @jsii.member(jsii_name="routesInput")
    def routes_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingConfigTrafficConfigRoutes"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingConfigTrafficConfigRoutes"]]], jsii.get(self, "routesInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ModelServingConfigTrafficConfig]:
        return typing.cast(typing.Optional[ModelServingConfigTrafficConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingConfigTrafficConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ed3546f7b58d1656c88678d778ef88d67153c95cb8fcf3363bb2f5cdb1f9774)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigTrafficConfigRoutes",
    jsii_struct_bases=[],
    name_mapping={
        "traffic_percentage": "trafficPercentage",
        "served_entity_name": "servedEntityName",
        "served_model_name": "servedModelName",
    },
)
class ModelServingConfigTrafficConfigRoutes:
    def __init__(
        self,
        *,
        traffic_percentage: jsii.Number,
        served_entity_name: typing.Optional[builtins.str] = None,
        served_model_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param traffic_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#traffic_percentage ModelServing#traffic_percentage}.
        :param served_entity_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#served_entity_name ModelServing#served_entity_name}.
        :param served_model_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#served_model_name ModelServing#served_model_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1034d01ae478d0ff7d53fa8e9eb3f1c39ce5e246f6938f2d2ff8db93266d84cc)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#traffic_percentage ModelServing#traffic_percentage}.'''
        result = self._values.get("traffic_percentage")
        assert result is not None, "Required property 'traffic_percentage' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def served_entity_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#served_entity_name ModelServing#served_entity_name}.'''
        result = self._values.get("served_entity_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def served_model_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#served_model_name ModelServing#served_model_name}.'''
        result = self._values.get("served_model_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigTrafficConfigRoutes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingConfigTrafficConfigRoutesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigTrafficConfigRoutesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7a51890fd2e83e06f326c7e4c2e56f53f42d2a7347050aeba6ca2e8851f42c13)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ModelServingConfigTrafficConfigRoutesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d50a454e94f6ba0de77ca3ed6e4c986773aafeecf1e7bdf013d3c9f0bfb06d9d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ModelServingConfigTrafficConfigRoutesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a171e44cdcb8fb5d35b9cf544b2f317c0b5a31052f8d7208c6cd6bc7ef45df13)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5d44c0aed82c54a25287ef87d8aa45152a3f4a88476b012faabf73df46cfaaf4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__14b0792afdfea0d401f6a4b08a68a01a419bda2856995bf92b3cb2c2ece2d4de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingConfigTrafficConfigRoutes]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingConfigTrafficConfigRoutes]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingConfigTrafficConfigRoutes]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d72e120537a643722e3ea01eaf526635108818279a9b0704008c436ca2e3c02)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ModelServingConfigTrafficConfigRoutesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigTrafficConfigRoutesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3ac51e4233ba30b56f41451336d2ab9323ee19d8cacf5a288fb6f25f8399ddac)
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
            type_hints = typing.get_type_hints(_typecheckingstub__30a3ef21a0628bece1da60e3e363f49bb44ff4960ed2932438f2f3f2e8e28fc0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "servedEntityName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="servedModelName")
    def served_model_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "servedModelName"))

    @served_model_name.setter
    def served_model_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ccf13241fbb6393fb91175bcbf263b744222f548e831da937cb15d48d8688ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "servedModelName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="trafficPercentage")
    def traffic_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "trafficPercentage"))

    @traffic_percentage.setter
    def traffic_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__343f7be9975e8626741942367396097be01927f29440a79139a39535ac8a8173)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "trafficPercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingConfigTrafficConfigRoutes]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingConfigTrafficConfigRoutes]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingConfigTrafficConfigRoutes]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4dcb2ae9c367370cace88cc97cb46ffe88301875cc46f2d6d6448cf8b18ec7f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingEmailNotifications",
    jsii_struct_bases=[],
    name_mapping={
        "on_update_failure": "onUpdateFailure",
        "on_update_success": "onUpdateSuccess",
    },
)
class ModelServingEmailNotifications:
    def __init__(
        self,
        *,
        on_update_failure: typing.Optional[typing.Sequence[builtins.str]] = None,
        on_update_success: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param on_update_failure: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#on_update_failure ModelServing#on_update_failure}.
        :param on_update_success: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#on_update_success ModelServing#on_update_success}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec15d8c68296bb16477a48a3639b5919a8d5aa14842f4e3952003bad9bc1b6a3)
            check_type(argname="argument on_update_failure", value=on_update_failure, expected_type=type_hints["on_update_failure"])
            check_type(argname="argument on_update_success", value=on_update_success, expected_type=type_hints["on_update_success"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if on_update_failure is not None:
            self._values["on_update_failure"] = on_update_failure
        if on_update_success is not None:
            self._values["on_update_success"] = on_update_success

    @builtins.property
    def on_update_failure(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#on_update_failure ModelServing#on_update_failure}.'''
        result = self._values.get("on_update_failure")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def on_update_success(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#on_update_success ModelServing#on_update_success}.'''
        result = self._values.get("on_update_success")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingEmailNotifications(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingEmailNotificationsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingEmailNotificationsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__50c76fd92ecfebd93e6f8469988dfd6918c23960301693a130ae752f3a17df65)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bb19928b2f7011b22fa9cbe2a32689bf4ba9f2e3341331e96eb11f9f9a01edf8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onUpdateFailure", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="onUpdateSuccess")
    def on_update_success(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "onUpdateSuccess"))

    @on_update_success.setter
    def on_update_success(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2b47dff0f66063a252df80f58960b26a918de3bb4bd2c3e41e6d9dbfc6888b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onUpdateSuccess", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ModelServingEmailNotifications]:
        return typing.cast(typing.Optional[ModelServingEmailNotifications], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingEmailNotifications],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a24f88b7eb74e78d7264c36b7a6f890219121146266f28bdf76d46d6c1a647eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingRateLimits",
    jsii_struct_bases=[],
    name_mapping={"calls": "calls", "renewal_period": "renewalPeriod", "key": "key"},
)
class ModelServingRateLimits:
    def __init__(
        self,
        *,
        calls: jsii.Number,
        renewal_period: builtins.str,
        key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param calls: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#calls ModelServing#calls}.
        :param renewal_period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#renewal_period ModelServing#renewal_period}.
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#key ModelServing#key}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2bc096bf5dd0480d8136763a51159848fe345d057322b64d9f93fc1a58719b6)
            check_type(argname="argument calls", value=calls, expected_type=type_hints["calls"])
            check_type(argname="argument renewal_period", value=renewal_period, expected_type=type_hints["renewal_period"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "calls": calls,
            "renewal_period": renewal_period,
        }
        if key is not None:
            self._values["key"] = key

    @builtins.property
    def calls(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#calls ModelServing#calls}.'''
        result = self._values.get("calls")
        assert result is not None, "Required property 'calls' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def renewal_period(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#renewal_period ModelServing#renewal_period}.'''
        result = self._values.get("renewal_period")
        assert result is not None, "Required property 'renewal_period' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#key ModelServing#key}.'''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingRateLimits(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingRateLimitsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingRateLimitsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c1362c38391e0cb26581a25774e7eed3b6e178f663ead9afee1161feeb83fb48)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ModelServingRateLimitsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61851880faeff49a81473200274e4ce2e204ab143df73de97a32d952b4570a7b)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ModelServingRateLimitsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__825f37b8790e58259c73e79d1dad7a668f733d725bf9af9b1b00831b59578300)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3d1401843efa3e74ab777e10b9feab0ef230eaea5db66f4fedb2078ee0e39558)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e47bd8423b35ca890f53c03d8d0be70442107984d50519d49c4ab0326be04cd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingRateLimits]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingRateLimits]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingRateLimits]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aabe8bc96732726ad1c9e42d2f57d12a265956a00f17aa2891088d19b091ec53)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ModelServingRateLimitsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingRateLimitsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__83414be43189d74dae6a84d3b6a5331272e36a2093d6b88c4d170f6fcc7166d8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetKey")
    def reset_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKey", []))

    @builtins.property
    @jsii.member(jsii_name="callsInput")
    def calls_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "callsInput"))

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="renewalPeriodInput")
    def renewal_period_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "renewalPeriodInput"))

    @builtins.property
    @jsii.member(jsii_name="calls")
    def calls(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "calls"))

    @calls.setter
    def calls(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56f669cb62b2a669d360afd50e30b208fbdd8522b0016c009cdd71c84a9ae901)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "calls", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc01a76da7a8d3824df4f3913e92b255d59c5c9f8d6b2767fe20975a7a9f99f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="renewalPeriod")
    def renewal_period(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "renewalPeriod"))

    @renewal_period.setter
    def renewal_period(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a14c2267ddb817069579eb9bf438ee0a312cddbdefa1eb8a7ae14c2cccb5034b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "renewalPeriod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingRateLimits]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingRateLimits]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingRateLimits]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb61e9bb41688605ab3418be9af2fc66a958f2fb816325a9450810b7b3c64146)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingTags",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class ModelServingTags:
    def __init__(
        self,
        *,
        key: builtins.str,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#key ModelServing#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#value ModelServing#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c62ce7cce72ef70c2428d7efe9f31163de11a07e4c94766ca334f8e343dcd0d)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
        }
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#key ModelServing#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#value ModelServing#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingTags(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingTagsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingTagsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c155cf36304447b4779b4f494bd3b9370f807b5926c72db693948914a4b55151)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ModelServingTagsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89eca721b95cf42590c1ba8cc3403371cf0d9b5a94888458923f984ec9dc970d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ModelServingTagsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3a2c05f9fa66fff11484970211c5e9ae0662030eecbecc2f2ea501dd8f1b8f4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__477ad4776aa26ecb9e618c7b0035cf66c938e01254c57404ae31523e057be727)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f64cbdc16de436c2c3d7bc1adf27bb37d42a8b2c14308c97f56a9d208680bcac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingTags]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingTags]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingTags]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13e9e5bd2d0014f499fe35c264e1a053c54bdc94a4b2d47f9a4d3aa057fb27d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ModelServingTagsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingTagsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__36b3532e5dc1504e1b7674aeab27c0175023fdac78e3d7eb290f91b9a2df070a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__791ce1ebcead96a87b728e97fcd3ff06dcc4f688709921baf24258441d8e868b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac92fbf7c52eb91a7d52b396b5fc11efec5f570e498e18fa941975426be8610e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingTags]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingTags]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingTags]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a608f26707d3f3f118ff4c5c2867c43fbbb58c1da84119abbf8089350b8728b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "update": "update"},
)
class ModelServingTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#create ModelServing#create}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#update ModelServing#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6740d3ce1034ef1c5164ea8e67bc93e961d0e6bee92c28b46a7d580aae113d72)
            check_type(argname="argument create", value=create, expected_type=type_hints["create"])
            check_type(argname="argument update", value=update, expected_type=type_hints["update"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#create ModelServing#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/model_serving#update ModelServing#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ad7cdc805e234f89caecb43dd029116fcd47986f72c09c48a3ef890d34cd6e0f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2d4d42baea57d3eecd43743b3e8ad0c09b839b4fd8a0a56b3e1473279f20bc4e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__463e97a8ca2acb32f0e249dce79fddab40fedb89cabb04620d42884d619be2ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c1feefc886a66c011e7d75efdbea27a7dfb17cf6eea23040fa7988b6826603c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ModelServing",
    "ModelServingAiGateway",
    "ModelServingAiGatewayFallbackConfig",
    "ModelServingAiGatewayFallbackConfigOutputReference",
    "ModelServingAiGatewayGuardrails",
    "ModelServingAiGatewayGuardrailsInput",
    "ModelServingAiGatewayGuardrailsInputOutputReference",
    "ModelServingAiGatewayGuardrailsInputPii",
    "ModelServingAiGatewayGuardrailsInputPiiOutputReference",
    "ModelServingAiGatewayGuardrailsOutput",
    "ModelServingAiGatewayGuardrailsOutputOutputReference",
    "ModelServingAiGatewayGuardrailsOutputPii",
    "ModelServingAiGatewayGuardrailsOutputPiiOutputReference",
    "ModelServingAiGatewayGuardrailsOutputReference",
    "ModelServingAiGatewayInferenceTableConfig",
    "ModelServingAiGatewayInferenceTableConfigOutputReference",
    "ModelServingAiGatewayOutputReference",
    "ModelServingAiGatewayRateLimits",
    "ModelServingAiGatewayRateLimitsList",
    "ModelServingAiGatewayRateLimitsOutputReference",
    "ModelServingAiGatewayUsageTrackingConfig",
    "ModelServingAiGatewayUsageTrackingConfigOutputReference",
    "ModelServingConfig",
    "ModelServingConfigA",
    "ModelServingConfigAOutputReference",
    "ModelServingConfigAutoCaptureConfig",
    "ModelServingConfigAutoCaptureConfigOutputReference",
    "ModelServingConfigServedEntities",
    "ModelServingConfigServedEntitiesExternalModel",
    "ModelServingConfigServedEntitiesExternalModelAi21LabsConfig",
    "ModelServingConfigServedEntitiesExternalModelAi21LabsConfigOutputReference",
    "ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig",
    "ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfigOutputReference",
    "ModelServingConfigServedEntitiesExternalModelAnthropicConfig",
    "ModelServingConfigServedEntitiesExternalModelAnthropicConfigOutputReference",
    "ModelServingConfigServedEntitiesExternalModelCohereConfig",
    "ModelServingConfigServedEntitiesExternalModelCohereConfigOutputReference",
    "ModelServingConfigServedEntitiesExternalModelCustomProviderConfig",
    "ModelServingConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth",
    "ModelServingConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuthOutputReference",
    "ModelServingConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth",
    "ModelServingConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuthOutputReference",
    "ModelServingConfigServedEntitiesExternalModelCustomProviderConfigOutputReference",
    "ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig",
    "ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfigOutputReference",
    "ModelServingConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig",
    "ModelServingConfigServedEntitiesExternalModelGoogleCloudVertexAiConfigOutputReference",
    "ModelServingConfigServedEntitiesExternalModelOpenaiConfig",
    "ModelServingConfigServedEntitiesExternalModelOpenaiConfigOutputReference",
    "ModelServingConfigServedEntitiesExternalModelOutputReference",
    "ModelServingConfigServedEntitiesExternalModelPalmConfig",
    "ModelServingConfigServedEntitiesExternalModelPalmConfigOutputReference",
    "ModelServingConfigServedEntitiesList",
    "ModelServingConfigServedEntitiesOutputReference",
    "ModelServingConfigServedModels",
    "ModelServingConfigServedModelsList",
    "ModelServingConfigServedModelsOutputReference",
    "ModelServingConfigTrafficConfig",
    "ModelServingConfigTrafficConfigOutputReference",
    "ModelServingConfigTrafficConfigRoutes",
    "ModelServingConfigTrafficConfigRoutesList",
    "ModelServingConfigTrafficConfigRoutesOutputReference",
    "ModelServingEmailNotifications",
    "ModelServingEmailNotificationsOutputReference",
    "ModelServingRateLimits",
    "ModelServingRateLimitsList",
    "ModelServingRateLimitsOutputReference",
    "ModelServingTags",
    "ModelServingTagsList",
    "ModelServingTagsOutputReference",
    "ModelServingTimeouts",
    "ModelServingTimeoutsOutputReference",
]

publication.publish()

def _typecheckingstub__fcdceab54e050923170b39eff538055f8b76b660bb8732c203c9c67261d31d37(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    ai_gateway: typing.Optional[typing.Union[ModelServingAiGateway, typing.Dict[builtins.str, typing.Any]]] = None,
    budget_policy_id: typing.Optional[builtins.str] = None,
    config: typing.Optional[typing.Union[ModelServingConfigA, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    email_notifications: typing.Optional[typing.Union[ModelServingEmailNotifications, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    rate_limits: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingRateLimits, typing.Dict[builtins.str, typing.Any]]]]] = None,
    route_optimized: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingTags, typing.Dict[builtins.str, typing.Any]]]]] = None,
    timeouts: typing.Optional[typing.Union[ModelServingTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__ee1bb539ded3a1716a5800f3c306bd3bf91c26ca2eb1bd182e8248cdbaff5430(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80a275a6bfdceace553e2be007a16e27fa4711760199dc7e1aa3df554d09920e(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingRateLimits, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9a326d60c6d2388605269123ef001af7186ca3f81f93ddf683edaaa2863033b(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingTags, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0d566a8ca84f82808361be591117475b17c993ad26a78d9b2a1a9dc810f962b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d495d7859885ddded479363c83b86f87c932a597926d0b2528792025cc752a11(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__754d4971dd64df250d28b3640fa44fa399b715301fc0dd43ff8d8304e9ef8d25(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eeb43c6ec513eda5c793054e174b6c273a821c9b323b20667ced44837696142c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d34de5d9b9fed3c9898fd854fd3464a901fd46e11ea543b532dd7d7a7df273a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d20f2c3755219d11514382f35601665878bc89f904a8e9fc1b0446c1b5275c4a(
    *,
    fallback_config: typing.Optional[typing.Union[ModelServingAiGatewayFallbackConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    guardrails: typing.Optional[typing.Union[ModelServingAiGatewayGuardrails, typing.Dict[builtins.str, typing.Any]]] = None,
    inference_table_config: typing.Optional[typing.Union[ModelServingAiGatewayInferenceTableConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    rate_limits: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingAiGatewayRateLimits, typing.Dict[builtins.str, typing.Any]]]]] = None,
    usage_tracking_config: typing.Optional[typing.Union[ModelServingAiGatewayUsageTrackingConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__701ce7f0a5acfcb5954469ee619c8f0fd11b46d959d772d902d0f6d9110d3248(
    *,
    enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5a6a471bbba8ab4a6d22b275622b1950ddc30e8d2e9db4c7fa07ec539696d59(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__074be50bae8c643f6ce3a55b4d11c9158fddb491281bd69d4dca7814a922b329(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d071b0a987a3a07349f67db236fefc8608f4b9b2240dd2162e265936cca9e9da(
    value: typing.Optional[ModelServingAiGatewayFallbackConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23233978ac7c7afa851e013c35b65df372202665674c78531b22b51134444acf(
    *,
    input: typing.Optional[typing.Union[ModelServingAiGatewayGuardrailsInput, typing.Dict[builtins.str, typing.Any]]] = None,
    output: typing.Optional[typing.Union[ModelServingAiGatewayGuardrailsOutput, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10bc8fe1b1ad77c3449c862fcf632beecfee459f26e8e3ef19e2cf3f9c87ffb9(
    *,
    invalid_keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
    pii: typing.Optional[typing.Union[ModelServingAiGatewayGuardrailsInputPii, typing.Dict[builtins.str, typing.Any]]] = None,
    safety: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    valid_topics: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be40d438526fc7c4b26bcd8fb1966decb78a477aa24c5f743cbd6876afbedc3e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be30c47b9f8392c82005c4714d69afd927a2e4128d0234daec48bc7bbcc22aa4(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9485bbe25a285d3fd2004b13f974eb8cccaf919d8c7732617d78ccf9e10118a7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a055d52f914b07e48516fb13fcec3049afcc8bac029935185bb954225f9e3f15(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d895f86afa6af4b36f3233794187324bcd3cf51b50eb9ecfedba0347f9ec7678(
    value: typing.Optional[ModelServingAiGatewayGuardrailsInput],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b475277a01edd50645fee8ea196ec320ff8d6ba0dbd6269e67f2f6664b1df5c(
    *,
    behavior: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__837abf08fbcd192a365dbd00321873606d2e16266ed7a87dfe5b43a331d28e67(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cc65d3ed87238263d4772d63f8d5128c5e89b63d160553ba956b09199d9d1ab(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cbb1b76a767619df9ecfe60dde9c3063c79370b5e969959f299b3360edabec2(
    value: typing.Optional[ModelServingAiGatewayGuardrailsInputPii],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f548d69157b58cd8398d69145143beb1e4e54267cb1b8b77e1e54810bc49a6c2(
    *,
    invalid_keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
    pii: typing.Optional[typing.Union[ModelServingAiGatewayGuardrailsOutputPii, typing.Dict[builtins.str, typing.Any]]] = None,
    safety: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    valid_topics: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83c9a450cdd4103e3510d73a3a94e3325c71495114d0ed0cd7e3dfe37ccc79a3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa1df921fbf5468202c64dd1e744d00224c96b9710c1e9f65efd8eeb9af3ef71(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ae7488d99494b8d7389b62eaa7d89aed5902d20dfcbdaa1a17db3ecc221d710(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5c18bb9d454083451fe947050a254c66190c3c00471e9069d1822022a498d10(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56db0ba3f16db8c24b5b9f5087e36a46901312ca22c8fb139e9c53265da47d67(
    value: typing.Optional[ModelServingAiGatewayGuardrailsOutput],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00608cb2e6ca08f41cc56ff2f0e178699afe3069582719b56f637d25334fa9c7(
    *,
    behavior: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db7e2b1dcffa2324c950b536e99c5414662556c9913c71baa1dd330123d7a65e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__018617612ef39f76acece0236edba7cb453409a10b3051f4908fd503b47a8481(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__611d0640b1a5e15838f158da92ac1b3c765a09bd27e5656ba420714f428ec5c0(
    value: typing.Optional[ModelServingAiGatewayGuardrailsOutputPii],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65a3cc711979faac9e1a4719183e502d256fe6392a49065e54d7a7a7de4973ca(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce1158a951e30d4eefb3d24cbacfc622a59fb2d19bbec8557c5545379264475f(
    value: typing.Optional[ModelServingAiGatewayGuardrails],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e4d5020d942b7ae2d9bd5bdfec5762919d692d98129acec818c004a64a3696d(
    *,
    catalog_name: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    schema_name: typing.Optional[builtins.str] = None,
    table_name_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a2563785aba3de18a87612f2207d74496620fa324689f9b5121216c64559f80(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a22eca4744ccae8295b824a610b4724c3d4a3abbfce2d7bad8991db11de07ff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e8f02ee39da1baccf024791fe4197f41eff4269ad6d40b893b4f631306cac12(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d34d429fc29e9504a4becb7cc1c1b8214a1aab5654d6a14ec403e143513d66ba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d2ce41ee52b23838dc8599d17f07aa841381a76f33896742ed95079840d74fe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17b1de74f932cd4b1ad6b25e355aec94b5a4207bdb7025155c9c22f41b5b3878(
    value: typing.Optional[ModelServingAiGatewayInferenceTableConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bfd3922a36ac9daf43294348f7c12373f1ed7d0a1ad431ee6f9a96209e227ca(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0bd70d0eaee59805f45831c75d3ea42514dde50993cef8e25adac744aab6605(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingAiGatewayRateLimits, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4eaf0079c4bbc7d152c2fd01885d79403434d9d10c9783925c4d1c613c37e692(
    value: typing.Optional[ModelServingAiGateway],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__471cdd7770b9ecb8fc419aaea437acccb2895584dd766e6bf6bdc137c5314da3(
    *,
    renewal_period: builtins.str,
    calls: typing.Optional[jsii.Number] = None,
    key: typing.Optional[builtins.str] = None,
    principal: typing.Optional[builtins.str] = None,
    tokens: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4749a9ca863d33734b709bd597f7485df7293e5d5981955fcb1977020062066e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7424ad869d07817c30ec5fcf326ccf5da3b7f7c1aa921e63879b01123c9f8b54(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c5827006339f47e87e6fb62e606fb9c84be888814813cf860d74a72ee5be9a4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8d2d3ae01789ce480148b558549a9547b11ca3dcd745f187cc644ad2cfe698c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2aedbb37dcb3e56327b8081eb7e329e8ccd74aed5340773b38f88214f8ed3f11(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30118c0679131c53c0d490aea759da7d1964983bc0c8014e1b7be561bd6a7ce0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingAiGatewayRateLimits]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ce27ce8c2b9f9ef764afc5f4924c8ea1de9acae8fa87dd88ae61079a89c69d7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d46d976942a0f8dea0a817f302c8a71f595a6c1e082ee96ff8766efa64e715df(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6050176ffba86707067e8d02087818cbb7ee25760a8b6552a1bfe314f854627f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__971740f22d738c496278b6ac6a91889f1a79c65661cf1a039a800f4f8f45fc5f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8141d81487fbdf3d7c2591674ab7c2b6d553f349e06b75a9e1fc2c9908df526b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ce89c379fde7986eac963cc2175c9f1865f6223fb5cd9d71e900aa6df99b558(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16b2b5e052b4b1b7dc8eeb46f717739a6b61dd7a325b3583d5c8cbac76669d5f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingAiGatewayRateLimits]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a71ae3be5012117ecde8e7927d576ee33a763b98088180dc610a7648bb55f223(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__195aaebdd8ff9aec3cacabf86a33cfd347169cce1a81858c2fb36a3b1218d020(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a956c9ef5a76e0935a37fc69655b0041e686dee9524415aec599f0dd2e5ec88d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4bd82eb47a29e7876d59f60112fe47ffe3e56fc6347d6139313d4cad0d80d581(
    value: typing.Optional[ModelServingAiGatewayUsageTrackingConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6ab99c61d3a667a89d9f5f2278213a6b075df770286584a1c864bfffbe20082(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    ai_gateway: typing.Optional[typing.Union[ModelServingAiGateway, typing.Dict[builtins.str, typing.Any]]] = None,
    budget_policy_id: typing.Optional[builtins.str] = None,
    config: typing.Optional[typing.Union[ModelServingConfigA, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    email_notifications: typing.Optional[typing.Union[ModelServingEmailNotifications, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    rate_limits: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingRateLimits, typing.Dict[builtins.str, typing.Any]]]]] = None,
    route_optimized: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingTags, typing.Dict[builtins.str, typing.Any]]]]] = None,
    timeouts: typing.Optional[typing.Union[ModelServingTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f209635c93e31eb79747b450ef07f331215993fe3c611af60329c1181395d96(
    *,
    auto_capture_config: typing.Optional[typing.Union[ModelServingConfigAutoCaptureConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    served_entities: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingConfigServedEntities, typing.Dict[builtins.str, typing.Any]]]]] = None,
    served_models: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingConfigServedModels, typing.Dict[builtins.str, typing.Any]]]]] = None,
    traffic_config: typing.Optional[typing.Union[ModelServingConfigTrafficConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39de19fd4e2e3b391a36cec3ae6b58c26f839e9b7717318f9c83712d464b8240(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9147fd79fb2787c00f1d1d5fcb304fbacd554791d29739786eb47f169656f6f9(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingConfigServedEntities, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64ca446d7fd23d5b8a13db8091cb8d50a52da9d34dc0d71f3453cc4df48cef58(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingConfigServedModels, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea9ca6d2b3625d2fe9064559e5ae3834b4a7d876e85a62ac1aedf940272c521b(
    value: typing.Optional[ModelServingConfigA],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebf8b2cb451924e6518496f1ef57ccd7f223277cadafa3d24b53b01883eebebe(
    *,
    catalog_name: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    schema_name: typing.Optional[builtins.str] = None,
    table_name_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67b5a32de74ec757f3fd7506a723ede01a5cbb72fe8a9e8f7f55a463e336efb9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d853ac5156bce5e1133f54bfb86fe697d8ede486fe731bfa34903faa9f25753c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f88136c1faf06edab8a7bc50c6c0024a15189007716a85bd8e4bdf7614acadd6(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7efdad892ab787aa5957098c51102ad9ba0b8cbd0427823bc099599637c9475(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8067336e1bc5f02cec3e8f5ba3e25eee6475ed8fb875a21dee0d49ed8a33c796(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db8d7706dcbc2a14ef38e7145ac608ca0bbc7781baea610fd87821dbd601e6f3(
    value: typing.Optional[ModelServingConfigAutoCaptureConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9403ea38a33e4adf7cbe8b181e16d03e70709409f2f5b3cd020360a19e5995d8(
    *,
    entity_name: typing.Optional[builtins.str] = None,
    entity_version: typing.Optional[builtins.str] = None,
    environment_vars: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    external_model: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModel, typing.Dict[builtins.str, typing.Any]]] = None,
    instance_profile_arn: typing.Optional[builtins.str] = None,
    max_provisioned_concurrency: typing.Optional[jsii.Number] = None,
    max_provisioned_throughput: typing.Optional[jsii.Number] = None,
    min_provisioned_concurrency: typing.Optional[jsii.Number] = None,
    min_provisioned_throughput: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    provisioned_model_units: typing.Optional[jsii.Number] = None,
    scale_to_zero_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    workload_size: typing.Optional[builtins.str] = None,
    workload_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83b566f9c1a169a08e2dd41b8ad9ddbe16d86060bfdb3621f6f0b19ed393bf4b(
    *,
    name: builtins.str,
    provider: builtins.str,
    task: builtins.str,
    ai21_labs_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelAi21LabsConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    amazon_bedrock_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    anthropic_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelAnthropicConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    cohere_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelCohereConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    custom_provider_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelCustomProviderConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    databricks_model_serving_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    google_cloud_vertex_ai_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    openai_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelOpenaiConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    palm_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelPalmConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c0ee9dc2d1327236ae97d5c3fe5c5338c3794a40d2d88c02560c83925676710(
    *,
    ai21_labs_api_key: typing.Optional[builtins.str] = None,
    ai21_labs_api_key_plaintext: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec48b6283533d5b4c9aeb09b046668b46db9832fe3be06b87645bbc1fe6b77af(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__edd2ee0da33d9d6eea9698dda6843afedb835973ae8037fa09e4c0271c49a7d8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d282adb0fc60caaab7e97d6b4dad4ad40925553dddb52a97b4ff71574fcc04b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b145ea06e1bd8516ff0cc11cbf9fd2f0e536da81a5b9c4cbc7ff9c0165bb85a2(
    value: typing.Optional[ModelServingConfigServedEntitiesExternalModelAi21LabsConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90dd82469e7808adf0a9158c33b32ac196f631841b5b828af93d7f461ae108ca(
    *,
    aws_region: builtins.str,
    bedrock_provider: builtins.str,
    aws_access_key_id: typing.Optional[builtins.str] = None,
    aws_access_key_id_plaintext: typing.Optional[builtins.str] = None,
    aws_secret_access_key: typing.Optional[builtins.str] = None,
    aws_secret_access_key_plaintext: typing.Optional[builtins.str] = None,
    instance_profile_arn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f80d852ac84bb277b80e781606f1e4dd2b8f0b03f4b4f4ce3d3d3f4f752061e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a72a91085af2cd622a5c4761f65046e6b7f2a78c1bd2cb36a4dcac5671bdb1f0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8133bf37f3c85f19bce5abc03f20201edaf6fc8221ffe5df7777c5c8c1ac6c12(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d32624b5e375ebc73dc077d306d42c18f51d38659a7f1881d39b43af1a5693cd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8628231e26f171719205ff1342000dc222ab9ce51be0e6d9ad62573609694543(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ab49af62430f7573f7b0d6955752f7f9cc4beb701051d0a3942de42d042983f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c269a46ec95800bb1f6e9e676994c75ad9c42fc985f8a721b147636f09ea1add(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff440325774f103952ce806a49c369c83ffba7c7a8f32abfb9bab976196c78b3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ee68940f0acb9b42fcf03a36fc4c76724008a5a5bd4d0a07014abf027865cf5(
    value: typing.Optional[ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__218f5a41e3d93d07362768598313f8b6139fdb7702b337199d420fb89c368361(
    *,
    anthropic_api_key: typing.Optional[builtins.str] = None,
    anthropic_api_key_plaintext: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd5800a1e5ff7cbebc7e2b6b8a7272a5844a5b75fcb4202bafab87d419f8cb2f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b023fe17c98d566c8fac5e33cf5eab2d6ab8b5f2aac678aab6bc169b3745228(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5848ba1341bb9431c45b0b69f1dac978fd02a025321db02af075278c3f843a68(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a64d693f11d3435c35e4ed3c8d0458aadee5227005cf5947d024560f5846c673(
    value: typing.Optional[ModelServingConfigServedEntitiesExternalModelAnthropicConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0dcb9995c75742d273441f3c12353f2a8a2afcd41c6de6865efd4504723a0455(
    *,
    cohere_api_base: typing.Optional[builtins.str] = None,
    cohere_api_key: typing.Optional[builtins.str] = None,
    cohere_api_key_plaintext: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49817b6641b2bf6dfba75fda89240974cad2adba5d155e98e85da7ac13731ecb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8016e448b70640ac1993c1def32afbb4bfa764c9638be4feb6b7c884c6ea246a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75b46b4f09d11ea820e7e30599eccb4dc33c186404ec5c41a642550f3c870525(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a6130a96a14102da4be21524f02627b913c1cc764316e95851a5760493b2a35(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a60f8a840727e7cd3ce21617d1ae19459196adef749e8e5126eb54fd90b745a(
    value: typing.Optional[ModelServingConfigServedEntitiesExternalModelCohereConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acefb3c90fd5fa5a76c875c3edd9195f1cd31e1134ec47148b34f99ba4061ef3(
    *,
    custom_provider_url: builtins.str,
    api_key_auth: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth, typing.Dict[builtins.str, typing.Any]]] = None,
    bearer_token_auth: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ea403d6efff0b91c769a3d4cea1936ff5b2b203ec568a52461627aeedec6e00(
    *,
    key: builtins.str,
    value: typing.Optional[builtins.str] = None,
    value_plaintext: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb360f86787ac25d68a33293ff2c056a6b2faa2487661cca7478588ebea83025(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6bc6d6c742e118629349376f8d1bb985bd4b7303c79ed1a78c4dcb66d48cdec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f7c1ba7d61da2693c8d6ea2ea2ea903f5d998978a45aebefaad253f32aa1ca9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28be31ba7f11dd44b5caca28fedf2aed1c80dbef628d53facf1a5cb77745fb5c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d46c545b237432a8ed3467497d409a2717ed45b59bedd0c1b670b50c7f7b6edc(
    value: typing.Optional[ModelServingConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ea00f39f8811accc2ea3a396d131a387872021812c42728c8bd01be5c259c45(
    *,
    token: typing.Optional[builtins.str] = None,
    token_plaintext: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97342de35125738cd1c3cbc111f9b1c2ba76ed4c8aa3cc9275528ae1734519f5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf74d09ad8e05e915922ff0858d4ee052a6377dd46fc3b4c4c1b87c4eb5bbf86(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7108bcd113e8183cf6d0da55f0c9684e2d52c129d2dcde5782045005aa2b94cd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04f8b7006e2f5c6e0736f875b49ebccb885528af2fca63a61ed59f37fb7802a8(
    value: typing.Optional[ModelServingConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__880bdcf1ed230d530d3ae04098e219309eb2abc4f4202744bc573219507d067b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01a15497db1e35c1dd1d02b3b151d7aed2ff8c599d1a8b26c31431387a3801d8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1bb9571a3126b8b0f119d9c6b50472a9499d0203230f0faa4f4a15a562554bba(
    value: typing.Optional[ModelServingConfigServedEntitiesExternalModelCustomProviderConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc7d014e30705b1d364c1fdbb4051d5a7521e5c6874f14751d9b24ade962ccae(
    *,
    databricks_workspace_url: builtins.str,
    databricks_api_token: typing.Optional[builtins.str] = None,
    databricks_api_token_plaintext: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cda49ad248f1b0eb4e12f1d86fc09682a280a677deaf69662836e58db84f468(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a09b862ceaf8807cca67fb6c462f92e28e9578762c5c262d8bfba2228fd0f6d4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd49280cf439abf571a338fc6412e818068c025e0d77cc72100dac32f0b9b6a5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__764fd45b87e6fd1d6cc9ef7428ca7893495c45311e54982f5cf24b55fe956143(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37a2eeb97c7e347fa469adfa492f6e516d30265f9a57baa620b6237d20f748bc(
    value: typing.Optional[ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92b6954ec6aa6882654c6ac61585c2b6514fa0a385b32c0c69b8458ab9cbae9b(
    *,
    project_id: builtins.str,
    region: builtins.str,
    private_key: typing.Optional[builtins.str] = None,
    private_key_plaintext: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7339c5e558b4e74c52f833742137d4bbcea4f72e83f86975eaee71599e7d600(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c09736953a1f4dc842c5ddfca94c10c1f2b54910f370d2882c93200b8e0b7d3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf6b5cb56b65f6edcf0b2595beb0d51e55d36de58c7e1ba783991d46acb6fb69(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4e43bac08a36bb8e92f526829ea8694cb6feaae67f7b6c76cfcbe99784cb350(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2fe18e54667c0b3b1ebf598df1007db79ba721ae23ad34eb9f2b455235075ee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__747458b582fdd786c5304b877f202e0d3bcc95124106a5e21746c03e185d5db3(
    value: typing.Optional[ModelServingConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8f3651cd444a6a03a04e10e5b69221f40bf7182b94e27a3f39209873e1a2293(
    *,
    microsoft_entra_client_id: typing.Optional[builtins.str] = None,
    microsoft_entra_client_secret: typing.Optional[builtins.str] = None,
    microsoft_entra_client_secret_plaintext: typing.Optional[builtins.str] = None,
    microsoft_entra_tenant_id: typing.Optional[builtins.str] = None,
    openai_api_base: typing.Optional[builtins.str] = None,
    openai_api_key: typing.Optional[builtins.str] = None,
    openai_api_key_plaintext: typing.Optional[builtins.str] = None,
    openai_api_type: typing.Optional[builtins.str] = None,
    openai_api_version: typing.Optional[builtins.str] = None,
    openai_deployment_name: typing.Optional[builtins.str] = None,
    openai_organization: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96eca2227ca1f6fbe25592666bfb974076efa4c4f49bad0f227b4a2e3eb17f28(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b01bce6ae02663c936859b6fdd65bf9c0787e0a2cbca469a27e0254691e4f99e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8acf6fc23afd1ec6f16b8d814ba0c5fd3202eb75dc88075e6fa2e70bf74e1a24(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__865c1cb72d08e3d90ac1f9581178c2014bb16d1a6af7900c9d40d558a483eca2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__810652b88b687685a4925c644374a2c91f370a298407a4299026d674b5c21875(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d910ae46138165d13f96fcad38ba4d03ea99b4f6398de8d21648bf91c47f812(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2942665469b2d114c5b1da0a35801aba473b6fd397a92822aba7a01d3bdb6a1e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c296616bcb2f780f9324a0d82e7f45784dfb1ce26cdb86d00ead5c681b6e9aa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffa62ef264416b3877aac41273f2288de305f9b5513e98b5feda0976afb36e2d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c39917ad5aa16b52b380336edcb2f53961c8750fdc6125952517ccc54b6a951(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__139733bf0f71f12b8e4408aa3bb941024091eb852488a633b731789178eda8c2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6bd90ea04878cc2aeedd21c4ab7495629f3d00b634d97096aff7e311c7d9b72(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0833c7b0577230e49679060b337fdaee600a3cc50d57218dab1a5fcc76ee558f(
    value: typing.Optional[ModelServingConfigServedEntitiesExternalModelOpenaiConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__286957a797d7d3795901e718c685222247720c7959b31372363ced1053c8349c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__186cb5665bc59aaa9ce409cb8208fb7dd40871e7acf79134bf4c7cdc5c10a2c1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12796f48f59357a3d01909964205037a61611468763c992eaf3a5e51a410b9d2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55764731d175dec17e4fc1dd16886f842c2d8074da5de0878b95679f89c7a6d9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23c418f265754be146809c589f248006a2e823e8931bce27139b60be00a944fb(
    value: typing.Optional[ModelServingConfigServedEntitiesExternalModel],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d7f69696e468cd3ad5ffddae6add89fbf9597eef2db2a900972795882f84260(
    *,
    palm_api_key: typing.Optional[builtins.str] = None,
    palm_api_key_plaintext: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2415e41a2d65031da7ad03ff288304364d2a75d69e744f5986dbebe1cd84314(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d267a559f3a647aa1bad3826b5c511002c6e84c231d14e688498f3452c1edc93(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a33122e6d04560c85f0d5112921621afc718b8a834763d918cd1908d3bf7a9cf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c92e50429bcc356c4a64039fd323e25eec3aac1617b8e44b20de759640c3439(
    value: typing.Optional[ModelServingConfigServedEntitiesExternalModelPalmConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5b118db3d06fdd140973d3aa4cc3a885623a42ff336d2eba7d45380b7f73959(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77acb6ce6c67f79a9b0d1314c0324692cb1fa6f244647ce53272762d81da2526(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a14f5528daebd60ea2786187c3c5a4423f153db7ab0e49a07d1ebac0cae40d3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b2a27fd791322888d58ee916ba218a9018446d6ac345466008049d6bd107087(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee9cad630026f7541c897b5d7427a66841f3a7b37ea702e67476de9e4e66337f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db21c169a62214a095fb313b873f0316c06668343c8a393d69f0adf180eee16d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingConfigServedEntities]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bce219b1818dd301c72b49d3cd1ee61649975cbfc261e27ce547ecf3c22dd279(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae5115ac461b91328a1e6dc01d00fc56cc73127601942a8e2bfdf61a81faef83(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a95a0cf2db47ff6a22b93698ae18fd680c16bfffea288ef207e3f6d3b19b3ba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e0ee29c76865b6a9038e2d80fdd880b5452ddf1d26a05c17b26c5a5c21de86e(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00de5f6a64e69f35f91ab15d64763aa2dcf66850be1d320dd964dc82d83d16db(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d50aa3719691b7a1493d8cbb7cafda8fb4902113822b2a31a9a43f0ecb4b95cc(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a225a3719b5f9c5ed1f2f06d7da50f6edaa8750290b4de359c01f3e40a080563(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de79c00c6f7b84582b448cb3d4202514d7fa7a8789b5b27fec93d1ed835ee369(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1f52003d4a91bc7d946132069fb47cefe31a03c327e8f02aa9ab78527fda020(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__433fc1fe0c4f22dff549f3df966f4772b6f051027df685b4697db5f8188cf8b1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b5652e3b9b3b2c1fbdda7fbd4a65bedf91f7780761c45270916e00ca4b69144(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__599c4926eb4037b5468d52469b0e74e25a1761e72aa97bfb197e66bd64775c50(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e75d8d050a460878e877a289cf925e1c7f4a6801b15a82d76bab5bca968748b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78afd2dd0ca10f2743b78f75b3e0ad3d2dae0e40f1c360b06b9dc9e867dce67d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4174906e58d55e3fcba05db5a4e8a4dd65ca404b2f456b42386ab0fd1cdb28a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingConfigServedEntities]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bec3cb547e17150f62247591fe28ea70f0c54212835f4df101f3b4570944be47(
    *,
    model_name: builtins.str,
    model_version: builtins.str,
    environment_vars: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    instance_profile_arn: typing.Optional[builtins.str] = None,
    max_provisioned_concurrency: typing.Optional[jsii.Number] = None,
    max_provisioned_throughput: typing.Optional[jsii.Number] = None,
    min_provisioned_concurrency: typing.Optional[jsii.Number] = None,
    min_provisioned_throughput: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    provisioned_model_units: typing.Optional[jsii.Number] = None,
    scale_to_zero_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    workload_size: typing.Optional[builtins.str] = None,
    workload_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff05e578ae924655a4766db44c640492b6da80d47a4d397d162294686bb36e28(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84178d8320aa70e5900bbea218aeecdfbe05a2428b168395a9aa09448d97dbbe(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77aa0d1b2688e799e89ca07474343e53c443abeaf05a0c5156a33508d59fd95a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8f1442c8f42d7e7012d749108f7abb52f31f2b526ec10327597cf72e34b592a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bd25af1f756a83a5d27b03efa85ec9bacb1572a074c8d1cb601c2981ae8b2ff(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ada08f44b74200500d8225f02a86080e59672509df4a491bf0c862b7d6f82931(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingConfigServedModels]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5e5fee82cb78ad16f4c3ce5d5b29f795f4c7e2b4d4ccb36068062744dd45bba(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c94b7c74795cba572f02b2d4bbeceffa53726338e6d644eea2330d1d67e2ab4(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__600c13055a167361ee8c1b924c85d37f4aed1c0dc1adcbde9c77bf70323c88a0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20f9b03a76829ba0f7a7044a4b3c493d25acb1ddea99af4c01fb72385a146ae3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fedb34b662eb91cf45e210d789ad69f7517ec0f36564f697e07a982785c3d72(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5aacea179332c7eab288223120cba027c0c7ac76a2dde1e6a910642a10f2c7e1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7209372cee7eb8021380d11654f8779390d77e8fa5034e208baa206edb8422f2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__246db0f2e3c2794ec642ff5589afcd225d22aeeef0173856cd1b8a19e3be72f6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8faa5d39a1c50c0937e9ada650301611ebdbcbb2c72a533d76d7a13350b7d4bc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d85df55ade7de8d5146a1a1809561baadddfe8c2162f49382f9749aca4a35517(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0afb2bdc6342bde8996d4341bbada5171208c933bac91cec2e70e4c3ebcb4af2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f13f0668cd4c89869f5cdd22f46f6bd6faed171f0a66453ab8cd82788afa283(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__310a1ec81c55dc2863fe2f526e0675e18185afcb588ed135018894a496895da5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92590622baa0c6b330e9ed5bbf461036c23f78b0a6fa109df1fa80da7b963ee6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2d23a7f41385d0449902edb78963b500da63de3a8166b4db1d089812f4e547f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingConfigServedModels]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26c7c05757d593b8a0348c6024c652a7d84c6460ca0619c9d6bf44268a2e6a30(
    *,
    routes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingConfigTrafficConfigRoutes, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a27c3dbafebf718cda970a54eb8a52a6feffd4ebdb9c01c773b771ed47506e52(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__753bbf141b0f2bf6e6d75290fc838f96cb1be6fbe13fa1104c5ff64d7b8af24c(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingConfigTrafficConfigRoutes, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ed3546f7b58d1656c88678d778ef88d67153c95cb8fcf3363bb2f5cdb1f9774(
    value: typing.Optional[ModelServingConfigTrafficConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1034d01ae478d0ff7d53fa8e9eb3f1c39ce5e246f6938f2d2ff8db93266d84cc(
    *,
    traffic_percentage: jsii.Number,
    served_entity_name: typing.Optional[builtins.str] = None,
    served_model_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a51890fd2e83e06f326c7e4c2e56f53f42d2a7347050aeba6ca2e8851f42c13(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d50a454e94f6ba0de77ca3ed6e4c986773aafeecf1e7bdf013d3c9f0bfb06d9d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a171e44cdcb8fb5d35b9cf544b2f317c0b5a31052f8d7208c6cd6bc7ef45df13(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d44c0aed82c54a25287ef87d8aa45152a3f4a88476b012faabf73df46cfaaf4(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14b0792afdfea0d401f6a4b08a68a01a419bda2856995bf92b3cb2c2ece2d4de(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d72e120537a643722e3ea01eaf526635108818279a9b0704008c436ca2e3c02(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingConfigTrafficConfigRoutes]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ac51e4233ba30b56f41451336d2ab9323ee19d8cacf5a288fb6f25f8399ddac(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30a3ef21a0628bece1da60e3e363f49bb44ff4960ed2932438f2f3f2e8e28fc0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ccf13241fbb6393fb91175bcbf263b744222f548e831da937cb15d48d8688ae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__343f7be9975e8626741942367396097be01927f29440a79139a39535ac8a8173(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4dcb2ae9c367370cace88cc97cb46ffe88301875cc46f2d6d6448cf8b18ec7f8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingConfigTrafficConfigRoutes]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec15d8c68296bb16477a48a3639b5919a8d5aa14842f4e3952003bad9bc1b6a3(
    *,
    on_update_failure: typing.Optional[typing.Sequence[builtins.str]] = None,
    on_update_success: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50c76fd92ecfebd93e6f8469988dfd6918c23960301693a130ae752f3a17df65(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb19928b2f7011b22fa9cbe2a32689bf4ba9f2e3341331e96eb11f9f9a01edf8(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2b47dff0f66063a252df80f58960b26a918de3bb4bd2c3e41e6d9dbfc6888b3(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a24f88b7eb74e78d7264c36b7a6f890219121146266f28bdf76d46d6c1a647eb(
    value: typing.Optional[ModelServingEmailNotifications],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2bc096bf5dd0480d8136763a51159848fe345d057322b64d9f93fc1a58719b6(
    *,
    calls: jsii.Number,
    renewal_period: builtins.str,
    key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1362c38391e0cb26581a25774e7eed3b6e178f663ead9afee1161feeb83fb48(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61851880faeff49a81473200274e4ce2e204ab143df73de97a32d952b4570a7b(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__825f37b8790e58259c73e79d1dad7a668f733d725bf9af9b1b00831b59578300(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d1401843efa3e74ab777e10b9feab0ef230eaea5db66f4fedb2078ee0e39558(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e47bd8423b35ca890f53c03d8d0be70442107984d50519d49c4ab0326be04cd8(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aabe8bc96732726ad1c9e42d2f57d12a265956a00f17aa2891088d19b091ec53(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingRateLimits]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83414be43189d74dae6a84d3b6a5331272e36a2093d6b88c4d170f6fcc7166d8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56f669cb62b2a669d360afd50e30b208fbdd8522b0016c009cdd71c84a9ae901(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc01a76da7a8d3824df4f3913e92b255d59c5c9f8d6b2767fe20975a7a9f99f1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a14c2267ddb817069579eb9bf438ee0a312cddbdefa1eb8a7ae14c2cccb5034b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb61e9bb41688605ab3418be9af2fc66a958f2fb816325a9450810b7b3c64146(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingRateLimits]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c62ce7cce72ef70c2428d7efe9f31163de11a07e4c94766ca334f8e343dcd0d(
    *,
    key: builtins.str,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c155cf36304447b4779b4f494bd3b9370f807b5926c72db693948914a4b55151(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89eca721b95cf42590c1ba8cc3403371cf0d9b5a94888458923f984ec9dc970d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3a2c05f9fa66fff11484970211c5e9ae0662030eecbecc2f2ea501dd8f1b8f4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__477ad4776aa26ecb9e618c7b0035cf66c938e01254c57404ae31523e057be727(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f64cbdc16de436c2c3d7bc1adf27bb37d42a8b2c14308c97f56a9d208680bcac(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13e9e5bd2d0014f499fe35c264e1a053c54bdc94a4b2d47f9a4d3aa057fb27d9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingTags]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36b3532e5dc1504e1b7674aeab27c0175023fdac78e3d7eb290f91b9a2df070a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__791ce1ebcead96a87b728e97fcd3ff06dcc4f688709921baf24258441d8e868b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac92fbf7c52eb91a7d52b396b5fc11efec5f570e498e18fa941975426be8610e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a608f26707d3f3f118ff4c5c2867c43fbbb58c1da84119abbf8089350b8728b6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingTags]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6740d3ce1034ef1c5164ea8e67bc93e961d0e6bee92c28b46a7d580aae113d72(
    *,
    create: typing.Optional[builtins.str] = None,
    update: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad7cdc805e234f89caecb43dd029116fcd47986f72c09c48a3ef890d34cd6e0f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d4d42baea57d3eecd43743b3e8ad0c09b839b4fd8a0a56b3e1473279f20bc4e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__463e97a8ca2acb32f0e249dce79fddab40fedb89cabb04620d42884d619be2ce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c1feefc886a66c011e7d75efdbea27a7dfb17cf6eea23040fa7988b6826603c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingTimeouts]],
) -> None:
    """Type checking stubs"""
    pass
