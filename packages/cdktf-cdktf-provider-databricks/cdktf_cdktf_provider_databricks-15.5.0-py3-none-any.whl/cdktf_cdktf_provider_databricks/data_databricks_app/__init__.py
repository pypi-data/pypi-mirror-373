r'''
# `data_databricks_app`

Refer to the Terraform Registry for docs: [`data_databricks_app`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app).
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


class DataDatabricksApp(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksApp",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app databricks_app}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app databricks_app} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#name DataDatabricksApp#name}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f0ce022004568ff5e253109396eece8a5fbd277f2a640530db20fd3555f6834)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataDatabricksAppConfig(
            name=name,
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
        '''Generates CDKTF code for importing a DataDatabricksApp resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDatabricksApp to import.
        :param import_from_id: The id of the existing DataDatabricksApp that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDatabricksApp to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b673f1de1f6da52cfb1b5896457971a4bec9ac2721f0d3b2351ca4d5117146e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

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
    @jsii.member(jsii_name="app")
    def app(self) -> "DataDatabricksAppAppOutputReference":
        return typing.cast("DataDatabricksAppAppOutputReference", jsii.get(self, "app"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__3feef38a02de41c08393b96e84868d66cc6770ca3489ebc29e3c90273e99c43d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppApp",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "budget_policy_id": "budgetPolicyId",
        "description": "description",
        "resources": "resources",
        "user_api_scopes": "userApiScopes",
    },
)
class DataDatabricksAppApp:
    def __init__(
        self,
        *,
        name: builtins.str,
        budget_policy_id: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        resources: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksAppAppResources", typing.Dict[builtins.str, typing.Any]]]]] = None,
        user_api_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#name DataDatabricksApp#name}.
        :param budget_policy_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#budget_policy_id DataDatabricksApp#budget_policy_id}.
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#description DataDatabricksApp#description}.
        :param resources: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#resources DataDatabricksApp#resources}.
        :param user_api_scopes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#user_api_scopes DataDatabricksApp#user_api_scopes}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43e4670df0b4e95281aa8f15f8d6f1b643ae427b77323aa965560d3c5b0f4e84)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument budget_policy_id", value=budget_policy_id, expected_type=type_hints["budget_policy_id"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument resources", value=resources, expected_type=type_hints["resources"])
            check_type(argname="argument user_api_scopes", value=user_api_scopes, expected_type=type_hints["user_api_scopes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if budget_policy_id is not None:
            self._values["budget_policy_id"] = budget_policy_id
        if description is not None:
            self._values["description"] = description
        if resources is not None:
            self._values["resources"] = resources
        if user_api_scopes is not None:
            self._values["user_api_scopes"] = user_api_scopes

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#name DataDatabricksApp#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def budget_policy_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#budget_policy_id DataDatabricksApp#budget_policy_id}.'''
        result = self._values.get("budget_policy_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#description DataDatabricksApp#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resources(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksAppAppResources"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#resources DataDatabricksApp#resources}.'''
        result = self._values.get("resources")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksAppAppResources"]]], result)

    @builtins.property
    def user_api_scopes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#user_api_scopes DataDatabricksApp#user_api_scopes}.'''
        result = self._values.get("user_api_scopes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppApp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppActiveDeployment",
    jsii_struct_bases=[],
    name_mapping={
        "deployment_id": "deploymentId",
        "mode": "mode",
        "source_code_path": "sourceCodePath",
    },
)
class DataDatabricksAppAppActiveDeployment:
    def __init__(
        self,
        *,
        deployment_id: typing.Optional[builtins.str] = None,
        mode: typing.Optional[builtins.str] = None,
        source_code_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param deployment_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#deployment_id DataDatabricksApp#deployment_id}.
        :param mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#mode DataDatabricksApp#mode}.
        :param source_code_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#source_code_path DataDatabricksApp#source_code_path}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07f4711583806e7694ce67324f7c2a7d0e6a7e02d3452b53695821d7328dff9f)
            check_type(argname="argument deployment_id", value=deployment_id, expected_type=type_hints["deployment_id"])
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
            check_type(argname="argument source_code_path", value=source_code_path, expected_type=type_hints["source_code_path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if deployment_id is not None:
            self._values["deployment_id"] = deployment_id
        if mode is not None:
            self._values["mode"] = mode
        if source_code_path is not None:
            self._values["source_code_path"] = source_code_path

    @builtins.property
    def deployment_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#deployment_id DataDatabricksApp#deployment_id}.'''
        result = self._values.get("deployment_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#mode DataDatabricksApp#mode}.'''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_code_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#source_code_path DataDatabricksApp#source_code_path}.'''
        result = self._values.get("source_code_path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppAppActiveDeployment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppActiveDeploymentDeploymentArtifacts",
    jsii_struct_bases=[],
    name_mapping={"source_code_path": "sourceCodePath"},
)
class DataDatabricksAppAppActiveDeploymentDeploymentArtifacts:
    def __init__(
        self,
        *,
        source_code_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param source_code_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#source_code_path DataDatabricksApp#source_code_path}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67345022ac46cf2ae5a669c5b6d75f1c9a37433a26a699dbae27a966c9c7b8d1)
            check_type(argname="argument source_code_path", value=source_code_path, expected_type=type_hints["source_code_path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if source_code_path is not None:
            self._values["source_code_path"] = source_code_path

    @builtins.property
    def source_code_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#source_code_path DataDatabricksApp#source_code_path}.'''
        result = self._values.get("source_code_path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppAppActiveDeploymentDeploymentArtifacts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppAppActiveDeploymentDeploymentArtifactsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppActiveDeploymentDeploymentArtifactsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__62e1076106fd372f777193eb77b562771a2cf5e59f0b9c44b82090c9dca57b63)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetSourceCodePath")
    def reset_source_code_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceCodePath", []))

    @builtins.property
    @jsii.member(jsii_name="sourceCodePathInput")
    def source_code_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceCodePathInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceCodePath")
    def source_code_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceCodePath"))

    @source_code_path.setter
    def source_code_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d38debada89b38b0668887b66db8160df281fdbe4f15bdc27f41e4cb8d8a1bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceCodePath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksAppAppActiveDeploymentDeploymentArtifacts]:
        return typing.cast(typing.Optional[DataDatabricksAppAppActiveDeploymentDeploymentArtifacts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksAppAppActiveDeploymentDeploymentArtifacts],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdc9ddcb553e377c0ce53eff68168574f7676315cdcb807c520b95d03e6d4174)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAppAppActiveDeploymentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppActiveDeploymentOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1dac4fa7695cb41f42af1ead02f367fa98308d700c6307467a1fd6eec46138e4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDeploymentId")
    def reset_deployment_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeploymentId", []))

    @jsii.member(jsii_name="resetMode")
    def reset_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMode", []))

    @jsii.member(jsii_name="resetSourceCodePath")
    def reset_source_code_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceCodePath", []))

    @builtins.property
    @jsii.member(jsii_name="createTime")
    def create_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createTime"))

    @builtins.property
    @jsii.member(jsii_name="creator")
    def creator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creator"))

    @builtins.property
    @jsii.member(jsii_name="deploymentArtifacts")
    def deployment_artifacts(
        self,
    ) -> DataDatabricksAppAppActiveDeploymentDeploymentArtifactsOutputReference:
        return typing.cast(DataDatabricksAppAppActiveDeploymentDeploymentArtifactsOutputReference, jsii.get(self, "deploymentArtifacts"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> "DataDatabricksAppAppActiveDeploymentStatusOutputReference":
        return typing.cast("DataDatabricksAppAppActiveDeploymentStatusOutputReference", jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="updateTime")
    def update_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updateTime"))

    @builtins.property
    @jsii.member(jsii_name="deploymentIdInput")
    def deployment_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deploymentIdInput"))

    @builtins.property
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modeInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceCodePathInput")
    def source_code_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceCodePathInput"))

    @builtins.property
    @jsii.member(jsii_name="deploymentId")
    def deployment_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deploymentId"))

    @deployment_id.setter
    def deployment_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e34ad3d2b69cb9e973430dbb810b78cd108ce6fd0b74f910a1d8e0a26a2efaa2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deploymentId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d73d49aeb62dcb6d418177bd3ae0bbc72306c9ed8f1f91404bdc15012752ceba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceCodePath")
    def source_code_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceCodePath"))

    @source_code_path.setter
    def source_code_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f1ebaeed7531b8d9ec378fd1094d2ae43ce6af3d094465db74e1e3d7f38396a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceCodePath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataDatabricksAppAppActiveDeployment]:
        return typing.cast(typing.Optional[DataDatabricksAppAppActiveDeployment], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksAppAppActiveDeployment],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c7b189a795f6f77480ea5c93471e17d540da917c4e32db05d6430288f86a480)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppActiveDeploymentStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksAppAppActiveDeploymentStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppAppActiveDeploymentStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppAppActiveDeploymentStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppActiveDeploymentStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bd0b4a396fe5c01b468bf7cd50946d4912d7be0c694b38fff952af8db4d51761)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="message")
    def message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "message"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksAppAppActiveDeploymentStatus]:
        return typing.cast(typing.Optional[DataDatabricksAppAppActiveDeploymentStatus], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksAppAppActiveDeploymentStatus],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffadc2e787f8507ea0afa102d9a601793363a09e658aae305bfd8b7a46e5b2d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppAppStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksAppAppAppStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppAppAppStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppAppAppStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppAppStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__509853b1ce6017a7ca645c0a1f122efbd3b133bd6dc4c7f6accad30f91ef18bb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="message")
    def message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "message"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataDatabricksAppAppAppStatus]:
        return typing.cast(typing.Optional[DataDatabricksAppAppAppStatus], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksAppAppAppStatus],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e7fafebeb2f7b70dabec078db9455f284bca4370668c050cb22c987100d4daa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppComputeStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksAppAppComputeStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppAppComputeStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppAppComputeStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppComputeStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7c36c8b9146c54ef83ca29249df0646c537763ec5678109606844e60b8d53c3d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="message")
    def message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "message"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataDatabricksAppAppComputeStatus]:
        return typing.cast(typing.Optional[DataDatabricksAppAppComputeStatus], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksAppAppComputeStatus],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__173c1bb6401f29596e88214f54adca1899fc7f57031bdc8e446d239fb39e5bd5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAppAppOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7f3b2518db223e4e5310604754a41f3d739d6969131eb9db28ba824cf84d9e9e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putResources")
    def put_resources(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksAppAppResources", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc070e6aa75826d1aee422a08662e32b3d2e7a2d33197cbf740ffca295f7f4d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putResources", [value]))

    @jsii.member(jsii_name="resetBudgetPolicyId")
    def reset_budget_policy_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBudgetPolicyId", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetResources")
    def reset_resources(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResources", []))

    @jsii.member(jsii_name="resetUserApiScopes")
    def reset_user_api_scopes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserApiScopes", []))

    @builtins.property
    @jsii.member(jsii_name="activeDeployment")
    def active_deployment(self) -> DataDatabricksAppAppActiveDeploymentOutputReference:
        return typing.cast(DataDatabricksAppAppActiveDeploymentOutputReference, jsii.get(self, "activeDeployment"))

    @builtins.property
    @jsii.member(jsii_name="appStatus")
    def app_status(self) -> DataDatabricksAppAppAppStatusOutputReference:
        return typing.cast(DataDatabricksAppAppAppStatusOutputReference, jsii.get(self, "appStatus"))

    @builtins.property
    @jsii.member(jsii_name="computeStatus")
    def compute_status(self) -> DataDatabricksAppAppComputeStatusOutputReference:
        return typing.cast(DataDatabricksAppAppComputeStatusOutputReference, jsii.get(self, "computeStatus"))

    @builtins.property
    @jsii.member(jsii_name="createTime")
    def create_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createTime"))

    @builtins.property
    @jsii.member(jsii_name="creator")
    def creator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creator"))

    @builtins.property
    @jsii.member(jsii_name="defaultSourceCodePath")
    def default_source_code_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultSourceCodePath"))

    @builtins.property
    @jsii.member(jsii_name="effectiveBudgetPolicyId")
    def effective_budget_policy_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "effectiveBudgetPolicyId"))

    @builtins.property
    @jsii.member(jsii_name="effectiveUserApiScopes")
    def effective_user_api_scopes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "effectiveUserApiScopes"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="oauth2AppClientId")
    def oauth2_app_client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oauth2AppClientId"))

    @builtins.property
    @jsii.member(jsii_name="oauth2AppIntegrationId")
    def oauth2_app_integration_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oauth2AppIntegrationId"))

    @builtins.property
    @jsii.member(jsii_name="pendingDeployment")
    def pending_deployment(
        self,
    ) -> "DataDatabricksAppAppPendingDeploymentOutputReference":
        return typing.cast("DataDatabricksAppAppPendingDeploymentOutputReference", jsii.get(self, "pendingDeployment"))

    @builtins.property
    @jsii.member(jsii_name="resources")
    def resources(self) -> "DataDatabricksAppAppResourcesList":
        return typing.cast("DataDatabricksAppAppResourcesList", jsii.get(self, "resources"))

    @builtins.property
    @jsii.member(jsii_name="servicePrincipalClientId")
    def service_principal_client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "servicePrincipalClientId"))

    @builtins.property
    @jsii.member(jsii_name="servicePrincipalId")
    def service_principal_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "servicePrincipalId"))

    @builtins.property
    @jsii.member(jsii_name="servicePrincipalName")
    def service_principal_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "servicePrincipalName"))

    @builtins.property
    @jsii.member(jsii_name="updater")
    def updater(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updater"))

    @builtins.property
    @jsii.member(jsii_name="updateTime")
    def update_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updateTime"))

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property
    @jsii.member(jsii_name="budgetPolicyIdInput")
    def budget_policy_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "budgetPolicyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="resourcesInput")
    def resources_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksAppAppResources"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksAppAppResources"]]], jsii.get(self, "resourcesInput"))

    @builtins.property
    @jsii.member(jsii_name="userApiScopesInput")
    def user_api_scopes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "userApiScopesInput"))

    @builtins.property
    @jsii.member(jsii_name="budgetPolicyId")
    def budget_policy_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "budgetPolicyId"))

    @budget_policy_id.setter
    def budget_policy_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa61422038334aa5213e5957b0db6446741bc9b4d374fa67ab9fb89a112f6b62)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "budgetPolicyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cca80ecf9d60cbb265200b55aab089649563a7d918329e065bd5133e6e14b3e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa9d7f845ea60a6e070a7c292af99bbabd03ccf2ca81dc4e8ab3b5229976af04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userApiScopes")
    def user_api_scopes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "userApiScopes"))

    @user_api_scopes.setter
    def user_api_scopes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc3de84740c667d0f99021c6789703c208263ae4561b3149d40d0ac3733f003c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userApiScopes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataDatabricksAppApp]:
        return typing.cast(typing.Optional[DataDatabricksAppApp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[DataDatabricksAppApp]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5c91a7ee6b91ad3f5ac2db42b0c1d027f1355be8ec46cc3d1818873072dc89f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppPendingDeployment",
    jsii_struct_bases=[],
    name_mapping={
        "deployment_id": "deploymentId",
        "mode": "mode",
        "source_code_path": "sourceCodePath",
    },
)
class DataDatabricksAppAppPendingDeployment:
    def __init__(
        self,
        *,
        deployment_id: typing.Optional[builtins.str] = None,
        mode: typing.Optional[builtins.str] = None,
        source_code_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param deployment_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#deployment_id DataDatabricksApp#deployment_id}.
        :param mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#mode DataDatabricksApp#mode}.
        :param source_code_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#source_code_path DataDatabricksApp#source_code_path}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ca7d1c1116c3c252ff1688989072eac86a7770c82795c695ec6b44ca12260fc)
            check_type(argname="argument deployment_id", value=deployment_id, expected_type=type_hints["deployment_id"])
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
            check_type(argname="argument source_code_path", value=source_code_path, expected_type=type_hints["source_code_path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if deployment_id is not None:
            self._values["deployment_id"] = deployment_id
        if mode is not None:
            self._values["mode"] = mode
        if source_code_path is not None:
            self._values["source_code_path"] = source_code_path

    @builtins.property
    def deployment_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#deployment_id DataDatabricksApp#deployment_id}.'''
        result = self._values.get("deployment_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#mode DataDatabricksApp#mode}.'''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_code_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#source_code_path DataDatabricksApp#source_code_path}.'''
        result = self._values.get("source_code_path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppAppPendingDeployment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppPendingDeploymentDeploymentArtifacts",
    jsii_struct_bases=[],
    name_mapping={"source_code_path": "sourceCodePath"},
)
class DataDatabricksAppAppPendingDeploymentDeploymentArtifacts:
    def __init__(
        self,
        *,
        source_code_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param source_code_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#source_code_path DataDatabricksApp#source_code_path}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c130a3c3872f1b972cd7c2ffb16258f15cacc2df6177e19c048fb3bd0b7c176e)
            check_type(argname="argument source_code_path", value=source_code_path, expected_type=type_hints["source_code_path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if source_code_path is not None:
            self._values["source_code_path"] = source_code_path

    @builtins.property
    def source_code_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#source_code_path DataDatabricksApp#source_code_path}.'''
        result = self._values.get("source_code_path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppAppPendingDeploymentDeploymentArtifacts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppAppPendingDeploymentDeploymentArtifactsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppPendingDeploymentDeploymentArtifactsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__30dd973871602a1c961d0b2820bf9fec2593600bc338c7a4e09debc399c3edcc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetSourceCodePath")
    def reset_source_code_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceCodePath", []))

    @builtins.property
    @jsii.member(jsii_name="sourceCodePathInput")
    def source_code_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceCodePathInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceCodePath")
    def source_code_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceCodePath"))

    @source_code_path.setter
    def source_code_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8799bafbcc0228941be5c946e23c9046b60e247dfddc8fd8b85898555fcfe0fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceCodePath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksAppAppPendingDeploymentDeploymentArtifacts]:
        return typing.cast(typing.Optional[DataDatabricksAppAppPendingDeploymentDeploymentArtifacts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksAppAppPendingDeploymentDeploymentArtifacts],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4305b73444632d7f0a991a51f52fe4a7c45f21842757682a96ecb60da2ea666)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAppAppPendingDeploymentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppPendingDeploymentOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__258f8b6a3962797d0f6453b6d7155edad16a1e8984c76eb55fdf3093dcb72b02)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDeploymentId")
    def reset_deployment_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeploymentId", []))

    @jsii.member(jsii_name="resetMode")
    def reset_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMode", []))

    @jsii.member(jsii_name="resetSourceCodePath")
    def reset_source_code_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceCodePath", []))

    @builtins.property
    @jsii.member(jsii_name="createTime")
    def create_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createTime"))

    @builtins.property
    @jsii.member(jsii_name="creator")
    def creator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creator"))

    @builtins.property
    @jsii.member(jsii_name="deploymentArtifacts")
    def deployment_artifacts(
        self,
    ) -> DataDatabricksAppAppPendingDeploymentDeploymentArtifactsOutputReference:
        return typing.cast(DataDatabricksAppAppPendingDeploymentDeploymentArtifactsOutputReference, jsii.get(self, "deploymentArtifacts"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> "DataDatabricksAppAppPendingDeploymentStatusOutputReference":
        return typing.cast("DataDatabricksAppAppPendingDeploymentStatusOutputReference", jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="updateTime")
    def update_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updateTime"))

    @builtins.property
    @jsii.member(jsii_name="deploymentIdInput")
    def deployment_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deploymentIdInput"))

    @builtins.property
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modeInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceCodePathInput")
    def source_code_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceCodePathInput"))

    @builtins.property
    @jsii.member(jsii_name="deploymentId")
    def deployment_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deploymentId"))

    @deployment_id.setter
    def deployment_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29a77a6980dfe55b86e43f2ffd7b4c816de0e8bcb509bff1f73f21a4b4cdbb4a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deploymentId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9347059a1424f7fcee0c57489543148a5838c3a9508c81df98e0cb0cd05750f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceCodePath")
    def source_code_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceCodePath"))

    @source_code_path.setter
    def source_code_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf4d25275aa40728f27863a6a8cf1ef20ab65b66cdd4e38621319450be975805)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceCodePath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataDatabricksAppAppPendingDeployment]:
        return typing.cast(typing.Optional[DataDatabricksAppAppPendingDeployment], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksAppAppPendingDeployment],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee3d243c9fbaa17c10df37536f858413721fa63de23aa0a722c8ef31f9f5db75)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppPendingDeploymentStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksAppAppPendingDeploymentStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppAppPendingDeploymentStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppAppPendingDeploymentStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppPendingDeploymentStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bb6084681e1d687edf76cbe69ead2cc45fdbdf1d1e29600f5a5463469a50b544)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="message")
    def message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "message"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksAppAppPendingDeploymentStatus]:
        return typing.cast(typing.Optional[DataDatabricksAppAppPendingDeploymentStatus], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksAppAppPendingDeploymentStatus],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__089ad5851b337d08235f55e4f373d7c91a0793745d553732abbb3093173948bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppResources",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "database": "database",
        "description": "description",
        "job": "job",
        "secret": "secret",
        "serving_endpoint": "servingEndpoint",
        "sql_warehouse": "sqlWarehouse",
        "uc_securable": "ucSecurable",
    },
)
class DataDatabricksAppAppResources:
    def __init__(
        self,
        *,
        name: builtins.str,
        database: typing.Optional[typing.Union["DataDatabricksAppAppResourcesDatabase", typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        job: typing.Optional[typing.Union["DataDatabricksAppAppResourcesJob", typing.Dict[builtins.str, typing.Any]]] = None,
        secret: typing.Optional[typing.Union["DataDatabricksAppAppResourcesSecret", typing.Dict[builtins.str, typing.Any]]] = None,
        serving_endpoint: typing.Optional[typing.Union["DataDatabricksAppAppResourcesServingEndpoint", typing.Dict[builtins.str, typing.Any]]] = None,
        sql_warehouse: typing.Optional[typing.Union["DataDatabricksAppAppResourcesSqlWarehouse", typing.Dict[builtins.str, typing.Any]]] = None,
        uc_securable: typing.Optional[typing.Union["DataDatabricksAppAppResourcesUcSecurable", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#name DataDatabricksApp#name}.
        :param database: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#database DataDatabricksApp#database}.
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#description DataDatabricksApp#description}.
        :param job: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#job DataDatabricksApp#job}.
        :param secret: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#secret DataDatabricksApp#secret}.
        :param serving_endpoint: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#serving_endpoint DataDatabricksApp#serving_endpoint}.
        :param sql_warehouse: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#sql_warehouse DataDatabricksApp#sql_warehouse}.
        :param uc_securable: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#uc_securable DataDatabricksApp#uc_securable}.
        '''
        if isinstance(database, dict):
            database = DataDatabricksAppAppResourcesDatabase(**database)
        if isinstance(job, dict):
            job = DataDatabricksAppAppResourcesJob(**job)
        if isinstance(secret, dict):
            secret = DataDatabricksAppAppResourcesSecret(**secret)
        if isinstance(serving_endpoint, dict):
            serving_endpoint = DataDatabricksAppAppResourcesServingEndpoint(**serving_endpoint)
        if isinstance(sql_warehouse, dict):
            sql_warehouse = DataDatabricksAppAppResourcesSqlWarehouse(**sql_warehouse)
        if isinstance(uc_securable, dict):
            uc_securable = DataDatabricksAppAppResourcesUcSecurable(**uc_securable)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0fb10be780cec5a535ea4d8b83172f041293d530254765ed0a933fa61245374)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument database", value=database, expected_type=type_hints["database"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument job", value=job, expected_type=type_hints["job"])
            check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
            check_type(argname="argument serving_endpoint", value=serving_endpoint, expected_type=type_hints["serving_endpoint"])
            check_type(argname="argument sql_warehouse", value=sql_warehouse, expected_type=type_hints["sql_warehouse"])
            check_type(argname="argument uc_securable", value=uc_securable, expected_type=type_hints["uc_securable"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if database is not None:
            self._values["database"] = database
        if description is not None:
            self._values["description"] = description
        if job is not None:
            self._values["job"] = job
        if secret is not None:
            self._values["secret"] = secret
        if serving_endpoint is not None:
            self._values["serving_endpoint"] = serving_endpoint
        if sql_warehouse is not None:
            self._values["sql_warehouse"] = sql_warehouse
        if uc_securable is not None:
            self._values["uc_securable"] = uc_securable

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#name DataDatabricksApp#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def database(self) -> typing.Optional["DataDatabricksAppAppResourcesDatabase"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#database DataDatabricksApp#database}.'''
        result = self._values.get("database")
        return typing.cast(typing.Optional["DataDatabricksAppAppResourcesDatabase"], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#description DataDatabricksApp#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def job(self) -> typing.Optional["DataDatabricksAppAppResourcesJob"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#job DataDatabricksApp#job}.'''
        result = self._values.get("job")
        return typing.cast(typing.Optional["DataDatabricksAppAppResourcesJob"], result)

    @builtins.property
    def secret(self) -> typing.Optional["DataDatabricksAppAppResourcesSecret"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#secret DataDatabricksApp#secret}.'''
        result = self._values.get("secret")
        return typing.cast(typing.Optional["DataDatabricksAppAppResourcesSecret"], result)

    @builtins.property
    def serving_endpoint(
        self,
    ) -> typing.Optional["DataDatabricksAppAppResourcesServingEndpoint"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#serving_endpoint DataDatabricksApp#serving_endpoint}.'''
        result = self._values.get("serving_endpoint")
        return typing.cast(typing.Optional["DataDatabricksAppAppResourcesServingEndpoint"], result)

    @builtins.property
    def sql_warehouse(
        self,
    ) -> typing.Optional["DataDatabricksAppAppResourcesSqlWarehouse"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#sql_warehouse DataDatabricksApp#sql_warehouse}.'''
        result = self._values.get("sql_warehouse")
        return typing.cast(typing.Optional["DataDatabricksAppAppResourcesSqlWarehouse"], result)

    @builtins.property
    def uc_securable(
        self,
    ) -> typing.Optional["DataDatabricksAppAppResourcesUcSecurable"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#uc_securable DataDatabricksApp#uc_securable}.'''
        result = self._values.get("uc_securable")
        return typing.cast(typing.Optional["DataDatabricksAppAppResourcesUcSecurable"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppAppResources(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppResourcesDatabase",
    jsii_struct_bases=[],
    name_mapping={
        "database_name": "databaseName",
        "instance_name": "instanceName",
        "permission": "permission",
    },
)
class DataDatabricksAppAppResourcesDatabase:
    def __init__(
        self,
        *,
        database_name: builtins.str,
        instance_name: builtins.str,
        permission: builtins.str,
    ) -> None:
        '''
        :param database_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#database_name DataDatabricksApp#database_name}.
        :param instance_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#instance_name DataDatabricksApp#instance_name}.
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#permission DataDatabricksApp#permission}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__565136257b2bfbca0f1e132925c559e0416220b54d8153359efb158315a31b20)
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument instance_name", value=instance_name, expected_type=type_hints["instance_name"])
            check_type(argname="argument permission", value=permission, expected_type=type_hints["permission"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "database_name": database_name,
            "instance_name": instance_name,
            "permission": permission,
        }

    @builtins.property
    def database_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#database_name DataDatabricksApp#database_name}.'''
        result = self._values.get("database_name")
        assert result is not None, "Required property 'database_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instance_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#instance_name DataDatabricksApp#instance_name}.'''
        result = self._values.get("instance_name")
        assert result is not None, "Required property 'instance_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def permission(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#permission DataDatabricksApp#permission}.'''
        result = self._values.get("permission")
        assert result is not None, "Required property 'permission' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppAppResourcesDatabase(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppAppResourcesDatabaseOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppResourcesDatabaseOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dc788242fd17584e4f2fda0478c8545fac1b9a095b94fbd1999812f307ad72d0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="databaseNameInput")
    def database_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseNameInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceNameInput")
    def instance_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceNameInput"))

    @builtins.property
    @jsii.member(jsii_name="permissionInput")
    def permission_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "permissionInput"))

    @builtins.property
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "databaseName"))

    @database_name.setter
    def database_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ce962f73fd0cfeacc0c7c46a544941b3b21abf12eb17bd897540ba39630f75d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "databaseName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instanceName")
    def instance_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceName"))

    @instance_name.setter
    def instance_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__985c1d6a197687d708acafe8b8af16ef2962b28bd75f12f971866ac9e4f3a792)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="permission")
    def permission(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permission"))

    @permission.setter
    def permission(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17ca82adb4759a7f7b00f2f1d7fbe6c1fbe9d2224df6157b5a6b54e7e1dcccee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permission", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResourcesDatabase]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResourcesDatabase]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResourcesDatabase]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b24ea27058efad8054803580ad9ddaa2cd89cb78f8fa4ec17082e488e4b72ff1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppResourcesJob",
    jsii_struct_bases=[],
    name_mapping={"id": "id", "permission": "permission"},
)
class DataDatabricksAppAppResourcesJob:
    def __init__(self, *, id: builtins.str, permission: builtins.str) -> None:
        '''
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#id DataDatabricksApp#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#permission DataDatabricksApp#permission}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c02726d903612396a1bb9ed10d8be76f7429b0ca6485e6f6008e3208a6858559)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument permission", value=permission, expected_type=type_hints["permission"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
            "permission": permission,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#id DataDatabricksApp#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def permission(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#permission DataDatabricksApp#permission}.'''
        result = self._values.get("permission")
        assert result is not None, "Required property 'permission' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppAppResourcesJob(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppAppResourcesJobOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppResourcesJobOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__376e6b11b0cfdebc9b1c9370c19aa7594209dd3f05c3faba7e4a98398de0fec0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="permissionInput")
    def permission_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "permissionInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0106a086afb44bb07993d7342debff44e97b8ba4fb1355739ed8c43cc372521a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="permission")
    def permission(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permission"))

    @permission.setter
    def permission(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24043cda4e4f8e305ff81edea9c7a2095fa26ec1e059b77cb9b8cdc9b2a8abeb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permission", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResourcesJob]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResourcesJob]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResourcesJob]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92e12613dd2fe06054dde0960b3b2f03415acdab43c05e950a22e25af04646fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAppAppResourcesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppResourcesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__435fa4c92211a5324bde412354a8d4bb6a84ec2f2ed600f22f898ccd8f2037c9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "DataDatabricksAppAppResourcesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__418293d3bbb8099f34f29a3d39ae9a3467c2e847d3dbaee90d03ebcbe27a31f0)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksAppAppResourcesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce4e91a2a2d4303f9d6628e6b3f99e1312dd496ea9619a329596826763675d3e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__95e5eccdb46aeb02258d7584c7bd406e6e7b1259d0ee2cc1dc7f63c18bbbf7f3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4a74b643a6730956250780b4b1e489ba154acdb5025a65059fd334b38dba7c94)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAppAppResources]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAppAppResources]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAppAppResources]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11f0c3614501fa5762f08de90594e2eaff115ba79d98a3c96bf6ac6c6e7823a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAppAppResourcesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppResourcesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__011037957b4cfae4c9b6fbc26e17a89ce17369c45425045f1abc42972416c667)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putDatabase")
    def put_database(
        self,
        *,
        database_name: builtins.str,
        instance_name: builtins.str,
        permission: builtins.str,
    ) -> None:
        '''
        :param database_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#database_name DataDatabricksApp#database_name}.
        :param instance_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#instance_name DataDatabricksApp#instance_name}.
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#permission DataDatabricksApp#permission}.
        '''
        value = DataDatabricksAppAppResourcesDatabase(
            database_name=database_name,
            instance_name=instance_name,
            permission=permission,
        )

        return typing.cast(None, jsii.invoke(self, "putDatabase", [value]))

    @jsii.member(jsii_name="putJob")
    def put_job(self, *, id: builtins.str, permission: builtins.str) -> None:
        '''
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#id DataDatabricksApp#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#permission DataDatabricksApp#permission}.
        '''
        value = DataDatabricksAppAppResourcesJob(id=id, permission=permission)

        return typing.cast(None, jsii.invoke(self, "putJob", [value]))

    @jsii.member(jsii_name="putSecret")
    def put_secret(
        self,
        *,
        key: builtins.str,
        permission: builtins.str,
        scope: builtins.str,
    ) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#key DataDatabricksApp#key}.
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#permission DataDatabricksApp#permission}.
        :param scope: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#scope DataDatabricksApp#scope}.
        '''
        value = DataDatabricksAppAppResourcesSecret(
            key=key, permission=permission, scope=scope
        )

        return typing.cast(None, jsii.invoke(self, "putSecret", [value]))

    @jsii.member(jsii_name="putServingEndpoint")
    def put_serving_endpoint(
        self,
        *,
        name: builtins.str,
        permission: builtins.str,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#name DataDatabricksApp#name}.
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#permission DataDatabricksApp#permission}.
        '''
        value = DataDatabricksAppAppResourcesServingEndpoint(
            name=name, permission=permission
        )

        return typing.cast(None, jsii.invoke(self, "putServingEndpoint", [value]))

    @jsii.member(jsii_name="putSqlWarehouse")
    def put_sql_warehouse(self, *, id: builtins.str, permission: builtins.str) -> None:
        '''
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#id DataDatabricksApp#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#permission DataDatabricksApp#permission}.
        '''
        value = DataDatabricksAppAppResourcesSqlWarehouse(id=id, permission=permission)

        return typing.cast(None, jsii.invoke(self, "putSqlWarehouse", [value]))

    @jsii.member(jsii_name="putUcSecurable")
    def put_uc_securable(
        self,
        *,
        permission: builtins.str,
        securable_full_name: builtins.str,
        securable_type: builtins.str,
    ) -> None:
        '''
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#permission DataDatabricksApp#permission}.
        :param securable_full_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#securable_full_name DataDatabricksApp#securable_full_name}.
        :param securable_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#securable_type DataDatabricksApp#securable_type}.
        '''
        value = DataDatabricksAppAppResourcesUcSecurable(
            permission=permission,
            securable_full_name=securable_full_name,
            securable_type=securable_type,
        )

        return typing.cast(None, jsii.invoke(self, "putUcSecurable", [value]))

    @jsii.member(jsii_name="resetDatabase")
    def reset_database(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatabase", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetJob")
    def reset_job(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJob", []))

    @jsii.member(jsii_name="resetSecret")
    def reset_secret(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecret", []))

    @jsii.member(jsii_name="resetServingEndpoint")
    def reset_serving_endpoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServingEndpoint", []))

    @jsii.member(jsii_name="resetSqlWarehouse")
    def reset_sql_warehouse(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSqlWarehouse", []))

    @jsii.member(jsii_name="resetUcSecurable")
    def reset_uc_securable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUcSecurable", []))

    @builtins.property
    @jsii.member(jsii_name="database")
    def database(self) -> DataDatabricksAppAppResourcesDatabaseOutputReference:
        return typing.cast(DataDatabricksAppAppResourcesDatabaseOutputReference, jsii.get(self, "database"))

    @builtins.property
    @jsii.member(jsii_name="job")
    def job(self) -> DataDatabricksAppAppResourcesJobOutputReference:
        return typing.cast(DataDatabricksAppAppResourcesJobOutputReference, jsii.get(self, "job"))

    @builtins.property
    @jsii.member(jsii_name="secret")
    def secret(self) -> "DataDatabricksAppAppResourcesSecretOutputReference":
        return typing.cast("DataDatabricksAppAppResourcesSecretOutputReference", jsii.get(self, "secret"))

    @builtins.property
    @jsii.member(jsii_name="servingEndpoint")
    def serving_endpoint(
        self,
    ) -> "DataDatabricksAppAppResourcesServingEndpointOutputReference":
        return typing.cast("DataDatabricksAppAppResourcesServingEndpointOutputReference", jsii.get(self, "servingEndpoint"))

    @builtins.property
    @jsii.member(jsii_name="sqlWarehouse")
    def sql_warehouse(
        self,
    ) -> "DataDatabricksAppAppResourcesSqlWarehouseOutputReference":
        return typing.cast("DataDatabricksAppAppResourcesSqlWarehouseOutputReference", jsii.get(self, "sqlWarehouse"))

    @builtins.property
    @jsii.member(jsii_name="ucSecurable")
    def uc_securable(self) -> "DataDatabricksAppAppResourcesUcSecurableOutputReference":
        return typing.cast("DataDatabricksAppAppResourcesUcSecurableOutputReference", jsii.get(self, "ucSecurable"))

    @builtins.property
    @jsii.member(jsii_name="databaseInput")
    def database_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResourcesDatabase]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResourcesDatabase]], jsii.get(self, "databaseInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="jobInput")
    def job_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResourcesJob]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResourcesJob]], jsii.get(self, "jobInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="secretInput")
    def secret_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAppAppResourcesSecret"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAppAppResourcesSecret"]], jsii.get(self, "secretInput"))

    @builtins.property
    @jsii.member(jsii_name="servingEndpointInput")
    def serving_endpoint_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAppAppResourcesServingEndpoint"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAppAppResourcesServingEndpoint"]], jsii.get(self, "servingEndpointInput"))

    @builtins.property
    @jsii.member(jsii_name="sqlWarehouseInput")
    def sql_warehouse_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAppAppResourcesSqlWarehouse"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAppAppResourcesSqlWarehouse"]], jsii.get(self, "sqlWarehouseInput"))

    @builtins.property
    @jsii.member(jsii_name="ucSecurableInput")
    def uc_securable_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAppAppResourcesUcSecurable"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAppAppResourcesUcSecurable"]], jsii.get(self, "ucSecurableInput"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e82fd010ea1504abfbd19ad522fb0907c5de05eb7ce9f9745f9ba43299f8490c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__604c29e8103952b0cc15f0fd0c5a8ce3c3bbf3d8cbb1d929a244215d21911985)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResources]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResources]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResources]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f00f3d017092fe113b59d34f702792fce8d7a6cea866eb8a00a2350bef25856c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppResourcesSecret",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "permission": "permission", "scope": "scope"},
)
class DataDatabricksAppAppResourcesSecret:
    def __init__(
        self,
        *,
        key: builtins.str,
        permission: builtins.str,
        scope: builtins.str,
    ) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#key DataDatabricksApp#key}.
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#permission DataDatabricksApp#permission}.
        :param scope: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#scope DataDatabricksApp#scope}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1adaba5934969ccce39731ecc93354744ecc0f77d9dda6bb7ff4d0b161f4ae3)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument permission", value=permission, expected_type=type_hints["permission"])
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
            "permission": permission,
            "scope": scope,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#key DataDatabricksApp#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def permission(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#permission DataDatabricksApp#permission}.'''
        result = self._values.get("permission")
        assert result is not None, "Required property 'permission' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def scope(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#scope DataDatabricksApp#scope}.'''
        result = self._values.get("scope")
        assert result is not None, "Required property 'scope' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppAppResourcesSecret(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppAppResourcesSecretOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppResourcesSecretOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__570b87d4aae6f61edf409be8654dd974a1346d6d6e4fefa91f6337201b0284b2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="permissionInput")
    def permission_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "permissionInput"))

    @builtins.property
    @jsii.member(jsii_name="scopeInput")
    def scope_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scopeInput"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ab4570f5a5e75f1c6ac7cb9d5f3b187d804851362515e7f56338261c4786118)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="permission")
    def permission(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permission"))

    @permission.setter
    def permission(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22fda5a3894b531ba19758c9c4e10b840d474d956caa717e3bc167f66160eccc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permission", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scope")
    def scope(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scope"))

    @scope.setter
    def scope(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__485b19f74f664f4269e153f1ed3bffdec7220e22da53ca835f5a6492bbd5e6ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scope", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResourcesSecret]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResourcesSecret]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResourcesSecret]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c2fed2141fe39ec07f4e4ebe142a42e55fbabcac167a9847782d2193d82c12a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppResourcesServingEndpoint",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "permission": "permission"},
)
class DataDatabricksAppAppResourcesServingEndpoint:
    def __init__(self, *, name: builtins.str, permission: builtins.str) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#name DataDatabricksApp#name}.
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#permission DataDatabricksApp#permission}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d828032c0f1b448dd9acc2d246e2ab1de4f358a450cc758b1ffc9eafdf38ed6)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument permission", value=permission, expected_type=type_hints["permission"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "permission": permission,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#name DataDatabricksApp#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def permission(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#permission DataDatabricksApp#permission}.'''
        result = self._values.get("permission")
        assert result is not None, "Required property 'permission' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppAppResourcesServingEndpoint(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppAppResourcesServingEndpointOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppResourcesServingEndpointOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__46d919df2eb5f0713f68e643df762b57d1c0b934554d9a2ee9f84ad88f2590f9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="permissionInput")
    def permission_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "permissionInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef63f2944564e43b903760963d6fcd959cf6ff98f4e007ac4ece2beb7983fc3d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="permission")
    def permission(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permission"))

    @permission.setter
    def permission(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c95e6faf8d4d072e6dbf38104bad9de4663d768fcb9430b49f2aba56f6ef8d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permission", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResourcesServingEndpoint]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResourcesServingEndpoint]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResourcesServingEndpoint]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e376434de71e2c722311f32644f982892386bd1c7bfae712dd71673f2071317)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppResourcesSqlWarehouse",
    jsii_struct_bases=[],
    name_mapping={"id": "id", "permission": "permission"},
)
class DataDatabricksAppAppResourcesSqlWarehouse:
    def __init__(self, *, id: builtins.str, permission: builtins.str) -> None:
        '''
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#id DataDatabricksApp#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#permission DataDatabricksApp#permission}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57a75365f026cbc494698cf4bcc9ba3f1e9ff8651b204f32bdd4001645f7d813)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument permission", value=permission, expected_type=type_hints["permission"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
            "permission": permission,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#id DataDatabricksApp#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def permission(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#permission DataDatabricksApp#permission}.'''
        result = self._values.get("permission")
        assert result is not None, "Required property 'permission' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppAppResourcesSqlWarehouse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppAppResourcesSqlWarehouseOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppResourcesSqlWarehouseOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f7ca2159dc0d54954537c6c2cdeab41af566a9e3fe97f978a3d986f0473cff41)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="permissionInput")
    def permission_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "permissionInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4162cfdfadc82aead255444a3a5bdf16c3cd5e721675872b00d9493a2b251f05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="permission")
    def permission(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permission"))

    @permission.setter
    def permission(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b205aea94685bdc2bc8cfe5c348f7531ea689f0691eb8480606e0d62198a2424)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permission", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResourcesSqlWarehouse]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResourcesSqlWarehouse]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResourcesSqlWarehouse]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__494474b238f843d871fbddcbf71a08823e0c99d0369ce8f22baa8c6e84886c9c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppResourcesUcSecurable",
    jsii_struct_bases=[],
    name_mapping={
        "permission": "permission",
        "securable_full_name": "securableFullName",
        "securable_type": "securableType",
    },
)
class DataDatabricksAppAppResourcesUcSecurable:
    def __init__(
        self,
        *,
        permission: builtins.str,
        securable_full_name: builtins.str,
        securable_type: builtins.str,
    ) -> None:
        '''
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#permission DataDatabricksApp#permission}.
        :param securable_full_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#securable_full_name DataDatabricksApp#securable_full_name}.
        :param securable_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#securable_type DataDatabricksApp#securable_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0736cf1d1a9b7f638a8f8f568acfde906f0a36848b034fdd2b2b51d650fe47e8)
            check_type(argname="argument permission", value=permission, expected_type=type_hints["permission"])
            check_type(argname="argument securable_full_name", value=securable_full_name, expected_type=type_hints["securable_full_name"])
            check_type(argname="argument securable_type", value=securable_type, expected_type=type_hints["securable_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "permission": permission,
            "securable_full_name": securable_full_name,
            "securable_type": securable_type,
        }

    @builtins.property
    def permission(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#permission DataDatabricksApp#permission}.'''
        result = self._values.get("permission")
        assert result is not None, "Required property 'permission' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def securable_full_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#securable_full_name DataDatabricksApp#securable_full_name}.'''
        result = self._values.get("securable_full_name")
        assert result is not None, "Required property 'securable_full_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def securable_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#securable_type DataDatabricksApp#securable_type}.'''
        result = self._values.get("securable_type")
        assert result is not None, "Required property 'securable_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppAppResourcesUcSecurable(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppAppResourcesUcSecurableOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppAppResourcesUcSecurableOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2fe614aa8e1de579bb6a67d5e28cfc45e108b567282c0a46c01a63ae5eade859)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="permissionInput")
    def permission_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "permissionInput"))

    @builtins.property
    @jsii.member(jsii_name="securableFullNameInput")
    def securable_full_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "securableFullNameInput"))

    @builtins.property
    @jsii.member(jsii_name="securableTypeInput")
    def securable_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "securableTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="permission")
    def permission(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permission"))

    @permission.setter
    def permission(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f82a04f64a058962796554c8438e33464251efb26cfd7e35b7d65ee2733a118a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permission", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="securableFullName")
    def securable_full_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "securableFullName"))

    @securable_full_name.setter
    def securable_full_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0bd49851d6329e33e17c874f71e7354f04d23ab23bf032c595ae23bf97b61ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "securableFullName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="securableType")
    def securable_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "securableType"))

    @securable_type.setter
    def securable_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__975397d35d83d0d938a144b7cd3cd8cee12110f88fbacfaf87bb048caec25ba1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "securableType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResourcesUcSecurable]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResourcesUcSecurable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResourcesUcSecurable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56b5974bbdc2418ee34b53ccdbdace8f4a11402d11df0120343100a9d31ca755)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApp.DataDatabricksAppConfig",
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
    },
)
class DataDatabricksAppConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#name DataDatabricksApp#name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__841c13f74893327a3246e8c0ebb9736571b5a1e9bbeffbb846e37f7d49c34c10)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/app#name DataDatabricksApp#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataDatabricksApp",
    "DataDatabricksAppApp",
    "DataDatabricksAppAppActiveDeployment",
    "DataDatabricksAppAppActiveDeploymentDeploymentArtifacts",
    "DataDatabricksAppAppActiveDeploymentDeploymentArtifactsOutputReference",
    "DataDatabricksAppAppActiveDeploymentOutputReference",
    "DataDatabricksAppAppActiveDeploymentStatus",
    "DataDatabricksAppAppActiveDeploymentStatusOutputReference",
    "DataDatabricksAppAppAppStatus",
    "DataDatabricksAppAppAppStatusOutputReference",
    "DataDatabricksAppAppComputeStatus",
    "DataDatabricksAppAppComputeStatusOutputReference",
    "DataDatabricksAppAppOutputReference",
    "DataDatabricksAppAppPendingDeployment",
    "DataDatabricksAppAppPendingDeploymentDeploymentArtifacts",
    "DataDatabricksAppAppPendingDeploymentDeploymentArtifactsOutputReference",
    "DataDatabricksAppAppPendingDeploymentOutputReference",
    "DataDatabricksAppAppPendingDeploymentStatus",
    "DataDatabricksAppAppPendingDeploymentStatusOutputReference",
    "DataDatabricksAppAppResources",
    "DataDatabricksAppAppResourcesDatabase",
    "DataDatabricksAppAppResourcesDatabaseOutputReference",
    "DataDatabricksAppAppResourcesJob",
    "DataDatabricksAppAppResourcesJobOutputReference",
    "DataDatabricksAppAppResourcesList",
    "DataDatabricksAppAppResourcesOutputReference",
    "DataDatabricksAppAppResourcesSecret",
    "DataDatabricksAppAppResourcesSecretOutputReference",
    "DataDatabricksAppAppResourcesServingEndpoint",
    "DataDatabricksAppAppResourcesServingEndpointOutputReference",
    "DataDatabricksAppAppResourcesSqlWarehouse",
    "DataDatabricksAppAppResourcesSqlWarehouseOutputReference",
    "DataDatabricksAppAppResourcesUcSecurable",
    "DataDatabricksAppAppResourcesUcSecurableOutputReference",
    "DataDatabricksAppConfig",
]

