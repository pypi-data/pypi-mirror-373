r'''
# `data_databricks_apps`

Refer to the Terraform Registry for docs: [`data_databricks_apps`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps).
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


class DataDatabricksApps(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksApps",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps databricks_apps}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps databricks_apps} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9d93698de7735f41c60eff12b51fbb30c09ac727b22d30480a191f776b151e8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataDatabricksAppsConfig(
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
        '''Generates CDKTF code for importing a DataDatabricksApps resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDatabricksApps to import.
        :param import_from_id: The id of the existing DataDatabricksApps that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDatabricksApps to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c73ba5ae6f97a984c8ccfb30413c1e5ff7921ef93bbe63550ae541d6077163e6)
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
    def app(self) -> "DataDatabricksAppsAppList":
        return typing.cast("DataDatabricksAppsAppList", jsii.get(self, "app"))


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsApp",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "budget_policy_id": "budgetPolicyId",
        "description": "description",
        "resources": "resources",
        "user_api_scopes": "userApiScopes",
    },
)
class DataDatabricksAppsApp:
    def __init__(
        self,
        *,
        name: builtins.str,
        budget_policy_id: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        resources: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksAppsAppResources", typing.Dict[builtins.str, typing.Any]]]]] = None,
        user_api_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#name DataDatabricksApps#name}.
        :param budget_policy_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#budget_policy_id DataDatabricksApps#budget_policy_id}.
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#description DataDatabricksApps#description}.
        :param resources: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#resources DataDatabricksApps#resources}.
        :param user_api_scopes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#user_api_scopes DataDatabricksApps#user_api_scopes}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3f374e496785c6018b1021fd64679ee0225334871ea795fe6462566967cde96)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#name DataDatabricksApps#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def budget_policy_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#budget_policy_id DataDatabricksApps#budget_policy_id}.'''
        result = self._values.get("budget_policy_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#description DataDatabricksApps#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resources(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksAppsAppResources"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#resources DataDatabricksApps#resources}.'''
        result = self._values.get("resources")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksAppsAppResources"]]], result)

    @builtins.property
    def user_api_scopes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#user_api_scopes DataDatabricksApps#user_api_scopes}.'''
        result = self._values.get("user_api_scopes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppsApp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppActiveDeployment",
    jsii_struct_bases=[],
    name_mapping={
        "deployment_id": "deploymentId",
        "mode": "mode",
        "source_code_path": "sourceCodePath",
    },
)
class DataDatabricksAppsAppActiveDeployment:
    def __init__(
        self,
        *,
        deployment_id: typing.Optional[builtins.str] = None,
        mode: typing.Optional[builtins.str] = None,
        source_code_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param deployment_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#deployment_id DataDatabricksApps#deployment_id}.
        :param mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#mode DataDatabricksApps#mode}.
        :param source_code_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#source_code_path DataDatabricksApps#source_code_path}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74c08037689a1b8433e156bd2d8c2e2a8e70311250fec932df969cdbfa4a52f2)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#deployment_id DataDatabricksApps#deployment_id}.'''
        result = self._values.get("deployment_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#mode DataDatabricksApps#mode}.'''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_code_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#source_code_path DataDatabricksApps#source_code_path}.'''
        result = self._values.get("source_code_path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppsAppActiveDeployment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppActiveDeploymentDeploymentArtifacts",
    jsii_struct_bases=[],
    name_mapping={"source_code_path": "sourceCodePath"},
)
class DataDatabricksAppsAppActiveDeploymentDeploymentArtifacts:
    def __init__(
        self,
        *,
        source_code_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param source_code_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#source_code_path DataDatabricksApps#source_code_path}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b95081f0843a5072c1742b2cf0cc51d11d0fee480851b64565f8ac43d025506f)
            check_type(argname="argument source_code_path", value=source_code_path, expected_type=type_hints["source_code_path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if source_code_path is not None:
            self._values["source_code_path"] = source_code_path

    @builtins.property
    def source_code_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#source_code_path DataDatabricksApps#source_code_path}.'''
        result = self._values.get("source_code_path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppsAppActiveDeploymentDeploymentArtifacts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppsAppActiveDeploymentDeploymentArtifactsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppActiveDeploymentDeploymentArtifactsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c8d9e9d52c60510780d08863409a34007a7f9e66c7137a99f934ca4658f882f1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3f195ab21cd50a6ca571ac5bf57d46ff2ff3b8e4e0f771afdcf8a8b6ca7728cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceCodePath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksAppsAppActiveDeploymentDeploymentArtifacts]:
        return typing.cast(typing.Optional[DataDatabricksAppsAppActiveDeploymentDeploymentArtifacts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksAppsAppActiveDeploymentDeploymentArtifacts],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__405cd036db808f72e890633fa1136f650f5df75c13cfd690675f5e8314f5f918)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAppsAppActiveDeploymentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppActiveDeploymentOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__59b8c0928879f53e5f4650e5c05d659956e3711b241aeda02b98d5e326dbee5f)
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
    ) -> DataDatabricksAppsAppActiveDeploymentDeploymentArtifactsOutputReference:
        return typing.cast(DataDatabricksAppsAppActiveDeploymentDeploymentArtifactsOutputReference, jsii.get(self, "deploymentArtifacts"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> "DataDatabricksAppsAppActiveDeploymentStatusOutputReference":
        return typing.cast("DataDatabricksAppsAppActiveDeploymentStatusOutputReference", jsii.get(self, "status"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__243f558f1041d2a3076d952752afc73f735a6cf00eaec19a87f617c79fd4bfb6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deploymentId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__485438f0d38d7fbc26dae5c17878cf74ea72f5da55022d17a5892f48a01fcfd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceCodePath")
    def source_code_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceCodePath"))

    @source_code_path.setter
    def source_code_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f890e8ec65a7aa3d7741ee11a7f197082b768ddf341a5272e49294525fe13b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceCodePath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataDatabricksAppsAppActiveDeployment]:
        return typing.cast(typing.Optional[DataDatabricksAppsAppActiveDeployment], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksAppsAppActiveDeployment],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46838f1ce9b70f78bbe08104f9d61751d5effed3eff66f01b526b791ddcd0534)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppActiveDeploymentStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksAppsAppActiveDeploymentStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppsAppActiveDeploymentStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppsAppActiveDeploymentStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppActiveDeploymentStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__608cb2338cb2fd1d1e1190f4f689faacfdfda5e18813899774e32479bd2c402b)
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
    ) -> typing.Optional[DataDatabricksAppsAppActiveDeploymentStatus]:
        return typing.cast(typing.Optional[DataDatabricksAppsAppActiveDeploymentStatus], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksAppsAppActiveDeploymentStatus],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0786ee1852fcd29907b92f6613f1fbbaed2ced4d97dd94504cefe84c987afd7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppAppStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksAppsAppAppStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppsAppAppStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppsAppAppStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppAppStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__de5906ce6acb3f83f33d6bacdd9e0776435457252023da5bf79e53b548be4ce3)
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
    def internal_value(self) -> typing.Optional[DataDatabricksAppsAppAppStatus]:
        return typing.cast(typing.Optional[DataDatabricksAppsAppAppStatus], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksAppsAppAppStatus],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e864bd30787ecbd79b32ac6087d83ae73a8bb91703c663484ae962d9dbd5ad7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppComputeStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksAppsAppComputeStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppsAppComputeStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppsAppComputeStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppComputeStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__27f93eb00fe32e0513a9e213f44885102ddbec94ef60d71574aa97395f4265d1)
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
    def internal_value(self) -> typing.Optional[DataDatabricksAppsAppComputeStatus]:
        return typing.cast(typing.Optional[DataDatabricksAppsAppComputeStatus], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksAppsAppComputeStatus],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c247e8ce557194641c5d99f3be51320bbfd34852ce9bcf072378386214be909d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAppsAppList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cffabbef0320357eeee12a66e9bb55efd2f82d7b4250f175b2131bb838359863)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "DataDatabricksAppsAppOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fa696204dda6ed0f33d7523ad94bbaf94551047753cf9e0211b2c1502a8e7c2)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksAppsAppOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62521ccd4ff628e8c3e7c9595af9b38a78948cefd28f43592ddb2ee2badf6e86)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a357b95988f084778aa5c8a170b8cbcdf771624cec9bffccfa05e83d0d9eff00)
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
            type_hints = typing.get_type_hints(_typecheckingstub__157220e3568457d568a87b54bd16091e37a3e9dfbbbaa72f537c7dcb23f0af96)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAppsApp]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAppsApp]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAppsApp]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54346482493cc9cd91737d4934cf58ff56ba14807e1606159f14cac557e07c0c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAppsAppOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b27fc4f7e444d244a5106d9e68ba94982fab75fab416e1b2f1bc01b18da2f707)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putResources")
    def put_resources(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksAppsAppResources", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54a4f4f3c6b73d1c2824c8c39808f15e285c08c31601021d189b48b3958b16e7)
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
    def active_deployment(self) -> DataDatabricksAppsAppActiveDeploymentOutputReference:
        return typing.cast(DataDatabricksAppsAppActiveDeploymentOutputReference, jsii.get(self, "activeDeployment"))

    @builtins.property
    @jsii.member(jsii_name="appStatus")
    def app_status(self) -> DataDatabricksAppsAppAppStatusOutputReference:
        return typing.cast(DataDatabricksAppsAppAppStatusOutputReference, jsii.get(self, "appStatus"))

    @builtins.property
    @jsii.member(jsii_name="computeStatus")
    def compute_status(self) -> DataDatabricksAppsAppComputeStatusOutputReference:
        return typing.cast(DataDatabricksAppsAppComputeStatusOutputReference, jsii.get(self, "computeStatus"))

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
    ) -> "DataDatabricksAppsAppPendingDeploymentOutputReference":
        return typing.cast("DataDatabricksAppsAppPendingDeploymentOutputReference", jsii.get(self, "pendingDeployment"))

    @builtins.property
    @jsii.member(jsii_name="resources")
    def resources(self) -> "DataDatabricksAppsAppResourcesList":
        return typing.cast("DataDatabricksAppsAppResourcesList", jsii.get(self, "resources"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksAppsAppResources"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksAppsAppResources"]]], jsii.get(self, "resourcesInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__ac16fe9a03c850538dc81d587f0020945e74e6b4c60cb1901a5104d77cad00bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "budgetPolicyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f7cefc9abb71bfb29e91f2be143656ed9c63d9f415bb45d5a125adc90a7920e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc9d34fba6e25ad02bb276652016539a60a2dc0793bc19f7c20a2f0aafc3446d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userApiScopes")
    def user_api_scopes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "userApiScopes"))

    @user_api_scopes.setter
    def user_api_scopes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0707b1ca3f18996d113c44339193e04383c82710c7da559e702ac9c6b17e73cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userApiScopes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataDatabricksAppsApp]:
        return typing.cast(typing.Optional[DataDatabricksAppsApp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[DataDatabricksAppsApp]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30d282a3f60ad63dc484f71ed65799d8c36bcf4d09941e14bd71ba7f9b070c60)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppPendingDeployment",
    jsii_struct_bases=[],
    name_mapping={
        "deployment_id": "deploymentId",
        "mode": "mode",
        "source_code_path": "sourceCodePath",
    },
)
class DataDatabricksAppsAppPendingDeployment:
    def __init__(
        self,
        *,
        deployment_id: typing.Optional[builtins.str] = None,
        mode: typing.Optional[builtins.str] = None,
        source_code_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param deployment_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#deployment_id DataDatabricksApps#deployment_id}.
        :param mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#mode DataDatabricksApps#mode}.
        :param source_code_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#source_code_path DataDatabricksApps#source_code_path}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74abd36acba74130fff14af9a03150b917ecdcc34876a6ec9949a73c635e48e0)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#deployment_id DataDatabricksApps#deployment_id}.'''
        result = self._values.get("deployment_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#mode DataDatabricksApps#mode}.'''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_code_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#source_code_path DataDatabricksApps#source_code_path}.'''
        result = self._values.get("source_code_path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppsAppPendingDeployment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppPendingDeploymentDeploymentArtifacts",
    jsii_struct_bases=[],
    name_mapping={"source_code_path": "sourceCodePath"},
)
class DataDatabricksAppsAppPendingDeploymentDeploymentArtifacts:
    def __init__(
        self,
        *,
        source_code_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param source_code_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#source_code_path DataDatabricksApps#source_code_path}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cda869040ec653f93df1fe74b86ee5043795916619bba961eac4507cf17c9395)
            check_type(argname="argument source_code_path", value=source_code_path, expected_type=type_hints["source_code_path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if source_code_path is not None:
            self._values["source_code_path"] = source_code_path

    @builtins.property
    def source_code_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#source_code_path DataDatabricksApps#source_code_path}.'''
        result = self._values.get("source_code_path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppsAppPendingDeploymentDeploymentArtifacts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppsAppPendingDeploymentDeploymentArtifactsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppPendingDeploymentDeploymentArtifactsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c95b18dc20af14183b841b7403d12d42ee4aaf4465f327ce8d49305ee00eb41c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c362d037e3bcc6f9dc2f5c6e9349840de90a275953d8435aaa1d2e19614349ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceCodePath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksAppsAppPendingDeploymentDeploymentArtifacts]:
        return typing.cast(typing.Optional[DataDatabricksAppsAppPendingDeploymentDeploymentArtifacts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksAppsAppPendingDeploymentDeploymentArtifacts],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e512a457acc6998312aab7f9c360de6b39cdbfd3bd1a57a99281f3961ab9f4bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAppsAppPendingDeploymentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppPendingDeploymentOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f6396c5bedcbd8b2484d0a0d9401973ea22010fde95418092fb93e18c0a68048)
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
    ) -> DataDatabricksAppsAppPendingDeploymentDeploymentArtifactsOutputReference:
        return typing.cast(DataDatabricksAppsAppPendingDeploymentDeploymentArtifactsOutputReference, jsii.get(self, "deploymentArtifacts"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> "DataDatabricksAppsAppPendingDeploymentStatusOutputReference":
        return typing.cast("DataDatabricksAppsAppPendingDeploymentStatusOutputReference", jsii.get(self, "status"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__28642252c2ec7c36dca40c4d0ac36fc33bbe379ed99c3761774bfdd361eb797a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deploymentId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__401c594563dc11cb37561043f66785bbc8120b1088f1de0ea4fd1f7943796642)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceCodePath")
    def source_code_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceCodePath"))

    @source_code_path.setter
    def source_code_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__102fcc3852baf10610da5476617936d33c91e321ce3dd3e9240f6713d1946d85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceCodePath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataDatabricksAppsAppPendingDeployment]:
        return typing.cast(typing.Optional[DataDatabricksAppsAppPendingDeployment], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksAppsAppPendingDeployment],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a21fc0cb93ccd74edf2af8c4c925256eb44b9a25705da39991a490f6968b0ef3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppPendingDeploymentStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksAppsAppPendingDeploymentStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppsAppPendingDeploymentStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppsAppPendingDeploymentStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppPendingDeploymentStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0a1f8adc584911bf831b098004a87bf7d367ea0e393d6b4266acd26458d89a6c)
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
    ) -> typing.Optional[DataDatabricksAppsAppPendingDeploymentStatus]:
        return typing.cast(typing.Optional[DataDatabricksAppsAppPendingDeploymentStatus], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksAppsAppPendingDeploymentStatus],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5f77f265ea4becfbd09e187ec5544aeb42e1a0f2bdf29c8ecba2d553ce42a14)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppResources",
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
class DataDatabricksAppsAppResources:
    def __init__(
        self,
        *,
        name: builtins.str,
        database: typing.Optional[typing.Union["DataDatabricksAppsAppResourcesDatabase", typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        job: typing.Optional[typing.Union["DataDatabricksAppsAppResourcesJob", typing.Dict[builtins.str, typing.Any]]] = None,
        secret: typing.Optional[typing.Union["DataDatabricksAppsAppResourcesSecret", typing.Dict[builtins.str, typing.Any]]] = None,
        serving_endpoint: typing.Optional[typing.Union["DataDatabricksAppsAppResourcesServingEndpoint", typing.Dict[builtins.str, typing.Any]]] = None,
        sql_warehouse: typing.Optional[typing.Union["DataDatabricksAppsAppResourcesSqlWarehouse", typing.Dict[builtins.str, typing.Any]]] = None,
        uc_securable: typing.Optional[typing.Union["DataDatabricksAppsAppResourcesUcSecurable", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#name DataDatabricksApps#name}.
        :param database: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#database DataDatabricksApps#database}.
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#description DataDatabricksApps#description}.
        :param job: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#job DataDatabricksApps#job}.
        :param secret: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#secret DataDatabricksApps#secret}.
        :param serving_endpoint: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#serving_endpoint DataDatabricksApps#serving_endpoint}.
        :param sql_warehouse: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#sql_warehouse DataDatabricksApps#sql_warehouse}.
        :param uc_securable: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#uc_securable DataDatabricksApps#uc_securable}.
        '''
        if isinstance(database, dict):
            database = DataDatabricksAppsAppResourcesDatabase(**database)
        if isinstance(job, dict):
            job = DataDatabricksAppsAppResourcesJob(**job)
        if isinstance(secret, dict):
            secret = DataDatabricksAppsAppResourcesSecret(**secret)
        if isinstance(serving_endpoint, dict):
            serving_endpoint = DataDatabricksAppsAppResourcesServingEndpoint(**serving_endpoint)
        if isinstance(sql_warehouse, dict):
            sql_warehouse = DataDatabricksAppsAppResourcesSqlWarehouse(**sql_warehouse)
        if isinstance(uc_securable, dict):
            uc_securable = DataDatabricksAppsAppResourcesUcSecurable(**uc_securable)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5528e1b7f5a7b871c2c7edf64cb606cdb1619f1a8a7a89e098e4330fa857e9a4)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#name DataDatabricksApps#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def database(self) -> typing.Optional["DataDatabricksAppsAppResourcesDatabase"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#database DataDatabricksApps#database}.'''
        result = self._values.get("database")
        return typing.cast(typing.Optional["DataDatabricksAppsAppResourcesDatabase"], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#description DataDatabricksApps#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def job(self) -> typing.Optional["DataDatabricksAppsAppResourcesJob"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#job DataDatabricksApps#job}.'''
        result = self._values.get("job")
        return typing.cast(typing.Optional["DataDatabricksAppsAppResourcesJob"], result)

    @builtins.property
    def secret(self) -> typing.Optional["DataDatabricksAppsAppResourcesSecret"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#secret DataDatabricksApps#secret}.'''
        result = self._values.get("secret")
        return typing.cast(typing.Optional["DataDatabricksAppsAppResourcesSecret"], result)

    @builtins.property
    def serving_endpoint(
        self,
    ) -> typing.Optional["DataDatabricksAppsAppResourcesServingEndpoint"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#serving_endpoint DataDatabricksApps#serving_endpoint}.'''
        result = self._values.get("serving_endpoint")
        return typing.cast(typing.Optional["DataDatabricksAppsAppResourcesServingEndpoint"], result)

    @builtins.property
    def sql_warehouse(
        self,
    ) -> typing.Optional["DataDatabricksAppsAppResourcesSqlWarehouse"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#sql_warehouse DataDatabricksApps#sql_warehouse}.'''
        result = self._values.get("sql_warehouse")
        return typing.cast(typing.Optional["DataDatabricksAppsAppResourcesSqlWarehouse"], result)

    @builtins.property
    def uc_securable(
        self,
    ) -> typing.Optional["DataDatabricksAppsAppResourcesUcSecurable"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#uc_securable DataDatabricksApps#uc_securable}.'''
        result = self._values.get("uc_securable")
        return typing.cast(typing.Optional["DataDatabricksAppsAppResourcesUcSecurable"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppsAppResources(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppResourcesDatabase",
    jsii_struct_bases=[],
    name_mapping={
        "database_name": "databaseName",
        "instance_name": "instanceName",
        "permission": "permission",
    },
)
class DataDatabricksAppsAppResourcesDatabase:
    def __init__(
        self,
        *,
        database_name: builtins.str,
        instance_name: builtins.str,
        permission: builtins.str,
    ) -> None:
        '''
        :param database_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#database_name DataDatabricksApps#database_name}.
        :param instance_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#instance_name DataDatabricksApps#instance_name}.
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#permission DataDatabricksApps#permission}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__620e703281ca2fc90dbf06611bde6273362d8c38ee86858409db6a510e119e85)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#database_name DataDatabricksApps#database_name}.'''
        result = self._values.get("database_name")
        assert result is not None, "Required property 'database_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instance_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#instance_name DataDatabricksApps#instance_name}.'''
        result = self._values.get("instance_name")
        assert result is not None, "Required property 'instance_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def permission(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#permission DataDatabricksApps#permission}.'''
        result = self._values.get("permission")
        assert result is not None, "Required property 'permission' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppsAppResourcesDatabase(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppsAppResourcesDatabaseOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppResourcesDatabaseOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ba5bd466a14b91b47a9266ff623cc534ee8c562152b2b766954a62804b4684de)
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
            type_hints = typing.get_type_hints(_typecheckingstub__67aee34facdab99722c3f671dcd20b2b9ef8a232dbf7b78ba7ffc2a211249536)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "databaseName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instanceName")
    def instance_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceName"))

    @instance_name.setter
    def instance_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b11400e79ccedf1850bc51312593bedd1df8fd9996e603c083aed4d9bfc76ae3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="permission")
    def permission(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permission"))

    @permission.setter
    def permission(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2edb37f2c3d1ff9aef855ed28d5efa73746dab5e59906e1fc9fb3b418bb17cd6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permission", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResourcesDatabase]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResourcesDatabase]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResourcesDatabase]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c4ca1e7ee020d7ca7782e242681e2f205d4e68302ed93dbd5ec1df78dae1998)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppResourcesJob",
    jsii_struct_bases=[],
    name_mapping={"id": "id", "permission": "permission"},
)
class DataDatabricksAppsAppResourcesJob:
    def __init__(self, *, id: builtins.str, permission: builtins.str) -> None:
        '''
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#id DataDatabricksApps#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#permission DataDatabricksApps#permission}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__507f10c33130303588ac4ab69692a08e235f0d205ea3c8a7612682928a409761)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument permission", value=permission, expected_type=type_hints["permission"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
            "permission": permission,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#id DataDatabricksApps#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def permission(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#permission DataDatabricksApps#permission}.'''
        result = self._values.get("permission")
        assert result is not None, "Required property 'permission' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppsAppResourcesJob(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppsAppResourcesJobOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppResourcesJobOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d7996f12373aa25570ab7396f26a49e70fb76de7168776d44c41c8dc47b21771)
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
            type_hints = typing.get_type_hints(_typecheckingstub__371772580b0c5152dc0c1c51b96da36b590715f958048155eb0103be9ecc7771)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="permission")
    def permission(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permission"))

    @permission.setter
    def permission(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14119329790abdcc3de9d6f43b64841bcffceecd3a78787d7423f7e947365a2d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permission", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResourcesJob]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResourcesJob]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResourcesJob]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6cc19c9001053238256377b30b1ebd5cf8bce4dce5fb6acf3f35c2b7a0eeb22c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAppsAppResourcesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppResourcesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c67599862db056e903bceea6d0376a047b656b8a98341cd3534ec1d91dc73c10)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksAppsAppResourcesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22c65eddcad20e9c27cff9bc063ba95f49ff5a9f7b3f4a5d51072348e3eaebcb)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksAppsAppResourcesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ac6eb74b03eaff5d5ae2b84ffb624c1dd650e188438eb1c1f691342d22674ea)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ec3a7967da51cd6f447e634a0da5ec2f8d6b0518038f048fd3bd98cd15cad058)
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
            type_hints = typing.get_type_hints(_typecheckingstub__47cddebc50466c17d0c578d9a86c468bb9dd52b34425898da8e3bd621e034614)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAppsAppResources]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAppsAppResources]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAppsAppResources]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__204b5dd037ef732c2b8b5c2710a175d8d171581f6e5c4a95945b72c65cc19229)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAppsAppResourcesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppResourcesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d7c03394e799ed312fd58a25c24048ec2003f5cfc67b0dba7b87bddd8a2e74ee)
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
        :param database_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#database_name DataDatabricksApps#database_name}.
        :param instance_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#instance_name DataDatabricksApps#instance_name}.
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#permission DataDatabricksApps#permission}.
        '''
        value = DataDatabricksAppsAppResourcesDatabase(
            database_name=database_name,
            instance_name=instance_name,
            permission=permission,
        )

        return typing.cast(None, jsii.invoke(self, "putDatabase", [value]))

    @jsii.member(jsii_name="putJob")
    def put_job(self, *, id: builtins.str, permission: builtins.str) -> None:
        '''
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#id DataDatabricksApps#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#permission DataDatabricksApps#permission}.
        '''
        value = DataDatabricksAppsAppResourcesJob(id=id, permission=permission)

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
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#key DataDatabricksApps#key}.
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#permission DataDatabricksApps#permission}.
        :param scope: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#scope DataDatabricksApps#scope}.
        '''
        value = DataDatabricksAppsAppResourcesSecret(
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
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#name DataDatabricksApps#name}.
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#permission DataDatabricksApps#permission}.
        '''
        value = DataDatabricksAppsAppResourcesServingEndpoint(
            name=name, permission=permission
        )

        return typing.cast(None, jsii.invoke(self, "putServingEndpoint", [value]))

    @jsii.member(jsii_name="putSqlWarehouse")
    def put_sql_warehouse(self, *, id: builtins.str, permission: builtins.str) -> None:
        '''
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#id DataDatabricksApps#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#permission DataDatabricksApps#permission}.
        '''
        value = DataDatabricksAppsAppResourcesSqlWarehouse(
            id=id, permission=permission
        )

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
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#permission DataDatabricksApps#permission}.
        :param securable_full_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#securable_full_name DataDatabricksApps#securable_full_name}.
        :param securable_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#securable_type DataDatabricksApps#securable_type}.
        '''
        value = DataDatabricksAppsAppResourcesUcSecurable(
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
    def database(self) -> DataDatabricksAppsAppResourcesDatabaseOutputReference:
        return typing.cast(DataDatabricksAppsAppResourcesDatabaseOutputReference, jsii.get(self, "database"))

    @builtins.property
    @jsii.member(jsii_name="job")
    def job(self) -> DataDatabricksAppsAppResourcesJobOutputReference:
        return typing.cast(DataDatabricksAppsAppResourcesJobOutputReference, jsii.get(self, "job"))

    @builtins.property
    @jsii.member(jsii_name="secret")
    def secret(self) -> "DataDatabricksAppsAppResourcesSecretOutputReference":
        return typing.cast("DataDatabricksAppsAppResourcesSecretOutputReference", jsii.get(self, "secret"))

    @builtins.property
    @jsii.member(jsii_name="servingEndpoint")
    def serving_endpoint(
        self,
    ) -> "DataDatabricksAppsAppResourcesServingEndpointOutputReference":
        return typing.cast("DataDatabricksAppsAppResourcesServingEndpointOutputReference", jsii.get(self, "servingEndpoint"))

    @builtins.property
    @jsii.member(jsii_name="sqlWarehouse")
    def sql_warehouse(
        self,
    ) -> "DataDatabricksAppsAppResourcesSqlWarehouseOutputReference":
        return typing.cast("DataDatabricksAppsAppResourcesSqlWarehouseOutputReference", jsii.get(self, "sqlWarehouse"))

    @builtins.property
    @jsii.member(jsii_name="ucSecurable")
    def uc_securable(
        self,
    ) -> "DataDatabricksAppsAppResourcesUcSecurableOutputReference":
        return typing.cast("DataDatabricksAppsAppResourcesUcSecurableOutputReference", jsii.get(self, "ucSecurable"))

    @builtins.property
    @jsii.member(jsii_name="databaseInput")
    def database_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResourcesDatabase]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResourcesDatabase]], jsii.get(self, "databaseInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="jobInput")
    def job_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResourcesJob]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResourcesJob]], jsii.get(self, "jobInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="secretInput")
    def secret_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAppsAppResourcesSecret"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAppsAppResourcesSecret"]], jsii.get(self, "secretInput"))

    @builtins.property
    @jsii.member(jsii_name="servingEndpointInput")
    def serving_endpoint_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAppsAppResourcesServingEndpoint"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAppsAppResourcesServingEndpoint"]], jsii.get(self, "servingEndpointInput"))

    @builtins.property
    @jsii.member(jsii_name="sqlWarehouseInput")
    def sql_warehouse_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAppsAppResourcesSqlWarehouse"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAppsAppResourcesSqlWarehouse"]], jsii.get(self, "sqlWarehouseInput"))

    @builtins.property
    @jsii.member(jsii_name="ucSecurableInput")
    def uc_securable_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAppsAppResourcesUcSecurable"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAppsAppResourcesUcSecurable"]], jsii.get(self, "ucSecurableInput"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9b624135934b2884c5772b647b5e8c820c7a18b9f60cee7461c2c927c22da21)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10ec889d618d3e54d9a09bb177d52385c36c983e24272eb1119a82dadb617fa1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResources]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResources]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResources]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__431bf43a96e44364b5ee9624797cf6102460ac93aa652837f30ae67e00033ad7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppResourcesSecret",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "permission": "permission", "scope": "scope"},
)
class DataDatabricksAppsAppResourcesSecret:
    def __init__(
        self,
        *,
        key: builtins.str,
        permission: builtins.str,
        scope: builtins.str,
    ) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#key DataDatabricksApps#key}.
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#permission DataDatabricksApps#permission}.
        :param scope: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#scope DataDatabricksApps#scope}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e127fd23cba7ea0451afe4229fbd0b6f95759c507373513b914d25ac781fd93e)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#key DataDatabricksApps#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def permission(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#permission DataDatabricksApps#permission}.'''
        result = self._values.get("permission")
        assert result is not None, "Required property 'permission' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def scope(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#scope DataDatabricksApps#scope}.'''
        result = self._values.get("scope")
        assert result is not None, "Required property 'scope' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppsAppResourcesSecret(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppsAppResourcesSecretOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppResourcesSecretOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0bcea2efc4f9ed9e0bfb9892bf908177121ca20665194b9ec53de60e33f56c27)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4a3b7dd1017e176c1acfc84a74bc11778f3a8913b11e02612ceb52d4b4465fad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="permission")
    def permission(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permission"))

    @permission.setter
    def permission(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e63026be3ed8e7649744c79d63f2438343f40d65ea590b72db4c4efd6989f6f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permission", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scope")
    def scope(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scope"))

    @scope.setter
    def scope(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__087d754132303463a926c238a060c3eec9f0202d6f5b025ac10d6eee1e4c8848)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scope", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResourcesSecret]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResourcesSecret]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResourcesSecret]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c8f9bd574453753cd5f994308cb2df140b63571a6032d44789ebe249b296864)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppResourcesServingEndpoint",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "permission": "permission"},
)
class DataDatabricksAppsAppResourcesServingEndpoint:
    def __init__(self, *, name: builtins.str, permission: builtins.str) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#name DataDatabricksApps#name}.
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#permission DataDatabricksApps#permission}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff5096f1b409063b2eb2973afad09e6aa714c655a2d4365506514cb3a4893ccf)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument permission", value=permission, expected_type=type_hints["permission"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "permission": permission,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#name DataDatabricksApps#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def permission(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#permission DataDatabricksApps#permission}.'''
        result = self._values.get("permission")
        assert result is not None, "Required property 'permission' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppsAppResourcesServingEndpoint(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppsAppResourcesServingEndpointOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppResourcesServingEndpointOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cbf2f2b5e9dc8253ac304a8ca86ca389583381da4076007790eaf116003b63f5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__467785a24515bf01157bb7760edea89fe2b2da97c9fca94fd73105d034c0faca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="permission")
    def permission(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permission"))

    @permission.setter
    def permission(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b286552a83f3544f8fce775b8166b155eed81715e6e0b2cde4a8401b3ad039c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permission", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResourcesServingEndpoint]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResourcesServingEndpoint]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResourcesServingEndpoint]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d9181c5951d0e09869a45ec25d8b777f271595f337e49d54803747be7702c92)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppResourcesSqlWarehouse",
    jsii_struct_bases=[],
    name_mapping={"id": "id", "permission": "permission"},
)
class DataDatabricksAppsAppResourcesSqlWarehouse:
    def __init__(self, *, id: builtins.str, permission: builtins.str) -> None:
        '''
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#id DataDatabricksApps#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#permission DataDatabricksApps#permission}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce8d5796dbd8fc0e3f4fa92e144776349e3bdfdf1076fa96f6dd1996ffd12ea7)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument permission", value=permission, expected_type=type_hints["permission"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
            "permission": permission,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#id DataDatabricksApps#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def permission(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#permission DataDatabricksApps#permission}.'''
        result = self._values.get("permission")
        assert result is not None, "Required property 'permission' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppsAppResourcesSqlWarehouse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppsAppResourcesSqlWarehouseOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppResourcesSqlWarehouseOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bd3cc77086e3681a993d878732657646ff097aab4e016e2f40c78507d49b5383)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a4bbf24a25d276710c8a9bb9c391c3875e7df1e61613a3589c33d30505649db7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="permission")
    def permission(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permission"))

    @permission.setter
    def permission(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__127a39145bbfd35c2e904ee8d430ba4d2193a31df248c062d5b444448913f0b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permission", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResourcesSqlWarehouse]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResourcesSqlWarehouse]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResourcesSqlWarehouse]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f59ea7ae36f9d897c4fdcf03ac0b39e73c6208c56198f7787282b62f6a85ecbd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppResourcesUcSecurable",
    jsii_struct_bases=[],
    name_mapping={
        "permission": "permission",
        "securable_full_name": "securableFullName",
        "securable_type": "securableType",
    },
)
class DataDatabricksAppsAppResourcesUcSecurable:
    def __init__(
        self,
        *,
        permission: builtins.str,
        securable_full_name: builtins.str,
        securable_type: builtins.str,
    ) -> None:
        '''
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#permission DataDatabricksApps#permission}.
        :param securable_full_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#securable_full_name DataDatabricksApps#securable_full_name}.
        :param securable_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#securable_type DataDatabricksApps#securable_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b0acb854e459bc6779171b906c7fc8bafd5eb7a00fb29a4f3caa736feab3733)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#permission DataDatabricksApps#permission}.'''
        result = self._values.get("permission")
        assert result is not None, "Required property 'permission' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def securable_full_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#securable_full_name DataDatabricksApps#securable_full_name}.'''
        result = self._values.get("securable_full_name")
        assert result is not None, "Required property 'securable_full_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def securable_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps#securable_type DataDatabricksApps#securable_type}.'''
        result = self._values.get("securable_type")
        assert result is not None, "Required property 'securable_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppsAppResourcesUcSecurable(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppsAppResourcesUcSecurableOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsAppResourcesUcSecurableOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6a1bc769c8b20479b4b3e3bbf53778d0aae6ca36a9c4940081c76f8bbd62eb7e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3fd92a64290acf4d763187c27a9d29b61f2fc0eeaba433e33a8712b7b62a0b1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permission", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="securableFullName")
    def securable_full_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "securableFullName"))

    @securable_full_name.setter
    def securable_full_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e24a6e98d7f8752a25afde4519c3d2c19f912acb8e5a16e40a587a6ca0eb460)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "securableFullName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="securableType")
    def securable_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "securableType"))

    @securable_type.setter
    def securable_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24ab2f7466aa51bb9ca2d4bc92df35cc927268840f2ab61afea3a7ead4b1ecd2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "securableType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResourcesUcSecurable]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResourcesUcSecurable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResourcesUcSecurable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c96e50a80d1147c641907dfdc6f18fcd52db70f165ad1531b61a283bc20e728d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksApps.DataDatabricksAppsConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
    },
)
class DataDatabricksAppsConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93545533fa4d79c62355d5d25889485d9017a8c862df73bdc7859fc6f2652235)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
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

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataDatabricksApps",
    "DataDatabricksAppsApp",
    "DataDatabricksAppsAppActiveDeployment",
    "DataDatabricksAppsAppActiveDeploymentDeploymentArtifacts",
    "DataDatabricksAppsAppActiveDeploymentDeploymentArtifactsOutputReference",
    "DataDatabricksAppsAppActiveDeploymentOutputReference",
    "DataDatabricksAppsAppActiveDeploymentStatus",
    "DataDatabricksAppsAppActiveDeploymentStatusOutputReference",
    "DataDatabricksAppsAppAppStatus",
    "DataDatabricksAppsAppAppStatusOutputReference",
    "DataDatabricksAppsAppComputeStatus",
    "DataDatabricksAppsAppComputeStatusOutputReference",
    "DataDatabricksAppsAppList",
    "DataDatabricksAppsAppOutputReference",
    "DataDatabricksAppsAppPendingDeployment",
    "DataDatabricksAppsAppPendingDeploymentDeploymentArtifacts",
    "DataDatabricksAppsAppPendingDeploymentDeploymentArtifactsOutputReference",
    "DataDatabricksAppsAppPendingDeploymentOutputReference",
    "DataDatabricksAppsAppPendingDeploymentStatus",
    "DataDatabricksAppsAppPendingDeploymentStatusOutputReference",
    "DataDatabricksAppsAppResources",
    "DataDatabricksAppsAppResourcesDatabase",
    "DataDatabricksAppsAppResourcesDatabaseOutputReference",
    "DataDatabricksAppsAppResourcesJob",
    "DataDatabricksAppsAppResourcesJobOutputReference",
    "DataDatabricksAppsAppResourcesList",
    "DataDatabricksAppsAppResourcesOutputReference",
    "DataDatabricksAppsAppResourcesSecret",
    "DataDatabricksAppsAppResourcesSecretOutputReference",
    "DataDatabricksAppsAppResourcesServingEndpoint",
    "DataDatabricksAppsAppResourcesServingEndpointOutputReference",
    "DataDatabricksAppsAppResourcesSqlWarehouse",
    "DataDatabricksAppsAppResourcesSqlWarehouseOutputReference",
    "DataDatabricksAppsAppResourcesUcSecurable",
    "DataDatabricksAppsAppResourcesUcSecurableOutputReference",
    "DataDatabricksAppsConfig",
]

