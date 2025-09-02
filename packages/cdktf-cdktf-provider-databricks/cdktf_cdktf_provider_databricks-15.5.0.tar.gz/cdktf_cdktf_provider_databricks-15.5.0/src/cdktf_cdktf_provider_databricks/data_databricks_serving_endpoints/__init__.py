r'''
# `data_databricks_serving_endpoints`

Refer to the Terraform Registry for docs: [`data_databricks_serving_endpoints`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints).
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


class DataDatabricksServingEndpoints(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpoints",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints databricks_serving_endpoints}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        endpoints: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpoints", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints databricks_serving_endpoints} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param endpoints: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#endpoints DataDatabricksServingEndpoints#endpoints}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0615872e535cf70fd90ef47a9ccecdadf73e2e1090160ca2bdf08e0c86ae237)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataDatabricksServingEndpointsConfig(
            endpoints=endpoints,
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
        '''Generates CDKTF code for importing a DataDatabricksServingEndpoints resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDatabricksServingEndpoints to import.
        :param import_from_id: The id of the existing DataDatabricksServingEndpoints that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDatabricksServingEndpoints to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__764b54df4324e43433d2afd71a93aa0593a7d292f6d58c2921a1bea12c43de59)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putEndpoints")
    def put_endpoints(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpoints", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a4d221fb471fa46a66c8e05973304599beaebc17ee8141c10103431ff97a288)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putEndpoints", [value]))

    @jsii.member(jsii_name="resetEndpoints")
    def reset_endpoints(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndpoints", []))

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
    @jsii.member(jsii_name="endpoints")
    def endpoints(self) -> "DataDatabricksServingEndpointsEndpointsList":
        return typing.cast("DataDatabricksServingEndpointsEndpointsList", jsii.get(self, "endpoints"))

    @builtins.property
    @jsii.member(jsii_name="endpointsInput")
    def endpoints_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpoints"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpoints"]]], jsii.get(self, "endpointsInput"))


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "endpoints": "endpoints",
    },
)
class DataDatabricksServingEndpointsConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        endpoints: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpoints", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param endpoints: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#endpoints DataDatabricksServingEndpoints#endpoints}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a099ffdf60f577f97ff43c040e213e0785da1e6cde613a5556a0612ed231e75e)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument endpoints", value=endpoints, expected_type=type_hints["endpoints"])
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
        if endpoints is not None:
            self._values["endpoints"] = endpoints

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
    def endpoints(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpoints"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#endpoints DataDatabricksServingEndpoints#endpoints}.'''
        result = self._values.get("endpoints")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpoints"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpoints",
    jsii_struct_bases=[],
    name_mapping={
        "ai_gateway": "aiGateway",
        "budget_policy_id": "budgetPolicyId",
        "config": "config",
        "creation_timestamp": "creationTimestamp",
        "creator": "creator",
        "description": "description",
        "id": "id",
        "last_updated_timestamp": "lastUpdatedTimestamp",
        "name": "name",
        "state": "state",
        "tags": "tags",
        "task": "task",
        "usage_policy_id": "usagePolicyId",
    },
)
class DataDatabricksServingEndpointsEndpoints:
    def __init__(
        self,
        *,
        ai_gateway: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsAiGateway", typing.Dict[builtins.str, typing.Any]]]]] = None,
        budget_policy_id: typing.Optional[builtins.str] = None,
        config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
        creation_timestamp: typing.Optional[jsii.Number] = None,
        creator: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        last_updated_timestamp: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        state: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsState", typing.Dict[builtins.str, typing.Any]]]]] = None,
        tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsTags", typing.Dict[builtins.str, typing.Any]]]]] = None,
        task: typing.Optional[builtins.str] = None,
        usage_policy_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param ai_gateway: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#ai_gateway DataDatabricksServingEndpoints#ai_gateway}.
        :param budget_policy_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#budget_policy_id DataDatabricksServingEndpoints#budget_policy_id}.
        :param config: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#config DataDatabricksServingEndpoints#config}.
        :param creation_timestamp: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#creation_timestamp DataDatabricksServingEndpoints#creation_timestamp}.
        :param creator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#creator DataDatabricksServingEndpoints#creator}.
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#description DataDatabricksServingEndpoints#description}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#id DataDatabricksServingEndpoints#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param last_updated_timestamp: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#last_updated_timestamp DataDatabricksServingEndpoints#last_updated_timestamp}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#name DataDatabricksServingEndpoints#name}.
        :param state: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#state DataDatabricksServingEndpoints#state}.
        :param tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#tags DataDatabricksServingEndpoints#tags}.
        :param task: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#task DataDatabricksServingEndpoints#task}.
        :param usage_policy_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#usage_policy_id DataDatabricksServingEndpoints#usage_policy_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9af00d754714e76bce938fafd2d285851b7698f6eb5629462e9bd7a6d4f2ad05)
            check_type(argname="argument ai_gateway", value=ai_gateway, expected_type=type_hints["ai_gateway"])
            check_type(argname="argument budget_policy_id", value=budget_policy_id, expected_type=type_hints["budget_policy_id"])
            check_type(argname="argument config", value=config, expected_type=type_hints["config"])
            check_type(argname="argument creation_timestamp", value=creation_timestamp, expected_type=type_hints["creation_timestamp"])
            check_type(argname="argument creator", value=creator, expected_type=type_hints["creator"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument last_updated_timestamp", value=last_updated_timestamp, expected_type=type_hints["last_updated_timestamp"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument state", value=state, expected_type=type_hints["state"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument task", value=task, expected_type=type_hints["task"])
            check_type(argname="argument usage_policy_id", value=usage_policy_id, expected_type=type_hints["usage_policy_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if ai_gateway is not None:
            self._values["ai_gateway"] = ai_gateway
        if budget_policy_id is not None:
            self._values["budget_policy_id"] = budget_policy_id
        if config is not None:
            self._values["config"] = config
        if creation_timestamp is not None:
            self._values["creation_timestamp"] = creation_timestamp
        if creator is not None:
            self._values["creator"] = creator
        if description is not None:
            self._values["description"] = description
        if id is not None:
            self._values["id"] = id
        if last_updated_timestamp is not None:
            self._values["last_updated_timestamp"] = last_updated_timestamp
        if name is not None:
            self._values["name"] = name
        if state is not None:
            self._values["state"] = state
        if tags is not None:
            self._values["tags"] = tags
        if task is not None:
            self._values["task"] = task
        if usage_policy_id is not None:
            self._values["usage_policy_id"] = usage_policy_id

    @builtins.property
    def ai_gateway(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsAiGateway"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#ai_gateway DataDatabricksServingEndpoints#ai_gateway}.'''
        result = self._values.get("ai_gateway")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsAiGateway"]]], result)

    @builtins.property
    def budget_policy_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#budget_policy_id DataDatabricksServingEndpoints#budget_policy_id}.'''
        result = self._values.get("budget_policy_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def config(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfig"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#config DataDatabricksServingEndpoints#config}.'''
        result = self._values.get("config")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfig"]]], result)

    @builtins.property
    def creation_timestamp(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#creation_timestamp DataDatabricksServingEndpoints#creation_timestamp}.'''
        result = self._values.get("creation_timestamp")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def creator(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#creator DataDatabricksServingEndpoints#creator}.'''
        result = self._values.get("creator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#description DataDatabricksServingEndpoints#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#id DataDatabricksServingEndpoints#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def last_updated_timestamp(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#last_updated_timestamp DataDatabricksServingEndpoints#last_updated_timestamp}.'''
        result = self._values.get("last_updated_timestamp")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#name DataDatabricksServingEndpoints#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsState"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#state DataDatabricksServingEndpoints#state}.'''
        result = self._values.get("state")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsState"]]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsTags"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#tags DataDatabricksServingEndpoints#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsTags"]]], result)

    @builtins.property
    def task(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#task DataDatabricksServingEndpoints#task}.'''
        result = self._values.get("task")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def usage_policy_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#usage_policy_id DataDatabricksServingEndpoints#usage_policy_id}.'''
        result = self._values.get("usage_policy_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsEndpoints(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGateway",
    jsii_struct_bases=[],
    name_mapping={
        "fallback_config": "fallbackConfig",
        "guardrails": "guardrails",
        "inference_table_config": "inferenceTableConfig",
        "rate_limits": "rateLimits",
        "usage_tracking_config": "usageTrackingConfig",
    },
)
class DataDatabricksServingEndpointsEndpointsAiGateway:
    def __init__(
        self,
        *,
        fallback_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
        guardrails: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsAiGatewayGuardrails", typing.Dict[builtins.str, typing.Any]]]]] = None,
        inference_table_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
        rate_limits: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsAiGatewayRateLimits", typing.Dict[builtins.str, typing.Any]]]]] = None,
        usage_tracking_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param fallback_config: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#fallback_config DataDatabricksServingEndpoints#fallback_config}.
        :param guardrails: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#guardrails DataDatabricksServingEndpoints#guardrails}.
        :param inference_table_config: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#inference_table_config DataDatabricksServingEndpoints#inference_table_config}.
        :param rate_limits: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#rate_limits DataDatabricksServingEndpoints#rate_limits}.
        :param usage_tracking_config: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#usage_tracking_config DataDatabricksServingEndpoints#usage_tracking_config}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85ef6c12abf6a5cd33b515e14f50d444f428b033cec0aa5fe188b1c884642f8c)
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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfig"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#fallback_config DataDatabricksServingEndpoints#fallback_config}.'''
        result = self._values.get("fallback_config")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfig"]]], result)

    @builtins.property
    def guardrails(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsAiGatewayGuardrails"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#guardrails DataDatabricksServingEndpoints#guardrails}.'''
        result = self._values.get("guardrails")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsAiGatewayGuardrails"]]], result)

    @builtins.property
    def inference_table_config(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfig"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#inference_table_config DataDatabricksServingEndpoints#inference_table_config}.'''
        result = self._values.get("inference_table_config")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfig"]]], result)

    @builtins.property
    def rate_limits(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsAiGatewayRateLimits"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#rate_limits DataDatabricksServingEndpoints#rate_limits}.'''
        result = self._values.get("rate_limits")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsAiGatewayRateLimits"]]], result)

    @builtins.property
    def usage_tracking_config(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfig"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#usage_tracking_config DataDatabricksServingEndpoints#usage_tracking_config}.'''
        result = self._values.get("usage_tracking_config")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfig"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsEndpointsAiGateway(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfig",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled"},
)
class DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfig:
    def __init__(
        self,
        *,
        enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#enabled DataDatabricksServingEndpoints#enabled}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdd8afca0c1a952abf274be5fe6312e1a9b16742e470341a0d33ae89ef2cba7e)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "enabled": enabled,
        }

    @builtins.property
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#enabled DataDatabricksServingEndpoints#enabled}.'''
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfigList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfigList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__39349c94f774405496b1679b3d26390ef22f0ead8b3a4a7301fbfe2fa172d253)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfigOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5c5d3ce044071beed6bdcd636382acd171391e9818f5eb6fcbfb030d61c611c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfigOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e509ca129d4936bb9f94586d592186873e6f9c2c81b1e112dde26f6d1be98507)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7e9c8ba56ee48759785f839712f7612cd315f895b4978f7199f5458ddcc3de72)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1e92c42cd34a59d42fa0b26ba83e3833588bb7adbbc6f9d0450a43df6743951b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfig]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfig]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60e8d7c03d3752fb6bbfe0af3fad902502fb8b8ad09a9ef1587de04321a96697)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__507ad4451274e138326b4499f36c7b2c8978912d52a982e09c116a13896798ee)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

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
            type_hints = typing.get_type_hints(_typecheckingstub__bde4678302a68fa9a408399e6f8d8f5dc4aa04d0166bdd7876ca1819d83a62b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5d476909660310d3e804f82eccf2ecebaa89afb058ac9661b7e7f86bc4aa97c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGatewayGuardrails",
    jsii_struct_bases=[],
    name_mapping={"input": "input", "output": "output"},
)
class DataDatabricksServingEndpointsEndpointsAiGatewayGuardrails:
    def __init__(
        self,
        *,
        input: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInput", typing.Dict[builtins.str, typing.Any]]]]] = None,
        output: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutput", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param input: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#input DataDatabricksServingEndpoints#input}.
        :param output: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#output DataDatabricksServingEndpoints#output}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b35a2904cf15bf1c7c0cce86c7c8b0402319026d5c474d79a27c6a531bcd1671)
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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInput"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#input DataDatabricksServingEndpoints#input}.'''
        result = self._values.get("input")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInput"]]], result)

    @builtins.property
    def output(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutput"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#output DataDatabricksServingEndpoints#output}.'''
        result = self._values.get("output")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutput"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsEndpointsAiGatewayGuardrails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInput",
    jsii_struct_bases=[],
    name_mapping={
        "invalid_keywords": "invalidKeywords",
        "pii": "pii",
        "safety": "safety",
        "valid_topics": "validTopics",
    },
)
class DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInput:
    def __init__(
        self,
        *,
        invalid_keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        pii: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPii", typing.Dict[builtins.str, typing.Any]]]]] = None,
        safety: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        valid_topics: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param invalid_keywords: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#invalid_keywords DataDatabricksServingEndpoints#invalid_keywords}.
        :param pii: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#pii DataDatabricksServingEndpoints#pii}.
        :param safety: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#safety DataDatabricksServingEndpoints#safety}.
        :param valid_topics: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#valid_topics DataDatabricksServingEndpoints#valid_topics}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27c6fa0bb79dac22f957d3b70853f2087e5d8a5fad26fbc1f5e281f9ea386f15)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#invalid_keywords DataDatabricksServingEndpoints#invalid_keywords}.'''
        result = self._values.get("invalid_keywords")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def pii(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPii"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#pii DataDatabricksServingEndpoints#pii}.'''
        result = self._values.get("pii")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPii"]]], result)

    @builtins.property
    def safety(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#safety DataDatabricksServingEndpoints#safety}.'''
        result = self._values.get("safety")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def valid_topics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#valid_topics DataDatabricksServingEndpoints#valid_topics}.'''
        result = self._values.get("valid_topics")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInput(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__862dfe6ec870b187215fb6c93310517d79ae9623eaefc08511bd7b262dac9030)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc2c447973d4d57c9b2c4d1a3c5750f86fd78075d9e9443a2965f1fcf0f1c884)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f147aa44ed253c5e55603e4260e6b50414d03d36771eb1c3269488c69aeb491)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3ed687939da48ed725dbbb6c92cc668d50e65a6e177a69bea1d5d535bc1d5ac5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0286483674aaa0f59899fe987afb3e9467b8b0e11a6fde3d1c2d139ae7642aa0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInput]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInput]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInput]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a70c46354ea268cf90ac27cb143ca49130c650da3b38c0e9d377048b4d65b2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bf87a8be50a7805f87073b6bfe6eeb106aff1c0ace45eb8e4aec26686992debe)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putPii")
    def put_pii(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPii", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cbcef1d861b390680d76622b0f02b449d0a85b2c294e0046577dedddb4e36002)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
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
    ) -> "DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPiiList":
        return typing.cast("DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPiiList", jsii.get(self, "pii"))

    @builtins.property
    @jsii.member(jsii_name="invalidKeywordsInput")
    def invalid_keywords_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "invalidKeywordsInput"))

    @builtins.property
    @jsii.member(jsii_name="piiInput")
    def pii_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPii"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPii"]]], jsii.get(self, "piiInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__bc1afc98beb85a3803122387fe368b7ace73f6f06fab4a40c0c6d75ce3b1edf9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a2c11de8a82790674577220460d8c8bc5dd169538c129edfde1f67daff576f39)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "safety", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="validTopics")
    def valid_topics(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "validTopics"))

    @valid_topics.setter
    def valid_topics(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__397a2231b624861594aa02d1dc07d079f9c07e24c03cff9bb2ab7e05fe27365d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "validTopics", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInput]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInput]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInput]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__418c9164be5fb206ef20db43b872c88e9b25038f453c80621ff083242fa26511)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPii",
    jsii_struct_bases=[],
    name_mapping={"behavior": "behavior"},
)
class DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPii:
    def __init__(self, *, behavior: typing.Optional[builtins.str] = None) -> None:
        '''
        :param behavior: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#behavior DataDatabricksServingEndpoints#behavior}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7487c802d2f64b05d982ec79e13dbaf096d95ffb6605019656f41bd46dfd6dc9)
            check_type(argname="argument behavior", value=behavior, expected_type=type_hints["behavior"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if behavior is not None:
            self._values["behavior"] = behavior

    @builtins.property
    def behavior(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#behavior DataDatabricksServingEndpoints#behavior}.'''
        result = self._values.get("behavior")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPii(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPiiList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPiiList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__179c7224d88195b2d8c41685bad158678f1e8b3ace0b160f0395dc9f5fea9f88)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPiiOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b538485c7495ece19b6b8dc82207a17d19a9f14f2fed066fee2b41cd6d66f27f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPiiOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84512a7158a8c06d9471dd0f19e95d33b8746919188638c9db332a636cee63e1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6735f9edde734e4ae5ef2b3ee3a1a990330bc9e492723f4275f3b76695e50443)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b7355e8abd4b488574cc5c26384c54512b02f297466a25a74582dda943bc380a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPii]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPii]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPii]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ba98203666d535e172e86b0b6a5bf530dd434c51c89312956d858a68427a3aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPiiOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPiiOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7215e1c21c69b5a1d27e6bbfef1f7998dffd0e8c59957adf123244d3264d7386)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

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
            type_hints = typing.get_type_hints(_typecheckingstub__d8ae34dada995457e92d5b86b29746485b725f5850bc0590a48083732d6d97db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "behavior", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPii]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPii]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPii]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be7199664685820f755b70a1ccb9a7032e30a7a955cd33a57f596e302faee1b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6fd297938781b70e91f9eaefb773bda8e9dc608a7cd735ad986458602a4355ff)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__786e078d137f0f586618487fd8983bedae054b459b97076d43b0366f4eaf34ea)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c0bfb33cca14beba305aaae00df5de426d323043c96a738bd168ef3e3b7ba8a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ad3cf6dc428c0157587d6ac8d419beb661076bb32bde3594e808851c09b17fe4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__98e69c2374bdfdc2031061384c06c31034ebf46f6844ad4bf585df59e4a5b6aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrails]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrails]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrails]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad0fadb4df817f5d95bc305dc909c5a7ca2c722d507b3d81b358c55adb641018)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutput",
    jsii_struct_bases=[],
    name_mapping={
        "invalid_keywords": "invalidKeywords",
        "pii": "pii",
        "safety": "safety",
        "valid_topics": "validTopics",
    },
)
class DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutput:
    def __init__(
        self,
        *,
        invalid_keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        pii: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPii", typing.Dict[builtins.str, typing.Any]]]]] = None,
        safety: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        valid_topics: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param invalid_keywords: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#invalid_keywords DataDatabricksServingEndpoints#invalid_keywords}.
        :param pii: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#pii DataDatabricksServingEndpoints#pii}.
        :param safety: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#safety DataDatabricksServingEndpoints#safety}.
        :param valid_topics: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#valid_topics DataDatabricksServingEndpoints#valid_topics}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3943d4edc35bad60ac260aca63b1c0d01bc177daaa955ce6d7412d02b114909f)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#invalid_keywords DataDatabricksServingEndpoints#invalid_keywords}.'''
        result = self._values.get("invalid_keywords")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def pii(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPii"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#pii DataDatabricksServingEndpoints#pii}.'''
        result = self._values.get("pii")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPii"]]], result)

    @builtins.property
    def safety(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#safety DataDatabricksServingEndpoints#safety}.'''
        result = self._values.get("safety")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def valid_topics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#valid_topics DataDatabricksServingEndpoints#valid_topics}.'''
        result = self._values.get("valid_topics")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutput(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e883a54c60fa890cc7afda6fad542d4a037d6c7f48221db614204cfef4e8c50d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48730d3afd101325402b2ce7479040d4448ec7cf11929334f7e185134730286e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7781baad1132cddfe41719c14bbbdf9dced94a5f6d8a9d85e649a58ab6b5874)
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
            type_hints = typing.get_type_hints(_typecheckingstub__03b6daa51dada3304393b168146b2ad270aa1c8c02dfad0735d86faae976adf5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5401b4789b54bbe1e5d9cc63caf4820667e1ab810db7432d3ad74e9ecf646974)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutput]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutput]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutput]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__754c7e8eea5e50c2c89ab612027137751fcd7f0d234e251a161c8c5dcbcca714)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d7b7d148aa0bbf4148e6ae5424a8fd3774cd4c69c67289a290e50100388e2489)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putPii")
    def put_pii(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPii", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca9282553db5a76c35d565330d715ee7638a1cd8e0b73b4d2c933cf81edf50d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
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
    ) -> "DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPiiList":
        return typing.cast("DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPiiList", jsii.get(self, "pii"))

    @builtins.property
    @jsii.member(jsii_name="invalidKeywordsInput")
    def invalid_keywords_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "invalidKeywordsInput"))

    @builtins.property
    @jsii.member(jsii_name="piiInput")
    def pii_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPii"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPii"]]], jsii.get(self, "piiInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__cb8af2b59cad36a6582758c608b9938ce26be61c07b9c950231c16bc71af25db)
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
            type_hints = typing.get_type_hints(_typecheckingstub__623af87c35a2d74465ed536383ecb7cf831b5c6a0c0b0d6e96dababfec253ad2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "safety", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="validTopics")
    def valid_topics(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "validTopics"))

    @valid_topics.setter
    def valid_topics(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a71c6e8543ea9914d0786790df2427292a1d3e44c12fe9585d172d574255390)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "validTopics", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutput]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutput]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutput]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__147130f79b1d3e1ab0f545fce582bf9dbdf2a6abf2e61ea2439b53f6fa38f754)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPii",
    jsii_struct_bases=[],
    name_mapping={"behavior": "behavior"},
)
class DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPii:
    def __init__(self, *, behavior: typing.Optional[builtins.str] = None) -> None:
        '''
        :param behavior: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#behavior DataDatabricksServingEndpoints#behavior}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__470dd95dd2a424232fd36f77030942f46aa744716caf08f257cc416b67f297b0)
            check_type(argname="argument behavior", value=behavior, expected_type=type_hints["behavior"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if behavior is not None:
            self._values["behavior"] = behavior

    @builtins.property
    def behavior(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#behavior DataDatabricksServingEndpoints#behavior}.'''
        result = self._values.get("behavior")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPii(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPiiList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPiiList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f9ec2dbd719e274dedfa7a52aaf0d7d217d5eba94ef9d85588f151866f44a18a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPiiOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5633d1980556ca7695b6ad069d3d1c6168b2baec051de889ab582c51091c8254)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPiiOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20e4711a8185636db51a44ac8cbb7f51090ec67bd216e44814b663059304dc6a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bec22fc38f7e283326bc95a0c7637c037047c2e6d17929377232ad914ca738fb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__94fd71352e17aa006145248fbc10bbe75a529f782797b06a2a15fc8a0817eab4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPii]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPii]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPii]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__103b26c8f2bd70abf136265e525a7091eb46ef59d5f3497d443ad93558a32991)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPiiOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPiiOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1721f17b3b0d7fc1b373db9dc8716f7033a2c6168c7a4d5661d6d4047cca240d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

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
            type_hints = typing.get_type_hints(_typecheckingstub__ef9b59ea7b3129109a60ae2bf421d2c3f58c21fdda79e30d9436c40e2cbcc838)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "behavior", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPii]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPii]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPii]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf2e5f5c1921fc6a7fc7dbf9ed8e818cf199fafefa9741dfcb66d9670a9263ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__545ffca41630ab2ad6c26ec1ef9741ae9b8d636b66a1f97d506fb03fb8c1aab5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putInput")
    def put_input(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInput, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb24f16555c197c4fa946eab776c66aa1298c4b3de94a41dc9e970523bf9b9fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putInput", [value]))

    @jsii.member(jsii_name="putOutput")
    def put_output(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutput, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff3fa7014cf544df85be7d9e2cd453b87db8387fbd4bcc42328f3f7da49a7f07)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
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
    ) -> DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputList:
        return typing.cast(DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputList, jsii.get(self, "input"))

    @builtins.property
    @jsii.member(jsii_name="output")
    def output(
        self,
    ) -> DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputList:
        return typing.cast(DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputList, jsii.get(self, "output"))

    @builtins.property
    @jsii.member(jsii_name="inputInput")
    def input_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInput]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInput]]], jsii.get(self, "inputInput"))

    @builtins.property
    @jsii.member(jsii_name="outputInput")
    def output_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutput]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutput]]], jsii.get(self, "outputInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayGuardrails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayGuardrails]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayGuardrails]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4ac4d7d05b551b415d4cb93b23302ee64d1d87d04d5f3364657edc6faabcaae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfig",
    jsii_struct_bases=[],
    name_mapping={
        "catalog_name": "catalogName",
        "enabled": "enabled",
        "schema_name": "schemaName",
        "table_name_prefix": "tableNamePrefix",
    },
)
class DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfig:
    def __init__(
        self,
        *,
        catalog_name: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        schema_name: typing.Optional[builtins.str] = None,
        table_name_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param catalog_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#catalog_name DataDatabricksServingEndpoints#catalog_name}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#enabled DataDatabricksServingEndpoints#enabled}.
        :param schema_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#schema_name DataDatabricksServingEndpoints#schema_name}.
        :param table_name_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#table_name_prefix DataDatabricksServingEndpoints#table_name_prefix}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18b3a8bf3e7e0377083098da2e516ab8e36685dffd1fe8afeeb2c940ff3cfc10)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#catalog_name DataDatabricksServingEndpoints#catalog_name}.'''
        result = self._values.get("catalog_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#enabled DataDatabricksServingEndpoints#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def schema_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#schema_name DataDatabricksServingEndpoints#schema_name}.'''
        result = self._values.get("schema_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def table_name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#table_name_prefix DataDatabricksServingEndpoints#table_name_prefix}.'''
        result = self._values.get("table_name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfigList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfigList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ee77fa981d8cf39a8a5d452407926091769c6a842495a193de3ad8678a0b1c81)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfigOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64991490810460d510b5870a92713ba7315c6b21885f12f71872003d8cd5c077)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfigOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__954f59f98b1348459eba60c6585d6e8a21138e386fa8aab84ba6491a9407ca6e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__227c6d0619144c0d1b93f39393bc5cbb86bc7d0e7217d8b9df20722af13e9238)
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
            type_hints = typing.get_type_hints(_typecheckingstub__496adebda8d7a7de5a7730876ee04893126757b31bd6cb9a8217088ddc6db822)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfig]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfig]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a30f31c07c3a716cfb2cbd7f2a37511e6be712a52c365be19931091c23065840)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6453dad98327dbea8e84b4e25d10343a2d3f1ba7aeac923e1910ecf04c590316)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

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
            type_hints = typing.get_type_hints(_typecheckingstub__c38bb23f65ea4087ef265bfd634cacf0b85031a543decd901ba9322f918b00f2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__28c0d73bdc4f7ffbfa0a4a90b68e548eb4678add3a0e918b2a8e88a38ea49b26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="schemaName")
    def schema_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schemaName"))

    @schema_name.setter
    def schema_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9deecda72312cb7a1cb376a5eadc694fbc95a402d816e202b207fe8ad5acdcbd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "schemaName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tableNamePrefix")
    def table_name_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tableNamePrefix"))

    @table_name_prefix.setter
    def table_name_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bef79bf1917bd6b4d67f85b1ab54a4bc7ef50efb87206a3c57aeb2884b813751)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tableNamePrefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d12a1fbc752fdcc4d093861ff09cd4dfe77eaff15b20d0327c7edfb945032016)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsAiGatewayList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGatewayList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e1e50dcff637f3629ad195574ba72a6d05d2d2f033660587b1aaa779c7e79f29)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksServingEndpointsEndpointsAiGatewayOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7e37c14373966f84028c3997788e5793adbb98776039f7a0a9eb0e6ef2f6848)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksServingEndpointsEndpointsAiGatewayOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cbfc2a1f2b0ac294d66c082cf6de3bcab6079fd5932c6104a3e4d71abcc0cc67)
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
            type_hints = typing.get_type_hints(_typecheckingstub__239d8948a653cb4d445c8acf0a3f7f5a005715ac475dd7d5c152f36188d3bed1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c8296e639700632f7adadd246a3652fc6ec5bf74164888a797125263d9071bf4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGateway]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGateway]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGateway]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a881d348517413e4055dc6c107b23282fee7045201f345b0b7a7b4765049b2d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsAiGatewayOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGatewayOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__679e36b908666867397a6f7ca0a7c9d9b305187cd8bedcb32ec5c38fa493778e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putFallbackConfig")
    def put_fallback_config(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfig, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d405342a42d85dbf6e7fb09ba62ade812a2767f53f53d82802c32a187464ea6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putFallbackConfig", [value]))

    @jsii.member(jsii_name="putGuardrails")
    def put_guardrails(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrails, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2e0e33c054334c12459dda69306a3fc8b4122e2b097b8f08f8b4c1f44a7b7f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putGuardrails", [value]))

    @jsii.member(jsii_name="putInferenceTableConfig")
    def put_inference_table_config(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfig, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76818eaa322e8e38115fc827ee62856abe731fcb005a0d6e9f5f042fe16c388b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putInferenceTableConfig", [value]))

    @jsii.member(jsii_name="putRateLimits")
    def put_rate_limits(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsAiGatewayRateLimits", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9aeaccb1cfbc3510b0fa93143d4e79ea0dbfd6a71aa75df6ea49c9607fa4ed25)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRateLimits", [value]))

    @jsii.member(jsii_name="putUsageTrackingConfig")
    def put_usage_tracking_config(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfig", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee3d3da13b492df2b37012e5950e1023e4d616abeba7912afbc91f0ab2df1ca7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
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
    ) -> DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfigList:
        return typing.cast(DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfigList, jsii.get(self, "fallbackConfig"))

    @builtins.property
    @jsii.member(jsii_name="guardrails")
    def guardrails(
        self,
    ) -> DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsList:
        return typing.cast(DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsList, jsii.get(self, "guardrails"))

    @builtins.property
    @jsii.member(jsii_name="inferenceTableConfig")
    def inference_table_config(
        self,
    ) -> DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfigList:
        return typing.cast(DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfigList, jsii.get(self, "inferenceTableConfig"))

    @builtins.property
    @jsii.member(jsii_name="rateLimits")
    def rate_limits(
        self,
    ) -> "DataDatabricksServingEndpointsEndpointsAiGatewayRateLimitsList":
        return typing.cast("DataDatabricksServingEndpointsEndpointsAiGatewayRateLimitsList", jsii.get(self, "rateLimits"))

    @builtins.property
    @jsii.member(jsii_name="usageTrackingConfig")
    def usage_tracking_config(
        self,
    ) -> "DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfigList":
        return typing.cast("DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfigList", jsii.get(self, "usageTrackingConfig"))

    @builtins.property
    @jsii.member(jsii_name="fallbackConfigInput")
    def fallback_config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfig]]], jsii.get(self, "fallbackConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="guardrailsInput")
    def guardrails_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrails]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrails]]], jsii.get(self, "guardrailsInput"))

    @builtins.property
    @jsii.member(jsii_name="inferenceTableConfigInput")
    def inference_table_config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfig]]], jsii.get(self, "inferenceTableConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="rateLimitsInput")
    def rate_limits_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsAiGatewayRateLimits"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsAiGatewayRateLimits"]]], jsii.get(self, "rateLimitsInput"))

    @builtins.property
    @jsii.member(jsii_name="usageTrackingConfigInput")
    def usage_tracking_config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfig"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfig"]]], jsii.get(self, "usageTrackingConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGateway]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGateway]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGateway]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1909db5f1f4774fb07a6f4176437c9e65116197a0b3ab3c3cb2597f85b348b86)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGatewayRateLimits",
    jsii_struct_bases=[],
    name_mapping={
        "renewal_period": "renewalPeriod",
        "calls": "calls",
        "key": "key",
        "principal": "principal",
        "tokens": "tokens",
    },
)
class DataDatabricksServingEndpointsEndpointsAiGatewayRateLimits:
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
        :param renewal_period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#renewal_period DataDatabricksServingEndpoints#renewal_period}.
        :param calls: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#calls DataDatabricksServingEndpoints#calls}.
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#key DataDatabricksServingEndpoints#key}.
        :param principal: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#principal DataDatabricksServingEndpoints#principal}.
        :param tokens: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#tokens DataDatabricksServingEndpoints#tokens}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a45f38c3405f5e0a49a103dc227c9fce97a0b7f17d52770c252241b3bf96b98)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#renewal_period DataDatabricksServingEndpoints#renewal_period}.'''
        result = self._values.get("renewal_period")
        assert result is not None, "Required property 'renewal_period' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def calls(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#calls DataDatabricksServingEndpoints#calls}.'''
        result = self._values.get("calls")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#key DataDatabricksServingEndpoints#key}.'''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def principal(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#principal DataDatabricksServingEndpoints#principal}.'''
        result = self._values.get("principal")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tokens(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#tokens DataDatabricksServingEndpoints#tokens}.'''
        result = self._values.get("tokens")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsEndpointsAiGatewayRateLimits(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksServingEndpointsEndpointsAiGatewayRateLimitsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGatewayRateLimitsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3768383c43f406bd01462629c61b41ec9d667a7da01e7207652a2c53dca0e5b0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksServingEndpointsEndpointsAiGatewayRateLimitsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3b30f0470c3da5262d5611a74a4840df248f7160853b7fba7a6423b20b12031)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksServingEndpointsEndpointsAiGatewayRateLimitsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30af78a711399c81472fde0a6635b4a88bf6a4ff27d00dacc4a625e73a1ee819)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8e122e32bb121825e4f23e0a15ad68bff6eb074dcbfa72b4d3de1c741606000f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__879da07e1c55371f77cb390dd912fe9b5a2a0c01f17e57aad63e5151e2609e79)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayRateLimits]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayRateLimits]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayRateLimits]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05b0b98c6f9bd434afc09d3e8a8a250ac626dfef243e782daf2ffece5e2369f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsAiGatewayRateLimitsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGatewayRateLimitsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__95ec05510b98754bb479fd661c52cbf26390b8d890aa55d03a46a26f701ae34a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a7748c580e7b515bdc10ebd826e49eeb41b85648b74d5c693877e8b8b59a813f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "calls", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0b94b7af0fb7454881f000da23697cf985c31bd2ccfd8c78a98f64772039870)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="principal")
    def principal(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "principal"))

    @principal.setter
    def principal(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a1958557921572acac7bd14832c9690947560cb3f58513b1d91e302072aa2ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "principal", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="renewalPeriod")
    def renewal_period(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "renewalPeriod"))

    @renewal_period.setter
    def renewal_period(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e207d05d22d36e747ea537cd2566fd3baec3f56379e6dfa5b625da6e000e001)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "renewalPeriod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokens")
    def tokens(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokens"))

    @tokens.setter
    def tokens(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea134e1a76a599bf356f3756cf7b1f409293a55be85864c7dc3811a4b4b7935c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokens", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayRateLimits]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayRateLimits]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayRateLimits]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c19a709f749c1795751965101e73f2969150ccb300ba7a42aff43ce220e9bde2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfig",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled"},
)
class DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfig:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#enabled DataDatabricksServingEndpoints#enabled}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__319b4b6959716456a7612ed5a7bf2d0fef1666340672eb4bd3a7c9b337f6bab1)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#enabled DataDatabricksServingEndpoints#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfigList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfigList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4a3140666e6e5ab2a3c85611709e46f6c82abeebe414f9167770e78d3913b882)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfigOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8c8c36233cc954c136cefef999da70e2eeac348b5f344be8904dd7fd978d4b0)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfigOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66c705a9b1701effeb6b21f0f506cd2d23702390af0e931d916fb7c78f0895be)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1d77ff02f7369c13ce574bff798ddf7b06091d70988cc1425b03cea136b1c577)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0b3f64d455f90bea17bbf21ce43a3147b8ef1f41aa79ff2b7f687216ddf12441)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfig]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfig]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22f202503fd88864d213b92750e110052b9c94e6359eabd4a9b2e87f4cf10521)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__95875e8d77bf719fa23e9fc879b76bebdd79022bf5893d8e9b32f26b3b4412fc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

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
            type_hints = typing.get_type_hints(_typecheckingstub__fd8b9e0d0bb4520ff5b172ed852c0c22fb54f3114e90709fd9e070c16a95e5aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db3b6f5f02e30bbb67d0a1f1194cd11b7a7bab902eb9769b42dca411f20b2a40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfig",
    jsii_struct_bases=[],
    name_mapping={
        "served_entities": "servedEntities",
        "served_models": "servedModels",
    },
)
class DataDatabricksServingEndpointsEndpointsConfig:
    def __init__(
        self,
        *,
        served_entities: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsConfigServedEntities", typing.Dict[builtins.str, typing.Any]]]]] = None,
        served_models: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsConfigServedModels", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param served_entities: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#served_entities DataDatabricksServingEndpoints#served_entities}.
        :param served_models: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#served_models DataDatabricksServingEndpoints#served_models}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__318e34ba71d0735fcb978f87b893dd06f3e2ae62b9bb0571482525ace9e3ddfc)
            check_type(argname="argument served_entities", value=served_entities, expected_type=type_hints["served_entities"])
            check_type(argname="argument served_models", value=served_models, expected_type=type_hints["served_models"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if served_entities is not None:
            self._values["served_entities"] = served_entities
        if served_models is not None:
            self._values["served_models"] = served_models

    @builtins.property
    def served_entities(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntities"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#served_entities DataDatabricksServingEndpoints#served_entities}.'''
        result = self._values.get("served_entities")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntities"]]], result)

    @builtins.property
    def served_models(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedModels"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#served_models DataDatabricksServingEndpoints#served_models}.'''
        result = self._values.get("served_models")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedModels"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsEndpointsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksServingEndpointsEndpointsConfigList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3aa5769705431b6ae7cfb84c5acc648f662b948462c42ea7b3c012a47dccbe2b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksServingEndpointsEndpointsConfigOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f979bc60aadf5548cd91c9867d7b72d30a35144509e46b11d69e89097dd6c10)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksServingEndpointsEndpointsConfigOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06ad0aecf8bee61207204555519ac53819b3763178ffde0a00d416dde7178045)
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
            type_hints = typing.get_type_hints(_typecheckingstub__282818ea4831d9e49b7e4c327bab112c01315eb6e4f0cd481b1b79472fd35e28)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b422f85c63232665977d03205a6b3a26f9379eaff45484f36cda49e1974e28d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfig]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfig]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__792c178b1944fb9e0b1b6d30bc50aec5bd19a10b23449960b5ef983977292648)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4834c4415bb91d07d5a58561f5deaeef806c06034787b7140ba6395d8814fc68)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putServedEntities")
    def put_served_entities(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsConfigServedEntities", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4d9a1648e111628e0a4c898d35b35f89999db054a773243da70d0625349383d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putServedEntities", [value]))

    @jsii.member(jsii_name="putServedModels")
    def put_served_models(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsConfigServedModels", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a936387de6ee9cd5dca339f05c6878bb313662fbe4b2326fd51ad2a39b031007)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putServedModels", [value]))

    @jsii.member(jsii_name="resetServedEntities")
    def reset_served_entities(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServedEntities", []))

    @jsii.member(jsii_name="resetServedModels")
    def reset_served_models(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServedModels", []))

    @builtins.property
    @jsii.member(jsii_name="servedEntities")
    def served_entities(
        self,
    ) -> "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesList":
        return typing.cast("DataDatabricksServingEndpointsEndpointsConfigServedEntitiesList", jsii.get(self, "servedEntities"))

    @builtins.property
    @jsii.member(jsii_name="servedModels")
    def served_models(
        self,
    ) -> "DataDatabricksServingEndpointsEndpointsConfigServedModelsList":
        return typing.cast("DataDatabricksServingEndpointsEndpointsConfigServedModelsList", jsii.get(self, "servedModels"))

    @builtins.property
    @jsii.member(jsii_name="servedEntitiesInput")
    def served_entities_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntities"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntities"]]], jsii.get(self, "servedEntitiesInput"))

    @builtins.property
    @jsii.member(jsii_name="servedModelsInput")
    def served_models_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedModels"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedModels"]]], jsii.get(self, "servedModelsInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38cf2b4078d086f25600bdba53d131fe92283b4717f9ff5bc78d0b51d757ea3b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntities",
    jsii_struct_bases=[],
    name_mapping={
        "entity_name": "entityName",
        "entity_version": "entityVersion",
        "external_model": "externalModel",
        "foundation_model": "foundationModel",
        "name": "name",
    },
)
class DataDatabricksServingEndpointsEndpointsConfigServedEntities:
    def __init__(
        self,
        *,
        entity_name: typing.Optional[builtins.str] = None,
        entity_version: typing.Optional[builtins.str] = None,
        external_model: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModel", typing.Dict[builtins.str, typing.Any]]]]] = None,
        foundation_model: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModel", typing.Dict[builtins.str, typing.Any]]]]] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param entity_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#entity_name DataDatabricksServingEndpoints#entity_name}.
        :param entity_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#entity_version DataDatabricksServingEndpoints#entity_version}.
        :param external_model: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#external_model DataDatabricksServingEndpoints#external_model}.
        :param foundation_model: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#foundation_model DataDatabricksServingEndpoints#foundation_model}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#name DataDatabricksServingEndpoints#name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35aade4f67c1db209e3e6520d43014060ce466ef0fff6459e16c728a46efd1a9)
            check_type(argname="argument entity_name", value=entity_name, expected_type=type_hints["entity_name"])
            check_type(argname="argument entity_version", value=entity_version, expected_type=type_hints["entity_version"])
            check_type(argname="argument external_model", value=external_model, expected_type=type_hints["external_model"])
            check_type(argname="argument foundation_model", value=foundation_model, expected_type=type_hints["foundation_model"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if entity_name is not None:
            self._values["entity_name"] = entity_name
        if entity_version is not None:
            self._values["entity_version"] = entity_version
        if external_model is not None:
            self._values["external_model"] = external_model
        if foundation_model is not None:
            self._values["foundation_model"] = foundation_model
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def entity_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#entity_name DataDatabricksServingEndpoints#entity_name}.'''
        result = self._values.get("entity_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def entity_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#entity_version DataDatabricksServingEndpoints#entity_version}.'''
        result = self._values.get("entity_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def external_model(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModel"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#external_model DataDatabricksServingEndpoints#external_model}.'''
        result = self._values.get("external_model")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModel"]]], result)

    @builtins.property
    def foundation_model(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModel"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#foundation_model DataDatabricksServingEndpoints#foundation_model}.'''
        result = self._values.get("foundation_model")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModel"]]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#name DataDatabricksServingEndpoints#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsEndpointsConfigServedEntities(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModel",
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
class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModel:
    def __init__(
        self,
        *,
        name: builtins.str,
        provider: builtins.str,
        task: builtins.str,
        ai21_labs_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
        amazon_bedrock_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
        anthropic_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
        cohere_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
        custom_provider_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
        databricks_model_serving_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
        google_cloud_vertex_ai_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
        openai_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
        palm_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#name DataDatabricksServingEndpoints#name}.
        :param provider: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#provider DataDatabricksServingEndpoints#provider}.
        :param task: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#task DataDatabricksServingEndpoints#task}.
        :param ai21_labs_config: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#ai21labs_config DataDatabricksServingEndpoints#ai21labs_config}.
        :param amazon_bedrock_config: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#amazon_bedrock_config DataDatabricksServingEndpoints#amazon_bedrock_config}.
        :param anthropic_config: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#anthropic_config DataDatabricksServingEndpoints#anthropic_config}.
        :param cohere_config: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#cohere_config DataDatabricksServingEndpoints#cohere_config}.
        :param custom_provider_config: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#custom_provider_config DataDatabricksServingEndpoints#custom_provider_config}.
        :param databricks_model_serving_config: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#databricks_model_serving_config DataDatabricksServingEndpoints#databricks_model_serving_config}.
        :param google_cloud_vertex_ai_config: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#google_cloud_vertex_ai_config DataDatabricksServingEndpoints#google_cloud_vertex_ai_config}.
        :param openai_config: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#openai_config DataDatabricksServingEndpoints#openai_config}.
        :param palm_config: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#palm_config DataDatabricksServingEndpoints#palm_config}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcb637d379a732656c5b3aa28afcb98386c9e1b32ae6a94e953588adac0cb82b)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#name DataDatabricksServingEndpoints#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def provider(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#provider DataDatabricksServingEndpoints#provider}.'''
        result = self._values.get("provider")
        assert result is not None, "Required property 'provider' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def task(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#task DataDatabricksServingEndpoints#task}.'''
        result = self._values.get("task")
        assert result is not None, "Required property 'task' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ai21_labs_config(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfig"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#ai21labs_config DataDatabricksServingEndpoints#ai21labs_config}.'''
        result = self._values.get("ai21_labs_config")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfig"]]], result)

    @builtins.property
    def amazon_bedrock_config(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfig"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#amazon_bedrock_config DataDatabricksServingEndpoints#amazon_bedrock_config}.'''
        result = self._values.get("amazon_bedrock_config")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfig"]]], result)

    @builtins.property
    def anthropic_config(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfig"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#anthropic_config DataDatabricksServingEndpoints#anthropic_config}.'''
        result = self._values.get("anthropic_config")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfig"]]], result)

    @builtins.property
    def cohere_config(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfig"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#cohere_config DataDatabricksServingEndpoints#cohere_config}.'''
        result = self._values.get("cohere_config")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfig"]]], result)

    @builtins.property
    def custom_provider_config(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfig"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#custom_provider_config DataDatabricksServingEndpoints#custom_provider_config}.'''
        result = self._values.get("custom_provider_config")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfig"]]], result)

    @builtins.property
    def databricks_model_serving_config(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfig"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#databricks_model_serving_config DataDatabricksServingEndpoints#databricks_model_serving_config}.'''
        result = self._values.get("databricks_model_serving_config")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfig"]]], result)

    @builtins.property
    def google_cloud_vertex_ai_config(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#google_cloud_vertex_ai_config DataDatabricksServingEndpoints#google_cloud_vertex_ai_config}.'''
        result = self._values.get("google_cloud_vertex_ai_config")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig"]]], result)

    @builtins.property
    def openai_config(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfig"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#openai_config DataDatabricksServingEndpoints#openai_config}.'''
        result = self._values.get("openai_config")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfig"]]], result)

    @builtins.property
    def palm_config(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfig"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#palm_config DataDatabricksServingEndpoints#palm_config}.'''
        result = self._values.get("palm_config")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfig"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModel(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfig",
    jsii_struct_bases=[],
    name_mapping={
        "ai21_labs_api_key": "ai21LabsApiKey",
        "ai21_labs_api_key_plaintext": "ai21LabsApiKeyPlaintext",
    },
)
class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfig:
    def __init__(
        self,
        *,
        ai21_labs_api_key: typing.Optional[builtins.str] = None,
        ai21_labs_api_key_plaintext: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param ai21_labs_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#ai21labs_api_key DataDatabricksServingEndpoints#ai21labs_api_key}.
        :param ai21_labs_api_key_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#ai21labs_api_key_plaintext DataDatabricksServingEndpoints#ai21labs_api_key_plaintext}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01d9e43e91cc024c26ba9505d7bfb9f00171b8d6b47ecbe80aced93f5550b98c)
            check_type(argname="argument ai21_labs_api_key", value=ai21_labs_api_key, expected_type=type_hints["ai21_labs_api_key"])
            check_type(argname="argument ai21_labs_api_key_plaintext", value=ai21_labs_api_key_plaintext, expected_type=type_hints["ai21_labs_api_key_plaintext"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if ai21_labs_api_key is not None:
            self._values["ai21_labs_api_key"] = ai21_labs_api_key
        if ai21_labs_api_key_plaintext is not None:
            self._values["ai21_labs_api_key_plaintext"] = ai21_labs_api_key_plaintext

    @builtins.property
    def ai21_labs_api_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#ai21labs_api_key DataDatabricksServingEndpoints#ai21labs_api_key}.'''
        result = self._values.get("ai21_labs_api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ai21_labs_api_key_plaintext(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#ai21labs_api_key_plaintext DataDatabricksServingEndpoints#ai21labs_api_key_plaintext}.'''
        result = self._values.get("ai21_labs_api_key_plaintext")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfigList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfigList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3260ead522251fa26fb19c03b2cf8d86f15bfa868a3e65294f96ed504a662d20)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfigOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8dbd4b46742dec060066e20ea2843e31d7ba9eb3a97f441361f9ab5ddf4cf25)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfigOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1acc981bbaa3f1f1891916793184cf0ce9023759328be47448fd92f0cc2223c9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f7db1b8cecbc2447b1c075ffe87ab2c8954ad2a9d77c33e0cf744201794a7bb3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__df3214caa3c4eb4ade1b9666fcc957c2d88a8a7505e19cb5b32efa2740a6f4f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfig]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfig]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2035b462fc6f4d282a8c6bb124f198222a51c633a499d47f92bf10a308006da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c8d414e2e869fc38bb0bd2e7a689dd3094f434175e416ae509124844b6ed6124)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

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
            type_hints = typing.get_type_hints(_typecheckingstub__bfffa675168632adac0eb2cf3602eb9fbe0044bb0e23ea8ac296056bbe8e2881)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ai21LabsApiKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ai21LabsApiKeyPlaintext")
    def ai21_labs_api_key_plaintext(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ai21LabsApiKeyPlaintext"))

    @ai21_labs_api_key_plaintext.setter
    def ai21_labs_api_key_plaintext(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__faab66f997258ed1b4d63c78b436ced166f67103da2033e225fc56c02dd70029)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ai21LabsApiKeyPlaintext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f587b1b04c1905659a035d470fd789c0c0924190e168bcddba823b31e8a4615)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfig",
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
class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfig:
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
        :param aws_region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#aws_region DataDatabricksServingEndpoints#aws_region}.
        :param bedrock_provider: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#bedrock_provider DataDatabricksServingEndpoints#bedrock_provider}.
        :param aws_access_key_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#aws_access_key_id DataDatabricksServingEndpoints#aws_access_key_id}.
        :param aws_access_key_id_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#aws_access_key_id_plaintext DataDatabricksServingEndpoints#aws_access_key_id_plaintext}.
        :param aws_secret_access_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#aws_secret_access_key DataDatabricksServingEndpoints#aws_secret_access_key}.
        :param aws_secret_access_key_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#aws_secret_access_key_plaintext DataDatabricksServingEndpoints#aws_secret_access_key_plaintext}.
        :param instance_profile_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#instance_profile_arn DataDatabricksServingEndpoints#instance_profile_arn}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c0c2cd7bd67e4904dcbf2c1f67722d8b18507dcbebcc2db6470cfac5e309a30)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#aws_region DataDatabricksServingEndpoints#aws_region}.'''
        result = self._values.get("aws_region")
        assert result is not None, "Required property 'aws_region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bedrock_provider(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#bedrock_provider DataDatabricksServingEndpoints#bedrock_provider}.'''
        result = self._values.get("bedrock_provider")
        assert result is not None, "Required property 'bedrock_provider' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def aws_access_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#aws_access_key_id DataDatabricksServingEndpoints#aws_access_key_id}.'''
        result = self._values.get("aws_access_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_access_key_id_plaintext(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#aws_access_key_id_plaintext DataDatabricksServingEndpoints#aws_access_key_id_plaintext}.'''
        result = self._values.get("aws_access_key_id_plaintext")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_secret_access_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#aws_secret_access_key DataDatabricksServingEndpoints#aws_secret_access_key}.'''
        result = self._values.get("aws_secret_access_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_secret_access_key_plaintext(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#aws_secret_access_key_plaintext DataDatabricksServingEndpoints#aws_secret_access_key_plaintext}.'''
        result = self._values.get("aws_secret_access_key_plaintext")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_profile_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#instance_profile_arn DataDatabricksServingEndpoints#instance_profile_arn}.'''
        result = self._values.get("instance_profile_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfigList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfigList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5ec98538569a6f29f62973f9399f9185a5ddeb4f202212e1ae2619437c181379)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfigOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62c8f58dc15447e4bb3ff68b4dcd2d1623958e9d681e790cd3dfe88dbfde98c8)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfigOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d7ae51806d1ab5d61c4064fe4f6bdad2d69154fc3d7ff3f39248cc0c23dd2ad)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1a4387b52c37a655c256960d4bd56922d957c0bf017c5c7163d94b51169c60d4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__731b156f6f0bf31712c93dbd4210025b6bc12204dc698cc4ac18dc8ef7d53af2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfig]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfig]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3ab6338f9553abd1645c027bfe88c04978019250407fc2aba73165923ce420f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4b8680774b9e862cf6ab048e791546453eabe3070f636cdd3f1a8bfa9b5f815b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

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
            type_hints = typing.get_type_hints(_typecheckingstub__682528ad3ecbb0a01d1f7b213d03184374ef88bd5d83fde21e36a7ab71bf1477)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsAccessKeyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="awsAccessKeyIdPlaintext")
    def aws_access_key_id_plaintext(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsAccessKeyIdPlaintext"))

    @aws_access_key_id_plaintext.setter
    def aws_access_key_id_plaintext(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0171a207a3a8e5a2a4ad469c89a15384a9060eff5ec1327680e148017facad08)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsAccessKeyIdPlaintext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="awsRegion")
    def aws_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsRegion"))

    @aws_region.setter
    def aws_region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5d1754661fa47f03b2c09cf13b413273f5264f91594a11e3359f6a9b750aa2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsRegion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="awsSecretAccessKey")
    def aws_secret_access_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsSecretAccessKey"))

    @aws_secret_access_key.setter
    def aws_secret_access_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac5c9ebff3e84ec1dfd874ebe6a3d3c3a5e1179d64952ada6c4e5c34c675e2d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsSecretAccessKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="awsSecretAccessKeyPlaintext")
    def aws_secret_access_key_plaintext(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsSecretAccessKeyPlaintext"))

    @aws_secret_access_key_plaintext.setter
    def aws_secret_access_key_plaintext(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b962847da8bf7ac0a836221c7d1b3767ab3fae15725961f2c82dc4fe5ee3bb37)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsSecretAccessKeyPlaintext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bedrockProvider")
    def bedrock_provider(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bedrockProvider"))

    @bedrock_provider.setter
    def bedrock_provider(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d088af06719d7b4e4608b1bcb3dd9ac07ae2a293b6dc78da5494fd9e8e6f80b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bedrockProvider", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instanceProfileArn")
    def instance_profile_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceProfileArn"))

    @instance_profile_arn.setter
    def instance_profile_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__760fa3fc911162822c8014c0329e9ff3e613cad01b6b026a41315d97dfa92e60)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceProfileArn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b92a59fc978f0c4a13a4eb27b0f5d8ae377ac9b21415d9885aeb2641d8c846b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfig",
    jsii_struct_bases=[],
    name_mapping={
        "anthropic_api_key": "anthropicApiKey",
        "anthropic_api_key_plaintext": "anthropicApiKeyPlaintext",
    },
)
class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfig:
    def __init__(
        self,
        *,
        anthropic_api_key: typing.Optional[builtins.str] = None,
        anthropic_api_key_plaintext: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param anthropic_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#anthropic_api_key DataDatabricksServingEndpoints#anthropic_api_key}.
        :param anthropic_api_key_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#anthropic_api_key_plaintext DataDatabricksServingEndpoints#anthropic_api_key_plaintext}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e06a86eeeb52e40c5ab2db35e72056e0d9fd891c0a08e55c9396ed9a8605e059)
            check_type(argname="argument anthropic_api_key", value=anthropic_api_key, expected_type=type_hints["anthropic_api_key"])
            check_type(argname="argument anthropic_api_key_plaintext", value=anthropic_api_key_plaintext, expected_type=type_hints["anthropic_api_key_plaintext"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if anthropic_api_key is not None:
            self._values["anthropic_api_key"] = anthropic_api_key
        if anthropic_api_key_plaintext is not None:
            self._values["anthropic_api_key_plaintext"] = anthropic_api_key_plaintext

    @builtins.property
    def anthropic_api_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#anthropic_api_key DataDatabricksServingEndpoints#anthropic_api_key}.'''
        result = self._values.get("anthropic_api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def anthropic_api_key_plaintext(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#anthropic_api_key_plaintext DataDatabricksServingEndpoints#anthropic_api_key_plaintext}.'''
        result = self._values.get("anthropic_api_key_plaintext")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfigList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfigList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ca3d06c0cffdcf6561f566cfef7b24bf75d86d5bd4a1abc71038c7490ec96257)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfigOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__868695df448e5ab59896fedc28c829eee811743c2b997f8eb328e707ded006ad)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfigOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c17eacc1465f3794a91f768a962e23cf31d45a909ec972e534134941eca8dcb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__068d7187665b88ee7797c51e61633a63fe57c32be726a18527c835d5bf4717fb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6f0a6dfb2318b5375671c1158e9d1ce1eff32637f4cc8223a36b39a7a16266d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfig]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfig]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6bc976f8b0f082a2a0e74d469605e7867db3a5a61232a614138ffe9cfd956576)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__632c15cf5f2cea4972ed888c096add24fb2cd5063ef9dde775c5ec8a015803f8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

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
            type_hints = typing.get_type_hints(_typecheckingstub__4bbe8038d7d4cfcc5ebadc8c04cb00c575b101eedeb9f549c76b58a7ccd5e58e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "anthropicApiKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="anthropicApiKeyPlaintext")
    def anthropic_api_key_plaintext(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "anthropicApiKeyPlaintext"))

    @anthropic_api_key_plaintext.setter
    def anthropic_api_key_plaintext(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__abe5b9a4a06ab62759926577773f7b3730dc3407f28966cb5cecb4f5f2b287b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "anthropicApiKeyPlaintext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1951ea85f879100f474d9ee2dcfc46b9a210982e4933dc6ef95dee0f006f9adf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfig",
    jsii_struct_bases=[],
    name_mapping={
        "cohere_api_base": "cohereApiBase",
        "cohere_api_key": "cohereApiKey",
        "cohere_api_key_plaintext": "cohereApiKeyPlaintext",
    },
)
class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfig:
    def __init__(
        self,
        *,
        cohere_api_base: typing.Optional[builtins.str] = None,
        cohere_api_key: typing.Optional[builtins.str] = None,
        cohere_api_key_plaintext: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cohere_api_base: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#cohere_api_base DataDatabricksServingEndpoints#cohere_api_base}.
        :param cohere_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#cohere_api_key DataDatabricksServingEndpoints#cohere_api_key}.
        :param cohere_api_key_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#cohere_api_key_plaintext DataDatabricksServingEndpoints#cohere_api_key_plaintext}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3da1bc932c86ac379f248865a60c6f120d0f86e2caa12b8d8085d3f60538f31f)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#cohere_api_base DataDatabricksServingEndpoints#cohere_api_base}.'''
        result = self._values.get("cohere_api_base")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cohere_api_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#cohere_api_key DataDatabricksServingEndpoints#cohere_api_key}.'''
        result = self._values.get("cohere_api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cohere_api_key_plaintext(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#cohere_api_key_plaintext DataDatabricksServingEndpoints#cohere_api_key_plaintext}.'''
        result = self._values.get("cohere_api_key_plaintext")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfigList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfigList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e9cf196cf33cd12de6153f0391dfb87849a5061f5b6ac41d8d1a10532ad69141)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfigOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a60386b4e5d4100866774b75ddca991ad69360a3e812452b0d3aaffbdedd2ffe)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfigOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3728478588fd7e1ceb018b0eef9c8ef7a49c5a83f6d5c5f00af362e59d507335)
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
            type_hints = typing.get_type_hints(_typecheckingstub__05901f979dc677d298ea0e7715ef2ad18a9a1ac906c9a97155e0f5e93dbf71ba)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6f1e3a018e9da076b7ebb5847b3f1c6d94f6c3eac6799c19dd2f62cb50e66c83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfig]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfig]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c61578e2e7eccf75f19ac8379ebd4ba631b3e703f4a20383d6a634a6faa25df4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a17721bfb07dec68c2a053c43201b9dfbb656a994d004d17d5e6467ddf749ed3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

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
            type_hints = typing.get_type_hints(_typecheckingstub__34c1c3c066fcebf454f78814764838b2cbd9ac11aca18f3a20e951202f6d9635)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cohereApiBase", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cohereApiKey")
    def cohere_api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cohereApiKey"))

    @cohere_api_key.setter
    def cohere_api_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da5d687a4b941eae5a1687df1a221930a2e696ce27e08e6be7f15284e0ef364e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cohereApiKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cohereApiKeyPlaintext")
    def cohere_api_key_plaintext(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cohereApiKeyPlaintext"))

    @cohere_api_key_plaintext.setter
    def cohere_api_key_plaintext(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c9ca6ae685bd6aada09607229d7e4a8f4d97f32fc44e576df717d89360a439c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cohereApiKeyPlaintext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d7a52dbd05a55717eea5be6197b6c748ebdc2db0f391df0b7605a1abab03975)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfig",
    jsii_struct_bases=[],
    name_mapping={
        "custom_provider_url": "customProviderUrl",
        "api_key_auth": "apiKeyAuth",
        "bearer_token_auth": "bearerTokenAuth",
    },
)
class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfig:
    def __init__(
        self,
        *,
        custom_provider_url: builtins.str,
        api_key_auth: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth", typing.Dict[builtins.str, typing.Any]]]]] = None,
        bearer_token_auth: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param custom_provider_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#custom_provider_url DataDatabricksServingEndpoints#custom_provider_url}.
        :param api_key_auth: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#api_key_auth DataDatabricksServingEndpoints#api_key_auth}.
        :param bearer_token_auth: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#bearer_token_auth DataDatabricksServingEndpoints#bearer_token_auth}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__664a1971124ff643d01b13d59a6e6b2292859a27cbc406da599a7f3dc573b120)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#custom_provider_url DataDatabricksServingEndpoints#custom_provider_url}.'''
        result = self._values.get("custom_provider_url")
        assert result is not None, "Required property 'custom_provider_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def api_key_auth(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#api_key_auth DataDatabricksServingEndpoints#api_key_auth}.'''
        result = self._values.get("api_key_auth")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth"]]], result)

    @builtins.property
    def bearer_token_auth(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#bearer_token_auth DataDatabricksServingEndpoints#bearer_token_auth}.'''
        result = self._values.get("bearer_token_auth")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value", "value_plaintext": "valuePlaintext"},
)
class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth:
    def __init__(
        self,
        *,
        key: builtins.str,
        value: typing.Optional[builtins.str] = None,
        value_plaintext: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#key DataDatabricksServingEndpoints#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#value DataDatabricksServingEndpoints#value}.
        :param value_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#value_plaintext DataDatabricksServingEndpoints#value_plaintext}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36b92cb282a8221ded619edd175db91c0b70d30442833dce469ba8644e000c32)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#key DataDatabricksServingEndpoints#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#value DataDatabricksServingEndpoints#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value_plaintext(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#value_plaintext DataDatabricksServingEndpoints#value_plaintext}.'''
        result = self._values.get("value_plaintext")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuthList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuthList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__db5856197682457899c1d9114aef0f9ec3cebc37b1fd34a3dad5ef948fb04e41)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuthOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3008c2534a82b71d7eaca416d2e829529528aa3f2daa7b2a75b3664d8d0bdb82)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuthOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5052c35f4bf41d78d84c1173ae76026ddeaeb65b02e5f746921839b80d629fa8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c4b64dade8124c15d68b10e19f5374a7b16549b2eb0725a8e8026d37c6bc3229)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ec575da1f23d3d2b8a6c1e328737599325fa807af9e17963b99539f876609f86)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__804fc87a27ded6716038c924ccba33bb8a355799ff6e7479b302126262a586b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuthOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuthOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4bbf4562c39fad3c24e70eaf69dc4fb50b4c09f20ab35f34cb32963a4b204398)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

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
            type_hints = typing.get_type_hints(_typecheckingstub__02327d191a559b8a74560d472779fb0239c9ed73dbcbc946e4d25c602dc396c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa9182000bcd679e382b523981070919ad8b640b214eea65666954fa782f7063)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="valuePlaintext")
    def value_plaintext(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "valuePlaintext"))

    @value_plaintext.setter
    def value_plaintext(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd9f772469076a1626bad7f1556d871cc84188e71d0b748a0a24a8a9476e0bfc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "valuePlaintext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c09121157c9dc85eea0b71ac268cb03cdad0af3044e4b8647b93975ebb7cb582)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth",
    jsii_struct_bases=[],
    name_mapping={"token": "token", "token_plaintext": "tokenPlaintext"},
)
class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth:
    def __init__(
        self,
        *,
        token: typing.Optional[builtins.str] = None,
        token_plaintext: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#token DataDatabricksServingEndpoints#token}.
        :param token_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#token_plaintext DataDatabricksServingEndpoints#token_plaintext}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9f3c23622156978320041982f29d5b6955cf0083b5cf66afb6cfc7e8231c2ae)
            check_type(argname="argument token", value=token, expected_type=type_hints["token"])
            check_type(argname="argument token_plaintext", value=token_plaintext, expected_type=type_hints["token_plaintext"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if token is not None:
            self._values["token"] = token
        if token_plaintext is not None:
            self._values["token_plaintext"] = token_plaintext

    @builtins.property
    def token(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#token DataDatabricksServingEndpoints#token}.'''
        result = self._values.get("token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def token_plaintext(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#token_plaintext DataDatabricksServingEndpoints#token_plaintext}.'''
        result = self._values.get("token_plaintext")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuthList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuthList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__95053fc8e5974f9059c53e4e605852f43b982c94841eedb063287bd33e0c2935)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuthOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94326c8f2ea0a54adb27e16aa78bf46451bbe7d1641193f19eff93e3e2b9fcd5)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuthOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d708ed7c5fc2daadf6493b2f940576fba596e9230426074b44005de27636883)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d82eb60153b8aae5590d21b136f254d41ab5deb41ede180b2f27fe1d8037c2e9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__08db302c9442b6b1b0ff207854dc9f0414c195b6a6c030beb086f085d038bbb9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84381fe4402cc93eac21e77b946a3bd5fd67278dccc7f0701200944344cfa21a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuthOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuthOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__da130584221935d7ede5487c811518dcf34fb34c6076b111aaf884bbcf6b4da5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

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
            type_hints = typing.get_type_hints(_typecheckingstub__b50b7a42484aa5c849b0144d938f850b7df4d41fa0b836f4a2d3c1c8f34cd8ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "token", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenPlaintext")
    def token_plaintext(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tokenPlaintext"))

    @token_plaintext.setter
    def token_plaintext(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94232b69038d8ab39dba7c9980f92aa8c75c86fd01b889edae2641c3b9e87a43)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenPlaintext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4c6b8a9618523956f4a03123e25f7b95223dfba9b5e23172afd1794573e0625)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__43308adbf2a458af54faf5c8c4b98f98a3ba25595d55102d7f1cc7cd1fd1277c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f04102ef8b226935dfb249efe4cdfb1d777f103bbfe3d9fd987292ba096121b)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e705b31ff8a945efdcee6ef1a4497e8748e8170541ee994bd843a0e9f80605d4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__498e0287bcf7999353272da33e2ad9649dbb45abe804d1e1e3a55ac39849c81f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__20361b1531f94a8511810a7de5bd2c5d4f69559cfa7d0de6530d2e592035c3c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfig]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfig]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b41ec7e8fffa54024eedf0ce453e9e8f4b9a0dd31bef5eb119f9719db92c945)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__28832b0860f47160d48542bd35ed64303bedd840a24470694da4f6e982eb98f9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putApiKeyAuth")
    def put_api_key_auth(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ccae83aacb41be7bb11f23a3f6037e4303e2557ecfa2333b8156cecc82309070)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putApiKeyAuth", [value]))

    @jsii.member(jsii_name="putBearerTokenAuth")
    def put_bearer_token_auth(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbe9a3f946531d36eacd183f96c2370e1ded506717d43b7321f0728ed6a7dc91)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
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
    ) -> DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuthList:
        return typing.cast(DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuthList, jsii.get(self, "apiKeyAuth"))

    @builtins.property
    @jsii.member(jsii_name="bearerTokenAuth")
    def bearer_token_auth(
        self,
    ) -> DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuthList:
        return typing.cast(DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuthList, jsii.get(self, "bearerTokenAuth"))

    @builtins.property
    @jsii.member(jsii_name="apiKeyAuthInput")
    def api_key_auth_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth]]], jsii.get(self, "apiKeyAuthInput"))

    @builtins.property
    @jsii.member(jsii_name="bearerTokenAuthInput")
    def bearer_token_auth_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth]]], jsii.get(self, "bearerTokenAuthInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__761b960e3698e12ad0c82dca43cc1ca5b95a1bdf0829b2f66d0e5202c924e96a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customProviderUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5db7febdeee5ffc6d6f298ce1ba041fe0d6e50d5abf912a312835014ce787350)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfig",
    jsii_struct_bases=[],
    name_mapping={
        "databricks_workspace_url": "databricksWorkspaceUrl",
        "databricks_api_token": "databricksApiToken",
        "databricks_api_token_plaintext": "databricksApiTokenPlaintext",
    },
)
class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfig:
    def __init__(
        self,
        *,
        databricks_workspace_url: builtins.str,
        databricks_api_token: typing.Optional[builtins.str] = None,
        databricks_api_token_plaintext: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param databricks_workspace_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#databricks_workspace_url DataDatabricksServingEndpoints#databricks_workspace_url}.
        :param databricks_api_token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#databricks_api_token DataDatabricksServingEndpoints#databricks_api_token}.
        :param databricks_api_token_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#databricks_api_token_plaintext DataDatabricksServingEndpoints#databricks_api_token_plaintext}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a88a082c6906c017809fb4dcb3d42876bd94931394072cc0cbce2cb2f3501525)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#databricks_workspace_url DataDatabricksServingEndpoints#databricks_workspace_url}.'''
        result = self._values.get("databricks_workspace_url")
        assert result is not None, "Required property 'databricks_workspace_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def databricks_api_token(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#databricks_api_token DataDatabricksServingEndpoints#databricks_api_token}.'''
        result = self._values.get("databricks_api_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def databricks_api_token_plaintext(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#databricks_api_token_plaintext DataDatabricksServingEndpoints#databricks_api_token_plaintext}.'''
        result = self._values.get("databricks_api_token_plaintext")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfigList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfigList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__39f14e7f780eab9ae7a92811aa9e5519a3dccf76ee356f1bff0859efd0f994e7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfigOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__479705da800d9a234b39fce73f885fff71e6bba94cd2f601c37f6f39ab61271c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfigOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04643f7d6fcfa4258a07add8a9b00b85519517c17bb5cad89c70e782f7d84d5b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d5545247c3079343c2b0c2fea48e1f06dcf58a0e935e5862e0f2d2989b709328)
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
            type_hints = typing.get_type_hints(_typecheckingstub__57736c4697aa7643b452e05ae7d7112520744e456df83a0a7952642c06cc3601)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfig]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfig]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94f315a661e7dcaced13c296c150de713040e24e46cfd301f464f030da469af3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e0d4e9f3cefe5f6dbcb95eaf1097c099dfc31ff6b42e41766f2792792dc2b3a5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

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
            type_hints = typing.get_type_hints(_typecheckingstub__8f188fefc92913a40cfef0b7d104383494f6f40b41c4332cd2327776c2a4c772)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "databricksApiToken", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="databricksApiTokenPlaintext")
    def databricks_api_token_plaintext(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "databricksApiTokenPlaintext"))

    @databricks_api_token_plaintext.setter
    def databricks_api_token_plaintext(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7c4e0b9a6f2150b6d421cd67960d3db5b3707ea1835f3891471e3e35a4b5683)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "databricksApiTokenPlaintext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="databricksWorkspaceUrl")
    def databricks_workspace_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "databricksWorkspaceUrl"))

    @databricks_workspace_url.setter
    def databricks_workspace_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65553b134e43356e3aeddf6e4c151feb2e653c3868d05c6c0f0e6e2ad0833e1a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "databricksWorkspaceUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed25fff6bb414dbe6b855a552755b1944d095a776895d55dd17a45e585273c30)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig",
    jsii_struct_bases=[],
    name_mapping={
        "project_id": "projectId",
        "region": "region",
        "private_key": "privateKey",
        "private_key_plaintext": "privateKeyPlaintext",
    },
)
class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig:
    def __init__(
        self,
        *,
        project_id: builtins.str,
        region: builtins.str,
        private_key: typing.Optional[builtins.str] = None,
        private_key_plaintext: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#project_id DataDatabricksServingEndpoints#project_id}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#region DataDatabricksServingEndpoints#region}.
        :param private_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#private_key DataDatabricksServingEndpoints#private_key}.
        :param private_key_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#private_key_plaintext DataDatabricksServingEndpoints#private_key_plaintext}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e352edeaa86c4a032144f25eb8e6977146fc99d63076e2c0a203c9005754d644)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#project_id DataDatabricksServingEndpoints#project_id}.'''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#region DataDatabricksServingEndpoints#region}.'''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def private_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#private_key DataDatabricksServingEndpoints#private_key}.'''
        result = self._values.get("private_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def private_key_plaintext(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#private_key_plaintext DataDatabricksServingEndpoints#private_key_plaintext}.'''
        result = self._values.get("private_key_plaintext")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfigList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfigList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8b55e65f89b9b3a4169f38324e05a9eab484057202dacb0c9e99c70c13052a87)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfigOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__707bff8675a1bc3c0aafe800e5adc172ee54bb36c4145bec4da9c272a8fe06fc)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfigOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ccde555a382a6803fabdd8eaebe919449be5542dddf8b8639846dedf7bff8389)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cded0cec26539959bdbb9626654873b0c414e5c9defe9ccad0bd3350f2c90a4a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d881339bb9936bf1ee968d4fc37ad989439530da9baaa9cb401b727aea8ec050)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__702b8cbbae927e4036df022c26075d6f772ca3e49e7f16421731d3c0ef440c15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__70a0d75017ac8f3aad179e0f4a2a5fa365f075bc3f7468b098d14a7fb2b36a53)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

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
            type_hints = typing.get_type_hints(_typecheckingstub__20543f53ac751ad35a2e3d2e3b1035977f7ef6989784f99efa3f71931ee2f2b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="privateKeyPlaintext")
    def private_key_plaintext(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKeyPlaintext"))

    @private_key_plaintext.setter
    def private_key_plaintext(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81263e3305784c618326ab43371911bd5e27abaa033e47c2c93aaaf37239e0a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateKeyPlaintext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93b8474c18d731b527f052912d722acd0041e3e9da173f18513641468e8fc044)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cbe8a6bd9fc6cf510be679b8c4fb442b01cb79e3c3fc92660035d2c2ef6336ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c2f9df3a6961610110e5c67cacad9bf26cd9c6d0df833ff93560eec5b36e2ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__22c3f07dc7de3f5436fe505be98fb2bd08e303b5e4911558b3f5c58944f9f689)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9499ef20b8d5615a6038b0c5fda2b89d8dbe4a2824f491a7541da23b5c98332d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__749b0095a6a9f208fcf71dcd45a3462f2f9420ae45630b12244d4418cd23c544)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6ba36f5f00fafa9a821fa71cf30f648172b9277e3118962eecac4d6fb363db1c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4418069997efaf3612841c22e8c7a4e1814a8636576490e5d196a8ef22316cc3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModel]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModel]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModel]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2139f23573bd8a2454c9b270b5be176e281eebaa8147a7fb9aaccd3c9f6c8a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfig",
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
class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfig:
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
        :param microsoft_entra_client_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#microsoft_entra_client_id DataDatabricksServingEndpoints#microsoft_entra_client_id}.
        :param microsoft_entra_client_secret: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#microsoft_entra_client_secret DataDatabricksServingEndpoints#microsoft_entra_client_secret}.
        :param microsoft_entra_client_secret_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#microsoft_entra_client_secret_plaintext DataDatabricksServingEndpoints#microsoft_entra_client_secret_plaintext}.
        :param microsoft_entra_tenant_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#microsoft_entra_tenant_id DataDatabricksServingEndpoints#microsoft_entra_tenant_id}.
        :param openai_api_base: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#openai_api_base DataDatabricksServingEndpoints#openai_api_base}.
        :param openai_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#openai_api_key DataDatabricksServingEndpoints#openai_api_key}.
        :param openai_api_key_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#openai_api_key_plaintext DataDatabricksServingEndpoints#openai_api_key_plaintext}.
        :param openai_api_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#openai_api_type DataDatabricksServingEndpoints#openai_api_type}.
        :param openai_api_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#openai_api_version DataDatabricksServingEndpoints#openai_api_version}.
        :param openai_deployment_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#openai_deployment_name DataDatabricksServingEndpoints#openai_deployment_name}.
        :param openai_organization: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#openai_organization DataDatabricksServingEndpoints#openai_organization}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa450c31451584ff4963d81c9f94f2e4a6a4d1e3d1e37831a3fb74fb3943420b)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#microsoft_entra_client_id DataDatabricksServingEndpoints#microsoft_entra_client_id}.'''
        result = self._values.get("microsoft_entra_client_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def microsoft_entra_client_secret(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#microsoft_entra_client_secret DataDatabricksServingEndpoints#microsoft_entra_client_secret}.'''
        result = self._values.get("microsoft_entra_client_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def microsoft_entra_client_secret_plaintext(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#microsoft_entra_client_secret_plaintext DataDatabricksServingEndpoints#microsoft_entra_client_secret_plaintext}.'''
        result = self._values.get("microsoft_entra_client_secret_plaintext")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def microsoft_entra_tenant_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#microsoft_entra_tenant_id DataDatabricksServingEndpoints#microsoft_entra_tenant_id}.'''
        result = self._values.get("microsoft_entra_tenant_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def openai_api_base(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#openai_api_base DataDatabricksServingEndpoints#openai_api_base}.'''
        result = self._values.get("openai_api_base")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def openai_api_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#openai_api_key DataDatabricksServingEndpoints#openai_api_key}.'''
        result = self._values.get("openai_api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def openai_api_key_plaintext(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#openai_api_key_plaintext DataDatabricksServingEndpoints#openai_api_key_plaintext}.'''
        result = self._values.get("openai_api_key_plaintext")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def openai_api_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#openai_api_type DataDatabricksServingEndpoints#openai_api_type}.'''
        result = self._values.get("openai_api_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def openai_api_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#openai_api_version DataDatabricksServingEndpoints#openai_api_version}.'''
        result = self._values.get("openai_api_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def openai_deployment_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#openai_deployment_name DataDatabricksServingEndpoints#openai_deployment_name}.'''
        result = self._values.get("openai_deployment_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def openai_organization(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#openai_organization DataDatabricksServingEndpoints#openai_organization}.'''
        result = self._values.get("openai_organization")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfigList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfigList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0ff29216064bd8980e39e11cadf3561c5abe915cf064bcf1b20c233a4e93bf9e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfigOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efaca5c16510e1db24e3b457a2b121fa841cd20547fc2c4a7d89b231403db460)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfigOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9316a4c6d10cc3414b7d1ed39d114b986167034a9d3d56da499f456e08dc0ea0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3c3f8c617fc4f2627f967e8e1d77f6abdb81dc02c3f1baf4e299c0445d0cbeb2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__33993396fa486e44a26dabf652ebef02801ad9fb2b44acc200ac7bbeeebdd49e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfig]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfig]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca4a67a0029e6e3d5405c61fd1653ad5c446103f6cafb44e452dc93d7c25a6bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__62087b49e13912584961fc21096f97f744d653ad943b96937ccb06da5fc29afc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

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
            type_hints = typing.get_type_hints(_typecheckingstub__151a1b479f9573a11ede874c9757db5d01b2d771e9249a67ece89ee9e2cc5542)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "microsoftEntraClientId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="microsoftEntraClientSecret")
    def microsoft_entra_client_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "microsoftEntraClientSecret"))

    @microsoft_entra_client_secret.setter
    def microsoft_entra_client_secret(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e77f02290a4e9c4c80154a59de516a68dfe7f07706e8a49cad7332e82a8f1650)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "microsoftEntraClientSecret", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="microsoftEntraClientSecretPlaintext")
    def microsoft_entra_client_secret_plaintext(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "microsoftEntraClientSecretPlaintext"))

    @microsoft_entra_client_secret_plaintext.setter
    def microsoft_entra_client_secret_plaintext(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9359dc95ecf8fb2806bbded14e538a3f8c93dfc54034e8c6c75db08a2c482fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "microsoftEntraClientSecretPlaintext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="microsoftEntraTenantId")
    def microsoft_entra_tenant_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "microsoftEntraTenantId"))

    @microsoft_entra_tenant_id.setter
    def microsoft_entra_tenant_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__201167e4dee00cfd060f8ff339ee4216e903b4831777664d6a1fe59e6dd7277f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "microsoftEntraTenantId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="openaiApiBase")
    def openai_api_base(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "openaiApiBase"))

    @openai_api_base.setter
    def openai_api_base(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2c8f119b919ab010eaf15a21c5ff9783e22960f8c28c0a7ff9fffcc569a36ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "openaiApiBase", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="openaiApiKey")
    def openai_api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "openaiApiKey"))

    @openai_api_key.setter
    def openai_api_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26f14ad5bbf0bf1d5c24ef5028e58a74b9f3585bd4cce0375d426a7e2c358b0e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "openaiApiKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="openaiApiKeyPlaintext")
    def openai_api_key_plaintext(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "openaiApiKeyPlaintext"))

    @openai_api_key_plaintext.setter
    def openai_api_key_plaintext(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__209b3edca2003562484edfd76cc1974dbd3274910afbb3d1ec60249937358cb7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "openaiApiKeyPlaintext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="openaiApiType")
    def openai_api_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "openaiApiType"))

    @openai_api_type.setter
    def openai_api_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__898eb41160d6a359e8b82f6c73e47dbcf083a521580bf95082cbd042ac1fcbf5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "openaiApiType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="openaiApiVersion")
    def openai_api_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "openaiApiVersion"))

    @openai_api_version.setter
    def openai_api_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f28784b75d6d0ed9c7e4f1ea8c10e8ca7a4e6ca1f29318ed4718fb74d412271)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "openaiApiVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="openaiDeploymentName")
    def openai_deployment_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "openaiDeploymentName"))

    @openai_deployment_name.setter
    def openai_deployment_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0c3e2b7504ce455d5b2dbe9dd74cc561119a9ef87464e77afd7215f486ecaf1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "openaiDeploymentName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="openaiOrganization")
    def openai_organization(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "openaiOrganization"))

    @openai_organization.setter
    def openai_organization(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4e40b35d1deefa2eaec3b4a866cebe9d80257ae4a6ddc70c72c150e15b0b2bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "openaiOrganization", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8a842ccacea4dbe30af54108cec0d0cb9e02591e56d873da66ffca8c6c2f6b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__523bf0c100327207c97409e2e8087b5e51758bc1ecab5f4d82aa625093e16e23)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putAi21LabsConfig")
    def put_ai21_labs_config(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfig, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__318e1bfc57dcd5089bd4930c31bba5bd5ecbe89c3365b85f59fe3afc9e7b70e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAi21LabsConfig", [value]))

    @jsii.member(jsii_name="putAmazonBedrockConfig")
    def put_amazon_bedrock_config(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfig, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c484c12f019655722c664b641592310fe1da43820f1939920f99ea6aad2eb39)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAmazonBedrockConfig", [value]))

    @jsii.member(jsii_name="putAnthropicConfig")
    def put_anthropic_config(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfig, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a49adfa1ff6fdc3f756140d7af9a09cc47fb9ad60528fa880c8e86887e9dd3b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAnthropicConfig", [value]))

    @jsii.member(jsii_name="putCohereConfig")
    def put_cohere_config(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfig, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd54626fc3983219ad7e69b54c1902333f43748b9ac743ac3784732be5f2df65)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCohereConfig", [value]))

    @jsii.member(jsii_name="putCustomProviderConfig")
    def put_custom_provider_config(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfig, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f4c192f8e5fbcd12ad9a8164a11cc1f2732a78f5e7e26b90da7f50773ab5415)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCustomProviderConfig", [value]))

    @jsii.member(jsii_name="putDatabricksModelServingConfig")
    def put_databricks_model_serving_config(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfig, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8036f82c3781ed782ea48e4e485a0ab1729a3c2614d7d0395eb09fa5b0b7e488)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDatabricksModelServingConfig", [value]))

    @jsii.member(jsii_name="putGoogleCloudVertexAiConfig")
    def put_google_cloud_vertex_ai_config(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6991f219bb8c153ac502ed777a6b87460af44f198408e003631aef628657fd60)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putGoogleCloudVertexAiConfig", [value]))

    @jsii.member(jsii_name="putOpenaiConfig")
    def put_openai_config(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfig, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef3180277c37e2f0b8be970fb3a893ca1fc5efddb532fc3ad2c0982bf4717962)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putOpenaiConfig", [value]))

    @jsii.member(jsii_name="putPalmConfig")
    def put_palm_config(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfig", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0386e5c732bd1007374028065b7780c59637ce424cc86b64ec59701518c98c38)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
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
    ) -> DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfigList:
        return typing.cast(DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfigList, jsii.get(self, "ai21LabsConfig"))

    @builtins.property
    @jsii.member(jsii_name="amazonBedrockConfig")
    def amazon_bedrock_config(
        self,
    ) -> DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfigList:
        return typing.cast(DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfigList, jsii.get(self, "amazonBedrockConfig"))

    @builtins.property
    @jsii.member(jsii_name="anthropicConfig")
    def anthropic_config(
        self,
    ) -> DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfigList:
        return typing.cast(DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfigList, jsii.get(self, "anthropicConfig"))

    @builtins.property
    @jsii.member(jsii_name="cohereConfig")
    def cohere_config(
        self,
    ) -> DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfigList:
        return typing.cast(DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfigList, jsii.get(self, "cohereConfig"))

    @builtins.property
    @jsii.member(jsii_name="customProviderConfig")
    def custom_provider_config(
        self,
    ) -> DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigList:
        return typing.cast(DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigList, jsii.get(self, "customProviderConfig"))

    @builtins.property
    @jsii.member(jsii_name="databricksModelServingConfig")
    def databricks_model_serving_config(
        self,
    ) -> DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfigList:
        return typing.cast(DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfigList, jsii.get(self, "databricksModelServingConfig"))

    @builtins.property
    @jsii.member(jsii_name="googleCloudVertexAiConfig")
    def google_cloud_vertex_ai_config(
        self,
    ) -> DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfigList:
        return typing.cast(DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfigList, jsii.get(self, "googleCloudVertexAiConfig"))

    @builtins.property
    @jsii.member(jsii_name="openaiConfig")
    def openai_config(
        self,
    ) -> DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfigList:
        return typing.cast(DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfigList, jsii.get(self, "openaiConfig"))

    @builtins.property
    @jsii.member(jsii_name="palmConfig")
    def palm_config(
        self,
    ) -> "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfigList":
        return typing.cast("DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfigList", jsii.get(self, "palmConfig"))

    @builtins.property
    @jsii.member(jsii_name="ai21LabsConfigInput")
    def ai21_labs_config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfig]]], jsii.get(self, "ai21LabsConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="amazonBedrockConfigInput")
    def amazon_bedrock_config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfig]]], jsii.get(self, "amazonBedrockConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="anthropicConfigInput")
    def anthropic_config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfig]]], jsii.get(self, "anthropicConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="cohereConfigInput")
    def cohere_config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfig]]], jsii.get(self, "cohereConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="customProviderConfigInput")
    def custom_provider_config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfig]]], jsii.get(self, "customProviderConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="databricksModelServingConfigInput")
    def databricks_model_serving_config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfig]]], jsii.get(self, "databricksModelServingConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="googleCloudVertexAiConfigInput")
    def google_cloud_vertex_ai_config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig]]], jsii.get(self, "googleCloudVertexAiConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="openaiConfigInput")
    def openai_config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfig]]], jsii.get(self, "openaiConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="palmConfigInput")
    def palm_config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfig"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfig"]]], jsii.get(self, "palmConfigInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__af091d48e2850bb2e4e173f493cec509042a2018c94a7577cd2e504e965e5df8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="provider")
    def provider(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "provider"))

    @provider.setter
    def provider(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2dd02ffa4ac3143cf3868fd4f15b7eab754c0123263d9264b1d408a447566b17)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "provider", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="task")
    def task(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "task"))

    @task.setter
    def task(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__002ee06ba380c98b3dfc9c138f6eb3d3e912d91969c1ee8ab76eeb49cb2f278d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "task", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModel]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModel]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModel]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5210aee1bdfa2d081e03b6428a3008f0fe5ae6b151b088dfb68f23c19da744c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfig",
    jsii_struct_bases=[],
    name_mapping={
        "palm_api_key": "palmApiKey",
        "palm_api_key_plaintext": "palmApiKeyPlaintext",
    },
)
class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfig:
    def __init__(
        self,
        *,
        palm_api_key: typing.Optional[builtins.str] = None,
        palm_api_key_plaintext: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param palm_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#palm_api_key DataDatabricksServingEndpoints#palm_api_key}.
        :param palm_api_key_plaintext: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#palm_api_key_plaintext DataDatabricksServingEndpoints#palm_api_key_plaintext}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6aec3d47ac9c8b0eb864a54cc229695f36e9cb1ae2b6e5d70a7adf31901b9982)
            check_type(argname="argument palm_api_key", value=palm_api_key, expected_type=type_hints["palm_api_key"])
            check_type(argname="argument palm_api_key_plaintext", value=palm_api_key_plaintext, expected_type=type_hints["palm_api_key_plaintext"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if palm_api_key is not None:
            self._values["palm_api_key"] = palm_api_key
        if palm_api_key_plaintext is not None:
            self._values["palm_api_key_plaintext"] = palm_api_key_plaintext

    @builtins.property
    def palm_api_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#palm_api_key DataDatabricksServingEndpoints#palm_api_key}.'''
        result = self._values.get("palm_api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def palm_api_key_plaintext(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#palm_api_key_plaintext DataDatabricksServingEndpoints#palm_api_key_plaintext}.'''
        result = self._values.get("palm_api_key_plaintext")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfigList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfigList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c0cbbd138ad7e623b84be28e2dedb8c7e981efed9aae72124a65b1e955e2b811)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfigOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f7ea2f9043b821195e0cc573e356cfe5cf3cb17d27615f47b186addb18b3eef)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfigOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fae5ec082e5d618209619c854168822220fbef2b98d6ac4477478b365087ab88)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2722807a75b6574b2f3a19c6a50ea7fc5bf9f3f3ee6989c5bc889acf66018bb4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4980001c994d4a3f61e9a9e84dc3cd0b3aceb11bc8d4e069ab1dad0d562fba83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfig]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfig]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e958701bb712d621dbb8c507271a1fd84aad46108d7b08ebca382d926b53d30)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d1e6b329f750916395a8bccee15371b87c7a364632d104937c35190e1b7c7c3e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

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
            type_hints = typing.get_type_hints(_typecheckingstub__2af48394aaac54591974b0868d44b29df20a6244bea5b2612addc323f670f6f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "palmApiKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="palmApiKeyPlaintext")
    def palm_api_key_plaintext(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "palmApiKeyPlaintext"))

    @palm_api_key_plaintext.setter
    def palm_api_key_plaintext(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a1fdb4d717224314c2610fb6930b1040a67dabe78c7574ab06860d7322c7a3d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "palmApiKeyPlaintext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__005e27e03dc6298ce5f3da262ab95467ad9447e1d135c19e6bee076c1e609ac0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModel",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "display_name": "displayName",
        "docs": "docs",
        "name": "name",
    },
)
class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModel:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        display_name: typing.Optional[builtins.str] = None,
        docs: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#description DataDatabricksServingEndpoints#description}.
        :param display_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#display_name DataDatabricksServingEndpoints#display_name}.
        :param docs: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#docs DataDatabricksServingEndpoints#docs}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#name DataDatabricksServingEndpoints#name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73c28a4c2d20ebe832ef8c074f34a63ad625a98c356245ceb0c84e30734470f9)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument display_name", value=display_name, expected_type=type_hints["display_name"])
            check_type(argname="argument docs", value=docs, expected_type=type_hints["docs"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if display_name is not None:
            self._values["display_name"] = display_name
        if docs is not None:
            self._values["docs"] = docs
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#description DataDatabricksServingEndpoints#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def display_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#display_name DataDatabricksServingEndpoints#display_name}.'''
        result = self._values.get("display_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def docs(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#docs DataDatabricksServingEndpoints#docs}.'''
        result = self._values.get("docs")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#name DataDatabricksServingEndpoints#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModel(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModelList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModelList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1041c547de21329bba69276c7bb6aa52c1f5d99b930b7a5254f897ab5b9921b8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModelOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d81b8e71a8f495032360f73ffd5ab08e82ca710b3adcf5596c8a0200998bcfc)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModelOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a447109ea4c8b2218f4fc5e355fcdd364b2c8c6b7406201b65ac0037358dc2a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2fdcb495cd0892238dcffc4c1da910f1029a41df12c7087b3e5ad883231bdd0c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0fb2e667e05e8ff7e0d386919d88ef9c038c4ea3773c0b4ec93c123060deebd4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModel]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModel]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModel]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71e18d3862f5bb903a3f2efc2a384fefccb2ce3b70adbbdcc65505d940df37a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModelOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModelOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a092dbd41137602daeeb8b32527887caf9c9f5c1dcf54b1d8975eec827119941)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDisplayName")
    def reset_display_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisplayName", []))

    @jsii.member(jsii_name="resetDocs")
    def reset_docs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDocs", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="displayNameInput")
    def display_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "displayNameInput"))

    @builtins.property
    @jsii.member(jsii_name="docsInput")
    def docs_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "docsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__267532d195d28b67a45b1dce7af7ce5248e5cac805c9d1e874631e642c84521e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "displayName"))

    @display_name.setter
    def display_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e79d29e096f0717baed14350bd8cbfb79bc2ad84ed3c428a31c8feee1979fbea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "displayName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="docs")
    def docs(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "docs"))

    @docs.setter
    def docs(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0a40422568f5563275f68e2044dee1367e3075aa7f22bfd5e70b521e20c4bfb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "docs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b74d196e81469c58d267349512210eaab28ad0839b38a67eb4ad7b77fa6808d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModel]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModel]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModel]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__540f4e761653f935f2fba786f6454e2c0c1a6732e78b9882020c68a1e6006011)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8a095249799bd1c3f0fafc01bc58f2ee0d5e91838caf902ae8a3cbb11b10e37e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4edbc22a2d9361e39f53801336c1c6e99dfcd045c9dc6376c1cb6bc2e6dfcea)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksServingEndpointsEndpointsConfigServedEntitiesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__890abe1e15c535e1a4f55061c180a69cfc2888ffcb360f3a213d58f052039e9c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__99b95cd236bfff445e0ae50be443c3d240d1293eb1cbe2403c5558197cac125b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7aa306d34f0bdd2462d6a5bae0346aae8272546a78957d6a4f12b0f75391c6b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntities]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntities]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntities]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d43e63168e2335d90fd51165d53fa7923fc82bf58e9e3c195d0682966e3f8216)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsConfigServedEntitiesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedEntitiesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fe58e0f973da9541f1ca187a69ff7088242e4c066a0e0c02254b20dbd08026c7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putExternalModel")
    def put_external_model(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModel, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29a99d15f3bd8d0bdbd9ebac03be0cff08e44d16f86a6f6c341edc07db372aa1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putExternalModel", [value]))

    @jsii.member(jsii_name="putFoundationModel")
    def put_foundation_model(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModel, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aaf991d3333817e2bb3659f9514d0876c712d3dd0cff47fa5ad604470ec50bad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putFoundationModel", [value]))

    @jsii.member(jsii_name="resetEntityName")
    def reset_entity_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEntityName", []))

    @jsii.member(jsii_name="resetEntityVersion")
    def reset_entity_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEntityVersion", []))

    @jsii.member(jsii_name="resetExternalModel")
    def reset_external_model(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExternalModel", []))

    @jsii.member(jsii_name="resetFoundationModel")
    def reset_foundation_model(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFoundationModel", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @builtins.property
    @jsii.member(jsii_name="externalModel")
    def external_model(
        self,
    ) -> DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelList:
        return typing.cast(DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelList, jsii.get(self, "externalModel"))

    @builtins.property
    @jsii.member(jsii_name="foundationModel")
    def foundation_model(
        self,
    ) -> DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModelList:
        return typing.cast(DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModelList, jsii.get(self, "foundationModel"))

    @builtins.property
    @jsii.member(jsii_name="entityNameInput")
    def entity_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "entityNameInput"))

    @builtins.property
    @jsii.member(jsii_name="entityVersionInput")
    def entity_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "entityVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="externalModelInput")
    def external_model_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModel]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModel]]], jsii.get(self, "externalModelInput"))

    @builtins.property
    @jsii.member(jsii_name="foundationModelInput")
    def foundation_model_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModel]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModel]]], jsii.get(self, "foundationModelInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="entityName")
    def entity_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "entityName"))

    @entity_name.setter
    def entity_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__584af6c4fe038caa5aa35f7bdc48c83e43c8b2a53b7e6ab8532e220fa455dfaf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "entityName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="entityVersion")
    def entity_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "entityVersion"))

    @entity_version.setter
    def entity_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__865be2e725fbf65f451984dc9ed5435e44ca83317e63bf28775ebe9cda2e99d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "entityVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf3c81f2477ca0eacf2f1770bfd5913a4523a9a357eb13f0ba0deb45dbe8e40b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntities]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntities]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntities]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__383ce28bb3a0e1e535979e7ff792b1dc860abcd59ebdc8b044089278cf085414)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedModels",
    jsii_struct_bases=[],
    name_mapping={
        "model_name": "modelName",
        "model_version": "modelVersion",
        "name": "name",
    },
)
class DataDatabricksServingEndpointsEndpointsConfigServedModels:
    def __init__(
        self,
        *,
        model_name: typing.Optional[builtins.str] = None,
        model_version: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param model_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#model_name DataDatabricksServingEndpoints#model_name}.
        :param model_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#model_version DataDatabricksServingEndpoints#model_version}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#name DataDatabricksServingEndpoints#name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45a6a809139818fedba1dd3787a8dcc33ed004c183ccd23644ffbc0730dfa2f9)
            check_type(argname="argument model_name", value=model_name, expected_type=type_hints["model_name"])
            check_type(argname="argument model_version", value=model_version, expected_type=type_hints["model_version"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if model_name is not None:
            self._values["model_name"] = model_name
        if model_version is not None:
            self._values["model_version"] = model_version
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def model_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#model_name DataDatabricksServingEndpoints#model_name}.'''
        result = self._values.get("model_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def model_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#model_version DataDatabricksServingEndpoints#model_version}.'''
        result = self._values.get("model_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#name DataDatabricksServingEndpoints#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsEndpointsConfigServedModels(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksServingEndpointsEndpointsConfigServedModelsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedModelsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c1db026eedc70e7dc1c0f5cbbc81221f52c9ac2f19a5cc93606147ff10cfe797)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksServingEndpointsEndpointsConfigServedModelsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5cf0b40860d4edef5a67574a7e176bb0692b6918829399e71e4383082e649cc)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksServingEndpointsEndpointsConfigServedModelsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5298a2568d60d6c4e6f8208c7b1bd2adaaa4b6f9bf6467d4696ec4ac40ef072)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7c6e3d3c05c0402177023b3a1159d6585e87ed96b725b57357ba46feee931f97)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0d6529469aed9c1855f890f0485b84518b3466dfadfdc075ceefebbaa10b8644)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedModels]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedModels]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedModels]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31d685bc48b53d7db4027b048cb9f615183aaf15324c659e6b9d5bbbbac1f981)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsConfigServedModelsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsConfigServedModelsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dc886b22360a0bbeae0ea45af24cf8b777450eb75afe33da3fcee830a030c67c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetModelName")
    def reset_model_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetModelName", []))

    @jsii.member(jsii_name="resetModelVersion")
    def reset_model_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetModelVersion", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

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
    @jsii.member(jsii_name="modelName")
    def model_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modelName"))

    @model_name.setter
    def model_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a535d223fc02611d7f9f691a762b4533318cf1d354091ffaba62363cd9e7ae1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "modelName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="modelVersion")
    def model_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modelVersion"))

    @model_version.setter
    def model_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50d28ba8e15ffbe323c25158b078653b197cfe7716ed9acfb9fbe48f821af7ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "modelVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f60d625a274c101f6188bca7ccb8c6b4d89001e63f8938267c088d7ef34b149)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedModels]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedModels]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedModels]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60415b969e479732211f3e37813fa654e579da64dd5571ac6843dfc8ce01e2a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__89d77da8e515a476594c37eb5265ed936a10f9d99beb5cb2c188dd61585f000f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksServingEndpointsEndpointsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d0937f14440ada63348c63b95fd2beba378f537657a54e513e99781535c7c98)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksServingEndpointsEndpointsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79db4ae2aded3d9bc4e3086d2cc5e883043ecb518ffc0e6e49ce8893943fd63e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__13a6f7ba1ce46ec9cd81cc07573b24b4ba46bd00459fa98464f71010976c8175)
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
            type_hints = typing.get_type_hints(_typecheckingstub__230e4877de58cd4b28ff093c1e76062baef894909c94ea4421cfb49b9d585279)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpoints]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpoints]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpoints]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0598eb97fe3abd907285ca7017ffc13dd1647486f4b8bb4391c07755b9e828ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__54f1966ce9888f8573cda2c5a69c534c6092af6c480a88d3ab8d97b148ef809b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putAiGateway")
    def put_ai_gateway(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsAiGateway, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f447957ab90f0060383937d407b1602f6ae95c2ff89781667142056622aaaca6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAiGateway", [value]))

    @jsii.member(jsii_name="putConfig")
    def put_config(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfig, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5a526fbe6682245ccd4fae8c739b7fd1fa4b2528adbb82bc6818a286bd430a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putConfig", [value]))

    @jsii.member(jsii_name="putState")
    def put_state(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsState", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cd77ecf746774805cb34649c9c76ea5bffe4505d1000fe2fbc85977d15f875e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putState", [value]))

    @jsii.member(jsii_name="putTags")
    def put_tags(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksServingEndpointsEndpointsTags", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__887df617ecba8ffdb3b8767ebaed84b5903c997c3a1e7809275507bd6098a152)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTags", [value]))

    @jsii.member(jsii_name="resetAiGateway")
    def reset_ai_gateway(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAiGateway", []))

    @jsii.member(jsii_name="resetBudgetPolicyId")
    def reset_budget_policy_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBudgetPolicyId", []))

    @jsii.member(jsii_name="resetConfig")
    def reset_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfig", []))

    @jsii.member(jsii_name="resetCreationTimestamp")
    def reset_creation_timestamp(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreationTimestamp", []))

    @jsii.member(jsii_name="resetCreator")
    def reset_creator(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreator", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetLastUpdatedTimestamp")
    def reset_last_updated_timestamp(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLastUpdatedTimestamp", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetState")
    def reset_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetState", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTask")
    def reset_task(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTask", []))

    @jsii.member(jsii_name="resetUsagePolicyId")
    def reset_usage_policy_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsagePolicyId", []))

    @builtins.property
    @jsii.member(jsii_name="aiGateway")
    def ai_gateway(self) -> DataDatabricksServingEndpointsEndpointsAiGatewayList:
        return typing.cast(DataDatabricksServingEndpointsEndpointsAiGatewayList, jsii.get(self, "aiGateway"))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> DataDatabricksServingEndpointsEndpointsConfigList:
        return typing.cast(DataDatabricksServingEndpointsEndpointsConfigList, jsii.get(self, "config"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> "DataDatabricksServingEndpointsEndpointsStateList":
        return typing.cast("DataDatabricksServingEndpointsEndpointsStateList", jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> "DataDatabricksServingEndpointsEndpointsTagsList":
        return typing.cast("DataDatabricksServingEndpointsEndpointsTagsList", jsii.get(self, "tags"))

    @builtins.property
    @jsii.member(jsii_name="aiGatewayInput")
    def ai_gateway_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGateway]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGateway]]], jsii.get(self, "aiGatewayInput"))

    @builtins.property
    @jsii.member(jsii_name="budgetPolicyIdInput")
    def budget_policy_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "budgetPolicyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="configInput")
    def config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfig]]], jsii.get(self, "configInput"))

    @builtins.property
    @jsii.member(jsii_name="creationTimestampInput")
    def creation_timestamp_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "creationTimestampInput"))

    @builtins.property
    @jsii.member(jsii_name="creatorInput")
    def creator_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "creatorInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="lastUpdatedTimestampInput")
    def last_updated_timestamp_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "lastUpdatedTimestampInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="stateInput")
    def state_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsState"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsState"]]], jsii.get(self, "stateInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsTags"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksServingEndpointsEndpointsTags"]]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="taskInput")
    def task_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "taskInput"))

    @builtins.property
    @jsii.member(jsii_name="usagePolicyIdInput")
    def usage_policy_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usagePolicyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="budgetPolicyId")
    def budget_policy_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "budgetPolicyId"))

    @budget_policy_id.setter
    def budget_policy_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69bbe42858fb6743b6e8d910d10e0e173a588bcd573fff41abb38261225485c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "budgetPolicyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="creationTimestamp")
    def creation_timestamp(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "creationTimestamp"))

    @creation_timestamp.setter
    def creation_timestamp(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a77bfd5b9733e2bb04b8703d104931951de9ec6f9e55aa806ad14d15032ebb75)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "creationTimestamp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="creator")
    def creator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creator"))

    @creator.setter
    def creator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd846588ca1a0aad984aaaa7860c13953f8c62920f33685ebb8d877805738099)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "creator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e26783e996b88eb94b02e55294f175d038c1cca14895e8ea1bba86c9deda0cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc119a6c78e7d338509aba37600b9f98936701b7d2ead59e2ea49fe1f12213b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lastUpdatedTimestamp")
    def last_updated_timestamp(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lastUpdatedTimestamp"))

    @last_updated_timestamp.setter
    def last_updated_timestamp(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0f9e0f24d9b84421c82113969becccd0e92ae924b7e374f8e51f9aedc2d41c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lastUpdatedTimestamp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81f20cad7042b1f016d3c4659f92eeaacba3395a1c3c550b331bc834c51c0a08)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="task")
    def task(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "task"))

    @task.setter
    def task(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4bc43fcf94ad9d449dd5e51ee33e11c65032a86366a827cd45aa9655379debaf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "task", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usagePolicyId")
    def usage_policy_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usagePolicyId"))

    @usage_policy_id.setter
    def usage_policy_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce00eb6c6379bc864928977ee41bf26eddb6e9f1160e6cbe75891a7416a61369)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usagePolicyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpoints]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpoints]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpoints]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d698ddbe7350f3fa66cdcc2520caec8b71bfa2d06541a6d6774a035033c858a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsState",
    jsii_struct_bases=[],
    name_mapping={"config_update": "configUpdate", "ready": "ready"},
)
class DataDatabricksServingEndpointsEndpointsState:
    def __init__(
        self,
        *,
        config_update: typing.Optional[builtins.str] = None,
        ready: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param config_update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#config_update DataDatabricksServingEndpoints#config_update}.
        :param ready: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#ready DataDatabricksServingEndpoints#ready}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e86de07b39fcb30b2b39f2935d7e7f6ddcb3eea53b46a921a54c8bf9efb316e1)
            check_type(argname="argument config_update", value=config_update, expected_type=type_hints["config_update"])
            check_type(argname="argument ready", value=ready, expected_type=type_hints["ready"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if config_update is not None:
            self._values["config_update"] = config_update
        if ready is not None:
            self._values["ready"] = ready

    @builtins.property
    def config_update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#config_update DataDatabricksServingEndpoints#config_update}.'''
        result = self._values.get("config_update")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ready(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#ready DataDatabricksServingEndpoints#ready}.'''
        result = self._values.get("ready")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsEndpointsState(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksServingEndpointsEndpointsStateList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsStateList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__184d1a6b4dc0d83c70693c5405dc39b85ebbd1a959478e90beaa7dddc19f9fb2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksServingEndpointsEndpointsStateOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50dfa7f1e90a093047b28bd804f717a657c1bcdb3b696e3671e08fe22db0d36e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksServingEndpointsEndpointsStateOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9d5a3d71fcfa2b7b14c6eeadf19541b419de6e3dd1f1d8b65488c06d0259eb6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2415586cef3807ce818f846c83d3f5cf04b173f6553f07d2a7e19459e6a942c2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6ffe88cced1ec5f203ce4518ea976614bda5b4012a49e47080258e881a110d93)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsState]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsState]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsState]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90fd8ad89cafee7160fb8fa05d89ccb72039e22876cce3a775dd69789c5fe1df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsStateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsStateOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3df0451da3a748bec5a0e2ab735ff62ede06c927774bb61045f0d5456f040b11)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetConfigUpdate")
    def reset_config_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfigUpdate", []))

    @jsii.member(jsii_name="resetReady")
    def reset_ready(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReady", []))

    @builtins.property
    @jsii.member(jsii_name="configUpdateInput")
    def config_update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "configUpdateInput"))

    @builtins.property
    @jsii.member(jsii_name="readyInput")
    def ready_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "readyInput"))

    @builtins.property
    @jsii.member(jsii_name="configUpdate")
    def config_update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configUpdate"))

    @config_update.setter
    def config_update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f7173b96a0188906d84b326fe1671461a10bd761d53a04a5b902ddb41c295de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configUpdate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ready")
    def ready(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ready"))

    @ready.setter
    def ready(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8869424209c014c1910a9493195d0bb357a92387bd140c6815cf191864ffa8c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ready", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsState]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsState]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsState]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8554442bf613d10faaf674203dda5e2643edcbf2b9ee20eda7af7287b85f1a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsTags",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class DataDatabricksServingEndpointsEndpointsTags:
    def __init__(
        self,
        *,
        key: builtins.str,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#key DataDatabricksServingEndpoints#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#value DataDatabricksServingEndpoints#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9c77ad665dfdceab12fc459a1bbaf3b5d9cd386614821b74c90887914265b25)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
        }
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#key DataDatabricksServingEndpoints#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/serving_endpoints#value DataDatabricksServingEndpoints#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksServingEndpointsEndpointsTags(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksServingEndpointsEndpointsTagsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsTagsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4660107dd093100a8d6f9ae10368da85edcc73441856eda68e1b0b134caf157e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksServingEndpointsEndpointsTagsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e85fd6fd17f0724e4e4552bb8135badb473974edb768467043d523701b34e35f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksServingEndpointsEndpointsTagsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d3100c790d1f7876bbe5ddea6da78e51592ee68dce254fd45906c2cbabf9b06)
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
            type_hints = typing.get_type_hints(_typecheckingstub__78130d8276f7707183d3c639f3d16aa2264ccf9fd152ac568a5d576d3f3428db)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9f084c13c755517d325889c0da81f8c2c0ff6474b9411f4e2ab68d92855a3342)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsTags]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsTags]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsTags]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f579f51c20fc85b7f478c121c37037471b1eec110f1d0c5cb9acec6c4c437807)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksServingEndpointsEndpointsTagsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksServingEndpoints.DataDatabricksServingEndpointsEndpointsTagsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d8fcc3d153ec43269fbea169ca811955f4018a8056e579c12c36cb1f994b1dca)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6d2e1c8e94de5fd78f781a9392e5bb1e8d09328f8704ca1f6d53ed592b1771e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9119b11d96f5034b0f0d8bdb69ac02e1e10c3a2c93d797d74f16f08a97dd0fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsTags]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsTags]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsTags]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eacbfa9fdaeb6c4df650d96d237d402033e301e0747c43340ec22768e135919f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataDatabricksServingEndpoints",
    "DataDatabricksServingEndpointsConfig",
    "DataDatabricksServingEndpointsEndpoints",
    "DataDatabricksServingEndpointsEndpointsAiGateway",
    "DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfig",
    "DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfigList",
    "DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfigOutputReference",
    "DataDatabricksServingEndpointsEndpointsAiGatewayGuardrails",
    "DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInput",
    "DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputList",
    "DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputOutputReference",
    "DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPii",
    "DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPiiList",
    "DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPiiOutputReference",
    "DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsList",
    "DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutput",
    "DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputList",
    "DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputOutputReference",
    "DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPii",
    "DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPiiList",
    "DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPiiOutputReference",
    "DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputReference",
    "DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfig",
    "DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfigList",
    "DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfigOutputReference",
    "DataDatabricksServingEndpointsEndpointsAiGatewayList",
    "DataDatabricksServingEndpointsEndpointsAiGatewayOutputReference",
    "DataDatabricksServingEndpointsEndpointsAiGatewayRateLimits",
    "DataDatabricksServingEndpointsEndpointsAiGatewayRateLimitsList",
    "DataDatabricksServingEndpointsEndpointsAiGatewayRateLimitsOutputReference",
    "DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfig",
    "DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfigList",
    "DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfigOutputReference",
    "DataDatabricksServingEndpointsEndpointsConfig",
    "DataDatabricksServingEndpointsEndpointsConfigList",
    "DataDatabricksServingEndpointsEndpointsConfigOutputReference",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntities",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModel",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfig",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfigList",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfigOutputReference",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfig",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfigList",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfigOutputReference",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfig",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfigList",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfigOutputReference",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfig",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfigList",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfigOutputReference",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfig",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuthList",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuthOutputReference",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuthList",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuthOutputReference",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigList",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigOutputReference",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfig",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfigList",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfigOutputReference",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfigList",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfigOutputReference",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelList",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfig",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfigList",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfigOutputReference",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOutputReference",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfig",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfigList",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfigOutputReference",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModel",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModelList",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModelOutputReference",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesList",
    "DataDatabricksServingEndpointsEndpointsConfigServedEntitiesOutputReference",
    "DataDatabricksServingEndpointsEndpointsConfigServedModels",
    "DataDatabricksServingEndpointsEndpointsConfigServedModelsList",
    "DataDatabricksServingEndpointsEndpointsConfigServedModelsOutputReference",
    "DataDatabricksServingEndpointsEndpointsList",
    "DataDatabricksServingEndpointsEndpointsOutputReference",
    "DataDatabricksServingEndpointsEndpointsState",
    "DataDatabricksServingEndpointsEndpointsStateList",
    "DataDatabricksServingEndpointsEndpointsStateOutputReference",
    "DataDatabricksServingEndpointsEndpointsTags",
    "DataDatabricksServingEndpointsEndpointsTagsList",
    "DataDatabricksServingEndpointsEndpointsTagsOutputReference",
]

