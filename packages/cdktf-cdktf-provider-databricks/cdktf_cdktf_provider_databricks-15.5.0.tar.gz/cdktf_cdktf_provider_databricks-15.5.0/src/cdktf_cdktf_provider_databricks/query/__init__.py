r'''
# `databricks_query`

Refer to the Terraform Registry for docs: [`databricks_query`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query).
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


class Query(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.query.Query",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query databricks_query}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        display_name: builtins.str,
        query_text: builtins.str,
        warehouse_id: builtins.str,
        apply_auto_limit: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        catalog: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        owner_user_name: typing.Optional[builtins.str] = None,
        parameter: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["QueryParameter", typing.Dict[builtins.str, typing.Any]]]]] = None,
        parent_path: typing.Optional[builtins.str] = None,
        run_as_mode: typing.Optional[builtins.str] = None,
        schema: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query databricks_query} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param display_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#display_name Query#display_name}.
        :param query_text: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#query_text Query#query_text}.
        :param warehouse_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#warehouse_id Query#warehouse_id}.
        :param apply_auto_limit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#apply_auto_limit Query#apply_auto_limit}.
        :param catalog: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#catalog Query#catalog}.
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#description Query#description}.
        :param owner_user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#owner_user_name Query#owner_user_name}.
        :param parameter: parameter block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#parameter Query#parameter}
        :param parent_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#parent_path Query#parent_path}.
        :param run_as_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#run_as_mode Query#run_as_mode}.
        :param schema: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#schema Query#schema}.
        :param tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#tags Query#tags}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e32924934e478c5575df4c9786ca2559e878b7f69042577e01ea683dadb83fe1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = QueryConfig(
            display_name=display_name,
            query_text=query_text,
            warehouse_id=warehouse_id,
            apply_auto_limit=apply_auto_limit,
            catalog=catalog,
            description=description,
            owner_user_name=owner_user_name,
            parameter=parameter,
            parent_path=parent_path,
            run_as_mode=run_as_mode,
            schema=schema,
            tags=tags,
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
        '''Generates CDKTF code for importing a Query resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the Query to import.
        :param import_from_id: The id of the existing Query that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the Query to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc29c362ffe1fa093d733f690a759a59d4f0e48d76ad2425fa3dac60f0c5105c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putParameter")
    def put_parameter(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["QueryParameter", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__136f37c6d894ab814c13191ade241bfeb153744d83bb11a865b6b9d51b765ac2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putParameter", [value]))

    @jsii.member(jsii_name="resetApplyAutoLimit")
    def reset_apply_auto_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApplyAutoLimit", []))

    @jsii.member(jsii_name="resetCatalog")
    def reset_catalog(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCatalog", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetOwnerUserName")
    def reset_owner_user_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOwnerUserName", []))

    @jsii.member(jsii_name="resetParameter")
    def reset_parameter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameter", []))

    @jsii.member(jsii_name="resetParentPath")
    def reset_parent_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParentPath", []))

    @jsii.member(jsii_name="resetRunAsMode")
    def reset_run_as_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunAsMode", []))

    @jsii.member(jsii_name="resetSchema")
    def reset_schema(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchema", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="lastModifierUserName")
    def last_modifier_user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastModifierUserName"))

    @builtins.property
    @jsii.member(jsii_name="lifecycleState")
    def lifecycle_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lifecycleState"))

    @builtins.property
    @jsii.member(jsii_name="parameter")
    def parameter(self) -> "QueryParameterList":
        return typing.cast("QueryParameterList", jsii.get(self, "parameter"))

    @builtins.property
    @jsii.member(jsii_name="updateTime")
    def update_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updateTime"))

    @builtins.property
    @jsii.member(jsii_name="applyAutoLimitInput")
    def apply_auto_limit_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "applyAutoLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="catalogInput")
    def catalog_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "catalogInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="displayNameInput")
    def display_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "displayNameInput"))

    @builtins.property
    @jsii.member(jsii_name="ownerUserNameInput")
    def owner_user_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ownerUserNameInput"))

    @builtins.property
    @jsii.member(jsii_name="parameterInput")
    def parameter_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["QueryParameter"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["QueryParameter"]]], jsii.get(self, "parameterInput"))

    @builtins.property
    @jsii.member(jsii_name="parentPathInput")
    def parent_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parentPathInput"))

    @builtins.property
    @jsii.member(jsii_name="queryTextInput")
    def query_text_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queryTextInput"))

    @builtins.property
    @jsii.member(jsii_name="runAsModeInput")
    def run_as_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "runAsModeInput"))

    @builtins.property
    @jsii.member(jsii_name="schemaInput")
    def schema_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schemaInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="warehouseIdInput")
    def warehouse_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "warehouseIdInput"))

    @builtins.property
    @jsii.member(jsii_name="applyAutoLimit")
    def apply_auto_limit(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "applyAutoLimit"))

    @apply_auto_limit.setter
    def apply_auto_limit(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c018f8fdeaca8d86d0ae08089da1eb3dfca6b38f0b38c6d7da38cccd1426c580)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "applyAutoLimit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="catalog")
    def catalog(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "catalog"))

    @catalog.setter
    def catalog(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa615482ea6fe3e2f839fe31872a8fb44c65096ba072289ba8a7653851c3ef88)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "catalog", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e7442aaa4700804fded49c678fba7ac230420cce498adbb129a31f691aad3d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "displayName"))

    @display_name.setter
    def display_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d81689bba2ab03997c5585019d83dcb44ea92738c6b31b22f4074566bd0138f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "displayName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ownerUserName")
    def owner_user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ownerUserName"))

    @owner_user_name.setter
    def owner_user_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__776d3601e757a01b3b1f6c3ca637f1b3f0222b3fedc39de1a2bbf86a57f351ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ownerUserName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parentPath")
    def parent_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parentPath"))

    @parent_path.setter
    def parent_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06fbb8219d910d29ebe60c49d807152aec533eb0af5bd0d28ab2b00533a2680b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parentPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="queryText")
    def query_text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queryText"))

    @query_text.setter
    def query_text(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56dce5f5eb9124b595b1563a5d0356ad58d8426fd1248f0ca3c36a63d4df5e90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "queryText", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runAsMode")
    def run_as_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runAsMode"))

    @run_as_mode.setter
    def run_as_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b791528085ef395e7eadb42d89e590aae4a0b7e520b5c262dfdbdbea19f0861e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runAsMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="schema")
    def schema(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schema"))

    @schema.setter
    def schema(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04585c9e15a9d96e47b3f18ec576259e1f710869c64257b6f46403d0976171c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "schema", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2939570ba0bb0f4ac8b1c430eed545fa6630d93dc70903dfa50b797e8c1bf081)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="warehouseId")
    def warehouse_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "warehouseId"))

    @warehouse_id.setter
    def warehouse_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8fd47699594888cd148511232f92205c867c5458a441b5e4ab4fab0d1754fc9c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "warehouseId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.query.QueryConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "display_name": "displayName",
        "query_text": "queryText",
        "warehouse_id": "warehouseId",
        "apply_auto_limit": "applyAutoLimit",
        "catalog": "catalog",
        "description": "description",
        "owner_user_name": "ownerUserName",
        "parameter": "parameter",
        "parent_path": "parentPath",
        "run_as_mode": "runAsMode",
        "schema": "schema",
        "tags": "tags",
    },
)
class QueryConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        display_name: builtins.str,
        query_text: builtins.str,
        warehouse_id: builtins.str,
        apply_auto_limit: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        catalog: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        owner_user_name: typing.Optional[builtins.str] = None,
        parameter: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["QueryParameter", typing.Dict[builtins.str, typing.Any]]]]] = None,
        parent_path: typing.Optional[builtins.str] = None,
        run_as_mode: typing.Optional[builtins.str] = None,
        schema: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param display_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#display_name Query#display_name}.
        :param query_text: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#query_text Query#query_text}.
        :param warehouse_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#warehouse_id Query#warehouse_id}.
        :param apply_auto_limit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#apply_auto_limit Query#apply_auto_limit}.
        :param catalog: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#catalog Query#catalog}.
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#description Query#description}.
        :param owner_user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#owner_user_name Query#owner_user_name}.
        :param parameter: parameter block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#parameter Query#parameter}
        :param parent_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#parent_path Query#parent_path}.
        :param run_as_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#run_as_mode Query#run_as_mode}.
        :param schema: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#schema Query#schema}.
        :param tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#tags Query#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27390797363df912885414bf0e6ddf85bd55b990d2559783c8a4249c06b2d473)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument display_name", value=display_name, expected_type=type_hints["display_name"])
            check_type(argname="argument query_text", value=query_text, expected_type=type_hints["query_text"])
            check_type(argname="argument warehouse_id", value=warehouse_id, expected_type=type_hints["warehouse_id"])
            check_type(argname="argument apply_auto_limit", value=apply_auto_limit, expected_type=type_hints["apply_auto_limit"])
            check_type(argname="argument catalog", value=catalog, expected_type=type_hints["catalog"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument owner_user_name", value=owner_user_name, expected_type=type_hints["owner_user_name"])
            check_type(argname="argument parameter", value=parameter, expected_type=type_hints["parameter"])
            check_type(argname="argument parent_path", value=parent_path, expected_type=type_hints["parent_path"])
            check_type(argname="argument run_as_mode", value=run_as_mode, expected_type=type_hints["run_as_mode"])
            check_type(argname="argument schema", value=schema, expected_type=type_hints["schema"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "display_name": display_name,
            "query_text": query_text,
            "warehouse_id": warehouse_id,
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
        if apply_auto_limit is not None:
            self._values["apply_auto_limit"] = apply_auto_limit
        if catalog is not None:
            self._values["catalog"] = catalog
        if description is not None:
            self._values["description"] = description
        if owner_user_name is not None:
            self._values["owner_user_name"] = owner_user_name
        if parameter is not None:
            self._values["parameter"] = parameter
        if parent_path is not None:
            self._values["parent_path"] = parent_path
        if run_as_mode is not None:
            self._values["run_as_mode"] = run_as_mode
        if schema is not None:
            self._values["schema"] = schema
        if tags is not None:
            self._values["tags"] = tags

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
    def display_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#display_name Query#display_name}.'''
        result = self._values.get("display_name")
        assert result is not None, "Required property 'display_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def query_text(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#query_text Query#query_text}.'''
        result = self._values.get("query_text")
        assert result is not None, "Required property 'query_text' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def warehouse_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#warehouse_id Query#warehouse_id}.'''
        result = self._values.get("warehouse_id")
        assert result is not None, "Required property 'warehouse_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def apply_auto_limit(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#apply_auto_limit Query#apply_auto_limit}.'''
        result = self._values.get("apply_auto_limit")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def catalog(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#catalog Query#catalog}.'''
        result = self._values.get("catalog")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#description Query#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def owner_user_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#owner_user_name Query#owner_user_name}.'''
        result = self._values.get("owner_user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameter(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["QueryParameter"]]]:
        '''parameter block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#parameter Query#parameter}
        '''
        result = self._values.get("parameter")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["QueryParameter"]]], result)

    @builtins.property
    def parent_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#parent_path Query#parent_path}.'''
        result = self._values.get("parent_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def run_as_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#run_as_mode Query#run_as_mode}.'''
        result = self._values.get("run_as_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def schema(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#schema Query#schema}.'''
        result = self._values.get("schema")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#tags Query#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QueryConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.query.QueryParameter",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "date_range_value": "dateRangeValue",
        "date_value": "dateValue",
        "enum_value": "enumValue",
        "numeric_value": "numericValue",
        "query_backed_value": "queryBackedValue",
        "text_value": "textValue",
        "title": "title",
    },
)
class QueryParameter:
    def __init__(
        self,
        *,
        name: builtins.str,
        date_range_value: typing.Optional[typing.Union["QueryParameterDateRangeValue", typing.Dict[builtins.str, typing.Any]]] = None,
        date_value: typing.Optional[typing.Union["QueryParameterDateValue", typing.Dict[builtins.str, typing.Any]]] = None,
        enum_value: typing.Optional[typing.Union["QueryParameterEnumValue", typing.Dict[builtins.str, typing.Any]]] = None,
        numeric_value: typing.Optional[typing.Union["QueryParameterNumericValue", typing.Dict[builtins.str, typing.Any]]] = None,
        query_backed_value: typing.Optional[typing.Union["QueryParameterQueryBackedValue", typing.Dict[builtins.str, typing.Any]]] = None,
        text_value: typing.Optional[typing.Union["QueryParameterTextValue", typing.Dict[builtins.str, typing.Any]]] = None,
        title: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#name Query#name}.
        :param date_range_value: date_range_value block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#date_range_value Query#date_range_value}
        :param date_value: date_value block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#date_value Query#date_value}
        :param enum_value: enum_value block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#enum_value Query#enum_value}
        :param numeric_value: numeric_value block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#numeric_value Query#numeric_value}
        :param query_backed_value: query_backed_value block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#query_backed_value Query#query_backed_value}
        :param text_value: text_value block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#text_value Query#text_value}
        :param title: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#title Query#title}.
        '''
        if isinstance(date_range_value, dict):
            date_range_value = QueryParameterDateRangeValue(**date_range_value)
        if isinstance(date_value, dict):
            date_value = QueryParameterDateValue(**date_value)
        if isinstance(enum_value, dict):
            enum_value = QueryParameterEnumValue(**enum_value)
        if isinstance(numeric_value, dict):
            numeric_value = QueryParameterNumericValue(**numeric_value)
        if isinstance(query_backed_value, dict):
            query_backed_value = QueryParameterQueryBackedValue(**query_backed_value)
        if isinstance(text_value, dict):
            text_value = QueryParameterTextValue(**text_value)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e846acabd00385a57bd8fbf4beab90319d8099522975de4cd90ab91e7ecb39b)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument date_range_value", value=date_range_value, expected_type=type_hints["date_range_value"])
            check_type(argname="argument date_value", value=date_value, expected_type=type_hints["date_value"])
            check_type(argname="argument enum_value", value=enum_value, expected_type=type_hints["enum_value"])
            check_type(argname="argument numeric_value", value=numeric_value, expected_type=type_hints["numeric_value"])
            check_type(argname="argument query_backed_value", value=query_backed_value, expected_type=type_hints["query_backed_value"])
            check_type(argname="argument text_value", value=text_value, expected_type=type_hints["text_value"])
            check_type(argname="argument title", value=title, expected_type=type_hints["title"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if date_range_value is not None:
            self._values["date_range_value"] = date_range_value
        if date_value is not None:
            self._values["date_value"] = date_value
        if enum_value is not None:
            self._values["enum_value"] = enum_value
        if numeric_value is not None:
            self._values["numeric_value"] = numeric_value
        if query_backed_value is not None:
            self._values["query_backed_value"] = query_backed_value
        if text_value is not None:
            self._values["text_value"] = text_value
        if title is not None:
            self._values["title"] = title

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#name Query#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def date_range_value(self) -> typing.Optional["QueryParameterDateRangeValue"]:
        '''date_range_value block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#date_range_value Query#date_range_value}
        '''
        result = self._values.get("date_range_value")
        return typing.cast(typing.Optional["QueryParameterDateRangeValue"], result)

    @builtins.property
    def date_value(self) -> typing.Optional["QueryParameterDateValue"]:
        '''date_value block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#date_value Query#date_value}
        '''
        result = self._values.get("date_value")
        return typing.cast(typing.Optional["QueryParameterDateValue"], result)

    @builtins.property
    def enum_value(self) -> typing.Optional["QueryParameterEnumValue"]:
        '''enum_value block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#enum_value Query#enum_value}
        '''
        result = self._values.get("enum_value")
        return typing.cast(typing.Optional["QueryParameterEnumValue"], result)

    @builtins.property
    def numeric_value(self) -> typing.Optional["QueryParameterNumericValue"]:
        '''numeric_value block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#numeric_value Query#numeric_value}
        '''
        result = self._values.get("numeric_value")
        return typing.cast(typing.Optional["QueryParameterNumericValue"], result)

    @builtins.property
    def query_backed_value(self) -> typing.Optional["QueryParameterQueryBackedValue"]:
        '''query_backed_value block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#query_backed_value Query#query_backed_value}
        '''
        result = self._values.get("query_backed_value")
        return typing.cast(typing.Optional["QueryParameterQueryBackedValue"], result)

    @builtins.property
    def text_value(self) -> typing.Optional["QueryParameterTextValue"]:
        '''text_value block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#text_value Query#text_value}
        '''
        result = self._values.get("text_value")
        return typing.cast(typing.Optional["QueryParameterTextValue"], result)

    @builtins.property
    def title(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#title Query#title}.'''
        result = self._values.get("title")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QueryParameter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.query.QueryParameterDateRangeValue",
    jsii_struct_bases=[],
    name_mapping={
        "date_range_value": "dateRangeValue",
        "dynamic_date_range_value": "dynamicDateRangeValue",
        "precision": "precision",
        "start_day_of_week": "startDayOfWeek",
    },
)
class QueryParameterDateRangeValue:
    def __init__(
        self,
        *,
        date_range_value: typing.Optional[typing.Union["QueryParameterDateRangeValueDateRangeValue", typing.Dict[builtins.str, typing.Any]]] = None,
        dynamic_date_range_value: typing.Optional[builtins.str] = None,
        precision: typing.Optional[builtins.str] = None,
        start_day_of_week: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param date_range_value: date_range_value block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#date_range_value Query#date_range_value}
        :param dynamic_date_range_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#dynamic_date_range_value Query#dynamic_date_range_value}.
        :param precision: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#precision Query#precision}.
        :param start_day_of_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#start_day_of_week Query#start_day_of_week}.
        '''
        if isinstance(date_range_value, dict):
            date_range_value = QueryParameterDateRangeValueDateRangeValue(**date_range_value)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e5ef48823cd3d6615c68ac64d116fb4eb5a4f24b3e846107185f9bb6cdf1051)
            check_type(argname="argument date_range_value", value=date_range_value, expected_type=type_hints["date_range_value"])
            check_type(argname="argument dynamic_date_range_value", value=dynamic_date_range_value, expected_type=type_hints["dynamic_date_range_value"])
            check_type(argname="argument precision", value=precision, expected_type=type_hints["precision"])
            check_type(argname="argument start_day_of_week", value=start_day_of_week, expected_type=type_hints["start_day_of_week"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if date_range_value is not None:
            self._values["date_range_value"] = date_range_value
        if dynamic_date_range_value is not None:
            self._values["dynamic_date_range_value"] = dynamic_date_range_value
        if precision is not None:
            self._values["precision"] = precision
        if start_day_of_week is not None:
            self._values["start_day_of_week"] = start_day_of_week

    @builtins.property
    def date_range_value(
        self,
    ) -> typing.Optional["QueryParameterDateRangeValueDateRangeValue"]:
        '''date_range_value block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#date_range_value Query#date_range_value}
        '''
        result = self._values.get("date_range_value")
        return typing.cast(typing.Optional["QueryParameterDateRangeValueDateRangeValue"], result)

    @builtins.property
    def dynamic_date_range_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#dynamic_date_range_value Query#dynamic_date_range_value}.'''
        result = self._values.get("dynamic_date_range_value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def precision(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#precision Query#precision}.'''
        result = self._values.get("precision")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def start_day_of_week(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#start_day_of_week Query#start_day_of_week}.'''
        result = self._values.get("start_day_of_week")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QueryParameterDateRangeValue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.query.QueryParameterDateRangeValueDateRangeValue",
    jsii_struct_bases=[],
    name_mapping={"end": "end", "start": "start"},
)
class QueryParameterDateRangeValueDateRangeValue:
    def __init__(self, *, end: builtins.str, start: builtins.str) -> None:
        '''
        :param end: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#end Query#end}.
        :param start: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#start Query#start}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__243c90edfdf7d26b7215bd427208a644a4b65d7f51f8c937c18de5e5d6be9f21)
            check_type(argname="argument end", value=end, expected_type=type_hints["end"])
            check_type(argname="argument start", value=start, expected_type=type_hints["start"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "end": end,
            "start": start,
        }

    @builtins.property
    def end(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#end Query#end}.'''
        result = self._values.get("end")
        assert result is not None, "Required property 'end' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def start(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#start Query#start}.'''
        result = self._values.get("start")
        assert result is not None, "Required property 'start' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QueryParameterDateRangeValueDateRangeValue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QueryParameterDateRangeValueDateRangeValueOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.query.QueryParameterDateRangeValueDateRangeValueOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d31c309ce6f024a9d7763a4e962819f597d4bbc42935aa0ba52c5e242e477d2e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="endInput")
    def end_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endInput"))

    @builtins.property
    @jsii.member(jsii_name="startInput")
    def start_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "startInput"))

    @builtins.property
    @jsii.member(jsii_name="end")
    def end(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "end"))

    @end.setter
    def end(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36ed08693726c4da8b4aa727fcbada4c5b0b083199a5d12e5923593bd2bb120c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "end", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="start")
    def start(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "start"))

    @start.setter
    def start(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ccaf2fa82a2823ebe40fb312237aa62f29cfe10a20b385870d2610e17ae59efe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "start", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[QueryParameterDateRangeValueDateRangeValue]:
        return typing.cast(typing.Optional[QueryParameterDateRangeValueDateRangeValue], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QueryParameterDateRangeValueDateRangeValue],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__214c5e6add6f3deb4d14eeba09b34c62202b9a717126f50c90af8fcd3c7ff9fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class QueryParameterDateRangeValueOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.query.QueryParameterDateRangeValueOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d8e8ae8473cde8d880f466cd767af828bbc90eadd091ceee41dabb69876cd85d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putDateRangeValue")
    def put_date_range_value(self, *, end: builtins.str, start: builtins.str) -> None:
        '''
        :param end: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#end Query#end}.
        :param start: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#start Query#start}.
        '''
        value = QueryParameterDateRangeValueDateRangeValue(end=end, start=start)

        return typing.cast(None, jsii.invoke(self, "putDateRangeValue", [value]))

    @jsii.member(jsii_name="resetDateRangeValue")
    def reset_date_range_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDateRangeValue", []))

    @jsii.member(jsii_name="resetDynamicDateRangeValue")
    def reset_dynamic_date_range_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDynamicDateRangeValue", []))

    @jsii.member(jsii_name="resetPrecision")
    def reset_precision(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrecision", []))

    @jsii.member(jsii_name="resetStartDayOfWeek")
    def reset_start_day_of_week(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartDayOfWeek", []))

    @builtins.property
    @jsii.member(jsii_name="dateRangeValue")
    def date_range_value(
        self,
    ) -> QueryParameterDateRangeValueDateRangeValueOutputReference:
        return typing.cast(QueryParameterDateRangeValueDateRangeValueOutputReference, jsii.get(self, "dateRangeValue"))

    @builtins.property
    @jsii.member(jsii_name="dateRangeValueInput")
    def date_range_value_input(
        self,
    ) -> typing.Optional[QueryParameterDateRangeValueDateRangeValue]:
        return typing.cast(typing.Optional[QueryParameterDateRangeValueDateRangeValue], jsii.get(self, "dateRangeValueInput"))

    @builtins.property
    @jsii.member(jsii_name="dynamicDateRangeValueInput")
    def dynamic_date_range_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dynamicDateRangeValueInput"))

    @builtins.property
    @jsii.member(jsii_name="precisionInput")
    def precision_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "precisionInput"))

    @builtins.property
    @jsii.member(jsii_name="startDayOfWeekInput")
    def start_day_of_week_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "startDayOfWeekInput"))

    @builtins.property
    @jsii.member(jsii_name="dynamicDateRangeValue")
    def dynamic_date_range_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dynamicDateRangeValue"))

    @dynamic_date_range_value.setter
    def dynamic_date_range_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b135f76db994b3e75db55eb0d42886aa67ac393e3023c4577eb4553b9f43259d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dynamicDateRangeValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="precision")
    def precision(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "precision"))

    @precision.setter
    def precision(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f1646fcd9d6bcc5d1731e0a8f82913a7e87c31168904f1c97978c6d6050514f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "precision", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startDayOfWeek")
    def start_day_of_week(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "startDayOfWeek"))

    @start_day_of_week.setter
    def start_day_of_week(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b03a8a0cf9bd483bb332b6a1b58ed6f322c033dec1a1cd26bbcc36f9730d5ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startDayOfWeek", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[QueryParameterDateRangeValue]:
        return typing.cast(typing.Optional[QueryParameterDateRangeValue], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QueryParameterDateRangeValue],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fceaa8c05ace558f64f69cb0b362a5e75be102579a1fb5843e8accabe4446ff3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.query.QueryParameterDateValue",
    jsii_struct_bases=[],
    name_mapping={
        "date_value": "dateValue",
        "dynamic_date_value": "dynamicDateValue",
        "precision": "precision",
    },
)
class QueryParameterDateValue:
    def __init__(
        self,
        *,
        date_value: typing.Optional[builtins.str] = None,
        dynamic_date_value: typing.Optional[builtins.str] = None,
        precision: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param date_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#date_value Query#date_value}.
        :param dynamic_date_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#dynamic_date_value Query#dynamic_date_value}.
        :param precision: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#precision Query#precision}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6c6dbbd4f9017cb5dbb1de88f0cedb81a1c3f6f13f4881ddae918fe7ff436b1)
            check_type(argname="argument date_value", value=date_value, expected_type=type_hints["date_value"])
            check_type(argname="argument dynamic_date_value", value=dynamic_date_value, expected_type=type_hints["dynamic_date_value"])
            check_type(argname="argument precision", value=precision, expected_type=type_hints["precision"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if date_value is not None:
            self._values["date_value"] = date_value
        if dynamic_date_value is not None:
            self._values["dynamic_date_value"] = dynamic_date_value
        if precision is not None:
            self._values["precision"] = precision

    @builtins.property
    def date_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#date_value Query#date_value}.'''
        result = self._values.get("date_value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dynamic_date_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#dynamic_date_value Query#dynamic_date_value}.'''
        result = self._values.get("dynamic_date_value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def precision(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#precision Query#precision}.'''
        result = self._values.get("precision")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QueryParameterDateValue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QueryParameterDateValueOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.query.QueryParameterDateValueOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ee39a41f4b08575ff09cf192a1eb1b63c986bf7a7f9ccccdebbcca6c1dd66aff)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDateValue")
    def reset_date_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDateValue", []))

    @jsii.member(jsii_name="resetDynamicDateValue")
    def reset_dynamic_date_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDynamicDateValue", []))

    @jsii.member(jsii_name="resetPrecision")
    def reset_precision(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrecision", []))

    @builtins.property
    @jsii.member(jsii_name="dateValueInput")
    def date_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dateValueInput"))

    @builtins.property
    @jsii.member(jsii_name="dynamicDateValueInput")
    def dynamic_date_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dynamicDateValueInput"))

    @builtins.property
    @jsii.member(jsii_name="precisionInput")
    def precision_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "precisionInput"))

    @builtins.property
    @jsii.member(jsii_name="dateValue")
    def date_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dateValue"))

    @date_value.setter
    def date_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f859b452531a77250d868d10c90c2d5841b80f90791784257796008a7a347b66)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dateValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dynamicDateValue")
    def dynamic_date_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dynamicDateValue"))

    @dynamic_date_value.setter
    def dynamic_date_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f8bb5feb8b551ac04de009ff57e6f3e478049e157bbcc944e2ee36272b75b69)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dynamicDateValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="precision")
    def precision(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "precision"))

    @precision.setter
    def precision(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45e1ffa637877505dbd76de8821ecd516a0aac222f72d03a61507a3364fad8d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "precision", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[QueryParameterDateValue]:
        return typing.cast(typing.Optional[QueryParameterDateValue], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[QueryParameterDateValue]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbc130439bce9f136a65c7dc5f77c3dd3f31e102c38c4a69fb970fe3c1477530)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.query.QueryParameterEnumValue",
    jsii_struct_bases=[],
    name_mapping={
        "enum_options": "enumOptions",
        "multi_values_options": "multiValuesOptions",
        "values": "values",
    },
)
class QueryParameterEnumValue:
    def __init__(
        self,
        *,
        enum_options: typing.Optional[builtins.str] = None,
        multi_values_options: typing.Optional[typing.Union["QueryParameterEnumValueMultiValuesOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        values: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param enum_options: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#enum_options Query#enum_options}.
        :param multi_values_options: multi_values_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#multi_values_options Query#multi_values_options}
        :param values: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#values Query#values}.
        '''
        if isinstance(multi_values_options, dict):
            multi_values_options = QueryParameterEnumValueMultiValuesOptions(**multi_values_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcd8a5c0e0b22ea2c7436de1c960a25ffda5970937d4ad0509168641a0332ec1)
            check_type(argname="argument enum_options", value=enum_options, expected_type=type_hints["enum_options"])
            check_type(argname="argument multi_values_options", value=multi_values_options, expected_type=type_hints["multi_values_options"])
            check_type(argname="argument values", value=values, expected_type=type_hints["values"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enum_options is not None:
            self._values["enum_options"] = enum_options
        if multi_values_options is not None:
            self._values["multi_values_options"] = multi_values_options
        if values is not None:
            self._values["values"] = values

    @builtins.property
    def enum_options(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#enum_options Query#enum_options}.'''
        result = self._values.get("enum_options")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def multi_values_options(
        self,
    ) -> typing.Optional["QueryParameterEnumValueMultiValuesOptions"]:
        '''multi_values_options block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#multi_values_options Query#multi_values_options}
        '''
        result = self._values.get("multi_values_options")
        return typing.cast(typing.Optional["QueryParameterEnumValueMultiValuesOptions"], result)

    @builtins.property
    def values(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#values Query#values}.'''
        result = self._values.get("values")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QueryParameterEnumValue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.query.QueryParameterEnumValueMultiValuesOptions",
    jsii_struct_bases=[],
    name_mapping={"prefix": "prefix", "separator": "separator", "suffix": "suffix"},
)
class QueryParameterEnumValueMultiValuesOptions:
    def __init__(
        self,
        *,
        prefix: typing.Optional[builtins.str] = None,
        separator: typing.Optional[builtins.str] = None,
        suffix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#prefix Query#prefix}.
        :param separator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#separator Query#separator}.
        :param suffix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#suffix Query#suffix}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__079cc49d37489dba69b2c9928feacd9ffe0fafefc22bbb1103e47a73f86947c4)
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
            check_type(argname="argument separator", value=separator, expected_type=type_hints["separator"])
            check_type(argname="argument suffix", value=suffix, expected_type=type_hints["suffix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if prefix is not None:
            self._values["prefix"] = prefix
        if separator is not None:
            self._values["separator"] = separator
        if suffix is not None:
            self._values["suffix"] = suffix

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#prefix Query#prefix}.'''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def separator(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#separator Query#separator}.'''
        result = self._values.get("separator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def suffix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#suffix Query#suffix}.'''
        result = self._values.get("suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QueryParameterEnumValueMultiValuesOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QueryParameterEnumValueMultiValuesOptionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.query.QueryParameterEnumValueMultiValuesOptionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7eb354e9f4127b03895c7427287adf18e4b31c0ac6565965900ca6b27a4e0079)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetPrefix")
    def reset_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefix", []))

    @jsii.member(jsii_name="resetSeparator")
    def reset_separator(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSeparator", []))

    @jsii.member(jsii_name="resetSuffix")
    def reset_suffix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSuffix", []))

    @builtins.property
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prefixInput"))

    @builtins.property
    @jsii.member(jsii_name="separatorInput")
    def separator_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "separatorInput"))

    @builtins.property
    @jsii.member(jsii_name="suffixInput")
    def suffix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "suffixInput"))

    @builtins.property
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa4efa8c31c2bf92c5cf4ee1be5f478130a3d8fa1238765a02d84ada7097cca6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "prefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="separator")
    def separator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "separator"))

    @separator.setter
    def separator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fd8e0a0bfb23e43d80e03160435104571c51c46b72a847de8f5e40b82540d7e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "separator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="suffix")
    def suffix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "suffix"))

    @suffix.setter
    def suffix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3cd36db946a853d9bf805f584653e47cfd6adf4c152ce82bbc4200ef3ef11723)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "suffix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[QueryParameterEnumValueMultiValuesOptions]:
        return typing.cast(typing.Optional[QueryParameterEnumValueMultiValuesOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QueryParameterEnumValueMultiValuesOptions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9616decc58289c5ed1bdebddd983f81bccab4fb3b1e4331713d6b9709e7afe79)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class QueryParameterEnumValueOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.query.QueryParameterEnumValueOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a504ded86f85ac67d0fb974dd4968901622269b46cb1af07ff1428cd591a77f2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putMultiValuesOptions")
    def put_multi_values_options(
        self,
        *,
        prefix: typing.Optional[builtins.str] = None,
        separator: typing.Optional[builtins.str] = None,
        suffix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#prefix Query#prefix}.
        :param separator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#separator Query#separator}.
        :param suffix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#suffix Query#suffix}.
        '''
        value = QueryParameterEnumValueMultiValuesOptions(
            prefix=prefix, separator=separator, suffix=suffix
        )

        return typing.cast(None, jsii.invoke(self, "putMultiValuesOptions", [value]))

    @jsii.member(jsii_name="resetEnumOptions")
    def reset_enum_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnumOptions", []))

    @jsii.member(jsii_name="resetMultiValuesOptions")
    def reset_multi_values_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMultiValuesOptions", []))

    @jsii.member(jsii_name="resetValues")
    def reset_values(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValues", []))

    @builtins.property
    @jsii.member(jsii_name="multiValuesOptions")
    def multi_values_options(
        self,
    ) -> QueryParameterEnumValueMultiValuesOptionsOutputReference:
        return typing.cast(QueryParameterEnumValueMultiValuesOptionsOutputReference, jsii.get(self, "multiValuesOptions"))

    @builtins.property
    @jsii.member(jsii_name="enumOptionsInput")
    def enum_options_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "enumOptionsInput"))

    @builtins.property
    @jsii.member(jsii_name="multiValuesOptionsInput")
    def multi_values_options_input(
        self,
    ) -> typing.Optional[QueryParameterEnumValueMultiValuesOptions]:
        return typing.cast(typing.Optional[QueryParameterEnumValueMultiValuesOptions], jsii.get(self, "multiValuesOptionsInput"))

    @builtins.property
    @jsii.member(jsii_name="valuesInput")
    def values_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "valuesInput"))

    @builtins.property
    @jsii.member(jsii_name="enumOptions")
    def enum_options(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "enumOptions"))

    @enum_options.setter
    def enum_options(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b086f01a3bd648b955d41f24c01cc36997fce08e76281c892be3ace4094ff049)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enumOptions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="values")
    def values(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "values"))

    @values.setter
    def values(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb3e2b59a1b941a526a385df0e880e9409525f47c3fafe931239a18e0143cfad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "values", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[QueryParameterEnumValue]:
        return typing.cast(typing.Optional[QueryParameterEnumValue], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[QueryParameterEnumValue]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c28b5e936014d448fe643303f2d19c3e53f70ba122c5b172251d61758addb83b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class QueryParameterList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.query.QueryParameterList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d6dd585ae82d3c92066204f959dc5f5678076ab0e8137d58d5b1610cd9b2768f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "QueryParameterOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__220d15014a62124d4244dac2022c3588c97acf8c150c431b7a02a1f097814e06)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("QueryParameterOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80482534eede85499b8005ca55f5552d5a10aea156d7f3245a8162b234e77e1e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d9bdb34519b239a81a805e2cc819be4afcc29f677eed2418cc001e2da9153419)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c41ae6d10202705862150bd1baad45c815e0f1ade3ecfaab2bece88a954d4c0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[QueryParameter]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[QueryParameter]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[QueryParameter]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__632ec8b68a34c1c73d263adde724e2f362586898ff726860816dd81400d34524)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.query.QueryParameterNumericValue",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class QueryParameterNumericValue:
    def __init__(self, *, value: jsii.Number) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#value Query#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__237e48018a4394f4a59709e27c8e75664c4794064c13785151d4e4c73b305b4e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "value": value,
        }

    @builtins.property
    def value(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#value Query#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QueryParameterNumericValue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QueryParameterNumericValueOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.query.QueryParameterNumericValueOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__784abf6ffa9622aacc6cadfe76327a4842f3b4ed465dd723d4b22e4565ecd7df)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "value"))

    @value.setter
    def value(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40c83bdb5c9540633252165d0c6fb3793a508582629907dc595c38be675942ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[QueryParameterNumericValue]:
        return typing.cast(typing.Optional[QueryParameterNumericValue], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QueryParameterNumericValue],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a2bfe9f9b9d4608f4723b040d06511f1f90966d4ee60aed21e097ff88f75726)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class QueryParameterOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.query.QueryParameterOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__42e8afd7d7eea0260b998ab452cd85f37c195e605dbb0fc5c1033a3f2497cd58)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putDateRangeValue")
    def put_date_range_value(
        self,
        *,
        date_range_value: typing.Optional[typing.Union[QueryParameterDateRangeValueDateRangeValue, typing.Dict[builtins.str, typing.Any]]] = None,
        dynamic_date_range_value: typing.Optional[builtins.str] = None,
        precision: typing.Optional[builtins.str] = None,
        start_day_of_week: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param date_range_value: date_range_value block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#date_range_value Query#date_range_value}
        :param dynamic_date_range_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#dynamic_date_range_value Query#dynamic_date_range_value}.
        :param precision: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#precision Query#precision}.
        :param start_day_of_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#start_day_of_week Query#start_day_of_week}.
        '''
        value = QueryParameterDateRangeValue(
            date_range_value=date_range_value,
            dynamic_date_range_value=dynamic_date_range_value,
            precision=precision,
            start_day_of_week=start_day_of_week,
        )

        return typing.cast(None, jsii.invoke(self, "putDateRangeValue", [value]))

    @jsii.member(jsii_name="putDateValue")
    def put_date_value(
        self,
        *,
        date_value: typing.Optional[builtins.str] = None,
        dynamic_date_value: typing.Optional[builtins.str] = None,
        precision: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param date_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#date_value Query#date_value}.
        :param dynamic_date_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#dynamic_date_value Query#dynamic_date_value}.
        :param precision: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#precision Query#precision}.
        '''
        value = QueryParameterDateValue(
            date_value=date_value,
            dynamic_date_value=dynamic_date_value,
            precision=precision,
        )

        return typing.cast(None, jsii.invoke(self, "putDateValue", [value]))

    @jsii.member(jsii_name="putEnumValue")
    def put_enum_value(
        self,
        *,
        enum_options: typing.Optional[builtins.str] = None,
        multi_values_options: typing.Optional[typing.Union[QueryParameterEnumValueMultiValuesOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        values: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param enum_options: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#enum_options Query#enum_options}.
        :param multi_values_options: multi_values_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#multi_values_options Query#multi_values_options}
        :param values: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#values Query#values}.
        '''
        value = QueryParameterEnumValue(
            enum_options=enum_options,
            multi_values_options=multi_values_options,
            values=values,
        )

        return typing.cast(None, jsii.invoke(self, "putEnumValue", [value]))

    @jsii.member(jsii_name="putNumericValue")
    def put_numeric_value(self, *, value: jsii.Number) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#value Query#value}.
        '''
        value_ = QueryParameterNumericValue(value=value)

        return typing.cast(None, jsii.invoke(self, "putNumericValue", [value_]))

    @jsii.member(jsii_name="putQueryBackedValue")
    def put_query_backed_value(
        self,
        *,
        query_id: builtins.str,
        multi_values_options: typing.Optional[typing.Union["QueryParameterQueryBackedValueMultiValuesOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        values: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param query_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#query_id Query#query_id}.
        :param multi_values_options: multi_values_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#multi_values_options Query#multi_values_options}
        :param values: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#values Query#values}.
        '''
        value = QueryParameterQueryBackedValue(
            query_id=query_id, multi_values_options=multi_values_options, values=values
        )

        return typing.cast(None, jsii.invoke(self, "putQueryBackedValue", [value]))

    @jsii.member(jsii_name="putTextValue")
    def put_text_value(self, *, value: builtins.str) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#value Query#value}.
        '''
        value_ = QueryParameterTextValue(value=value)

        return typing.cast(None, jsii.invoke(self, "putTextValue", [value_]))

    @jsii.member(jsii_name="resetDateRangeValue")
    def reset_date_range_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDateRangeValue", []))

    @jsii.member(jsii_name="resetDateValue")
    def reset_date_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDateValue", []))

    @jsii.member(jsii_name="resetEnumValue")
    def reset_enum_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnumValue", []))

    @jsii.member(jsii_name="resetNumericValue")
    def reset_numeric_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumericValue", []))

    @jsii.member(jsii_name="resetQueryBackedValue")
    def reset_query_backed_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQueryBackedValue", []))

    @jsii.member(jsii_name="resetTextValue")
    def reset_text_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTextValue", []))

    @jsii.member(jsii_name="resetTitle")
    def reset_title(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTitle", []))

    @builtins.property
    @jsii.member(jsii_name="dateRangeValue")
    def date_range_value(self) -> QueryParameterDateRangeValueOutputReference:
        return typing.cast(QueryParameterDateRangeValueOutputReference, jsii.get(self, "dateRangeValue"))

    @builtins.property
    @jsii.member(jsii_name="dateValue")
    def date_value(self) -> QueryParameterDateValueOutputReference:
        return typing.cast(QueryParameterDateValueOutputReference, jsii.get(self, "dateValue"))

    @builtins.property
    @jsii.member(jsii_name="enumValue")
    def enum_value(self) -> QueryParameterEnumValueOutputReference:
        return typing.cast(QueryParameterEnumValueOutputReference, jsii.get(self, "enumValue"))

    @builtins.property
    @jsii.member(jsii_name="numericValue")
    def numeric_value(self) -> QueryParameterNumericValueOutputReference:
        return typing.cast(QueryParameterNumericValueOutputReference, jsii.get(self, "numericValue"))

    @builtins.property
    @jsii.member(jsii_name="queryBackedValue")
    def query_backed_value(self) -> "QueryParameterQueryBackedValueOutputReference":
        return typing.cast("QueryParameterQueryBackedValueOutputReference", jsii.get(self, "queryBackedValue"))

    @builtins.property
    @jsii.member(jsii_name="textValue")
    def text_value(self) -> "QueryParameterTextValueOutputReference":
        return typing.cast("QueryParameterTextValueOutputReference", jsii.get(self, "textValue"))

    @builtins.property
    @jsii.member(jsii_name="dateRangeValueInput")
    def date_range_value_input(self) -> typing.Optional[QueryParameterDateRangeValue]:
        return typing.cast(typing.Optional[QueryParameterDateRangeValue], jsii.get(self, "dateRangeValueInput"))

    @builtins.property
    @jsii.member(jsii_name="dateValueInput")
    def date_value_input(self) -> typing.Optional[QueryParameterDateValue]:
        return typing.cast(typing.Optional[QueryParameterDateValue], jsii.get(self, "dateValueInput"))

    @builtins.property
    @jsii.member(jsii_name="enumValueInput")
    def enum_value_input(self) -> typing.Optional[QueryParameterEnumValue]:
        return typing.cast(typing.Optional[QueryParameterEnumValue], jsii.get(self, "enumValueInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="numericValueInput")
    def numeric_value_input(self) -> typing.Optional[QueryParameterNumericValue]:
        return typing.cast(typing.Optional[QueryParameterNumericValue], jsii.get(self, "numericValueInput"))

    @builtins.property
    @jsii.member(jsii_name="queryBackedValueInput")
    def query_backed_value_input(
        self,
    ) -> typing.Optional["QueryParameterQueryBackedValue"]:
        return typing.cast(typing.Optional["QueryParameterQueryBackedValue"], jsii.get(self, "queryBackedValueInput"))

    @builtins.property
    @jsii.member(jsii_name="textValueInput")
    def text_value_input(self) -> typing.Optional["QueryParameterTextValue"]:
        return typing.cast(typing.Optional["QueryParameterTextValue"], jsii.get(self, "textValueInput"))

    @builtins.property
    @jsii.member(jsii_name="titleInput")
    def title_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "titleInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d4d61ac5833ff9471fdaf1c807530a566268cc88ad35ceaa84bbee18f019cd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @title.setter
    def title(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c53a03ff0fc1f54c05a3340e4e2899b9b648fad4231239ff96262d40539e6b25)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "title", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, QueryParameter]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, QueryParameter]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, QueryParameter]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93047f8ef12f070300bb51d940512ea7bc26e9949c53e63d6a8c22e27a55e116)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.query.QueryParameterQueryBackedValue",
    jsii_struct_bases=[],
    name_mapping={
        "query_id": "queryId",
        "multi_values_options": "multiValuesOptions",
        "values": "values",
    },
)
class QueryParameterQueryBackedValue:
    def __init__(
        self,
        *,
        query_id: builtins.str,
        multi_values_options: typing.Optional[typing.Union["QueryParameterQueryBackedValueMultiValuesOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        values: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param query_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#query_id Query#query_id}.
        :param multi_values_options: multi_values_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#multi_values_options Query#multi_values_options}
        :param values: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#values Query#values}.
        '''
        if isinstance(multi_values_options, dict):
            multi_values_options = QueryParameterQueryBackedValueMultiValuesOptions(**multi_values_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71fadc71445e38f699901b6f62f0879ad2a93b2e1167002aba5bf96830c5e7b2)
            check_type(argname="argument query_id", value=query_id, expected_type=type_hints["query_id"])
            check_type(argname="argument multi_values_options", value=multi_values_options, expected_type=type_hints["multi_values_options"])
            check_type(argname="argument values", value=values, expected_type=type_hints["values"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "query_id": query_id,
        }
        if multi_values_options is not None:
            self._values["multi_values_options"] = multi_values_options
        if values is not None:
            self._values["values"] = values

    @builtins.property
    def query_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#query_id Query#query_id}.'''
        result = self._values.get("query_id")
        assert result is not None, "Required property 'query_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def multi_values_options(
        self,
    ) -> typing.Optional["QueryParameterQueryBackedValueMultiValuesOptions"]:
        '''multi_values_options block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#multi_values_options Query#multi_values_options}
        '''
        result = self._values.get("multi_values_options")
        return typing.cast(typing.Optional["QueryParameterQueryBackedValueMultiValuesOptions"], result)

    @builtins.property
    def values(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#values Query#values}.'''
        result = self._values.get("values")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QueryParameterQueryBackedValue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.query.QueryParameterQueryBackedValueMultiValuesOptions",
    jsii_struct_bases=[],
    name_mapping={"prefix": "prefix", "separator": "separator", "suffix": "suffix"},
)
class QueryParameterQueryBackedValueMultiValuesOptions:
    def __init__(
        self,
        *,
        prefix: typing.Optional[builtins.str] = None,
        separator: typing.Optional[builtins.str] = None,
        suffix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#prefix Query#prefix}.
        :param separator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#separator Query#separator}.
        :param suffix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#suffix Query#suffix}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__170c84ca3de9350142536adeac1ac594a5b92b5b28b90063f87954b3b4d94300)
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
            check_type(argname="argument separator", value=separator, expected_type=type_hints["separator"])
            check_type(argname="argument suffix", value=suffix, expected_type=type_hints["suffix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if prefix is not None:
            self._values["prefix"] = prefix
        if separator is not None:
            self._values["separator"] = separator
        if suffix is not None:
            self._values["suffix"] = suffix

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#prefix Query#prefix}.'''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def separator(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#separator Query#separator}.'''
        result = self._values.get("separator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def suffix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#suffix Query#suffix}.'''
        result = self._values.get("suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QueryParameterQueryBackedValueMultiValuesOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QueryParameterQueryBackedValueMultiValuesOptionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.query.QueryParameterQueryBackedValueMultiValuesOptionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7e9a58b75e9ef88c1384602fcf7b3b4e7d7aad6a1e9cd5f1d135c949494e51c9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetPrefix")
    def reset_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefix", []))

    @jsii.member(jsii_name="resetSeparator")
    def reset_separator(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSeparator", []))

    @jsii.member(jsii_name="resetSuffix")
    def reset_suffix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSuffix", []))

    @builtins.property
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prefixInput"))

    @builtins.property
    @jsii.member(jsii_name="separatorInput")
    def separator_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "separatorInput"))

    @builtins.property
    @jsii.member(jsii_name="suffixInput")
    def suffix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "suffixInput"))

    @builtins.property
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3eb6f8a3e9e51ae0c03a4c04afa5907051b98e51032d197ac3291f0602601eb4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "prefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="separator")
    def separator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "separator"))

    @separator.setter
    def separator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07ecf6faf551e8958ec592a4dce617be97b0d02da06243992aacf31cd15eaea3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "separator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="suffix")
    def suffix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "suffix"))

    @suffix.setter
    def suffix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da8fcd7f45405e54ca20e322ed6842d34573d0315ed31c30ce50920939708ede)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "suffix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[QueryParameterQueryBackedValueMultiValuesOptions]:
        return typing.cast(typing.Optional[QueryParameterQueryBackedValueMultiValuesOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QueryParameterQueryBackedValueMultiValuesOptions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3bb45cf793bbb9952aa36480c1ee232aee14662abe7c8f43f539d1557ce96a2d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class QueryParameterQueryBackedValueOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.query.QueryParameterQueryBackedValueOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3c04c90046e8db23824fb21c6332fcea2bed26f602fe839dd39cfaf23eccfb3a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putMultiValuesOptions")
    def put_multi_values_options(
        self,
        *,
        prefix: typing.Optional[builtins.str] = None,
        separator: typing.Optional[builtins.str] = None,
        suffix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#prefix Query#prefix}.
        :param separator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#separator Query#separator}.
        :param suffix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#suffix Query#suffix}.
        '''
        value = QueryParameterQueryBackedValueMultiValuesOptions(
            prefix=prefix, separator=separator, suffix=suffix
        )

        return typing.cast(None, jsii.invoke(self, "putMultiValuesOptions", [value]))

    @jsii.member(jsii_name="resetMultiValuesOptions")
    def reset_multi_values_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMultiValuesOptions", []))

    @jsii.member(jsii_name="resetValues")
    def reset_values(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValues", []))

    @builtins.property
    @jsii.member(jsii_name="multiValuesOptions")
    def multi_values_options(
        self,
    ) -> QueryParameterQueryBackedValueMultiValuesOptionsOutputReference:
        return typing.cast(QueryParameterQueryBackedValueMultiValuesOptionsOutputReference, jsii.get(self, "multiValuesOptions"))

    @builtins.property
    @jsii.member(jsii_name="multiValuesOptionsInput")
    def multi_values_options_input(
        self,
    ) -> typing.Optional[QueryParameterQueryBackedValueMultiValuesOptions]:
        return typing.cast(typing.Optional[QueryParameterQueryBackedValueMultiValuesOptions], jsii.get(self, "multiValuesOptionsInput"))

    @builtins.property
    @jsii.member(jsii_name="queryIdInput")
    def query_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queryIdInput"))

    @builtins.property
    @jsii.member(jsii_name="valuesInput")
    def values_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "valuesInput"))

    @builtins.property
    @jsii.member(jsii_name="queryId")
    def query_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queryId"))

    @query_id.setter
    def query_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c03164b879fef2aa126cf651f7e0c5867de738ae2b43b1ce6422f91af32969df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "queryId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="values")
    def values(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "values"))

    @values.setter
    def values(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee58229e360330483eadc4ec52166a71a0e55f7f53fd6f1d40751a24163a2606)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "values", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[QueryParameterQueryBackedValue]:
        return typing.cast(typing.Optional[QueryParameterQueryBackedValue], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QueryParameterQueryBackedValue],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89c32af90492f686de778b2a07c942e4d4503fd0cc49f230bc0b241b4fc30191)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.query.QueryParameterTextValue",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class QueryParameterTextValue:
    def __init__(self, *, value: builtins.str) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#value Query#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b369a4e65a686aabe960c23a208740331da1f2b5af733307d06f0334a6a0cf02)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "value": value,
        }

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/query#value Query#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QueryParameterTextValue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QueryParameterTextValueOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.query.QueryParameterTextValueOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__24cce06e1497e373a65682bd9eef58230873ba5e66107165dd483ed5e9ac9928)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4be959e9c25b2d4fe8ab6c8ab149c94558f67bfa3fb4c1d72a66f1d7b445d55)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[QueryParameterTextValue]:
        return typing.cast(typing.Optional[QueryParameterTextValue], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[QueryParameterTextValue]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bd2cffd487628061818e7a734e7f281a43bb2d8cd5edd71e7917b0b14b7f113)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "Query",
    "QueryConfig",
    "QueryParameter",
    "QueryParameterDateRangeValue",
    "QueryParameterDateRangeValueDateRangeValue",
    "QueryParameterDateRangeValueDateRangeValueOutputReference",
    "QueryParameterDateRangeValueOutputReference",
    "QueryParameterDateValue",
    "QueryParameterDateValueOutputReference",
    "QueryParameterEnumValue",
    "QueryParameterEnumValueMultiValuesOptions",
    "QueryParameterEnumValueMultiValuesOptionsOutputReference",
    "QueryParameterEnumValueOutputReference",
    "QueryParameterList",
    "QueryParameterNumericValue",
    "QueryParameterNumericValueOutputReference",
    "QueryParameterOutputReference",
    "QueryParameterQueryBackedValue",
    "QueryParameterQueryBackedValueMultiValuesOptions",
    "QueryParameterQueryBackedValueMultiValuesOptionsOutputReference",
    "QueryParameterQueryBackedValueOutputReference",
    "QueryParameterTextValue",
    "QueryParameterTextValueOutputReference",
]

publication.publish()

def _typecheckingstub__e32924934e478c5575df4c9786ca2559e878b7f69042577e01ea683dadb83fe1(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    display_name: builtins.str,
    query_text: builtins.str,
    warehouse_id: builtins.str,
    apply_auto_limit: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    catalog: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    owner_user_name: typing.Optional[builtins.str] = None,
    parameter: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[QueryParameter, typing.Dict[builtins.str, typing.Any]]]]] = None,
    parent_path: typing.Optional[builtins.str] = None,
    run_as_mode: typing.Optional[builtins.str] = None,
    schema: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
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

def _typecheckingstub__cc29c362ffe1fa093d733f690a759a59d4f0e48d76ad2425fa3dac60f0c5105c(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__136f37c6d894ab814c13191ade241bfeb153744d83bb11a865b6b9d51b765ac2(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[QueryParameter, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c018f8fdeaca8d86d0ae08089da1eb3dfca6b38f0b38c6d7da38cccd1426c580(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa615482ea6fe3e2f839fe31872a8fb44c65096ba072289ba8a7653851c3ef88(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e7442aaa4700804fded49c678fba7ac230420cce498adbb129a31f691aad3d6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d81689bba2ab03997c5585019d83dcb44ea92738c6b31b22f4074566bd0138f3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__776d3601e757a01b3b1f6c3ca637f1b3f0222b3fedc39de1a2bbf86a57f351ca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06fbb8219d910d29ebe60c49d807152aec533eb0af5bd0d28ab2b00533a2680b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56dce5f5eb9124b595b1563a5d0356ad58d8426fd1248f0ca3c36a63d4df5e90(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b791528085ef395e7eadb42d89e590aae4a0b7e520b5c262dfdbdbea19f0861e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04585c9e15a9d96e47b3f18ec576259e1f710869c64257b6f46403d0976171c2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2939570ba0bb0f4ac8b1c430eed545fa6630d93dc70903dfa50b797e8c1bf081(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8fd47699594888cd148511232f92205c867c5458a441b5e4ab4fab0d1754fc9c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27390797363df912885414bf0e6ddf85bd55b990d2559783c8a4249c06b2d473(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    display_name: builtins.str,
    query_text: builtins.str,
    warehouse_id: builtins.str,
    apply_auto_limit: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    catalog: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    owner_user_name: typing.Optional[builtins.str] = None,
    parameter: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[QueryParameter, typing.Dict[builtins.str, typing.Any]]]]] = None,
    parent_path: typing.Optional[builtins.str] = None,
    run_as_mode: typing.Optional[builtins.str] = None,
    schema: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e846acabd00385a57bd8fbf4beab90319d8099522975de4cd90ab91e7ecb39b(
    *,
    name: builtins.str,
    date_range_value: typing.Optional[typing.Union[QueryParameterDateRangeValue, typing.Dict[builtins.str, typing.Any]]] = None,
    date_value: typing.Optional[typing.Union[QueryParameterDateValue, typing.Dict[builtins.str, typing.Any]]] = None,
    enum_value: typing.Optional[typing.Union[QueryParameterEnumValue, typing.Dict[builtins.str, typing.Any]]] = None,
    numeric_value: typing.Optional[typing.Union[QueryParameterNumericValue, typing.Dict[builtins.str, typing.Any]]] = None,
    query_backed_value: typing.Optional[typing.Union[QueryParameterQueryBackedValue, typing.Dict[builtins.str, typing.Any]]] = None,
    text_value: typing.Optional[typing.Union[QueryParameterTextValue, typing.Dict[builtins.str, typing.Any]]] = None,
    title: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e5ef48823cd3d6615c68ac64d116fb4eb5a4f24b3e846107185f9bb6cdf1051(
    *,
    date_range_value: typing.Optional[typing.Union[QueryParameterDateRangeValueDateRangeValue, typing.Dict[builtins.str, typing.Any]]] = None,
    dynamic_date_range_value: typing.Optional[builtins.str] = None,
    precision: typing.Optional[builtins.str] = None,
    start_day_of_week: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__243c90edfdf7d26b7215bd427208a644a4b65d7f51f8c937c18de5e5d6be9f21(
    *,
    end: builtins.str,
    start: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d31c309ce6f024a9d7763a4e962819f597d4bbc42935aa0ba52c5e242e477d2e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36ed08693726c4da8b4aa727fcbada4c5b0b083199a5d12e5923593bd2bb120c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccaf2fa82a2823ebe40fb312237aa62f29cfe10a20b385870d2610e17ae59efe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__214c5e6add6f3deb4d14eeba09b34c62202b9a717126f50c90af8fcd3c7ff9fb(
    value: typing.Optional[QueryParameterDateRangeValueDateRangeValue],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8e8ae8473cde8d880f466cd767af828bbc90eadd091ceee41dabb69876cd85d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b135f76db994b3e75db55eb0d42886aa67ac393e3023c4577eb4553b9f43259d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f1646fcd9d6bcc5d1731e0a8f82913a7e87c31168904f1c97978c6d6050514f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b03a8a0cf9bd483bb332b6a1b58ed6f322c033dec1a1cd26bbcc36f9730d5ba(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fceaa8c05ace558f64f69cb0b362a5e75be102579a1fb5843e8accabe4446ff3(
    value: typing.Optional[QueryParameterDateRangeValue],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6c6dbbd4f9017cb5dbb1de88f0cedb81a1c3f6f13f4881ddae918fe7ff436b1(
    *,
    date_value: typing.Optional[builtins.str] = None,
    dynamic_date_value: typing.Optional[builtins.str] = None,
    precision: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee39a41f4b08575ff09cf192a1eb1b63c986bf7a7f9ccccdebbcca6c1dd66aff(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f859b452531a77250d868d10c90c2d5841b80f90791784257796008a7a347b66(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f8bb5feb8b551ac04de009ff57e6f3e478049e157bbcc944e2ee36272b75b69(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45e1ffa637877505dbd76de8821ecd516a0aac222f72d03a61507a3364fad8d0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbc130439bce9f136a65c7dc5f77c3dd3f31e102c38c4a69fb970fe3c1477530(
    value: typing.Optional[QueryParameterDateValue],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcd8a5c0e0b22ea2c7436de1c960a25ffda5970937d4ad0509168641a0332ec1(
    *,
    enum_options: typing.Optional[builtins.str] = None,
    multi_values_options: typing.Optional[typing.Union[QueryParameterEnumValueMultiValuesOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    values: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__079cc49d37489dba69b2c9928feacd9ffe0fafefc22bbb1103e47a73f86947c4(
    *,
    prefix: typing.Optional[builtins.str] = None,
    separator: typing.Optional[builtins.str] = None,
    suffix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7eb354e9f4127b03895c7427287adf18e4b31c0ac6565965900ca6b27a4e0079(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa4efa8c31c2bf92c5cf4ee1be5f478130a3d8fa1238765a02d84ada7097cca6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fd8e0a0bfb23e43d80e03160435104571c51c46b72a847de8f5e40b82540d7e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cd36db946a853d9bf805f584653e47cfd6adf4c152ce82bbc4200ef3ef11723(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9616decc58289c5ed1bdebddd983f81bccab4fb3b1e4331713d6b9709e7afe79(
    value: typing.Optional[QueryParameterEnumValueMultiValuesOptions],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a504ded86f85ac67d0fb974dd4968901622269b46cb1af07ff1428cd591a77f2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b086f01a3bd648b955d41f24c01cc36997fce08e76281c892be3ace4094ff049(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb3e2b59a1b941a526a385df0e880e9409525f47c3fafe931239a18e0143cfad(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c28b5e936014d448fe643303f2d19c3e53f70ba122c5b172251d61758addb83b(
    value: typing.Optional[QueryParameterEnumValue],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6dd585ae82d3c92066204f959dc5f5678076ab0e8137d58d5b1610cd9b2768f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__220d15014a62124d4244dac2022c3588c97acf8c150c431b7a02a1f097814e06(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80482534eede85499b8005ca55f5552d5a10aea156d7f3245a8162b234e77e1e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9bdb34519b239a81a805e2cc819be4afcc29f677eed2418cc001e2da9153419(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c41ae6d10202705862150bd1baad45c815e0f1ade3ecfaab2bece88a954d4c0b(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__632ec8b68a34c1c73d263adde724e2f362586898ff726860816dd81400d34524(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[QueryParameter]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__237e48018a4394f4a59709e27c8e75664c4794064c13785151d4e4c73b305b4e(
    *,
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__784abf6ffa9622aacc6cadfe76327a4842f3b4ed465dd723d4b22e4565ecd7df(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40c83bdb5c9540633252165d0c6fb3793a508582629907dc595c38be675942ed(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a2bfe9f9b9d4608f4723b040d06511f1f90966d4ee60aed21e097ff88f75726(
    value: typing.Optional[QueryParameterNumericValue],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42e8afd7d7eea0260b998ab452cd85f37c195e605dbb0fc5c1033a3f2497cd58(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d4d61ac5833ff9471fdaf1c807530a566268cc88ad35ceaa84bbee18f019cd8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c53a03ff0fc1f54c05a3340e4e2899b9b648fad4231239ff96262d40539e6b25(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93047f8ef12f070300bb51d940512ea7bc26e9949c53e63d6a8c22e27a55e116(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, QueryParameter]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71fadc71445e38f699901b6f62f0879ad2a93b2e1167002aba5bf96830c5e7b2(
    *,
    query_id: builtins.str,
    multi_values_options: typing.Optional[typing.Union[QueryParameterQueryBackedValueMultiValuesOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    values: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__170c84ca3de9350142536adeac1ac594a5b92b5b28b90063f87954b3b4d94300(
    *,
    prefix: typing.Optional[builtins.str] = None,
    separator: typing.Optional[builtins.str] = None,
    suffix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e9a58b75e9ef88c1384602fcf7b3b4e7d7aad6a1e9cd5f1d135c949494e51c9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3eb6f8a3e9e51ae0c03a4c04afa5907051b98e51032d197ac3291f0602601eb4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07ecf6faf551e8958ec592a4dce617be97b0d02da06243992aacf31cd15eaea3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da8fcd7f45405e54ca20e322ed6842d34573d0315ed31c30ce50920939708ede(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bb45cf793bbb9952aa36480c1ee232aee14662abe7c8f43f539d1557ce96a2d(
    value: typing.Optional[QueryParameterQueryBackedValueMultiValuesOptions],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c04c90046e8db23824fb21c6332fcea2bed26f602fe839dd39cfaf23eccfb3a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c03164b879fef2aa126cf651f7e0c5867de738ae2b43b1ce6422f91af32969df(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee58229e360330483eadc4ec52166a71a0e55f7f53fd6f1d40751a24163a2606(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89c32af90492f686de778b2a07c942e4d4503fd0cc49f230bc0b241b4fc30191(
    value: typing.Optional[QueryParameterQueryBackedValue],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b369a4e65a686aabe960c23a208740331da1f2b5af733307d06f0334a6a0cf02(
    *,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24cce06e1497e373a65682bd9eef58230873ba5e66107165dd483ed5e9ac9928(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4be959e9c25b2d4fe8ab6c8ab149c94558f67bfa3fb4c1d72a66f1d7b445d55(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bd2cffd487628061818e7a734e7f281a43bb2d8cd5edd71e7917b0b14b7f113(
    value: typing.Optional[QueryParameterTextValue],
) -> None:
    """Type checking stubs"""
    pass