publication.publish()

def _typecheckingstub__d9d93698de7735f41c60eff12b51fbb30c09ac727b22d30480a191f776b151e8(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
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

def _typecheckingstub__c73ba5ae6f97a984c8ccfb30413c1e5ff7921ef93bbe63550ae541d6077163e6(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3f374e496785c6018b1021fd64679ee0225334871ea795fe6462566967cde96(
    *,
    name: builtins.str,
    budget_policy_id: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    resources: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksAppsAppResources, typing.Dict[builtins.str, typing.Any]]]]] = None,
    user_api_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74c08037689a1b8433e156bd2d8c2e2a8e70311250fec932df969cdbfa4a52f2(
    *,
    deployment_id: typing.Optional[builtins.str] = None,
    mode: typing.Optional[builtins.str] = None,
    source_code_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b95081f0843a5072c1742b2cf0cc51d11d0fee480851b64565f8ac43d025506f(
    *,
    source_code_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8d9e9d52c60510780d08863409a34007a7f9e66c7137a99f934ca4658f882f1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f195ab21cd50a6ca571ac5bf57d46ff2ff3b8e4e0f771afdcf8a8b6ca7728cf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__405cd036db808f72e890633fa1136f650f5df75c13cfd690675f5e8314f5f918(
    value: typing.Optional[DataDatabricksAppsAppActiveDeploymentDeploymentArtifacts],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59b8c0928879f53e5f4650e5c05d659956e3711b241aeda02b98d5e326dbee5f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__243f558f1041d2a3076d952752afc73f735a6cf00eaec19a87f617c79fd4bfb6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__485438f0d38d7fbc26dae5c17878cf74ea72f5da55022d17a5892f48a01fcfd8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f890e8ec65a7aa3d7741ee11a7f197082b768ddf341a5272e49294525fe13b4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46838f1ce9b70f78bbe08104f9d61751d5effed3eff66f01b526b791ddcd0534(
    value: typing.Optional[DataDatabricksAppsAppActiveDeployment],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__608cb2338cb2fd1d1e1190f4f689faacfdfda5e18813899774e32479bd2c402b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0786ee1852fcd29907b92f6613f1fbbaed2ced4d97dd94504cefe84c987afd7c(
    value: typing.Optional[DataDatabricksAppsAppActiveDeploymentStatus],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de5906ce6acb3f83f33d6bacdd9e0776435457252023da5bf79e53b548be4ce3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e864bd30787ecbd79b32ac6087d83ae73a8bb91703c663484ae962d9dbd5ad7c(
    value: typing.Optional[DataDatabricksAppsAppAppStatus],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27f93eb00fe32e0513a9e213f44885102ddbec94ef60d71574aa97395f4265d1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c247e8ce557194641c5d99f3be51320bbfd34852ce9bcf072378386214be909d(
    value: typing.Optional[DataDatabricksAppsAppComputeStatus],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cffabbef0320357eeee12a66e9bb55efd2f82d7b4250f175b2131bb838359863(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fa696204dda6ed0f33d7523ad94bbaf94551047753cf9e0211b2c1502a8e7c2(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62521ccd4ff628e8c3e7c9595af9b38a78948cefd28f43592ddb2ee2badf6e86(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a357b95988f084778aa5c8a170b8cbcdf771624cec9bffccfa05e83d0d9eff00(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__157220e3568457d568a87b54bd16091e37a3e9dfbbbaa72f537c7dcb23f0af96(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54346482493cc9cd91737d4934cf58ff56ba14807e1606159f14cac557e07c0c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAppsApp]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b27fc4f7e444d244a5106d9e68ba94982fab75fab416e1b2f1bc01b18da2f707(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54a4f4f3c6b73d1c2824c8c39808f15e285c08c31601021d189b48b3958b16e7(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksAppsAppResources, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac16fe9a03c850538dc81d587f0020945e74e6b4c60cb1901a5104d77cad00bb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f7cefc9abb71bfb29e91f2be143656ed9c63d9f415bb45d5a125adc90a7920e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc9d34fba6e25ad02bb276652016539a60a2dc0793bc19f7c20a2f0aafc3446d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0707b1ca3f18996d113c44339193e04383c82710c7da559e702ac9c6b17e73cb(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30d282a3f60ad63dc484f71ed65799d8c36bcf4d09941e14bd71ba7f9b070c60(
    value: typing.Optional[DataDatabricksAppsApp],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74abd36acba74130fff14af9a03150b917ecdcc34876a6ec9949a73c635e48e0(
    *,
    deployment_id: typing.Optional[builtins.str] = None,
    mode: typing.Optional[builtins.str] = None,
    source_code_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cda869040ec653f93df1fe74b86ee5043795916619bba961eac4507cf17c9395(
    *,
    source_code_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c95b18dc20af14183b841b7403d12d42ee4aaf4465f327ce8d49305ee00eb41c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c362d037e3bcc6f9dc2f5c6e9349840de90a275953d8435aaa1d2e19614349ea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e512a457acc6998312aab7f9c360de6b39cdbfd3bd1a57a99281f3961ab9f4bd(
    value: typing.Optional[DataDatabricksAppsAppPendingDeploymentDeploymentArtifacts],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6396c5bedcbd8b2484d0a0d9401973ea22010fde95418092fb93e18c0a68048(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28642252c2ec7c36dca40c4d0ac36fc33bbe379ed99c3761774bfdd361eb797a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__401c594563dc11cb37561043f66785bbc8120b1088f1de0ea4fd1f7943796642(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__102fcc3852baf10610da5476617936d33c91e321ce3dd3e9240f6713d1946d85(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a21fc0cb93ccd74edf2af8c4c925256eb44b9a25705da39991a490f6968b0ef3(
    value: typing.Optional[DataDatabricksAppsAppPendingDeployment],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a1f8adc584911bf831b098004a87bf7d367ea0e393d6b4266acd26458d89a6c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5f77f265ea4becfbd09e187ec5544aeb42e1a0f2bdf29c8ecba2d553ce42a14(
    value: typing.Optional[DataDatabricksAppsAppPendingDeploymentStatus],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5528e1b7f5a7b871c2c7edf64cb606cdb1619f1a8a7a89e098e4330fa857e9a4(
    *,
    name: builtins.str,
    database: typing.Optional[typing.Union[DataDatabricksAppsAppResourcesDatabase, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    job: typing.Optional[typing.Union[DataDatabricksAppsAppResourcesJob, typing.Dict[builtins.str, typing.Any]]] = None,
    secret: typing.Optional[typing.Union[DataDatabricksAppsAppResourcesSecret, typing.Dict[builtins.str, typing.Any]]] = None,
    serving_endpoint: typing.Optional[typing.Union[DataDatabricksAppsAppResourcesServingEndpoint, typing.Dict[builtins.str, typing.Any]]] = None,
    sql_warehouse: typing.Optional[typing.Union[DataDatabricksAppsAppResourcesSqlWarehouse, typing.Dict[builtins.str, typing.Any]]] = None,
    uc_securable: typing.Optional[typing.Union[DataDatabricksAppsAppResourcesUcSecurable, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__620e703281ca2fc90dbf06611bde6273362d8c38ee86858409db6a510e119e85(
    *,
    database_name: builtins.str,
    instance_name: builtins.str,
    permission: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba5bd466a14b91b47a9266ff623cc534ee8c562152b2b766954a62804b4684de(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67aee34facdab99722c3f671dcd20b2b9ef8a232dbf7b78ba7ffc2a211249536(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b11400e79ccedf1850bc51312593bedd1df8fd9996e603c083aed4d9bfc76ae3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2edb37f2c3d1ff9aef855ed28d5efa73746dab5e59906e1fc9fb3b418bb17cd6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c4ca1e7ee020d7ca7782e242681e2f205d4e68302ed93dbd5ec1df78dae1998(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResourcesDatabase]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__507f10c33130303588ac4ab69692a08e235f0d205ea3c8a7612682928a409761(
    *,
    id: builtins.str,
    permission: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7996f12373aa25570ab7396f26a49e70fb76de7168776d44c41c8dc47b21771(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__371772580b0c5152dc0c1c51b96da36b590715f958048155eb0103be9ecc7771(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14119329790abdcc3de9d6f43b64841bcffceecd3a78787d7423f7e947365a2d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cc19c9001053238256377b30b1ebd5cf8bce4dce5fb6acf3f35c2b7a0eeb22c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResourcesJob]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c67599862db056e903bceea6d0376a047b656b8a98341cd3534ec1d91dc73c10(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22c65eddcad20e9c27cff9bc063ba95f49ff5a9f7b3f4a5d51072348e3eaebcb(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ac6eb74b03eaff5d5ae2b84ffb624c1dd650e188438eb1c1f691342d22674ea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec3a7967da51cd6f447e634a0da5ec2f8d6b0518038f048fd3bd98cd15cad058(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47cddebc50466c17d0c578d9a86c468bb9dd52b34425898da8e3bd621e034614(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__204b5dd037ef732c2b8b5c2710a175d8d171581f6e5c4a95945b72c65cc19229(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAppsAppResources]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7c03394e799ed312fd58a25c24048ec2003f5cfc67b0dba7b87bddd8a2e74ee(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9b624135934b2884c5772b647b5e8c820c7a18b9f60cee7461c2c927c22da21(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10ec889d618d3e54d9a09bb177d52385c36c983e24272eb1119a82dadb617fa1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__431bf43a96e44364b5ee9624797cf6102460ac93aa652837f30ae67e00033ad7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResources]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e127fd23cba7ea0451afe4229fbd0b6f95759c507373513b914d25ac781fd93e(
    *,
    key: builtins.str,
    permission: builtins.str,
    scope: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bcea2efc4f9ed9e0bfb9892bf908177121ca20665194b9ec53de60e33f56c27(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a3b7dd1017e176c1acfc84a74bc11778f3a8913b11e02612ceb52d4b4465fad(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e63026be3ed8e7649744c79d63f2438343f40d65ea590b72db4c4efd6989f6f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__087d754132303463a926c238a060c3eec9f0202d6f5b025ac10d6eee1e4c8848(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c8f9bd574453753cd5f994308cb2df140b63571a6032d44789ebe249b296864(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResourcesSecret]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff5096f1b409063b2eb2973afad09e6aa714c655a2d4365506514cb3a4893ccf(
    *,
    name: builtins.str,
    permission: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbf2f2b5e9dc8253ac304a8ca86ca389583381da4076007790eaf116003b63f5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__467785a24515bf01157bb7760edea89fe2b2da97c9fca94fd73105d034c0faca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b286552a83f3544f8fce775b8166b155eed81715e6e0b2cde4a8401b3ad039c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d9181c5951d0e09869a45ec25d8b777f271595f337e49d54803747be7702c92(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResourcesServingEndpoint]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce8d5796dbd8fc0e3f4fa92e144776349e3bdfdf1076fa96f6dd1996ffd12ea7(
    *,
    id: builtins.str,
    permission: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd3cc77086e3681a993d878732657646ff097aab4e016e2f40c78507d49b5383(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4bbf24a25d276710c8a9bb9c391c3875e7df1e61613a3589c33d30505649db7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__127a39145bbfd35c2e904ee8d430ba4d2193a31df248c062d5b444448913f0b6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f59ea7ae36f9d897c4fdcf03ac0b39e73c6208c56198f7787282b62f6a85ecbd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResourcesSqlWarehouse]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b0acb854e459bc6779171b906c7fc8bafd5eb7a00fb29a4f3caa736feab3733(
    *,
    permission: builtins.str,
    securable_full_name: builtins.str,
    securable_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a1bc769c8b20479b4b3e3bbf53778d0aae6ca36a9c4940081c76f8bbd62eb7e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fd92a64290acf4d763187c27a9d29b61f2fc0eeaba433e33a8712b7b62a0b1d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e24a6e98d7f8752a25afde4519c3d2c19f912acb8e5a16e40a587a6ca0eb460(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24ab2f7466aa51bb9ca2d4bc92df35cc927268840f2ab61afea3a7ead4b1ecd2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c96e50a80d1147c641907dfdc6f18fcd52db70f165ad1531b61a283bc20e728d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsAppResourcesUcSecurable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93545533fa4d79c62355d5d25889485d9017a8c862df73bdc7859fc6f2652235(
    *,
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