publication.publish()

def _typecheckingstub__b0615872e535cf70fd90ef47a9ccecdadf73e2e1090160ca2bdf08e0c86ae237(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    endpoints: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpoints, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__764b54df4324e43433d2afd71a93aa0593a7d292f6d58c2921a1bea12c43de59(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a4d221fb471fa46a66c8e05973304599beaebc17ee8141c10103431ff97a288(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpoints, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a099ffdf60f577f97ff43c040e213e0785da1e6cde613a5556a0612ed231e75e(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    endpoints: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpoints, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9af00d754714e76bce938fafd2d285851b7698f6eb5629462e9bd7a6d4f2ad05(
    *,
    ai_gateway: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsAiGateway, typing.Dict[builtins.str, typing.Any]]]]] = None,
    budget_policy_id: typing.Optional[builtins.str] = None,
    config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
    creation_timestamp: typing.Optional[jsii.Number] = None,
    creator: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    last_updated_timestamp: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    state: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsState, typing.Dict[builtins.str, typing.Any]]]]] = None,
    tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsTags, typing.Dict[builtins.str, typing.Any]]]]] = None,
    task: typing.Optional[builtins.str] = None,
    usage_policy_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85ef6c12abf6a5cd33b515e14f50d444f428b033cec0aa5fe188b1c884642f8c(
    *,
    fallback_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
    guardrails: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrails, typing.Dict[builtins.str, typing.Any]]]]] = None,
    inference_table_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
    rate_limits: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsAiGatewayRateLimits, typing.Dict[builtins.str, typing.Any]]]]] = None,
    usage_tracking_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdd8afca0c1a952abf274be5fe6312e1a9b16742e470341a0d33ae89ef2cba7e(
    *,
    enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39349c94f774405496b1679b3d26390ef22f0ead8b3a4a7301fbfe2fa172d253(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5c5d3ce044071beed6bdcd636382acd171391e9818f5eb6fcbfb030d61c611c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e509ca129d4936bb9f94586d592186873e6f9c2c81b1e112dde26f6d1be98507(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e9c8ba56ee48759785f839712f7612cd315f895b4978f7199f5458ddcc3de72(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e92c42cd34a59d42fa0b26ba83e3833588bb7adbbc6f9d0450a43df6743951b(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60e8d7c03d3752fb6bbfe0af3fad902502fb8b8ad09a9ef1587de04321a96697(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfig]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__507ad4451274e138326b4499f36c7b2c8978912d52a982e09c116a13896798ee(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bde4678302a68fa9a408399e6f8d8f5dc4aa04d0166bdd7876ca1819d83a62b9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5d476909660310d3e804f82eccf2ecebaa89afb058ac9661b7e7f86bc4aa97c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfig]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b35a2904cf15bf1c7c0cce86c7c8b0402319026d5c474d79a27c6a531bcd1671(
    *,
    input: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInput, typing.Dict[builtins.str, typing.Any]]]]] = None,
    output: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutput, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27c6fa0bb79dac22f957d3b70853f2087e5d8a5fad26fbc1f5e281f9ea386f15(
    *,
    invalid_keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
    pii: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPii, typing.Dict[builtins.str, typing.Any]]]]] = None,
    safety: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    valid_topics: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__862dfe6ec870b187215fb6c93310517d79ae9623eaefc08511bd7b262dac9030(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc2c447973d4d57c9b2c4d1a3c5750f86fd78075d9e9443a2965f1fcf0f1c884(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f147aa44ed253c5e55603e4260e6b50414d03d36771eb1c3269488c69aeb491(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ed687939da48ed725dbbb6c92cc668d50e65a6e177a69bea1d5d535bc1d5ac5(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0286483674aaa0f59899fe987afb3e9467b8b0e11a6fde3d1c2d139ae7642aa0(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a70c46354ea268cf90ac27cb143ca49130c650da3b38c0e9d377048b4d65b2a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInput]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf87a8be50a7805f87073b6bfe6eeb106aff1c0ace45eb8e4aec26686992debe(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbcef1d861b390680d76622b0f02b449d0a85b2c294e0046577dedddb4e36002(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPii, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc1afc98beb85a3803122387fe368b7ace73f6f06fab4a40c0c6d75ce3b1edf9(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2c11de8a82790674577220460d8c8bc5dd169538c129edfde1f67daff576f39(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__397a2231b624861594aa02d1dc07d079f9c07e24c03cff9bb2ab7e05fe27365d(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__418c9164be5fb206ef20db43b872c88e9b25038f453c80621ff083242fa26511(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInput]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7487c802d2f64b05d982ec79e13dbaf096d95ffb6605019656f41bd46dfd6dc9(
    *,
    behavior: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__179c7224d88195b2d8c41685bad158678f1e8b3ace0b160f0395dc9f5fea9f88(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b538485c7495ece19b6b8dc82207a17d19a9f14f2fed066fee2b41cd6d66f27f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84512a7158a8c06d9471dd0f19e95d33b8746919188638c9db332a636cee63e1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6735f9edde734e4ae5ef2b3ee3a1a990330bc9e492723f4275f3b76695e50443(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7355e8abd4b488574cc5c26384c54512b02f297466a25a74582dda943bc380a(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ba98203666d535e172e86b0b6a5bf530dd434c51c89312956d858a68427a3aa(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPii]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7215e1c21c69b5a1d27e6bbfef1f7998dffd0e8c59957adf123244d3264d7386(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8ae34dada995457e92d5b86b29746485b725f5850bc0590a48083732d6d97db(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be7199664685820f755b70a1ccb9a7032e30a7a955cd33a57f596e302faee1b3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInputPii]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fd297938781b70e91f9eaefb773bda8e9dc608a7cd735ad986458602a4355ff(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__786e078d137f0f586618487fd8983bedae054b459b97076d43b0366f4eaf34ea(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c0bfb33cca14beba305aaae00df5de426d323043c96a738bd168ef3e3b7ba8a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad3cf6dc428c0157587d6ac8d419beb661076bb32bde3594e808851c09b17fe4(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98e69c2374bdfdc2031061384c06c31034ebf46f6844ad4bf585df59e4a5b6aa(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad0fadb4df817f5d95bc305dc909c5a7ca2c722d507b3d81b358c55adb641018(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrails]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3943d4edc35bad60ac260aca63b1c0d01bc177daaa955ce6d7412d02b114909f(
    *,
    invalid_keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
    pii: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPii, typing.Dict[builtins.str, typing.Any]]]]] = None,
    safety: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    valid_topics: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e883a54c60fa890cc7afda6fad542d4a037d6c7f48221db614204cfef4e8c50d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48730d3afd101325402b2ce7479040d4448ec7cf11929334f7e185134730286e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7781baad1132cddfe41719c14bbbdf9dced94a5f6d8a9d85e649a58ab6b5874(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03b6daa51dada3304393b168146b2ad270aa1c8c02dfad0735d86faae976adf5(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5401b4789b54bbe1e5d9cc63caf4820667e1ab810db7432d3ad74e9ecf646974(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__754c7e8eea5e50c2c89ab612027137751fcd7f0d234e251a161c8c5dcbcca714(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutput]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7b7d148aa0bbf4148e6ae5424a8fd3774cd4c69c67289a290e50100388e2489(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca9282553db5a76c35d565330d715ee7638a1cd8e0b73b4d2c933cf81edf50d3(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPii, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb8af2b59cad36a6582758c608b9938ce26be61c07b9c950231c16bc71af25db(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__623af87c35a2d74465ed536383ecb7cf831b5c6a0c0b0d6e96dababfec253ad2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a71c6e8543ea9914d0786790df2427292a1d3e44c12fe9585d172d574255390(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__147130f79b1d3e1ab0f545fce582bf9dbdf2a6abf2e61ea2439b53f6fa38f754(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutput]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__470dd95dd2a424232fd36f77030942f46aa744716caf08f257cc416b67f297b0(
    *,
    behavior: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9ec2dbd719e274dedfa7a52aaf0d7d217d5eba94ef9d85588f151866f44a18a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5633d1980556ca7695b6ad069d3d1c6168b2baec051de889ab582c51091c8254(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20e4711a8185636db51a44ac8cbb7f51090ec67bd216e44814b663059304dc6a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bec22fc38f7e283326bc95a0c7637c037047c2e6d17929377232ad914ca738fb(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94fd71352e17aa006145248fbc10bbe75a529f782797b06a2a15fc8a0817eab4(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__103b26c8f2bd70abf136265e525a7091eb46ef59d5f3497d443ad93558a32991(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPii]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1721f17b3b0d7fc1b373db9dc8716f7033a2c6168c7a4d5661d6d4047cca240d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef9b59ea7b3129109a60ae2bf421d2c3f58c21fdda79e30d9436c40e2cbcc838(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf2e5f5c1921fc6a7fc7dbf9ed8e818cf199fafefa9741dfcb66d9670a9263ed(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutputPii]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__545ffca41630ab2ad6c26ec1ef9741ae9b8d636b66a1f97d506fb03fb8c1aab5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb24f16555c197c4fa946eab776c66aa1298c4b3de94a41dc9e970523bf9b9fc(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsInput, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff3fa7014cf544df85be7d9e2cd453b87db8387fbd4bcc42328f3f7da49a7f07(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrailsOutput, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4ac4d7d05b551b415d4cb93b23302ee64d1d87d04d5f3364657edc6faabcaae(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayGuardrails]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18b3a8bf3e7e0377083098da2e516ab8e36685dffd1fe8afeeb2c940ff3cfc10(
    *,
    catalog_name: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    schema_name: typing.Optional[builtins.str] = None,
    table_name_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee77fa981d8cf39a8a5d452407926091769c6a842495a193de3ad8678a0b1c81(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64991490810460d510b5870a92713ba7315c6b21885f12f71872003d8cd5c077(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__954f59f98b1348459eba60c6585d6e8a21138e386fa8aab84ba6491a9407ca6e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__227c6d0619144c0d1b93f39393bc5cbb86bc7d0e7217d8b9df20722af13e9238(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__496adebda8d7a7de5a7730876ee04893126757b31bd6cb9a8217088ddc6db822(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a30f31c07c3a716cfb2cbd7f2a37511e6be712a52c365be19931091c23065840(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfig]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6453dad98327dbea8e84b4e25d10343a2d3f1ba7aeac923e1910ecf04c590316(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c38bb23f65ea4087ef265bfd634cacf0b85031a543decd901ba9322f918b00f2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28c0d73bdc4f7ffbfa0a4a90b68e548eb4678add3a0e918b2a8e88a38ea49b26(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9deecda72312cb7a1cb376a5eadc694fbc95a402d816e202b207fe8ad5acdcbd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bef79bf1917bd6b4d67f85b1ab54a4bc7ef50efb87206a3c57aeb2884b813751(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d12a1fbc752fdcc4d093861ff09cd4dfe77eaff15b20d0327c7edfb945032016(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfig]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1e50dcff637f3629ad195574ba72a6d05d2d2f033660587b1aaa779c7e79f29(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7e37c14373966f84028c3997788e5793adbb98776039f7a0a9eb0e6ef2f6848(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbfc2a1f2b0ac294d66c082cf6de3bcab6079fd5932c6104a3e4d71abcc0cc67(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__239d8948a653cb4d445c8acf0a3f7f5a005715ac475dd7d5c152f36188d3bed1(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8296e639700632f7adadd246a3652fc6ec5bf74164888a797125263d9071bf4(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a881d348517413e4055dc6c107b23282fee7045201f345b0b7a7b4765049b2d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGateway]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__679e36b908666867397a6f7ca0a7c9d9b305187cd8bedcb32ec5c38fa493778e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d405342a42d85dbf6e7fb09ba62ade812a2767f53f53d82802c32a187464ea6(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsAiGatewayFallbackConfig, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2e0e33c054334c12459dda69306a3fc8b4122e2b097b8f08f8b4c1f44a7b7f8(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsAiGatewayGuardrails, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76818eaa322e8e38115fc827ee62856abe731fcb005a0d6e9f5f042fe16c388b(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsAiGatewayInferenceTableConfig, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9aeaccb1cfbc3510b0fa93143d4e79ea0dbfd6a71aa75df6ea49c9607fa4ed25(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsAiGatewayRateLimits, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee3d3da13b492df2b37012e5950e1023e4d616abeba7912afbc91f0ab2df1ca7(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfig, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1909db5f1f4774fb07a6f4176437c9e65116197a0b3ab3c3cb2597f85b348b86(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGateway]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a45f38c3405f5e0a49a103dc227c9fce97a0b7f17d52770c252241b3bf96b98(
    *,
    renewal_period: builtins.str,
    calls: typing.Optional[jsii.Number] = None,
    key: typing.Optional[builtins.str] = None,
    principal: typing.Optional[builtins.str] = None,
    tokens: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3768383c43f406bd01462629c61b41ec9d667a7da01e7207652a2c53dca0e5b0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3b30f0470c3da5262d5611a74a4840df248f7160853b7fba7a6423b20b12031(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30af78a711399c81472fde0a6635b4a88bf6a4ff27d00dacc4a625e73a1ee819(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e122e32bb121825e4f23e0a15ad68bff6eb074dcbfa72b4d3de1c741606000f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__879da07e1c55371f77cb390dd912fe9b5a2a0c01f17e57aad63e5151e2609e79(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05b0b98c6f9bd434afc09d3e8a8a250ac626dfef243e782daf2ffece5e2369f0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayRateLimits]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95ec05510b98754bb479fd661c52cbf26390b8d890aa55d03a46a26f701ae34a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7748c580e7b515bdc10ebd826e49eeb41b85648b74d5c693877e8b8b59a813f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0b94b7af0fb7454881f000da23697cf985c31bd2ccfd8c78a98f64772039870(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a1958557921572acac7bd14832c9690947560cb3f58513b1d91e302072aa2ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e207d05d22d36e747ea537cd2566fd3baec3f56379e6dfa5b625da6e000e001(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea134e1a76a599bf356f3756cf7b1f409293a55be85864c7dc3811a4b4b7935c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c19a709f749c1795751965101e73f2969150ccb300ba7a42aff43ce220e9bde2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayRateLimits]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__319b4b6959716456a7612ed5a7bf2d0fef1666340672eb4bd3a7c9b337f6bab1(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a3140666e6e5ab2a3c85611709e46f6c82abeebe414f9167770e78d3913b882(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8c8c36233cc954c136cefef999da70e2eeac348b5f344be8904dd7fd978d4b0(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66c705a9b1701effeb6b21f0f506cd2d23702390af0e931d916fb7c78f0895be(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d77ff02f7369c13ce574bff798ddf7b06091d70988cc1425b03cea136b1c577(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b3f64d455f90bea17bbf21ce43a3147b8ef1f41aa79ff2b7f687216ddf12441(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22f202503fd88864d213b92750e110052b9c94e6359eabd4a9b2e87f4cf10521(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfig]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95875e8d77bf719fa23e9fc879b76bebdd79022bf5893d8e9b32f26b3b4412fc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd8b9e0d0bb4520ff5b172ed852c0c22fb54f3114e90709fd9e070c16a95e5aa(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db3b6f5f02e30bbb67d0a1f1194cd11b7a7bab902eb9769b42dca411f20b2a40(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsAiGatewayUsageTrackingConfig]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__318e34ba71d0735fcb978f87b893dd06f3e2ae62b9bb0571482525ace9e3ddfc(
    *,
    served_entities: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntities, typing.Dict[builtins.str, typing.Any]]]]] = None,
    served_models: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedModels, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3aa5769705431b6ae7cfb84c5acc648f662b948462c42ea7b3c012a47dccbe2b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f979bc60aadf5548cd91c9867d7b72d30a35144509e46b11d69e89097dd6c10(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06ad0aecf8bee61207204555519ac53819b3763178ffde0a00d416dde7178045(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__282818ea4831d9e49b7e4c327bab112c01315eb6e4f0cd481b1b79472fd35e28(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b422f85c63232665977d03205a6b3a26f9379eaff45484f36cda49e1974e28d7(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__792c178b1944fb9e0b1b6d30bc50aec5bd19a10b23449960b5ef983977292648(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfig]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4834c4415bb91d07d5a58561f5deaeef806c06034787b7140ba6395d8814fc68(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4d9a1648e111628e0a4c898d35b35f89999db054a773243da70d0625349383d(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntities, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a936387de6ee9cd5dca339f05c6878bb313662fbe4b2326fd51ad2a39b031007(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedModels, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38cf2b4078d086f25600bdba53d131fe92283b4717f9ff5bc78d0b51d757ea3b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfig]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35aade4f67c1db209e3e6520d43014060ce466ef0fff6459e16c728a46efd1a9(
    *,
    entity_name: typing.Optional[builtins.str] = None,
    entity_version: typing.Optional[builtins.str] = None,
    external_model: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModel, typing.Dict[builtins.str, typing.Any]]]]] = None,
    foundation_model: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModel, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcb637d379a732656c5b3aa28afcb98386c9e1b32ae6a94e953588adac0cb82b(
    *,
    name: builtins.str,
    provider: builtins.str,
    task: builtins.str,
    ai21_labs_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
    amazon_bedrock_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
    anthropic_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cohere_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
    custom_provider_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
    databricks_model_serving_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
    google_cloud_vertex_ai_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
    openai_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
    palm_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01d9e43e91cc024c26ba9505d7bfb9f00171b8d6b47ecbe80aced93f5550b98c(
    *,
    ai21_labs_api_key: typing.Optional[builtins.str] = None,
    ai21_labs_api_key_plaintext: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3260ead522251fa26fb19c03b2cf8d86f15bfa868a3e65294f96ed504a662d20(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8dbd4b46742dec060066e20ea2843e31d7ba9eb3a97f441361f9ab5ddf4cf25(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1acc981bbaa3f1f1891916793184cf0ce9023759328be47448fd92f0cc2223c9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7db1b8cecbc2447b1c075ffe87ab2c8954ad2a9d77c33e0cf744201794a7bb3(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df3214caa3c4eb4ade1b9666fcc957c2d88a8a7505e19cb5b32efa2740a6f4f8(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2035b462fc6f4d282a8c6bb124f198222a51c633a499d47f92bf10a308006da(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfig]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8d414e2e869fc38bb0bd2e7a689dd3094f434175e416ae509124844b6ed6124(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bfffa675168632adac0eb2cf3602eb9fbe0044bb0e23ea8ac296056bbe8e2881(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__faab66f997258ed1b4d63c78b436ced166f67103da2033e225fc56c02dd70029(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f587b1b04c1905659a035d470fd789c0c0924190e168bcddba823b31e8a4615(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfig]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c0c2cd7bd67e4904dcbf2c1f67722d8b18507dcbebcc2db6470cfac5e309a30(
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

def _typecheckingstub__5ec98538569a6f29f62973f9399f9185a5ddeb4f202212e1ae2619437c181379(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62c8f58dc15447e4bb3ff68b4dcd2d1623958e9d681e790cd3dfe88dbfde98c8(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d7ae51806d1ab5d61c4064fe4f6bdad2d69154fc3d7ff3f39248cc0c23dd2ad(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a4387b52c37a655c256960d4bd56922d957c0bf017c5c7163d94b51169c60d4(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__731b156f6f0bf31712c93dbd4210025b6bc12204dc698cc4ac18dc8ef7d53af2(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3ab6338f9553abd1645c027bfe88c04978019250407fc2aba73165923ce420f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfig]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b8680774b9e862cf6ab048e791546453eabe3070f636cdd3f1a8bfa9b5f815b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__682528ad3ecbb0a01d1f7b213d03184374ef88bd5d83fde21e36a7ab71bf1477(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0171a207a3a8e5a2a4ad469c89a15384a9060eff5ec1327680e148017facad08(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5d1754661fa47f03b2c09cf13b413273f5264f91594a11e3359f6a9b750aa2a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac5c9ebff3e84ec1dfd874ebe6a3d3c3a5e1179d64952ada6c4e5c34c675e2d1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b962847da8bf7ac0a836221c7d1b3767ab3fae15725961f2c82dc4fe5ee3bb37(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d088af06719d7b4e4608b1bcb3dd9ac07ae2a293b6dc78da5494fd9e8e6f80b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__760fa3fc911162822c8014c0329e9ff3e613cad01b6b026a41315d97dfa92e60(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b92a59fc978f0c4a13a4eb27b0f5d8ae377ac9b21415d9885aeb2641d8c846b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfig]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e06a86eeeb52e40c5ab2db35e72056e0d9fd891c0a08e55c9396ed9a8605e059(
    *,
    anthropic_api_key: typing.Optional[builtins.str] = None,
    anthropic_api_key_plaintext: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca3d06c0cffdcf6561f566cfef7b24bf75d86d5bd4a1abc71038c7490ec96257(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__868695df448e5ab59896fedc28c829eee811743c2b997f8eb328e707ded006ad(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c17eacc1465f3794a91f768a962e23cf31d45a909ec972e534134941eca8dcb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__068d7187665b88ee7797c51e61633a63fe57c32be726a18527c835d5bf4717fb(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f0a6dfb2318b5375671c1158e9d1ce1eff32637f4cc8223a36b39a7a16266d9(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6bc976f8b0f082a2a0e74d469605e7867db3a5a61232a614138ffe9cfd956576(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfig]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__632c15cf5f2cea4972ed888c096add24fb2cd5063ef9dde775c5ec8a015803f8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4bbe8038d7d4cfcc5ebadc8c04cb00c575b101eedeb9f549c76b58a7ccd5e58e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abe5b9a4a06ab62759926577773f7b3730dc3407f28966cb5cecb4f5f2b287b3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1951ea85f879100f474d9ee2dcfc46b9a210982e4933dc6ef95dee0f006f9adf(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfig]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3da1bc932c86ac379f248865a60c6f120d0f86e2caa12b8d8085d3f60538f31f(
    *,
    cohere_api_base: typing.Optional[builtins.str] = None,
    cohere_api_key: typing.Optional[builtins.str] = None,
    cohere_api_key_plaintext: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9cf196cf33cd12de6153f0391dfb87849a5061f5b6ac41d8d1a10532ad69141(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a60386b4e5d4100866774b75ddca991ad69360a3e812452b0d3aaffbdedd2ffe(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3728478588fd7e1ceb018b0eef9c8ef7a49c5a83f6d5c5f00af362e59d507335(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05901f979dc677d298ea0e7715ef2ad18a9a1ac906c9a97155e0f5e93dbf71ba(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f1e3a018e9da076b7ebb5847b3f1c6d94f6c3eac6799c19dd2f62cb50e66c83(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c61578e2e7eccf75f19ac8379ebd4ba631b3e703f4a20383d6a634a6faa25df4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfig]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a17721bfb07dec68c2a053c43201b9dfbb656a994d004d17d5e6467ddf749ed3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34c1c3c066fcebf454f78814764838b2cbd9ac11aca18f3a20e951202f6d9635(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da5d687a4b941eae5a1687df1a221930a2e696ce27e08e6be7f15284e0ef364e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c9ca6ae685bd6aada09607229d7e4a8f4d97f32fc44e576df717d89360a439c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d7a52dbd05a55717eea5be6197b6c748ebdc2db0f391df0b7605a1abab03975(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfig]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__664a1971124ff643d01b13d59a6e6b2292859a27cbc406da599a7f3dc573b120(
    *,
    custom_provider_url: builtins.str,
    api_key_auth: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth, typing.Dict[builtins.str, typing.Any]]]]] = None,
    bearer_token_auth: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36b92cb282a8221ded619edd175db91c0b70d30442833dce469ba8644e000c32(
    *,
    key: builtins.str,
    value: typing.Optional[builtins.str] = None,
    value_plaintext: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db5856197682457899c1d9114aef0f9ec3cebc37b1fd34a3dad5ef948fb04e41(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3008c2534a82b71d7eaca416d2e829529528aa3f2daa7b2a75b3664d8d0bdb82(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5052c35f4bf41d78d84c1173ae76026ddeaeb65b02e5f746921839b80d629fa8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4b64dade8124c15d68b10e19f5374a7b16549b2eb0725a8e8026d37c6bc3229(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec575da1f23d3d2b8a6c1e328737599325fa807af9e17963b99539f876609f86(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__804fc87a27ded6716038c924ccba33bb8a355799ff6e7479b302126262a586b7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4bbf4562c39fad3c24e70eaf69dc4fb50b4c09f20ab35f34cb32963a4b204398(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02327d191a559b8a74560d472779fb0239c9ed73dbcbc946e4d25c602dc396c0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa9182000bcd679e382b523981070919ad8b640b214eea65666954fa782f7063(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd9f772469076a1626bad7f1556d871cc84188e71d0b748a0a24a8a9476e0bfc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c09121157c9dc85eea0b71ac268cb03cdad0af3044e4b8647b93975ebb7cb582(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9f3c23622156978320041982f29d5b6955cf0083b5cf66afb6cfc7e8231c2ae(
    *,
    token: typing.Optional[builtins.str] = None,
    token_plaintext: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95053fc8e5974f9059c53e4e605852f43b982c94841eedb063287bd33e0c2935(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94326c8f2ea0a54adb27e16aa78bf46451bbe7d1641193f19eff93e3e2b9fcd5(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d708ed7c5fc2daadf6493b2f940576fba596e9230426074b44005de27636883(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d82eb60153b8aae5590d21b136f254d41ab5deb41ede180b2f27fe1d8037c2e9(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08db302c9442b6b1b0ff207854dc9f0414c195b6a6c030beb086f085d038bbb9(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84381fe4402cc93eac21e77b946a3bd5fd67278dccc7f0701200944344cfa21a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da130584221935d7ede5487c811518dcf34fb34c6076b111aaf884bbcf6b4da5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b50b7a42484aa5c849b0144d938f850b7df4d41fa0b836f4a2d3c1c8f34cd8ce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94232b69038d8ab39dba7c9980f92aa8c75c86fd01b889edae2641c3b9e87a43(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4c6b8a9618523956f4a03123e25f7b95223dfba9b5e23172afd1794573e0625(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43308adbf2a458af54faf5c8c4b98f98a3ba25595d55102d7f1cc7cd1fd1277c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f04102ef8b226935dfb249efe4cdfb1d777f103bbfe3d9fd987292ba096121b(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e705b31ff8a945efdcee6ef1a4497e8748e8170541ee994bd843a0e9f80605d4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__498e0287bcf7999353272da33e2ad9649dbb45abe804d1e1e3a55ac39849c81f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20361b1531f94a8511810a7de5bd2c5d4f69559cfa7d0de6530d2e592035c3c4(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b41ec7e8fffa54024eedf0ce453e9e8f4b9a0dd31bef5eb119f9719db92c945(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfig]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28832b0860f47160d48542bd35ed64303bedd840a24470694da4f6e982eb98f9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccae83aacb41be7bb11f23a3f6037e4303e2557ecfa2333b8156cecc82309070(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigApiKeyAuth, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbe9a3f946531d36eacd183f96c2370e1ded506717d43b7321f0728ed6a7dc91(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfigBearerTokenAuth, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__761b960e3698e12ad0c82dca43cc1ca5b95a1bdf0829b2f66d0e5202c924e96a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5db7febdeee5ffc6d6f298ce1ba041fe0d6e50d5abf912a312835014ce787350(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfig]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a88a082c6906c017809fb4dcb3d42876bd94931394072cc0cbce2cb2f3501525(
    *,
    databricks_workspace_url: builtins.str,
    databricks_api_token: typing.Optional[builtins.str] = None,
    databricks_api_token_plaintext: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39f14e7f780eab9ae7a92811aa9e5519a3dccf76ee356f1bff0859efd0f994e7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__479705da800d9a234b39fce73f885fff71e6bba94cd2f601c37f6f39ab61271c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04643f7d6fcfa4258a07add8a9b00b85519517c17bb5cad89c70e782f7d84d5b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5545247c3079343c2b0c2fea48e1f06dcf58a0e935e5862e0f2d2989b709328(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57736c4697aa7643b452e05ae7d7112520744e456df83a0a7952642c06cc3601(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94f315a661e7dcaced13c296c150de713040e24e46cfd301f464f030da469af3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfig]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0d4e9f3cefe5f6dbcb95eaf1097c099dfc31ff6b42e41766f2792792dc2b3a5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f188fefc92913a40cfef0b7d104383494f6f40b41c4332cd2327776c2a4c772(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7c4e0b9a6f2150b6d421cd67960d3db5b3707ea1835f3891471e3e35a4b5683(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65553b134e43356e3aeddf6e4c151feb2e653c3868d05c6c0f0e6e2ad0833e1a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed25fff6bb414dbe6b855a552755b1944d095a776895d55dd17a45e585273c30(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfig]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e352edeaa86c4a032144f25eb8e6977146fc99d63076e2c0a203c9005754d644(
    *,
    project_id: builtins.str,
    region: builtins.str,
    private_key: typing.Optional[builtins.str] = None,
    private_key_plaintext: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b55e65f89b9b3a4169f38324e05a9eab484057202dacb0c9e99c70c13052a87(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__707bff8675a1bc3c0aafe800e5adc172ee54bb36c4145bec4da9c272a8fe06fc(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccde555a382a6803fabdd8eaebe919449be5542dddf8b8639846dedf7bff8389(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cded0cec26539959bdbb9626654873b0c414e5c9defe9ccad0bd3350f2c90a4a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d881339bb9936bf1ee968d4fc37ad989439530da9baaa9cb401b727aea8ec050(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__702b8cbbae927e4036df022c26075d6f772ca3e49e7f16421731d3c0ef440c15(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70a0d75017ac8f3aad179e0f4a2a5fa365f075bc3f7468b098d14a7fb2b36a53(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20543f53ac751ad35a2e3d2e3b1035977f7ef6989784f99efa3f71931ee2f2b6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81263e3305784c618326ab43371911bd5e27abaa033e47c2c93aaaf37239e0a0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93b8474c18d731b527f052912d722acd0041e3e9da173f18513641468e8fc044(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbe8a6bd9fc6cf510be679b8c4fb442b01cb79e3c3fc92660035d2c2ef6336ea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c2f9df3a6961610110e5c67cacad9bf26cd9c6d0df833ff93560eec5b36e2ab(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22c3f07dc7de3f5436fe505be98fb2bd08e303b5e4911558b3f5c58944f9f689(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9499ef20b8d5615a6038b0c5fda2b89d8dbe4a2824f491a7541da23b5c98332d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__749b0095a6a9f208fcf71dcd45a3462f2f9420ae45630b12244d4418cd23c544(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ba36f5f00fafa9a821fa71cf30f648172b9277e3118962eecac4d6fb363db1c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4418069997efaf3612841c22e8c7a4e1814a8636576490e5d196a8ef22316cc3(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2139f23573bd8a2454c9b270b5be176e281eebaa8147a7fb9aaccd3c9f6c8a7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModel]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa450c31451584ff4963d81c9f94f2e4a6a4d1e3d1e37831a3fb74fb3943420b(
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

def _typecheckingstub__0ff29216064bd8980e39e11cadf3561c5abe915cf064bcf1b20c233a4e93bf9e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efaca5c16510e1db24e3b457a2b121fa841cd20547fc2c4a7d89b231403db460(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9316a4c6d10cc3414b7d1ed39d114b986167034a9d3d56da499f456e08dc0ea0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c3f8c617fc4f2627f967e8e1d77f6abdb81dc02c3f1baf4e299c0445d0cbeb2(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33993396fa486e44a26dabf652ebef02801ad9fb2b44acc200ac7bbeeebdd49e(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca4a67a0029e6e3d5405c61fd1653ad5c446103f6cafb44e452dc93d7c25a6bb(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfig]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62087b49e13912584961fc21096f97f744d653ad943b96937ccb06da5fc29afc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__151a1b479f9573a11ede874c9757db5d01b2d771e9249a67ece89ee9e2cc5542(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e77f02290a4e9c4c80154a59de516a68dfe7f07706e8a49cad7332e82a8f1650(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9359dc95ecf8fb2806bbded14e538a3f8c93dfc54034e8c6c75db08a2c482fc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__201167e4dee00cfd060f8ff339ee4216e903b4831777664d6a1fe59e6dd7277f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2c8f119b919ab010eaf15a21c5ff9783e22960f8c28c0a7ff9fffcc569a36ff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26f14ad5bbf0bf1d5c24ef5028e58a74b9f3585bd4cce0375d426a7e2c358b0e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__209b3edca2003562484edfd76cc1974dbd3274910afbb3d1ec60249937358cb7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__898eb41160d6a359e8b82f6c73e47dbcf083a521580bf95082cbd042ac1fcbf5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f28784b75d6d0ed9c7e4f1ea8c10e8ca7a4e6ca1f29318ed4718fb74d412271(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0c3e2b7504ce455d5b2dbe9dd74cc561119a9ef87464e77afd7215f486ecaf1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4e40b35d1deefa2eaec3b4a866cebe9d80257ae4a6ddc70c72c150e15b0b2bc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8a842ccacea4dbe30af54108cec0d0cb9e02591e56d873da66ffca8c6c2f6b4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfig]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__523bf0c100327207c97409e2e8087b5e51758bc1ecab5f4d82aa625093e16e23(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__318e1bfc57dcd5089bd4930c31bba5bd5ecbe89c3365b85f59fe3afc9e7b70e5(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAi21LabsConfig, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c484c12f019655722c664b641592310fe1da43820f1939920f99ea6aad2eb39(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAmazonBedrockConfig, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a49adfa1ff6fdc3f756140d7af9a09cc47fb9ad60528fa880c8e86887e9dd3b3(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelAnthropicConfig, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd54626fc3983219ad7e69b54c1902333f43748b9ac743ac3784732be5f2df65(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCohereConfig, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f4c192f8e5fbcd12ad9a8164a11cc1f2732a78f5e7e26b90da7f50773ab5415(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelCustomProviderConfig, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8036f82c3781ed782ea48e4e485a0ab1729a3c2614d7d0395eb09fa5b0b7e488(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelDatabricksModelServingConfig, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6991f219bb8c153ac502ed777a6b87460af44f198408e003631aef628657fd60(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelGoogleCloudVertexAiConfig, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef3180277c37e2f0b8be970fb3a893ca1fc5efddb532fc3ad2c0982bf4717962(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelOpenaiConfig, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0386e5c732bd1007374028065b7780c59637ce424cc86b64ec59701518c98c38(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfig, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af091d48e2850bb2e4e173f493cec509042a2018c94a7577cd2e504e965e5df8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2dd02ffa4ac3143cf3868fd4f15b7eab754c0123263d9264b1d408a447566b17(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__002ee06ba380c98b3dfc9c138f6eb3d3e912d91969c1ee8ab76eeb49cb2f278d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5210aee1bdfa2d081e03b6428a3008f0fe5ae6b151b088dfb68f23c19da744c0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModel]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6aec3d47ac9c8b0eb864a54cc229695f36e9cb1ae2b6e5d70a7adf31901b9982(
    *,
    palm_api_key: typing.Optional[builtins.str] = None,
    palm_api_key_plaintext: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0cbbd138ad7e623b84be28e2dedb8c7e981efed9aae72124a65b1e955e2b811(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f7ea2f9043b821195e0cc573e356cfe5cf3cb17d27615f47b186addb18b3eef(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fae5ec082e5d618209619c854168822220fbef2b98d6ac4477478b365087ab88(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2722807a75b6574b2f3a19c6a50ea7fc5bf9f3f3ee6989c5bc889acf66018bb4(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4980001c994d4a3f61e9a9e84dc3cd0b3aceb11bc8d4e069ab1dad0d562fba83(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e958701bb712d621dbb8c507271a1fd84aad46108d7b08ebca382d926b53d30(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfig]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1e6b329f750916395a8bccee15371b87c7a364632d104937c35190e1b7c7c3e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2af48394aaac54591974b0868d44b29df20a6244bea5b2612addc323f670f6f3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a1fdb4d717224314c2610fb6930b1040a67dabe78c7574ab06860d7322c7a3d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__005e27e03dc6298ce5f3da262ab95467ad9447e1d135c19e6bee076c1e609ac0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModelPalmConfig]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73c28a4c2d20ebe832ef8c074f34a63ad625a98c356245ceb0c84e30734470f9(
    *,
    description: typing.Optional[builtins.str] = None,
    display_name: typing.Optional[builtins.str] = None,
    docs: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1041c547de21329bba69276c7bb6aa52c1f5d99b930b7a5254f897ab5b9921b8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d81b8e71a8f495032360f73ffd5ab08e82ca710b3adcf5596c8a0200998bcfc(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a447109ea4c8b2218f4fc5e355fcdd364b2c8c6b7406201b65ac0037358dc2a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fdcb495cd0892238dcffc4c1da910f1029a41df12c7087b3e5ad883231bdd0c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fb2e667e05e8ff7e0d386919d88ef9c038c4ea3773c0b4ec93c123060deebd4(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71e18d3862f5bb903a3f2efc2a384fefccb2ce3b70adbbdcc65505d940df37a9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModel]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a092dbd41137602daeeb8b32527887caf9c9f5c1dcf54b1d8975eec827119941(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__267532d195d28b67a45b1dce7af7ce5248e5cac805c9d1e874631e642c84521e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e79d29e096f0717baed14350bd8cbfb79bc2ad84ed3c428a31c8feee1979fbea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0a40422568f5563275f68e2044dee1367e3075aa7f22bfd5e70b521e20c4bfb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b74d196e81469c58d267349512210eaab28ad0839b38a67eb4ad7b77fa6808d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__540f4e761653f935f2fba786f6454e2c0c1a6732e78b9882020c68a1e6006011(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModel]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a095249799bd1c3f0fafc01bc58f2ee0d5e91838caf902ae8a3cbb11b10e37e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4edbc22a2d9361e39f53801336c1c6e99dfcd045c9dc6376c1cb6bc2e6dfcea(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__890abe1e15c535e1a4f55061c180a69cfc2888ffcb360f3a213d58f052039e9c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99b95cd236bfff445e0ae50be443c3d240d1293eb1cbe2403c5558197cac125b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7aa306d34f0bdd2462d6a5bae0346aae8272546a78957d6a4f12b0f75391c6b2(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d43e63168e2335d90fd51165d53fa7923fc82bf58e9e3c195d0682966e3f8216(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedEntities]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe58e0f973da9541f1ca187a69ff7088242e4c066a0e0c02254b20dbd08026c7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29a99d15f3bd8d0bdbd9ebac03be0cff08e44d16f86a6f6c341edc07db372aa1(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesExternalModel, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aaf991d3333817e2bb3659f9514d0876c712d3dd0cff47fa5ad604470ec50bad(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfigServedEntitiesFoundationModel, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__584af6c4fe038caa5aa35f7bdc48c83e43c8b2a53b7e6ab8532e220fa455dfaf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__865be2e725fbf65f451984dc9ed5435e44ca83317e63bf28775ebe9cda2e99d2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf3c81f2477ca0eacf2f1770bfd5913a4523a9a357eb13f0ba0deb45dbe8e40b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__383ce28bb3a0e1e535979e7ff792b1dc860abcd59ebdc8b044089278cf085414(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedEntities]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45a6a809139818fedba1dd3787a8dcc33ed004c183ccd23644ffbc0730dfa2f9(
    *,
    model_name: typing.Optional[builtins.str] = None,
    model_version: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1db026eedc70e7dc1c0f5cbbc81221f52c9ac2f19a5cc93606147ff10cfe797(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5cf0b40860d4edef5a67574a7e176bb0692b6918829399e71e4383082e649cc(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5298a2568d60d6c4e6f8208c7b1bd2adaaa4b6f9bf6467d4696ec4ac40ef072(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c6e3d3c05c0402177023b3a1159d6585e87ed96b725b57357ba46feee931f97(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d6529469aed9c1855f890f0485b84518b3466dfadfdc075ceefebbaa10b8644(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31d685bc48b53d7db4027b048cb9f615183aaf15324c659e6b9d5bbbbac1f981(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsConfigServedModels]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc886b22360a0bbeae0ea45af24cf8b777450eb75afe33da3fcee830a030c67c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a535d223fc02611d7f9f691a762b4533318cf1d354091ffaba62363cd9e7ae1f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50d28ba8e15ffbe323c25158b078653b197cfe7716ed9acfb9fbe48f821af7ff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f60d625a274c101f6188bca7ccb8c6b4d89001e63f8938267c088d7ef34b149(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60415b969e479732211f3e37813fa654e579da64dd5571ac6843dfc8ce01e2a6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsConfigServedModels]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89d77da8e515a476594c37eb5265ed936a10f9d99beb5cb2c188dd61585f000f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d0937f14440ada63348c63b95fd2beba378f537657a54e513e99781535c7c98(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79db4ae2aded3d9bc4e3086d2cc5e883043ecb518ffc0e6e49ce8893943fd63e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13a6f7ba1ce46ec9cd81cc07573b24b4ba46bd00459fa98464f71010976c8175(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__230e4877de58cd4b28ff093c1e76062baef894909c94ea4421cfb49b9d585279(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0598eb97fe3abd907285ca7017ffc13dd1647486f4b8bb4391c07755b9e828ec(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpoints]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54f1966ce9888f8573cda2c5a69c534c6092af6c480a88d3ab8d97b148ef809b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f447957ab90f0060383937d407b1602f6ae95c2ff89781667142056622aaaca6(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsAiGateway, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5a526fbe6682245ccd4fae8c739b7fd1fa4b2528adbb82bc6818a286bd430a2(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsConfig, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cd77ecf746774805cb34649c9c76ea5bffe4505d1000fe2fbc85977d15f875e(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsState, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__887df617ecba8ffdb3b8767ebaed84b5903c997c3a1e7809275507bd6098a152(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksServingEndpointsEndpointsTags, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69bbe42858fb6743b6e8d910d10e0e173a588bcd573fff41abb38261225485c1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a77bfd5b9733e2bb04b8703d104931951de9ec6f9e55aa806ad14d15032ebb75(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd846588ca1a0aad984aaaa7860c13953f8c62920f33685ebb8d877805738099(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e26783e996b88eb94b02e55294f175d038c1cca14895e8ea1bba86c9deda0cb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc119a6c78e7d338509aba37600b9f98936701b7d2ead59e2ea49fe1f12213b1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0f9e0f24d9b84421c82113969becccd0e92ae924b7e374f8e51f9aedc2d41c5(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81f20cad7042b1f016d3c4659f92eeaacba3395a1c3c550b331bc834c51c0a08(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4bc43fcf94ad9d449dd5e51ee33e11c65032a86366a827cd45aa9655379debaf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce00eb6c6379bc864928977ee41bf26eddb6e9f1160e6cbe75891a7416a61369(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d698ddbe7350f3fa66cdcc2520caec8b71bfa2d06541a6d6774a035033c858a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpoints]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e86de07b39fcb30b2b39f2935d7e7f6ddcb3eea53b46a921a54c8bf9efb316e1(
    *,
    config_update: typing.Optional[builtins.str] = None,
    ready: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__184d1a6b4dc0d83c70693c5405dc39b85ebbd1a959478e90beaa7dddc19f9fb2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50dfa7f1e90a093047b28bd804f717a657c1bcdb3b696e3671e08fe22db0d36e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9d5a3d71fcfa2b7b14c6eeadf19541b419de6e3dd1f1d8b65488c06d0259eb6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2415586cef3807ce818f846c83d3f5cf04b173f6553f07d2a7e19459e6a942c2(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ffe88cced1ec5f203ce4518ea976614bda5b4012a49e47080258e881a110d93(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90fd8ad89cafee7160fb8fa05d89ccb72039e22876cce3a775dd69789c5fe1df(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsState]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3df0451da3a748bec5a0e2ab735ff62ede06c927774bb61045f0d5456f040b11(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f7173b96a0188906d84b326fe1671461a10bd761d53a04a5b902ddb41c295de(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8869424209c014c1910a9493195d0bb357a92387bd140c6815cf191864ffa8c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8554442bf613d10faaf674203dda5e2643edcbf2b9ee20eda7af7287b85f1a7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsState]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9c77ad665dfdceab12fc459a1bbaf3b5d9cd386614821b74c90887914265b25(
    *,
    key: builtins.str,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4660107dd093100a8d6f9ae10368da85edcc73441856eda68e1b0b134caf157e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e85fd6fd17f0724e4e4552bb8135badb473974edb768467043d523701b34e35f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d3100c790d1f7876bbe5ddea6da78e51592ee68dce254fd45906c2cbabf9b06(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78130d8276f7707183d3c639f3d16aa2264ccf9fd152ac568a5d576d3f3428db(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f084c13c755517d325889c0da81f8c2c0ff6474b9411f4e2ab68d92855a3342(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f579f51c20fc85b7f478c121c37037471b1eec110f1d0c5cb9acec6c4c437807(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksServingEndpointsEndpointsTags]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8fcc3d153ec43269fbea169ca811955f4018a8056e579c12c36cb1f994b1dca(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d2e1c8e94de5fd78f781a9392e5bb1e8d09328f8704ca1f6d53ed592b1771e3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9119b11d96f5034b0f0d8bdb69ac02e1e10c3a2c93d797d74f16f08a97dd0fc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eacbfa9fdaeb6c4df650d96d237d402033e301e0747c43340ec22768e135919f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksServingEndpointsEndpointsTags]],
) -> None:
    """Type checking stubs"""
    pass