publication.publish()

def _typecheckingstub__9f0ce022004568ff5e253109396eece8a5fbd277f2a640530db20fd3555f6834(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    name: builtins.str,
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

def _typecheckingstub__0b673f1de1f6da52cfb1b5896457971a4bec9ac2721f0d3b2351ca4d5117146e(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3feef38a02de41c08393b96e84868d66cc6770ca3489ebc29e3c90273e99c43d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43e4670df0b4e95281aa8f15f8d6f1b643ae427b77323aa965560d3c5b0f4e84(
    *,
    name: builtins.str,
    budget_policy_id: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    resources: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksAppAppResources, typing.Dict[builtins.str, typing.Any]]]]] = None,
    user_api_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07f4711583806e7694ce67324f7c2a7d0e6a7e02d3452b53695821d7328dff9f(
    *,
    deployment_id: typing.Optional[builtins.str] = None,
    mode: typing.Optional[builtins.str] = None,
    source_code_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67345022ac46cf2ae5a669c5b6d75f1c9a37433a26a699dbae27a966c9c7b8d1(
    *,
    source_code_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62e1076106fd372f777193eb77b562771a2cf5e59f0b9c44b82090c9dca57b63(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d38debada89b38b0668887b66db8160df281fdbe4f15bdc27f41e4cb8d8a1bb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdc9ddcb553e377c0ce53eff68168574f7676315cdcb807c520b95d03e6d4174(
    value: typing.Optional[DataDatabricksAppAppActiveDeploymentDeploymentArtifacts],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1dac4fa7695cb41f42af1ead02f367fa98308d700c6307467a1fd6eec46138e4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e34ad3d2b69cb9e973430dbb810b78cd108ce6fd0b74f910a1d8e0a26a2efaa2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d73d49aeb62dcb6d418177bd3ae0bbc72306c9ed8f1f91404bdc15012752ceba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f1ebaeed7531b8d9ec378fd1094d2ae43ce6af3d094465db74e1e3d7f38396a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c7b189a795f6f77480ea5c93471e17d540da917c4e32db05d6430288f86a480(
    value: typing.Optional[DataDatabricksAppAppActiveDeployment],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd0b4a396fe5c01b468bf7cd50946d4912d7be0c694b38fff952af8db4d51761(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffadc2e787f8507ea0afa102d9a601793363a09e658aae305bfd8b7a46e5b2d4(
    value: typing.Optional[DataDatabricksAppAppActiveDeploymentStatus],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__509853b1ce6017a7ca645c0a1f122efbd3b133bd6dc4c7f6accad30f91ef18bb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e7fafebeb2f7b70dabec078db9455f284bca4370668c050cb22c987100d4daa(
    value: typing.Optional[DataDatabricksAppAppAppStatus],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c36c8b9146c54ef83ca29249df0646c537763ec5678109606844e60b8d53c3d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__173c1bb6401f29596e88214f54adca1899fc7f57031bdc8e446d239fb39e5bd5(
    value: typing.Optional[DataDatabricksAppAppComputeStatus],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f3b2518db223e4e5310604754a41f3d739d6969131eb9db28ba824cf84d9e9e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc070e6aa75826d1aee422a08662e32b3d2e7a2d33197cbf740ffca295f7f4d0(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksAppAppResources, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa61422038334aa5213e5957b0db6446741bc9b4d374fa67ab9fb89a112f6b62(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cca80ecf9d60cbb265200b55aab089649563a7d918329e065bd5133e6e14b3e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa9d7f845ea60a6e070a7c292af99bbabd03ccf2ca81dc4e8ab3b5229976af04(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc3de84740c667d0f99021c6789703c208263ae4561b3149d40d0ac3733f003c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5c91a7ee6b91ad3f5ac2db42b0c1d027f1355be8ec46cc3d1818873072dc89f(
    value: typing.Optional[DataDatabricksAppApp],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ca7d1c1116c3c252ff1688989072eac86a7770c82795c695ec6b44ca12260fc(
    *,
    deployment_id: typing.Optional[builtins.str] = None,
    mode: typing.Optional[builtins.str] = None,
    source_code_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c130a3c3872f1b972cd7c2ffb16258f15cacc2df6177e19c048fb3bd0b7c176e(
    *,
    source_code_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30dd973871602a1c961d0b2820bf9fec2593600bc338c7a4e09debc399c3edcc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8799bafbcc0228941be5c946e23c9046b60e247dfddc8fd8b85898555fcfe0fe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4305b73444632d7f0a991a51f52fe4a7c45f21842757682a96ecb60da2ea666(
    value: typing.Optional[DataDatabricksAppAppPendingDeploymentDeploymentArtifacts],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__258f8b6a3962797d0f6453b6d7155edad16a1e8984c76eb55fdf3093dcb72b02(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29a77a6980dfe55b86e43f2ffd7b4c816de0e8bcb509bff1f73f21a4b4cdbb4a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9347059a1424f7fcee0c57489543148a5838c3a9508c81df98e0cb0cd05750f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf4d25275aa40728f27863a6a8cf1ef20ab65b66cdd4e38621319450be975805(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee3d243c9fbaa17c10df37536f858413721fa63de23aa0a722c8ef31f9f5db75(
    value: typing.Optional[DataDatabricksAppAppPendingDeployment],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb6084681e1d687edf76cbe69ead2cc45fdbdf1d1e29600f5a5463469a50b544(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__089ad5851b337d08235f55e4f373d7c91a0793745d553732abbb3093173948bf(
    value: typing.Optional[DataDatabricksAppAppPendingDeploymentStatus],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0fb10be780cec5a535ea4d8b83172f041293d530254765ed0a933fa61245374(
    *,
    name: builtins.str,
    database: typing.Optional[typing.Union[DataDatabricksAppAppResourcesDatabase, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    job: typing.Optional[typing.Union[DataDatabricksAppAppResourcesJob, typing.Dict[builtins.str, typing.Any]]] = None,
    secret: typing.Optional[typing.Union[DataDatabricksAppAppResourcesSecret, typing.Dict[builtins.str, typing.Any]]] = None,
    serving_endpoint: typing.Optional[typing.Union[DataDatabricksAppAppResourcesServingEndpoint, typing.Dict[builtins.str, typing.Any]]] = None,
    sql_warehouse: typing.Optional[typing.Union[DataDatabricksAppAppResourcesSqlWarehouse, typing.Dict[builtins.str, typing.Any]]] = None,
    uc_securable: typing.Optional[typing.Union[DataDatabricksAppAppResourcesUcSecurable, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__565136257b2bfbca0f1e132925c559e0416220b54d8153359efb158315a31b20(
    *,
    database_name: builtins.str,
    instance_name: builtins.str,
    permission: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc788242fd17584e4f2fda0478c8545fac1b9a095b94fbd1999812f307ad72d0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ce962f73fd0cfeacc0c7c46a544941b3b21abf12eb17bd897540ba39630f75d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__985c1d6a197687d708acafe8b8af16ef2962b28bd75f12f971866ac9e4f3a792(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17ca82adb4759a7f7b00f2f1d7fbe6c1fbe9d2224df6157b5a6b54e7e1dcccee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b24ea27058efad8054803580ad9ddaa2cd89cb78f8fa4ec17082e488e4b72ff1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResourcesDatabase]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c02726d903612396a1bb9ed10d8be76f7429b0ca6485e6f6008e3208a6858559(
    *,
    id: builtins.str,
    permission: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__376e6b11b0cfdebc9b1c9370c19aa7594209dd3f05c3faba7e4a98398de0fec0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0106a086afb44bb07993d7342debff44e97b8ba4fb1355739ed8c43cc372521a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24043cda4e4f8e305ff81edea9c7a2095fa26ec1e059b77cb9b8cdc9b2a8abeb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92e12613dd2fe06054dde0960b3b2f03415acdab43c05e950a22e25af04646fe(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResourcesJob]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__435fa4c92211a5324bde412354a8d4bb6a84ec2f2ed600f22f898ccd8f2037c9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__418293d3bbb8099f34f29a3d39ae9a3467c2e847d3dbaee90d03ebcbe27a31f0(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce4e91a2a2d4303f9d6628e6b3f99e1312dd496ea9619a329596826763675d3e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95e5eccdb46aeb02258d7584c7bd406e6e7b1259d0ee2cc1dc7f63c18bbbf7f3(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a74b643a6730956250780b4b1e489ba154acdb5025a65059fd334b38dba7c94(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11f0c3614501fa5762f08de90594e2eaff115ba79d98a3c96bf6ac6c6e7823a2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAppAppResources]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__011037957b4cfae4c9b6fbc26e17a89ce17369c45425045f1abc42972416c667(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e82fd010ea1504abfbd19ad522fb0907c5de05eb7ce9f9745f9ba43299f8490c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__604c29e8103952b0cc15f0fd0c5a8ce3c3bbf3d8cbb1d929a244215d21911985(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f00f3d017092fe113b59d34f702792fce8d7a6cea866eb8a00a2350bef25856c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResources]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1adaba5934969ccce39731ecc93354744ecc0f77d9dda6bb7ff4d0b161f4ae3(
    *,
    key: builtins.str,
    permission: builtins.str,
    scope: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__570b87d4aae6f61edf409be8654dd974a1346d6d6e4fefa91f6337201b0284b2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ab4570f5a5e75f1c6ac7cb9d5f3b187d804851362515e7f56338261c4786118(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22fda5a3894b531ba19758c9c4e10b840d474d956caa717e3bc167f66160eccc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__485b19f74f664f4269e153f1ed3bffdec7220e22da53ca835f5a6492bbd5e6ae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c2fed2141fe39ec07f4e4ebe142a42e55fbabcac167a9847782d2193d82c12a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResourcesSecret]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d828032c0f1b448dd9acc2d246e2ab1de4f358a450cc758b1ffc9eafdf38ed6(
    *,
    name: builtins.str,
    permission: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46d919df2eb5f0713f68e643df762b57d1c0b934554d9a2ee9f84ad88f2590f9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef63f2944564e43b903760963d6fcd959cf6ff98f4e007ac4ece2beb7983fc3d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c95e6faf8d4d072e6dbf38104bad9de4663d768fcb9430b49f2aba56f6ef8d8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e376434de71e2c722311f32644f982892386bd1c7bfae712dd71673f2071317(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResourcesServingEndpoint]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57a75365f026cbc494698cf4bcc9ba3f1e9ff8651b204f32bdd4001645f7d813(
    *,
    id: builtins.str,
    permission: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7ca2159dc0d54954537c6c2cdeab41af566a9e3fe97f978a3d986f0473cff41(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4162cfdfadc82aead255444a3a5bdf16c3cd5e721675872b00d9493a2b251f05(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b205aea94685bdc2bc8cfe5c348f7531ea689f0691eb8480606e0d62198a2424(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__494474b238f843d871fbddcbf71a08823e0c99d0369ce8f22baa8c6e84886c9c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResourcesSqlWarehouse]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0736cf1d1a9b7f638a8f8f568acfde906f0a36848b034fdd2b2b51d650fe47e8(
    *,
    permission: builtins.str,
    securable_full_name: builtins.str,
    securable_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fe614aa8e1de579bb6a67d5e28cfc45e108b567282c0a46c01a63ae5eade859(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f82a04f64a058962796554c8438e33464251efb26cfd7e35b7d65ee2733a118a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0bd49851d6329e33e17c874f71e7354f04d23ab23bf032c595ae23bf97b61ae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__975397d35d83d0d938a144b7cd3cd8cee12110f88fbacfaf87bb048caec25ba1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56b5974bbdc2418ee34b53ccdbdace8f4a11402d11df0120343100a9d31ca755(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppAppResourcesUcSecurable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__841c13f74893327a3246e8c0ebb9736571b5a1e9bbeffbb846e37f7d49c34c10(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass
