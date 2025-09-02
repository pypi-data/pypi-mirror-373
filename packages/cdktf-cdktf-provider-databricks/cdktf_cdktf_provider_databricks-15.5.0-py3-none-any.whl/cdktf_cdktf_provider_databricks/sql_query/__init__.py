r'''
# `databricks_sql_query`

Refer to the Terraform Registry for docs: [`databricks_sql_query`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query).
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


class SqlQuery(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQuery",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query databricks_sql_query}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        data_source_id: builtins.str,
        name: builtins.str,
        query: builtins.str,
        created_at: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        parameter: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["SqlQueryParameter", typing.Dict[builtins.str, typing.Any]]]]] = None,
        parent: typing.Optional[builtins.str] = None,
        run_as_role: typing.Optional[builtins.str] = None,
        schedule: typing.Optional[typing.Union["SqlQuerySchedule", typing.Dict[builtins.str, typing.Any]]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        updated_at: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query databricks_sql_query} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param data_source_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#data_source_id SqlQuery#data_source_id}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#name SqlQuery#name}.
        :param query: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#query SqlQuery#query}.
        :param created_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#created_at SqlQuery#created_at}.
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#description SqlQuery#description}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#id SqlQuery#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param parameter: parameter block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#parameter SqlQuery#parameter}
        :param parent: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#parent SqlQuery#parent}.
        :param run_as_role: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#run_as_role SqlQuery#run_as_role}.
        :param schedule: schedule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#schedule SqlQuery#schedule}
        :param tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#tags SqlQuery#tags}.
        :param updated_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#updated_at SqlQuery#updated_at}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__524a8bd60b3ff93d305683d68c92115f986997010e0ec6316cf9423ac98694eb)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = SqlQueryConfig(
            data_source_id=data_source_id,
            name=name,
            query=query,
            created_at=created_at,
            description=description,
            id=id,
            parameter=parameter,
            parent=parent,
            run_as_role=run_as_role,
            schedule=schedule,
            tags=tags,
            updated_at=updated_at,
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
        '''Generates CDKTF code for importing a SqlQuery resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the SqlQuery to import.
        :param import_from_id: The id of the existing SqlQuery that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the SqlQuery to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ef8f9f18d586e215cc47695d845c1b44ca76c127f142d0e63e1e810c0eddf12)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putParameter")
    def put_parameter(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["SqlQueryParameter", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2b56a9ebe162b1ba217e3a89e451c1aaf3b51954b2b6f037ce275dfd479826b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putParameter", [value]))

    @jsii.member(jsii_name="putSchedule")
    def put_schedule(
        self,
        *,
        continuous: typing.Optional[typing.Union["SqlQueryScheduleContinuous", typing.Dict[builtins.str, typing.Any]]] = None,
        daily: typing.Optional[typing.Union["SqlQueryScheduleDaily", typing.Dict[builtins.str, typing.Any]]] = None,
        weekly: typing.Optional[typing.Union["SqlQueryScheduleWeekly", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param continuous: continuous block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#continuous SqlQuery#continuous}
        :param daily: daily block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#daily SqlQuery#daily}
        :param weekly: weekly block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#weekly SqlQuery#weekly}
        '''
        value = SqlQuerySchedule(continuous=continuous, daily=daily, weekly=weekly)

        return typing.cast(None, jsii.invoke(self, "putSchedule", [value]))

    @jsii.member(jsii_name="resetCreatedAt")
    def reset_created_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatedAt", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetParameter")
    def reset_parameter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameter", []))

    @jsii.member(jsii_name="resetParent")
    def reset_parent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParent", []))

    @jsii.member(jsii_name="resetRunAsRole")
    def reset_run_as_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunAsRole", []))

    @jsii.member(jsii_name="resetSchedule")
    def reset_schedule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchedule", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetUpdatedAt")
    def reset_updated_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdatedAt", []))

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
    @jsii.member(jsii_name="parameter")
    def parameter(self) -> "SqlQueryParameterList":
        return typing.cast("SqlQueryParameterList", jsii.get(self, "parameter"))

    @builtins.property
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> "SqlQueryScheduleOutputReference":
        return typing.cast("SqlQueryScheduleOutputReference", jsii.get(self, "schedule"))

    @builtins.property
    @jsii.member(jsii_name="createdAtInput")
    def created_at_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdAtInput"))

    @builtins.property
    @jsii.member(jsii_name="dataSourceIdInput")
    def data_source_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataSourceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="parameterInput")
    def parameter_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["SqlQueryParameter"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["SqlQueryParameter"]]], jsii.get(self, "parameterInput"))

    @builtins.property
    @jsii.member(jsii_name="parentInput")
    def parent_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parentInput"))

    @builtins.property
    @jsii.member(jsii_name="queryInput")
    def query_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queryInput"))

    @builtins.property
    @jsii.member(jsii_name="runAsRoleInput")
    def run_as_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "runAsRoleInput"))

    @builtins.property
    @jsii.member(jsii_name="scheduleInput")
    def schedule_input(self) -> typing.Optional["SqlQuerySchedule"]:
        return typing.cast(typing.Optional["SqlQuerySchedule"], jsii.get(self, "scheduleInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="updatedAtInput")
    def updated_at_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updatedAtInput"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @created_at.setter
    def created_at(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5e07aed1dbcd31cbdab854ec13f6ebc05f842c903ad3db6117e575174c86763)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dataSourceId")
    def data_source_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataSourceId"))

    @data_source_id.setter
    def data_source_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d1ce5c5eb7cd556ea10048ab1a44c20a515b30183221b5e54defeddec2e6372)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataSourceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97f9e6c9b5003ba2059a4b5915efba3e4c525e9731aa7f08e7e3ac588ff962ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c0b117d4f3a2cfc6a811329a8847c89eca4cb39a06d1934a111692ffe812872)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c263d9980714de79fc51926fc6b3eff9538be6539beacea1f6b71644546564f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parent")
    def parent(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parent"))

    @parent.setter
    def parent(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a7395b77eeb1a0509d56db1d014e998cee2da6666366134e91f608a48cae7cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parent", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="query")
    def query(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "query"))

    @query.setter
    def query(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94bf7552667bd8fc4f86244a388a0095b3c7315a9a23efd89eb5ec326ce7477f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "query", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runAsRole")
    def run_as_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runAsRole"))

    @run_as_role.setter
    def run_as_role(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d34c2f7559e109eebf1c9fb9defdd0d7bf801db87c06c67e9d32d41027db5ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runAsRole", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dafbadfa47972d371f8519f91157ce51d44f4eaa635a86f9f6fd69a82e5343c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @updated_at.setter
    def updated_at(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be1b042034f3ddf8d8ceb4767013de549ce0e2b389f1d744846aac41cd128c9c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "updatedAt", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "data_source_id": "dataSourceId",
        "name": "name",
        "query": "query",
        "created_at": "createdAt",
        "description": "description",
        "id": "id",
        "parameter": "parameter",
        "parent": "parent",
        "run_as_role": "runAsRole",
        "schedule": "schedule",
        "tags": "tags",
        "updated_at": "updatedAt",
    },
)
class SqlQueryConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        data_source_id: builtins.str,
        name: builtins.str,
        query: builtins.str,
        created_at: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        parameter: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["SqlQueryParameter", typing.Dict[builtins.str, typing.Any]]]]] = None,
        parent: typing.Optional[builtins.str] = None,
        run_as_role: typing.Optional[builtins.str] = None,
        schedule: typing.Optional[typing.Union["SqlQuerySchedule", typing.Dict[builtins.str, typing.Any]]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        updated_at: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param data_source_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#data_source_id SqlQuery#data_source_id}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#name SqlQuery#name}.
        :param query: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#query SqlQuery#query}.
        :param created_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#created_at SqlQuery#created_at}.
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#description SqlQuery#description}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#id SqlQuery#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param parameter: parameter block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#parameter SqlQuery#parameter}
        :param parent: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#parent SqlQuery#parent}.
        :param run_as_role: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#run_as_role SqlQuery#run_as_role}.
        :param schedule: schedule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#schedule SqlQuery#schedule}
        :param tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#tags SqlQuery#tags}.
        :param updated_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#updated_at SqlQuery#updated_at}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(schedule, dict):
            schedule = SqlQuerySchedule(**schedule)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa7496d62934e8102301b3aeb79095478e90c80ab3551e47460bc21c7a9c098e)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument data_source_id", value=data_source_id, expected_type=type_hints["data_source_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument query", value=query, expected_type=type_hints["query"])
            check_type(argname="argument created_at", value=created_at, expected_type=type_hints["created_at"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument parameter", value=parameter, expected_type=type_hints["parameter"])
            check_type(argname="argument parent", value=parent, expected_type=type_hints["parent"])
            check_type(argname="argument run_as_role", value=run_as_role, expected_type=type_hints["run_as_role"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument updated_at", value=updated_at, expected_type=type_hints["updated_at"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "data_source_id": data_source_id,
            "name": name,
            "query": query,
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
        if created_at is not None:
            self._values["created_at"] = created_at
        if description is not None:
            self._values["description"] = description
        if id is not None:
            self._values["id"] = id
        if parameter is not None:
            self._values["parameter"] = parameter
        if parent is not None:
            self._values["parent"] = parent
        if run_as_role is not None:
            self._values["run_as_role"] = run_as_role
        if schedule is not None:
            self._values["schedule"] = schedule
        if tags is not None:
            self._values["tags"] = tags
        if updated_at is not None:
            self._values["updated_at"] = updated_at

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
    def data_source_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#data_source_id SqlQuery#data_source_id}.'''
        result = self._values.get("data_source_id")
        assert result is not None, "Required property 'data_source_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#name SqlQuery#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def query(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#query SqlQuery#query}.'''
        result = self._values.get("query")
        assert result is not None, "Required property 'query' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def created_at(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#created_at SqlQuery#created_at}.'''
        result = self._values.get("created_at")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#description SqlQuery#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#id SqlQuery#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameter(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["SqlQueryParameter"]]]:
        '''parameter block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#parameter SqlQuery#parameter}
        '''
        result = self._values.get("parameter")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["SqlQueryParameter"]]], result)

    @builtins.property
    def parent(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#parent SqlQuery#parent}.'''
        result = self._values.get("parent")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def run_as_role(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#run_as_role SqlQuery#run_as_role}.'''
        result = self._values.get("run_as_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def schedule(self) -> typing.Optional["SqlQuerySchedule"]:
        '''schedule block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#schedule SqlQuery#schedule}
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional["SqlQuerySchedule"], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#tags SqlQuery#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def updated_at(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#updated_at SqlQuery#updated_at}.'''
        result = self._values.get("updated_at")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SqlQueryConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameter",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "date": "date",
        "date_range": "dateRange",
        "datetime": "datetime",
        "datetime_range": "datetimeRange",
        "datetimesec": "datetimesec",
        "datetimesec_range": "datetimesecRange",
        "enum": "enum",
        "number": "number",
        "query": "query",
        "text": "text",
        "title": "title",
    },
)
class SqlQueryParameter:
    def __init__(
        self,
        *,
        name: builtins.str,
        date: typing.Optional[typing.Union["SqlQueryParameterDate", typing.Dict[builtins.str, typing.Any]]] = None,
        date_range: typing.Optional[typing.Union["SqlQueryParameterDateRange", typing.Dict[builtins.str, typing.Any]]] = None,
        datetime: typing.Optional[typing.Union["SqlQueryParameterDatetime", typing.Dict[builtins.str, typing.Any]]] = None,
        datetime_range: typing.Optional[typing.Union["SqlQueryParameterDatetimeRange", typing.Dict[builtins.str, typing.Any]]] = None,
        datetimesec: typing.Optional[typing.Union["SqlQueryParameterDatetimesec", typing.Dict[builtins.str, typing.Any]]] = None,
        datetimesec_range: typing.Optional[typing.Union["SqlQueryParameterDatetimesecRange", typing.Dict[builtins.str, typing.Any]]] = None,
        enum: typing.Optional[typing.Union["SqlQueryParameterEnum", typing.Dict[builtins.str, typing.Any]]] = None,
        number: typing.Optional[typing.Union["SqlQueryParameterNumber", typing.Dict[builtins.str, typing.Any]]] = None,
        query: typing.Optional[typing.Union["SqlQueryParameterQuery", typing.Dict[builtins.str, typing.Any]]] = None,
        text: typing.Optional[typing.Union["SqlQueryParameterText", typing.Dict[builtins.str, typing.Any]]] = None,
        title: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#name SqlQuery#name}.
        :param date: date block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#date SqlQuery#date}
        :param date_range: date_range block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#date_range SqlQuery#date_range}
        :param datetime: datetime block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#datetime SqlQuery#datetime}
        :param datetime_range: datetime_range block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#datetime_range SqlQuery#datetime_range}
        :param datetimesec: datetimesec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#datetimesec SqlQuery#datetimesec}
        :param datetimesec_range: datetimesec_range block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#datetimesec_range SqlQuery#datetimesec_range}
        :param enum: enum block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#enum SqlQuery#enum}
        :param number: number block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#number SqlQuery#number}
        :param query: query block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#query SqlQuery#query}
        :param text: text block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#text SqlQuery#text}
        :param title: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#title SqlQuery#title}.
        '''
        if isinstance(date, dict):
            date = SqlQueryParameterDate(**date)
        if isinstance(date_range, dict):
            date_range = SqlQueryParameterDateRange(**date_range)
        if isinstance(datetime, dict):
            datetime = SqlQueryParameterDatetime(**datetime)
        if isinstance(datetime_range, dict):
            datetime_range = SqlQueryParameterDatetimeRange(**datetime_range)
        if isinstance(datetimesec, dict):
            datetimesec = SqlQueryParameterDatetimesec(**datetimesec)
        if isinstance(datetimesec_range, dict):
            datetimesec_range = SqlQueryParameterDatetimesecRange(**datetimesec_range)
        if isinstance(enum, dict):
            enum = SqlQueryParameterEnum(**enum)
        if isinstance(number, dict):
            number = SqlQueryParameterNumber(**number)
        if isinstance(query, dict):
            query = SqlQueryParameterQuery(**query)
        if isinstance(text, dict):
            text = SqlQueryParameterText(**text)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0347eb58b4f36ddaf88cb73b2e45fee12f3c767a2fabc79a99151c050bb2c968)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument date", value=date, expected_type=type_hints["date"])
            check_type(argname="argument date_range", value=date_range, expected_type=type_hints["date_range"])
            check_type(argname="argument datetime", value=datetime, expected_type=type_hints["datetime"])
            check_type(argname="argument datetime_range", value=datetime_range, expected_type=type_hints["datetime_range"])
            check_type(argname="argument datetimesec", value=datetimesec, expected_type=type_hints["datetimesec"])
            check_type(argname="argument datetimesec_range", value=datetimesec_range, expected_type=type_hints["datetimesec_range"])
            check_type(argname="argument enum", value=enum, expected_type=type_hints["enum"])
            check_type(argname="argument number", value=number, expected_type=type_hints["number"])
            check_type(argname="argument query", value=query, expected_type=type_hints["query"])
            check_type(argname="argument text", value=text, expected_type=type_hints["text"])
            check_type(argname="argument title", value=title, expected_type=type_hints["title"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if date is not None:
            self._values["date"] = date
        if date_range is not None:
            self._values["date_range"] = date_range
        if datetime is not None:
            self._values["datetime"] = datetime
        if datetime_range is not None:
            self._values["datetime_range"] = datetime_range
        if datetimesec is not None:
            self._values["datetimesec"] = datetimesec
        if datetimesec_range is not None:
            self._values["datetimesec_range"] = datetimesec_range
        if enum is not None:
            self._values["enum"] = enum
        if number is not None:
            self._values["number"] = number
        if query is not None:
            self._values["query"] = query
        if text is not None:
            self._values["text"] = text
        if title is not None:
            self._values["title"] = title

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#name SqlQuery#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def date(self) -> typing.Optional["SqlQueryParameterDate"]:
        '''date block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#date SqlQuery#date}
        '''
        result = self._values.get("date")
        return typing.cast(typing.Optional["SqlQueryParameterDate"], result)

    @builtins.property
    def date_range(self) -> typing.Optional["SqlQueryParameterDateRange"]:
        '''date_range block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#date_range SqlQuery#date_range}
        '''
        result = self._values.get("date_range")
        return typing.cast(typing.Optional["SqlQueryParameterDateRange"], result)

    @builtins.property
    def datetime(self) -> typing.Optional["SqlQueryParameterDatetime"]:
        '''datetime block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#datetime SqlQuery#datetime}
        '''
        result = self._values.get("datetime")
        return typing.cast(typing.Optional["SqlQueryParameterDatetime"], result)

    @builtins.property
    def datetime_range(self) -> typing.Optional["SqlQueryParameterDatetimeRange"]:
        '''datetime_range block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#datetime_range SqlQuery#datetime_range}
        '''
        result = self._values.get("datetime_range")
        return typing.cast(typing.Optional["SqlQueryParameterDatetimeRange"], result)

    @builtins.property
    def datetimesec(self) -> typing.Optional["SqlQueryParameterDatetimesec"]:
        '''datetimesec block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#datetimesec SqlQuery#datetimesec}
        '''
        result = self._values.get("datetimesec")
        return typing.cast(typing.Optional["SqlQueryParameterDatetimesec"], result)

    @builtins.property
    def datetimesec_range(self) -> typing.Optional["SqlQueryParameterDatetimesecRange"]:
        '''datetimesec_range block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#datetimesec_range SqlQuery#datetimesec_range}
        '''
        result = self._values.get("datetimesec_range")
        return typing.cast(typing.Optional["SqlQueryParameterDatetimesecRange"], result)

    @builtins.property
    def enum(self) -> typing.Optional["SqlQueryParameterEnum"]:
        '''enum block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#enum SqlQuery#enum}
        '''
        result = self._values.get("enum")
        return typing.cast(typing.Optional["SqlQueryParameterEnum"], result)

    @builtins.property
    def number(self) -> typing.Optional["SqlQueryParameterNumber"]:
        '''number block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#number SqlQuery#number}
        '''
        result = self._values.get("number")
        return typing.cast(typing.Optional["SqlQueryParameterNumber"], result)

    @builtins.property
    def query(self) -> typing.Optional["SqlQueryParameterQuery"]:
        '''query block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#query SqlQuery#query}
        '''
        result = self._values.get("query")
        return typing.cast(typing.Optional["SqlQueryParameterQuery"], result)

    @builtins.property
    def text(self) -> typing.Optional["SqlQueryParameterText"]:
        '''text block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#text SqlQuery#text}
        '''
        result = self._values.get("text")
        return typing.cast(typing.Optional["SqlQueryParameterText"], result)

    @builtins.property
    def title(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#title SqlQuery#title}.'''
        result = self._values.get("title")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SqlQueryParameter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterDate",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class SqlQueryParameterDate:
    def __init__(self, *, value: builtins.str) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf146c0521f6254bda9c6e968492f515fe6d99984e63d6cb1dc6c8f3afdf847e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "value": value,
        }

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SqlQueryParameterDate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SqlQueryParameterDateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterDateOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0e77f05f7e83b878cb0984d9d20a5561b04d040d88072e5fc1d772866496ec56)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0baf03565e745355e3f3a3871b59ffa1ed3c54bd1fab034618935cbffdd8ea8a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SqlQueryParameterDate]:
        return typing.cast(typing.Optional[SqlQueryParameterDate], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[SqlQueryParameterDate]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e6e58fabdcf81fc880cba49d3519eddae369788e7a6e2a960bfdde2034936f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterDateRange",
    jsii_struct_bases=[],
    name_mapping={"range": "range", "value": "value"},
)
class SqlQueryParameterDateRange:
    def __init__(
        self,
        *,
        range: typing.Optional[typing.Union["SqlQueryParameterDateRangeRange", typing.Dict[builtins.str, typing.Any]]] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param range: range block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#range SqlQuery#range}
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.
        '''
        if isinstance(range, dict):
            range = SqlQueryParameterDateRangeRange(**range)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e22f85eaf6f5a586dbad434431028633d1fd6153460a62bf1c6f8160bffcbd00)
            check_type(argname="argument range", value=range, expected_type=type_hints["range"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if range is not None:
            self._values["range"] = range
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def range(self) -> typing.Optional["SqlQueryParameterDateRangeRange"]:
        '''range block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#range SqlQuery#range}
        '''
        result = self._values.get("range")
        return typing.cast(typing.Optional["SqlQueryParameterDateRangeRange"], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SqlQueryParameterDateRange(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SqlQueryParameterDateRangeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterDateRangeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__444ec5e0e9e05ba51f98000245d246e6e13465ab0e21d795f7dd6b6481a22aa9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putRange")
    def put_range(self, *, end: builtins.str, start: builtins.str) -> None:
        '''
        :param end: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#end SqlQuery#end}.
        :param start: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#start SqlQuery#start}.
        '''
        value = SqlQueryParameterDateRangeRange(end=end, start=start)

        return typing.cast(None, jsii.invoke(self, "putRange", [value]))

    @jsii.member(jsii_name="resetRange")
    def reset_range(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRange", []))

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="range")
    def range(self) -> "SqlQueryParameterDateRangeRangeOutputReference":
        return typing.cast("SqlQueryParameterDateRangeRangeOutputReference", jsii.get(self, "range"))

    @builtins.property
    @jsii.member(jsii_name="rangeInput")
    def range_input(self) -> typing.Optional["SqlQueryParameterDateRangeRange"]:
        return typing.cast(typing.Optional["SqlQueryParameterDateRangeRange"], jsii.get(self, "rangeInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__eea95a1a7a6072c29099708bfaba6284408483d8b4ce9df8ef57a2624c5c814a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SqlQueryParameterDateRange]:
        return typing.cast(typing.Optional[SqlQueryParameterDateRange], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SqlQueryParameterDateRange],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33708275fae3e14d6351d6613dd060052f1dda11b819f21447df810f2fc06d22)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterDateRangeRange",
    jsii_struct_bases=[],
    name_mapping={"end": "end", "start": "start"},
)
class SqlQueryParameterDateRangeRange:
    def __init__(self, *, end: builtins.str, start: builtins.str) -> None:
        '''
        :param end: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#end SqlQuery#end}.
        :param start: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#start SqlQuery#start}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8eba84bb02fd70ce89222e5576fce94541cd8ac7022ec2652ec828d939763293)
            check_type(argname="argument end", value=end, expected_type=type_hints["end"])
            check_type(argname="argument start", value=start, expected_type=type_hints["start"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "end": end,
            "start": start,
        }

    @builtins.property
    def end(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#end SqlQuery#end}.'''
        result = self._values.get("end")
        assert result is not None, "Required property 'end' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def start(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#start SqlQuery#start}.'''
        result = self._values.get("start")
        assert result is not None, "Required property 'start' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SqlQueryParameterDateRangeRange(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SqlQueryParameterDateRangeRangeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterDateRangeRangeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9178ea3b6d50c679ce6c505844b40229df8c90bfd34b527fda1f585bdae5a92f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8896b1f03759ce27f0a36284dd1aaced423d260efc35f981911b74725fd7871c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "end", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="start")
    def start(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "start"))

    @start.setter
    def start(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebf21e054fed09e3108d29f334bb0874aaa3ac37cb45f1b9d7e2f7a1ca77d168)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "start", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SqlQueryParameterDateRangeRange]:
        return typing.cast(typing.Optional[SqlQueryParameterDateRangeRange], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SqlQueryParameterDateRangeRange],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4719a117e56efc00055e0353051a3427db22b18d8c53820bcd35b2b56d38ac8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterDatetime",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class SqlQueryParameterDatetime:
    def __init__(self, *, value: builtins.str) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__026a4754efa6d7c0bcca18a4215f8202964071f651ca33312fb4143a2f6301d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "value": value,
        }

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SqlQueryParameterDatetime(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SqlQueryParameterDatetimeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterDatetimeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7a1b7abeb75e9fab6678284ddb2dd19026dd7bfbed3373d193f69b7166552bda)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3469a227037e33c8408125cce17dc394d7b2291e9291b755c0d50e876c4a135d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SqlQueryParameterDatetime]:
        return typing.cast(typing.Optional[SqlQueryParameterDatetime], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[SqlQueryParameterDatetime]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e600ddcfd19771e9ad434d0e454528c3623e22b9afb4ef34cc5eccdc5bed9c26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterDatetimeRange",
    jsii_struct_bases=[],
    name_mapping={"range": "range", "value": "value"},
)
class SqlQueryParameterDatetimeRange:
    def __init__(
        self,
        *,
        range: typing.Optional[typing.Union["SqlQueryParameterDatetimeRangeRange", typing.Dict[builtins.str, typing.Any]]] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param range: range block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#range SqlQuery#range}
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.
        '''
        if isinstance(range, dict):
            range = SqlQueryParameterDatetimeRangeRange(**range)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d48e61c95ad0f50d69f39712a514b95d6751735ac098e4dbb0eaa777d9e31ca)
            check_type(argname="argument range", value=range, expected_type=type_hints["range"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if range is not None:
            self._values["range"] = range
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def range(self) -> typing.Optional["SqlQueryParameterDatetimeRangeRange"]:
        '''range block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#range SqlQuery#range}
        '''
        result = self._values.get("range")
        return typing.cast(typing.Optional["SqlQueryParameterDatetimeRangeRange"], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SqlQueryParameterDatetimeRange(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SqlQueryParameterDatetimeRangeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterDatetimeRangeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__852150fd54e372e93c9495c0e9e42c00a6b9f7caf2e64d40a91269ca97d42aad)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putRange")
    def put_range(self, *, end: builtins.str, start: builtins.str) -> None:
        '''
        :param end: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#end SqlQuery#end}.
        :param start: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#start SqlQuery#start}.
        '''
        value = SqlQueryParameterDatetimeRangeRange(end=end, start=start)

        return typing.cast(None, jsii.invoke(self, "putRange", [value]))

    @jsii.member(jsii_name="resetRange")
    def reset_range(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRange", []))

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="range")
    def range(self) -> "SqlQueryParameterDatetimeRangeRangeOutputReference":
        return typing.cast("SqlQueryParameterDatetimeRangeRangeOutputReference", jsii.get(self, "range"))

    @builtins.property
    @jsii.member(jsii_name="rangeInput")
    def range_input(self) -> typing.Optional["SqlQueryParameterDatetimeRangeRange"]:
        return typing.cast(typing.Optional["SqlQueryParameterDatetimeRangeRange"], jsii.get(self, "rangeInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__28f3d16de9193a48b738ea44b2bb0a148ae9e732a64d7db6dbc025e6a06e4560)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SqlQueryParameterDatetimeRange]:
        return typing.cast(typing.Optional[SqlQueryParameterDatetimeRange], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SqlQueryParameterDatetimeRange],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__908e522295073a7919fc72f9bd086ee1a207ad7f3878f3144bfe4c5d5e79cd47)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterDatetimeRangeRange",
    jsii_struct_bases=[],
    name_mapping={"end": "end", "start": "start"},
)
class SqlQueryParameterDatetimeRangeRange:
    def __init__(self, *, end: builtins.str, start: builtins.str) -> None:
        '''
        :param end: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#end SqlQuery#end}.
        :param start: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#start SqlQuery#start}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5244fd1ccda7611eea1bd8801b96151c1f41757acbc14703385313e0a8820715)
            check_type(argname="argument end", value=end, expected_type=type_hints["end"])
            check_type(argname="argument start", value=start, expected_type=type_hints["start"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "end": end,
            "start": start,
        }

    @builtins.property
    def end(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#end SqlQuery#end}.'''
        result = self._values.get("end")
        assert result is not None, "Required property 'end' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def start(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#start SqlQuery#start}.'''
        result = self._values.get("start")
        assert result is not None, "Required property 'start' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SqlQueryParameterDatetimeRangeRange(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SqlQueryParameterDatetimeRangeRangeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterDatetimeRangeRangeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c4eb5b6a4b0b3c2d6ffd44df370b8d3d9706e84ea6863a9bff91545e9007d789)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0fd415bf08ff08863a94431619379916fcfdd2cd9b514df0192d35d9a19605f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "end", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="start")
    def start(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "start"))

    @start.setter
    def start(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ccff14d67440c4114936eccbd19be3d8a5f501a61cf54d47d33e79828b664afe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "start", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SqlQueryParameterDatetimeRangeRange]:
        return typing.cast(typing.Optional[SqlQueryParameterDatetimeRangeRange], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SqlQueryParameterDatetimeRangeRange],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a7b7c5051f6118b94c0f066c1832049fa2b5c2631a1743d8b897ac97af80764)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterDatetimesec",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class SqlQueryParameterDatetimesec:
    def __init__(self, *, value: builtins.str) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2be8018a3f054e991eb612b9098a16106380fa5750ad9b3ecbe9f10746903b3f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "value": value,
        }

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SqlQueryParameterDatetimesec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SqlQueryParameterDatetimesecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterDatetimesecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e3fe084d6a9ffba8957c7271effd038d90745be857d507bb33fce3941570ccf0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ad0267b6fa861da429258bbc1fdfff4ad412d231c9758bce3d7ae1f05cdf160c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SqlQueryParameterDatetimesec]:
        return typing.cast(typing.Optional[SqlQueryParameterDatetimesec], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SqlQueryParameterDatetimesec],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca79157ff45803bb0db91f193f7b0b697aec693e930f87629bc043e05c5426b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterDatetimesecRange",
    jsii_struct_bases=[],
    name_mapping={"range": "range", "value": "value"},
)
class SqlQueryParameterDatetimesecRange:
    def __init__(
        self,
        *,
        range: typing.Optional[typing.Union["SqlQueryParameterDatetimesecRangeRange", typing.Dict[builtins.str, typing.Any]]] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param range: range block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#range SqlQuery#range}
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.
        '''
        if isinstance(range, dict):
            range = SqlQueryParameterDatetimesecRangeRange(**range)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fbb4fdb9ec4403b5582a8d27b2164222f07f3897b0b4d3986df7a1d13bd8c95)
            check_type(argname="argument range", value=range, expected_type=type_hints["range"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if range is not None:
            self._values["range"] = range
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def range(self) -> typing.Optional["SqlQueryParameterDatetimesecRangeRange"]:
        '''range block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#range SqlQuery#range}
        '''
        result = self._values.get("range")
        return typing.cast(typing.Optional["SqlQueryParameterDatetimesecRangeRange"], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SqlQueryParameterDatetimesecRange(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SqlQueryParameterDatetimesecRangeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterDatetimesecRangeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b7ac632d5d0b057ff23179c522f343e148d102a6c054c589e4318713a2848979)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putRange")
    def put_range(self, *, end: builtins.str, start: builtins.str) -> None:
        '''
        :param end: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#end SqlQuery#end}.
        :param start: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#start SqlQuery#start}.
        '''
        value = SqlQueryParameterDatetimesecRangeRange(end=end, start=start)

        return typing.cast(None, jsii.invoke(self, "putRange", [value]))

    @jsii.member(jsii_name="resetRange")
    def reset_range(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRange", []))

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="range")
    def range(self) -> "SqlQueryParameterDatetimesecRangeRangeOutputReference":
        return typing.cast("SqlQueryParameterDatetimesecRangeRangeOutputReference", jsii.get(self, "range"))

    @builtins.property
    @jsii.member(jsii_name="rangeInput")
    def range_input(self) -> typing.Optional["SqlQueryParameterDatetimesecRangeRange"]:
        return typing.cast(typing.Optional["SqlQueryParameterDatetimesecRangeRange"], jsii.get(self, "rangeInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__1b1c5926db5d2a5a720024d1d9f62259533344865f29ec2e1e21dcbc31d0ea81)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SqlQueryParameterDatetimesecRange]:
        return typing.cast(typing.Optional[SqlQueryParameterDatetimesecRange], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SqlQueryParameterDatetimesecRange],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75994c3de13f97afdd3a5241b8cbb67227bdb28dff5befe17ce4079a8f6c92ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterDatetimesecRangeRange",
    jsii_struct_bases=[],
    name_mapping={"end": "end", "start": "start"},
)
class SqlQueryParameterDatetimesecRangeRange:
    def __init__(self, *, end: builtins.str, start: builtins.str) -> None:
        '''
        :param end: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#end SqlQuery#end}.
        :param start: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#start SqlQuery#start}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ae87a0b9d8aed199eff7056984574daa166b7810bb08b12761c09e9854c8c63)
            check_type(argname="argument end", value=end, expected_type=type_hints["end"])
            check_type(argname="argument start", value=start, expected_type=type_hints["start"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "end": end,
            "start": start,
        }

    @builtins.property
    def end(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#end SqlQuery#end}.'''
        result = self._values.get("end")
        assert result is not None, "Required property 'end' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def start(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#start SqlQuery#start}.'''
        result = self._values.get("start")
        assert result is not None, "Required property 'start' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SqlQueryParameterDatetimesecRangeRange(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SqlQueryParameterDatetimesecRangeRangeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterDatetimesecRangeRangeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__09f87226bf3ea6cb2dd2e5cf9c83896da0efb0705637c96b33217cb9d41aa94d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__dac2a8053eb879f18ede5d42f33d01ebed9493813113f39aaf07d5675ebc89a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "end", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="start")
    def start(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "start"))

    @start.setter
    def start(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6859c0a7e820b0ada3395ae50a17fda92a1074fc5362f6c6053ebade3a990ce8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "start", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SqlQueryParameterDatetimesecRangeRange]:
        return typing.cast(typing.Optional[SqlQueryParameterDatetimesecRangeRange], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SqlQueryParameterDatetimesecRangeRange],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec13f69815ef1bb2500dcdaff56791dc410dc3454e7ab0ae6fa331ee8a825014)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterEnum",
    jsii_struct_bases=[],
    name_mapping={
        "options": "options",
        "multiple": "multiple",
        "value": "value",
        "values": "values",
    },
)
class SqlQueryParameterEnum:
    def __init__(
        self,
        *,
        options: typing.Sequence[builtins.str],
        multiple: typing.Optional[typing.Union["SqlQueryParameterEnumMultiple", typing.Dict[builtins.str, typing.Any]]] = None,
        value: typing.Optional[builtins.str] = None,
        values: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param options: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#options SqlQuery#options}.
        :param multiple: multiple block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#multiple SqlQuery#multiple}
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.
        :param values: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#values SqlQuery#values}.
        '''
        if isinstance(multiple, dict):
            multiple = SqlQueryParameterEnumMultiple(**multiple)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27f4b45f14d5762ae6661fd865d998aa0923ae369e23e89b96eb3bc000665037)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
            check_type(argname="argument multiple", value=multiple, expected_type=type_hints["multiple"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
            check_type(argname="argument values", value=values, expected_type=type_hints["values"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "options": options,
        }
        if multiple is not None:
            self._values["multiple"] = multiple
        if value is not None:
            self._values["value"] = value
        if values is not None:
            self._values["values"] = values

    @builtins.property
    def options(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#options SqlQuery#options}.'''
        result = self._values.get("options")
        assert result is not None, "Required property 'options' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def multiple(self) -> typing.Optional["SqlQueryParameterEnumMultiple"]:
        '''multiple block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#multiple SqlQuery#multiple}
        '''
        result = self._values.get("multiple")
        return typing.cast(typing.Optional["SqlQueryParameterEnumMultiple"], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def values(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#values SqlQuery#values}.'''
        result = self._values.get("values")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SqlQueryParameterEnum(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterEnumMultiple",
    jsii_struct_bases=[],
    name_mapping={"separator": "separator", "prefix": "prefix", "suffix": "suffix"},
)
class SqlQueryParameterEnumMultiple:
    def __init__(
        self,
        *,
        separator: builtins.str,
        prefix: typing.Optional[builtins.str] = None,
        suffix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param separator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#separator SqlQuery#separator}.
        :param prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#prefix SqlQuery#prefix}.
        :param suffix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#suffix SqlQuery#suffix}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81e1895124837d67e9f036b3f2458dbd0a96b584a57989cd0b407a947d7fad34)
            check_type(argname="argument separator", value=separator, expected_type=type_hints["separator"])
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
            check_type(argname="argument suffix", value=suffix, expected_type=type_hints["suffix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "separator": separator,
        }
        if prefix is not None:
            self._values["prefix"] = prefix
        if suffix is not None:
            self._values["suffix"] = suffix

    @builtins.property
    def separator(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#separator SqlQuery#separator}.'''
        result = self._values.get("separator")
        assert result is not None, "Required property 'separator' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#prefix SqlQuery#prefix}.'''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def suffix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#suffix SqlQuery#suffix}.'''
        result = self._values.get("suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SqlQueryParameterEnumMultiple(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SqlQueryParameterEnumMultipleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterEnumMultipleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7c1a4afe02fbb9de03b4dccf350792319b4a3ee23368ea63199494a41e948971)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetPrefix")
    def reset_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefix", []))

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
            type_hints = typing.get_type_hints(_typecheckingstub__b88b0f13a230cc2a5f12b108b7465fc8d064b9f9b6588d47df2415c4a57aef92)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "prefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="separator")
    def separator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "separator"))

    @separator.setter
    def separator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f80358e8d06acec0e2c3e44a52debff52c5bc1153531783983688d6fda02da2f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "separator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="suffix")
    def suffix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "suffix"))

    @suffix.setter
    def suffix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81e843c15e47a6032b8a68e637de6be8fdd601a5faf3bb3966fe303e397e1874)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "suffix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SqlQueryParameterEnumMultiple]:
        return typing.cast(typing.Optional[SqlQueryParameterEnumMultiple], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SqlQueryParameterEnumMultiple],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a6d1fbf61f008caa25fa07e96db273d25637435bbf71e4d59982fdb820df2a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class SqlQueryParameterEnumOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterEnumOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4f00e14c20c0e88831582caad8644472a93f69137e447258e7ec0dff0e6efd89)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putMultiple")
    def put_multiple(
        self,
        *,
        separator: builtins.str,
        prefix: typing.Optional[builtins.str] = None,
        suffix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param separator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#separator SqlQuery#separator}.
        :param prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#prefix SqlQuery#prefix}.
        :param suffix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#suffix SqlQuery#suffix}.
        '''
        value = SqlQueryParameterEnumMultiple(
            separator=separator, prefix=prefix, suffix=suffix
        )

        return typing.cast(None, jsii.invoke(self, "putMultiple", [value]))

    @jsii.member(jsii_name="resetMultiple")
    def reset_multiple(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMultiple", []))

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @jsii.member(jsii_name="resetValues")
    def reset_values(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValues", []))

    @builtins.property
    @jsii.member(jsii_name="multiple")
    def multiple(self) -> SqlQueryParameterEnumMultipleOutputReference:
        return typing.cast(SqlQueryParameterEnumMultipleOutputReference, jsii.get(self, "multiple"))

    @builtins.property
    @jsii.member(jsii_name="multipleInput")
    def multiple_input(self) -> typing.Optional[SqlQueryParameterEnumMultiple]:
        return typing.cast(typing.Optional[SqlQueryParameterEnumMultiple], jsii.get(self, "multipleInput"))

    @builtins.property
    @jsii.member(jsii_name="optionsInput")
    def options_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "optionsInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="valuesInput")
    def values_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "valuesInput"))

    @builtins.property
    @jsii.member(jsii_name="options")
    def options(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "options"))

    @options.setter
    def options(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57e563bf810fb6fd6d3b0ed9a3d66de97bf9a1dfa1f33e1681f3b88bf64be79b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "options", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b9cd0c26fe90f609e4d9955ed3cd3cbb69880e0956340201680a0dfc24c490c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="values")
    def values(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "values"))

    @values.setter
    def values(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__827ea4c64db089a768cb797d9c5e8b2dffa11a4f2e8f28c68659e98186b966f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "values", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SqlQueryParameterEnum]:
        return typing.cast(typing.Optional[SqlQueryParameterEnum], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[SqlQueryParameterEnum]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35f172f346caa41a942775a61e00c93f4b85dbc5c32ece65b89790462b2ad916)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class SqlQueryParameterList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__338e4e803938f0687ee90a2b311455c23bdb61fbde749e7e0a5b38ec9cc739c7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "SqlQueryParameterOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5850df8fa525b259541b38a52b53e78003e6e497e5b2c4454e5ff816d185e8b)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("SqlQueryParameterOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7f0fddff3539cb31d78654935ea423b2578d4d157453f678608bc1ca0c79a07)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5750b1a79f712e0bcc5d76d42423b72350d4bfb0347840ee74e150a7ed52f8f9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__04f05e31e58dd8065372faa1625729e788bf7058f96e4cac0e8d3f68c3b71379)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[SqlQueryParameter]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[SqlQueryParameter]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[SqlQueryParameter]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__164b0948943f22bff3a7b28b6dd74a90f5a390b5d42a99551161a42ec4f6f59a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterNumber",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class SqlQueryParameterNumber:
    def __init__(self, *, value: jsii.Number) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95f9fb77d8f72fbfbd338ca93eccd980d77ca89155b20cadc629363156413342)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "value": value,
        }

    @builtins.property
    def value(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SqlQueryParameterNumber(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SqlQueryParameterNumberOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterNumberOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d758c27f894e92bdae2e2e24a5be347b32651dc16ab51c0bdd3123e5102147ab)
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
            type_hints = typing.get_type_hints(_typecheckingstub__78223e165799e817973ada1d13ce908d4360c59014446391fcf559a2114c7a84)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SqlQueryParameterNumber]:
        return typing.cast(typing.Optional[SqlQueryParameterNumber], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[SqlQueryParameterNumber]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58290e4f5e931d75646a0cc3053de79cad3ae4f6b80aacab18568fe7d47a086e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class SqlQueryParameterOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__293548e368b2b9a5e7624309e573b93126b637ebf9850cad8d0e6a63930ce54b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putDate")
    def put_date(self, *, value: builtins.str) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.
        '''
        value_ = SqlQueryParameterDate(value=value)

        return typing.cast(None, jsii.invoke(self, "putDate", [value_]))

    @jsii.member(jsii_name="putDateRange")
    def put_date_range(
        self,
        *,
        range: typing.Optional[typing.Union[SqlQueryParameterDateRangeRange, typing.Dict[builtins.str, typing.Any]]] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param range: range block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#range SqlQuery#range}
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.
        '''
        value_ = SqlQueryParameterDateRange(range=range, value=value)

        return typing.cast(None, jsii.invoke(self, "putDateRange", [value_]))

    @jsii.member(jsii_name="putDatetime")
    def put_datetime(self, *, value: builtins.str) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.
        '''
        value_ = SqlQueryParameterDatetime(value=value)

        return typing.cast(None, jsii.invoke(self, "putDatetime", [value_]))

    @jsii.member(jsii_name="putDatetimeRange")
    def put_datetime_range(
        self,
        *,
        range: typing.Optional[typing.Union[SqlQueryParameterDatetimeRangeRange, typing.Dict[builtins.str, typing.Any]]] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param range: range block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#range SqlQuery#range}
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.
        '''
        value_ = SqlQueryParameterDatetimeRange(range=range, value=value)

        return typing.cast(None, jsii.invoke(self, "putDatetimeRange", [value_]))

    @jsii.member(jsii_name="putDatetimesec")
    def put_datetimesec(self, *, value: builtins.str) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.
        '''
        value_ = SqlQueryParameterDatetimesec(value=value)

        return typing.cast(None, jsii.invoke(self, "putDatetimesec", [value_]))

    @jsii.member(jsii_name="putDatetimesecRange")
    def put_datetimesec_range(
        self,
        *,
        range: typing.Optional[typing.Union[SqlQueryParameterDatetimesecRangeRange, typing.Dict[builtins.str, typing.Any]]] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param range: range block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#range SqlQuery#range}
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.
        '''
        value_ = SqlQueryParameterDatetimesecRange(range=range, value=value)

        return typing.cast(None, jsii.invoke(self, "putDatetimesecRange", [value_]))

    @jsii.member(jsii_name="putEnum")
    def put_enum(
        self,
        *,
        options: typing.Sequence[builtins.str],
        multiple: typing.Optional[typing.Union[SqlQueryParameterEnumMultiple, typing.Dict[builtins.str, typing.Any]]] = None,
        value: typing.Optional[builtins.str] = None,
        values: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param options: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#options SqlQuery#options}.
        :param multiple: multiple block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#multiple SqlQuery#multiple}
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.
        :param values: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#values SqlQuery#values}.
        '''
        value_ = SqlQueryParameterEnum(
            options=options, multiple=multiple, value=value, values=values
        )

        return typing.cast(None, jsii.invoke(self, "putEnum", [value_]))

    @jsii.member(jsii_name="putNumber")
    def put_number(self, *, value: jsii.Number) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.
        '''
        value_ = SqlQueryParameterNumber(value=value)

        return typing.cast(None, jsii.invoke(self, "putNumber", [value_]))

    @jsii.member(jsii_name="putQuery")
    def put_query(
        self,
        *,
        query_id: builtins.str,
        multiple: typing.Optional[typing.Union["SqlQueryParameterQueryMultiple", typing.Dict[builtins.str, typing.Any]]] = None,
        value: typing.Optional[builtins.str] = None,
        values: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param query_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#query_id SqlQuery#query_id}.
        :param multiple: multiple block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#multiple SqlQuery#multiple}
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.
        :param values: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#values SqlQuery#values}.
        '''
        value_ = SqlQueryParameterQuery(
            query_id=query_id, multiple=multiple, value=value, values=values
        )

        return typing.cast(None, jsii.invoke(self, "putQuery", [value_]))

    @jsii.member(jsii_name="putText")
    def put_text(self, *, value: builtins.str) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.
        '''
        value_ = SqlQueryParameterText(value=value)

        return typing.cast(None, jsii.invoke(self, "putText", [value_]))

    @jsii.member(jsii_name="resetDate")
    def reset_date(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDate", []))

    @jsii.member(jsii_name="resetDateRange")
    def reset_date_range(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDateRange", []))

    @jsii.member(jsii_name="resetDatetime")
    def reset_datetime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatetime", []))

    @jsii.member(jsii_name="resetDatetimeRange")
    def reset_datetime_range(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatetimeRange", []))

    @jsii.member(jsii_name="resetDatetimesec")
    def reset_datetimesec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatetimesec", []))

    @jsii.member(jsii_name="resetDatetimesecRange")
    def reset_datetimesec_range(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatetimesecRange", []))

    @jsii.member(jsii_name="resetEnum")
    def reset_enum(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnum", []))

    @jsii.member(jsii_name="resetNumber")
    def reset_number(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumber", []))

    @jsii.member(jsii_name="resetQuery")
    def reset_query(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQuery", []))

    @jsii.member(jsii_name="resetText")
    def reset_text(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetText", []))

    @jsii.member(jsii_name="resetTitle")
    def reset_title(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTitle", []))

    @builtins.property
    @jsii.member(jsii_name="date")
    def date(self) -> SqlQueryParameterDateOutputReference:
        return typing.cast(SqlQueryParameterDateOutputReference, jsii.get(self, "date"))

    @builtins.property
    @jsii.member(jsii_name="dateRange")
    def date_range(self) -> SqlQueryParameterDateRangeOutputReference:
        return typing.cast(SqlQueryParameterDateRangeOutputReference, jsii.get(self, "dateRange"))

    @builtins.property
    @jsii.member(jsii_name="datetime")
    def datetime(self) -> SqlQueryParameterDatetimeOutputReference:
        return typing.cast(SqlQueryParameterDatetimeOutputReference, jsii.get(self, "datetime"))

    @builtins.property
    @jsii.member(jsii_name="datetimeRange")
    def datetime_range(self) -> SqlQueryParameterDatetimeRangeOutputReference:
        return typing.cast(SqlQueryParameterDatetimeRangeOutputReference, jsii.get(self, "datetimeRange"))

    @builtins.property
    @jsii.member(jsii_name="datetimesec")
    def datetimesec(self) -> SqlQueryParameterDatetimesecOutputReference:
        return typing.cast(SqlQueryParameterDatetimesecOutputReference, jsii.get(self, "datetimesec"))

    @builtins.property
    @jsii.member(jsii_name="datetimesecRange")
    def datetimesec_range(self) -> SqlQueryParameterDatetimesecRangeOutputReference:
        return typing.cast(SqlQueryParameterDatetimesecRangeOutputReference, jsii.get(self, "datetimesecRange"))

    @builtins.property
    @jsii.member(jsii_name="enum")
    def enum(self) -> SqlQueryParameterEnumOutputReference:
        return typing.cast(SqlQueryParameterEnumOutputReference, jsii.get(self, "enum"))

    @builtins.property
    @jsii.member(jsii_name="number")
    def number(self) -> SqlQueryParameterNumberOutputReference:
        return typing.cast(SqlQueryParameterNumberOutputReference, jsii.get(self, "number"))

    @builtins.property
    @jsii.member(jsii_name="query")
    def query(self) -> "SqlQueryParameterQueryOutputReference":
        return typing.cast("SqlQueryParameterQueryOutputReference", jsii.get(self, "query"))

    @builtins.property
    @jsii.member(jsii_name="text")
    def text(self) -> "SqlQueryParameterTextOutputReference":
        return typing.cast("SqlQueryParameterTextOutputReference", jsii.get(self, "text"))

    @builtins.property
    @jsii.member(jsii_name="dateInput")
    def date_input(self) -> typing.Optional[SqlQueryParameterDate]:
        return typing.cast(typing.Optional[SqlQueryParameterDate], jsii.get(self, "dateInput"))

    @builtins.property
    @jsii.member(jsii_name="dateRangeInput")
    def date_range_input(self) -> typing.Optional[SqlQueryParameterDateRange]:
        return typing.cast(typing.Optional[SqlQueryParameterDateRange], jsii.get(self, "dateRangeInput"))

    @builtins.property
    @jsii.member(jsii_name="datetimeInput")
    def datetime_input(self) -> typing.Optional[SqlQueryParameterDatetime]:
        return typing.cast(typing.Optional[SqlQueryParameterDatetime], jsii.get(self, "datetimeInput"))

    @builtins.property
    @jsii.member(jsii_name="datetimeRangeInput")
    def datetime_range_input(self) -> typing.Optional[SqlQueryParameterDatetimeRange]:
        return typing.cast(typing.Optional[SqlQueryParameterDatetimeRange], jsii.get(self, "datetimeRangeInput"))

    @builtins.property
    @jsii.member(jsii_name="datetimesecInput")
    def datetimesec_input(self) -> typing.Optional[SqlQueryParameterDatetimesec]:
        return typing.cast(typing.Optional[SqlQueryParameterDatetimesec], jsii.get(self, "datetimesecInput"))

    @builtins.property
    @jsii.member(jsii_name="datetimesecRangeInput")
    def datetimesec_range_input(
        self,
    ) -> typing.Optional[SqlQueryParameterDatetimesecRange]:
        return typing.cast(typing.Optional[SqlQueryParameterDatetimesecRange], jsii.get(self, "datetimesecRangeInput"))

    @builtins.property
    @jsii.member(jsii_name="enumInput")
    def enum_input(self) -> typing.Optional[SqlQueryParameterEnum]:
        return typing.cast(typing.Optional[SqlQueryParameterEnum], jsii.get(self, "enumInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="numberInput")
    def number_input(self) -> typing.Optional[SqlQueryParameterNumber]:
        return typing.cast(typing.Optional[SqlQueryParameterNumber], jsii.get(self, "numberInput"))

    @builtins.property
    @jsii.member(jsii_name="queryInput")
    def query_input(self) -> typing.Optional["SqlQueryParameterQuery"]:
        return typing.cast(typing.Optional["SqlQueryParameterQuery"], jsii.get(self, "queryInput"))

    @builtins.property
    @jsii.member(jsii_name="textInput")
    def text_input(self) -> typing.Optional["SqlQueryParameterText"]:
        return typing.cast(typing.Optional["SqlQueryParameterText"], jsii.get(self, "textInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__62092ae9591109c5c45ac157f07be82b2838bff3589719bb02680732f0b5ce97)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @title.setter
    def title(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dac72c08f42d37e373120f8a2faffc7a052fb4f8009812ebf490fa9e2dd4e092)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "title", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SqlQueryParameter]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SqlQueryParameter]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SqlQueryParameter]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6554320435ca9aa14cbe306670b69867bb5cd5ed0c09e52a3cb88016f2aacb04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterQuery",
    jsii_struct_bases=[],
    name_mapping={
        "query_id": "queryId",
        "multiple": "multiple",
        "value": "value",
        "values": "values",
    },
)
class SqlQueryParameterQuery:
    def __init__(
        self,
        *,
        query_id: builtins.str,
        multiple: typing.Optional[typing.Union["SqlQueryParameterQueryMultiple", typing.Dict[builtins.str, typing.Any]]] = None,
        value: typing.Optional[builtins.str] = None,
        values: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param query_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#query_id SqlQuery#query_id}.
        :param multiple: multiple block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#multiple SqlQuery#multiple}
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.
        :param values: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#values SqlQuery#values}.
        '''
        if isinstance(multiple, dict):
            multiple = SqlQueryParameterQueryMultiple(**multiple)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8e2b5f947ed9fc6a447b08a812d48ae5c9156e9e0eddac29b2fcef36777c38e)
            check_type(argname="argument query_id", value=query_id, expected_type=type_hints["query_id"])
            check_type(argname="argument multiple", value=multiple, expected_type=type_hints["multiple"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
            check_type(argname="argument values", value=values, expected_type=type_hints["values"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "query_id": query_id,
        }
        if multiple is not None:
            self._values["multiple"] = multiple
        if value is not None:
            self._values["value"] = value
        if values is not None:
            self._values["values"] = values

    @builtins.property
    def query_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#query_id SqlQuery#query_id}.'''
        result = self._values.get("query_id")
        assert result is not None, "Required property 'query_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def multiple(self) -> typing.Optional["SqlQueryParameterQueryMultiple"]:
        '''multiple block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#multiple SqlQuery#multiple}
        '''
        result = self._values.get("multiple")
        return typing.cast(typing.Optional["SqlQueryParameterQueryMultiple"], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def values(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#values SqlQuery#values}.'''
        result = self._values.get("values")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SqlQueryParameterQuery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterQueryMultiple",
    jsii_struct_bases=[],
    name_mapping={"separator": "separator", "prefix": "prefix", "suffix": "suffix"},
)
class SqlQueryParameterQueryMultiple:
    def __init__(
        self,
        *,
        separator: builtins.str,
        prefix: typing.Optional[builtins.str] = None,
        suffix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param separator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#separator SqlQuery#separator}.
        :param prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#prefix SqlQuery#prefix}.
        :param suffix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#suffix SqlQuery#suffix}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6043a233f169b277af0bd5385752a715f5ea51d40f44967d3a661706b4f42758)
            check_type(argname="argument separator", value=separator, expected_type=type_hints["separator"])
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
            check_type(argname="argument suffix", value=suffix, expected_type=type_hints["suffix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "separator": separator,
        }
        if prefix is not None:
            self._values["prefix"] = prefix
        if suffix is not None:
            self._values["suffix"] = suffix

    @builtins.property
    def separator(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#separator SqlQuery#separator}.'''
        result = self._values.get("separator")
        assert result is not None, "Required property 'separator' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#prefix SqlQuery#prefix}.'''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def suffix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#suffix SqlQuery#suffix}.'''
        result = self._values.get("suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SqlQueryParameterQueryMultiple(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SqlQueryParameterQueryMultipleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterQueryMultipleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b71243a774c0c375691078935c47aad26077374b096cd04aa578616b75d91d4c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetPrefix")
    def reset_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefix", []))

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
            type_hints = typing.get_type_hints(_typecheckingstub__310a8478c150458de9b7b336e92dd2609c8c42c64fa31fed5db8dcb3485a716e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "prefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="separator")
    def separator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "separator"))

    @separator.setter
    def separator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4152f0af7d9f8bd00858561ed884c47477d8ef983b8cc338cb0e42621326fc10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "separator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="suffix")
    def suffix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "suffix"))

    @suffix.setter
    def suffix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__947d3bdffc88663783283741b83acd3bc834f3a78ea1fb21b98b137ebebdd804)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "suffix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SqlQueryParameterQueryMultiple]:
        return typing.cast(typing.Optional[SqlQueryParameterQueryMultiple], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SqlQueryParameterQueryMultiple],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e18ae8b38561bc8e17f83ccce02faffd3493bdb0c9f389556220025228d254ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class SqlQueryParameterQueryOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterQueryOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2a2961ebc20eeef593dd1f7cb2c95ad89b05de0f804b4e55b2d1231029731c2e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putMultiple")
    def put_multiple(
        self,
        *,
        separator: builtins.str,
        prefix: typing.Optional[builtins.str] = None,
        suffix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param separator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#separator SqlQuery#separator}.
        :param prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#prefix SqlQuery#prefix}.
        :param suffix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#suffix SqlQuery#suffix}.
        '''
        value = SqlQueryParameterQueryMultiple(
            separator=separator, prefix=prefix, suffix=suffix
        )

        return typing.cast(None, jsii.invoke(self, "putMultiple", [value]))

    @jsii.member(jsii_name="resetMultiple")
    def reset_multiple(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMultiple", []))

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @jsii.member(jsii_name="resetValues")
    def reset_values(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValues", []))

    @builtins.property
    @jsii.member(jsii_name="multiple")
    def multiple(self) -> SqlQueryParameterQueryMultipleOutputReference:
        return typing.cast(SqlQueryParameterQueryMultipleOutputReference, jsii.get(self, "multiple"))

    @builtins.property
    @jsii.member(jsii_name="multipleInput")
    def multiple_input(self) -> typing.Optional[SqlQueryParameterQueryMultiple]:
        return typing.cast(typing.Optional[SqlQueryParameterQueryMultiple], jsii.get(self, "multipleInput"))

    @builtins.property
    @jsii.member(jsii_name="queryIdInput")
    def query_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queryIdInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__96f15e7a41bc4867025cda18536efde79879d17ab6a3bf35800a9f14135dba2c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "queryId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cb78864c89a84c1017beb4754c84a98db8f9d7cd6b9bee60be6b5a014b82bb1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="values")
    def values(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "values"))

    @values.setter
    def values(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10ee5b4c051d15ea4aaf710117d24717137d26024e2ca24c68f706b2242c36ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "values", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SqlQueryParameterQuery]:
        return typing.cast(typing.Optional[SqlQueryParameterQuery], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[SqlQueryParameterQuery]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db9290a4b0f41ff306ceaf8a584ca887bef1bbe7aae4d6d07e63c82fd5e19a7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterText",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class SqlQueryParameterText:
    def __init__(self, *, value: builtins.str) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c69a585e6156e2d172caba6f0a1ec2532d58e14965eacc8a488588e82ef5e53c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "value": value,
        }

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#value SqlQuery#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SqlQueryParameterText(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SqlQueryParameterTextOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryParameterTextOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__89e3d3ac9cb100cadda8919f2319d18ee27719299b78a4d34ed73d23939b9f63)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d69e6198da0286b2e0dd0684f9ab7c8ab877c1d4c6e4c3a2d31c6e5a46abea45)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SqlQueryParameterText]:
        return typing.cast(typing.Optional[SqlQueryParameterText], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[SqlQueryParameterText]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e006cae5ed549ed666a4e83159bb94918687db05960e3fb1ce97e816e240f756)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQuerySchedule",
    jsii_struct_bases=[],
    name_mapping={"continuous": "continuous", "daily": "daily", "weekly": "weekly"},
)
class SqlQuerySchedule:
    def __init__(
        self,
        *,
        continuous: typing.Optional[typing.Union["SqlQueryScheduleContinuous", typing.Dict[builtins.str, typing.Any]]] = None,
        daily: typing.Optional[typing.Union["SqlQueryScheduleDaily", typing.Dict[builtins.str, typing.Any]]] = None,
        weekly: typing.Optional[typing.Union["SqlQueryScheduleWeekly", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param continuous: continuous block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#continuous SqlQuery#continuous}
        :param daily: daily block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#daily SqlQuery#daily}
        :param weekly: weekly block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#weekly SqlQuery#weekly}
        '''
        if isinstance(continuous, dict):
            continuous = SqlQueryScheduleContinuous(**continuous)
        if isinstance(daily, dict):
            daily = SqlQueryScheduleDaily(**daily)
        if isinstance(weekly, dict):
            weekly = SqlQueryScheduleWeekly(**weekly)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__196cbe3b5841d0707b7b58d9a8b59a53645fd0d6aa82376c59f580f2d997e8f6)
            check_type(argname="argument continuous", value=continuous, expected_type=type_hints["continuous"])
            check_type(argname="argument daily", value=daily, expected_type=type_hints["daily"])
            check_type(argname="argument weekly", value=weekly, expected_type=type_hints["weekly"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if continuous is not None:
            self._values["continuous"] = continuous
        if daily is not None:
            self._values["daily"] = daily
        if weekly is not None:
            self._values["weekly"] = weekly

    @builtins.property
    def continuous(self) -> typing.Optional["SqlQueryScheduleContinuous"]:
        '''continuous block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#continuous SqlQuery#continuous}
        '''
        result = self._values.get("continuous")
        return typing.cast(typing.Optional["SqlQueryScheduleContinuous"], result)

    @builtins.property
    def daily(self) -> typing.Optional["SqlQueryScheduleDaily"]:
        '''daily block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#daily SqlQuery#daily}
        '''
        result = self._values.get("daily")
        return typing.cast(typing.Optional["SqlQueryScheduleDaily"], result)

    @builtins.property
    def weekly(self) -> typing.Optional["SqlQueryScheduleWeekly"]:
        '''weekly block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#weekly SqlQuery#weekly}
        '''
        result = self._values.get("weekly")
        return typing.cast(typing.Optional["SqlQueryScheduleWeekly"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SqlQuerySchedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryScheduleContinuous",
    jsii_struct_bases=[],
    name_mapping={"interval_seconds": "intervalSeconds", "until_date": "untilDate"},
)
class SqlQueryScheduleContinuous:
    def __init__(
        self,
        *,
        interval_seconds: jsii.Number,
        until_date: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param interval_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#interval_seconds SqlQuery#interval_seconds}.
        :param until_date: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#until_date SqlQuery#until_date}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9d05fd1ed96d3d1a095d9e60fc4074542262251d1c8fe152159abe86cffb0b1)
            check_type(argname="argument interval_seconds", value=interval_seconds, expected_type=type_hints["interval_seconds"])
            check_type(argname="argument until_date", value=until_date, expected_type=type_hints["until_date"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "interval_seconds": interval_seconds,
        }
        if until_date is not None:
            self._values["until_date"] = until_date

    @builtins.property
    def interval_seconds(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#interval_seconds SqlQuery#interval_seconds}.'''
        result = self._values.get("interval_seconds")
        assert result is not None, "Required property 'interval_seconds' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def until_date(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#until_date SqlQuery#until_date}.'''
        result = self._values.get("until_date")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SqlQueryScheduleContinuous(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SqlQueryScheduleContinuousOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryScheduleContinuousOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f9a5030edbafed43d18cbfb9e5d429c794089332802a3f34c4b312c89b93259f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetUntilDate")
    def reset_until_date(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUntilDate", []))

    @builtins.property
    @jsii.member(jsii_name="intervalSecondsInput")
    def interval_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "intervalSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="untilDateInput")
    def until_date_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "untilDateInput"))

    @builtins.property
    @jsii.member(jsii_name="intervalSeconds")
    def interval_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "intervalSeconds"))

    @interval_seconds.setter
    def interval_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4386c21450a59e16ade5388c748e97138d9e66d770ec3875f1c1dd17f19a7247)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "intervalSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="untilDate")
    def until_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "untilDate"))

    @until_date.setter
    def until_date(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2f7c2b42caf175be078a0acccc369a4c8fb5c2aaa89440bdde6ad8bee055203)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "untilDate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SqlQueryScheduleContinuous]:
        return typing.cast(typing.Optional[SqlQueryScheduleContinuous], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SqlQueryScheduleContinuous],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__213f69924ca3a06944562a46b2888bbd66b36489032572aae576096f9aa1952d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryScheduleDaily",
    jsii_struct_bases=[],
    name_mapping={
        "interval_days": "intervalDays",
        "time_of_day": "timeOfDay",
        "until_date": "untilDate",
    },
)
class SqlQueryScheduleDaily:
    def __init__(
        self,
        *,
        interval_days: jsii.Number,
        time_of_day: builtins.str,
        until_date: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param interval_days: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#interval_days SqlQuery#interval_days}.
        :param time_of_day: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#time_of_day SqlQuery#time_of_day}.
        :param until_date: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#until_date SqlQuery#until_date}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01c1068332cb1e8e24d320e347dd3765a35703e32608c75f40f4e77101f53eb1)
            check_type(argname="argument interval_days", value=interval_days, expected_type=type_hints["interval_days"])
            check_type(argname="argument time_of_day", value=time_of_day, expected_type=type_hints["time_of_day"])
            check_type(argname="argument until_date", value=until_date, expected_type=type_hints["until_date"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "interval_days": interval_days,
            "time_of_day": time_of_day,
        }
        if until_date is not None:
            self._values["until_date"] = until_date

    @builtins.property
    def interval_days(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#interval_days SqlQuery#interval_days}.'''
        result = self._values.get("interval_days")
        assert result is not None, "Required property 'interval_days' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def time_of_day(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#time_of_day SqlQuery#time_of_day}.'''
        result = self._values.get("time_of_day")
        assert result is not None, "Required property 'time_of_day' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def until_date(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#until_date SqlQuery#until_date}.'''
        result = self._values.get("until_date")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SqlQueryScheduleDaily(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SqlQueryScheduleDailyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryScheduleDailyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0972a399436449e71732130daa5a3769c52868b9fb9a86a1ad0d352731f0eda1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetUntilDate")
    def reset_until_date(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUntilDate", []))

    @builtins.property
    @jsii.member(jsii_name="intervalDaysInput")
    def interval_days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "intervalDaysInput"))

    @builtins.property
    @jsii.member(jsii_name="timeOfDayInput")
    def time_of_day_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timeOfDayInput"))

    @builtins.property
    @jsii.member(jsii_name="untilDateInput")
    def until_date_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "untilDateInput"))

    @builtins.property
    @jsii.member(jsii_name="intervalDays")
    def interval_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "intervalDays"))

    @interval_days.setter
    def interval_days(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19b89ae7fb34a25d2ca39402a9f98a733cbbd3c722c36dcbd1f7367cbd37da8b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "intervalDays", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeOfDay")
    def time_of_day(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeOfDay"))

    @time_of_day.setter
    def time_of_day(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9743d833944299586b6da489a819b2fafb81c0389d69b614dfa7056b352ba40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeOfDay", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="untilDate")
    def until_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "untilDate"))

    @until_date.setter
    def until_date(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d753f65785537aee819176a7bd4f00fe95c755c3a726444523776b4bd9bcb3c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "untilDate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SqlQueryScheduleDaily]:
        return typing.cast(typing.Optional[SqlQueryScheduleDaily], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[SqlQueryScheduleDaily]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d096c325f45db1ff0b644dd468cf9f8f564102f2d4608127998f0bf1b1c3560)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class SqlQueryScheduleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryScheduleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ea1631a1f985c9822ad50a38f47ef62800871f771a6f8d7c2692a6c6975e956d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putContinuous")
    def put_continuous(
        self,
        *,
        interval_seconds: jsii.Number,
        until_date: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param interval_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#interval_seconds SqlQuery#interval_seconds}.
        :param until_date: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#until_date SqlQuery#until_date}.
        '''
        value = SqlQueryScheduleContinuous(
            interval_seconds=interval_seconds, until_date=until_date
        )

        return typing.cast(None, jsii.invoke(self, "putContinuous", [value]))

    @jsii.member(jsii_name="putDaily")
    def put_daily(
        self,
        *,
        interval_days: jsii.Number,
        time_of_day: builtins.str,
        until_date: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param interval_days: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#interval_days SqlQuery#interval_days}.
        :param time_of_day: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#time_of_day SqlQuery#time_of_day}.
        :param until_date: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#until_date SqlQuery#until_date}.
        '''
        value = SqlQueryScheduleDaily(
            interval_days=interval_days, time_of_day=time_of_day, until_date=until_date
        )

        return typing.cast(None, jsii.invoke(self, "putDaily", [value]))

    @jsii.member(jsii_name="putWeekly")
    def put_weekly(
        self,
        *,
        day_of_week: builtins.str,
        interval_weeks: jsii.Number,
        time_of_day: builtins.str,
        until_date: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param day_of_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#day_of_week SqlQuery#day_of_week}.
        :param interval_weeks: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#interval_weeks SqlQuery#interval_weeks}.
        :param time_of_day: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#time_of_day SqlQuery#time_of_day}.
        :param until_date: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#until_date SqlQuery#until_date}.
        '''
        value = SqlQueryScheduleWeekly(
            day_of_week=day_of_week,
            interval_weeks=interval_weeks,
            time_of_day=time_of_day,
            until_date=until_date,
        )

        return typing.cast(None, jsii.invoke(self, "putWeekly", [value]))

    @jsii.member(jsii_name="resetContinuous")
    def reset_continuous(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContinuous", []))

    @jsii.member(jsii_name="resetDaily")
    def reset_daily(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDaily", []))

    @jsii.member(jsii_name="resetWeekly")
    def reset_weekly(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWeekly", []))

    @builtins.property
    @jsii.member(jsii_name="continuous")
    def continuous(self) -> SqlQueryScheduleContinuousOutputReference:
        return typing.cast(SqlQueryScheduleContinuousOutputReference, jsii.get(self, "continuous"))

    @builtins.property
    @jsii.member(jsii_name="daily")
    def daily(self) -> SqlQueryScheduleDailyOutputReference:
        return typing.cast(SqlQueryScheduleDailyOutputReference, jsii.get(self, "daily"))

    @builtins.property
    @jsii.member(jsii_name="weekly")
    def weekly(self) -> "SqlQueryScheduleWeeklyOutputReference":
        return typing.cast("SqlQueryScheduleWeeklyOutputReference", jsii.get(self, "weekly"))

    @builtins.property
    @jsii.member(jsii_name="continuousInput")
    def continuous_input(self) -> typing.Optional[SqlQueryScheduleContinuous]:
        return typing.cast(typing.Optional[SqlQueryScheduleContinuous], jsii.get(self, "continuousInput"))

    @builtins.property
    @jsii.member(jsii_name="dailyInput")
    def daily_input(self) -> typing.Optional[SqlQueryScheduleDaily]:
        return typing.cast(typing.Optional[SqlQueryScheduleDaily], jsii.get(self, "dailyInput"))

    @builtins.property
    @jsii.member(jsii_name="weeklyInput")
    def weekly_input(self) -> typing.Optional["SqlQueryScheduleWeekly"]:
        return typing.cast(typing.Optional["SqlQueryScheduleWeekly"], jsii.get(self, "weeklyInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SqlQuerySchedule]:
        return typing.cast(typing.Optional[SqlQuerySchedule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[SqlQuerySchedule]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8214772b14edbc9e6a761a9ad757072370c69dd62de6def404f4e4ab5086c7db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryScheduleWeekly",
    jsii_struct_bases=[],
    name_mapping={
        "day_of_week": "dayOfWeek",
        "interval_weeks": "intervalWeeks",
        "time_of_day": "timeOfDay",
        "until_date": "untilDate",
    },
)
class SqlQueryScheduleWeekly:
    def __init__(
        self,
        *,
        day_of_week: builtins.str,
        interval_weeks: jsii.Number,
        time_of_day: builtins.str,
        until_date: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param day_of_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#day_of_week SqlQuery#day_of_week}.
        :param interval_weeks: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#interval_weeks SqlQuery#interval_weeks}.
        :param time_of_day: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#time_of_day SqlQuery#time_of_day}.
        :param until_date: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#until_date SqlQuery#until_date}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf65635a3685101330be6e83bd0567c2c6b427255dcaef0fcb94ffdf93cbfa1b)
            check_type(argname="argument day_of_week", value=day_of_week, expected_type=type_hints["day_of_week"])
            check_type(argname="argument interval_weeks", value=interval_weeks, expected_type=type_hints["interval_weeks"])
            check_type(argname="argument time_of_day", value=time_of_day, expected_type=type_hints["time_of_day"])
            check_type(argname="argument until_date", value=until_date, expected_type=type_hints["until_date"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "day_of_week": day_of_week,
            "interval_weeks": interval_weeks,
            "time_of_day": time_of_day,
        }
        if until_date is not None:
            self._values["until_date"] = until_date

    @builtins.property
    def day_of_week(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#day_of_week SqlQuery#day_of_week}.'''
        result = self._values.get("day_of_week")
        assert result is not None, "Required property 'day_of_week' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def interval_weeks(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#interval_weeks SqlQuery#interval_weeks}.'''
        result = self._values.get("interval_weeks")
        assert result is not None, "Required property 'interval_weeks' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def time_of_day(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#time_of_day SqlQuery#time_of_day}.'''
        result = self._values.get("time_of_day")
        assert result is not None, "Required property 'time_of_day' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def until_date(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/sql_query#until_date SqlQuery#until_date}.'''
        result = self._values.get("until_date")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SqlQueryScheduleWeekly(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SqlQueryScheduleWeeklyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.sqlQuery.SqlQueryScheduleWeeklyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a660d3530e12f067581024cbd38f401d9c23a020718398f1b530a4642e1d3984)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetUntilDate")
    def reset_until_date(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUntilDate", []))

    @builtins.property
    @jsii.member(jsii_name="dayOfWeekInput")
    def day_of_week_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dayOfWeekInput"))

    @builtins.property
    @jsii.member(jsii_name="intervalWeeksInput")
    def interval_weeks_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "intervalWeeksInput"))

    @builtins.property
    @jsii.member(jsii_name="timeOfDayInput")
    def time_of_day_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timeOfDayInput"))

    @builtins.property
    @jsii.member(jsii_name="untilDateInput")
    def until_date_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "untilDateInput"))

    @builtins.property
    @jsii.member(jsii_name="dayOfWeek")
    def day_of_week(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dayOfWeek"))

    @day_of_week.setter
    def day_of_week(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cf589f5b3d87290941df9d84af33f60dc9d4929fa4138fc763157f351f806f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dayOfWeek", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="intervalWeeks")
    def interval_weeks(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "intervalWeeks"))

    @interval_weeks.setter
    def interval_weeks(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e42ff4c206de92fb3a3e70c3f424533ff43c3c63c630e114d0e793f41eb50a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "intervalWeeks", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeOfDay")
    def time_of_day(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeOfDay"))

    @time_of_day.setter
    def time_of_day(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__979823d27b505754f30b98cd5c34fed2d8cf0b5ac50e2a2ccdb2166a72c9293e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeOfDay", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="untilDate")
    def until_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "untilDate"))

    @until_date.setter
    def until_date(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81df11da1792f86ca2acaf3f9642d65e5445e1998040146b83a361442d10eeca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "untilDate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SqlQueryScheduleWeekly]:
        return typing.cast(typing.Optional[SqlQueryScheduleWeekly], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[SqlQueryScheduleWeekly]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c9d183d69bda62fe0dd8f0165e84aa3a591847eeb19ded8e55e31518bedc7e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "SqlQuery",
    "SqlQueryConfig",
    "SqlQueryParameter",
    "SqlQueryParameterDate",
    "SqlQueryParameterDateOutputReference",
    "SqlQueryParameterDateRange",
    "SqlQueryParameterDateRangeOutputReference",
    "SqlQueryParameterDateRangeRange",
    "SqlQueryParameterDateRangeRangeOutputReference",
    "SqlQueryParameterDatetime",
    "SqlQueryParameterDatetimeOutputReference",
    "SqlQueryParameterDatetimeRange",
    "SqlQueryParameterDatetimeRangeOutputReference",
    "SqlQueryParameterDatetimeRangeRange",
    "SqlQueryParameterDatetimeRangeRangeOutputReference",
    "SqlQueryParameterDatetimesec",
    "SqlQueryParameterDatetimesecOutputReference",
    "SqlQueryParameterDatetimesecRange",
    "SqlQueryParameterDatetimesecRangeOutputReference",
    "SqlQueryParameterDatetimesecRangeRange",
    "SqlQueryParameterDatetimesecRangeRangeOutputReference",
    "SqlQueryParameterEnum",
    "SqlQueryParameterEnumMultiple",
    "SqlQueryParameterEnumMultipleOutputReference",
    "SqlQueryParameterEnumOutputReference",
    "SqlQueryParameterList",
    "SqlQueryParameterNumber",
    "SqlQueryParameterNumberOutputReference",
    "SqlQueryParameterOutputReference",
    "SqlQueryParameterQuery",
    "SqlQueryParameterQueryMultiple",
    "SqlQueryParameterQueryMultipleOutputReference",
    "SqlQueryParameterQueryOutputReference",
    "SqlQueryParameterText",
    "SqlQueryParameterTextOutputReference",
    "SqlQuerySchedule",
    "SqlQueryScheduleContinuous",
    "SqlQueryScheduleContinuousOutputReference",
    "SqlQueryScheduleDaily",
    "SqlQueryScheduleDailyOutputReference",
    "SqlQueryScheduleOutputReference",
    "SqlQueryScheduleWeekly",
    "SqlQueryScheduleWeeklyOutputReference",
]

publication.publish()

def _typecheckingstub__524a8bd60b3ff93d305683d68c92115f986997010e0ec6316cf9423ac98694eb(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    data_source_id: builtins.str,
    name: builtins.str,
    query: builtins.str,
    created_at: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    parameter: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[SqlQueryParameter, typing.Dict[builtins.str, typing.Any]]]]] = None,
    parent: typing.Optional[builtins.str] = None,
    run_as_role: typing.Optional[builtins.str] = None,
    schedule: typing.Optional[typing.Union[SqlQuerySchedule, typing.Dict[builtins.str, typing.Any]]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    updated_at: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__6ef8f9f18d586e215cc47695d845c1b44ca76c127f142d0e63e1e810c0eddf12(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2b56a9ebe162b1ba217e3a89e451c1aaf3b51954b2b6f037ce275dfd479826b(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[SqlQueryParameter, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5e07aed1dbcd31cbdab854ec13f6ebc05f842c903ad3db6117e575174c86763(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d1ce5c5eb7cd556ea10048ab1a44c20a515b30183221b5e54defeddec2e6372(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97f9e6c9b5003ba2059a4b5915efba3e4c525e9731aa7f08e7e3ac588ff962ba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c0b117d4f3a2cfc6a811329a8847c89eca4cb39a06d1934a111692ffe812872(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c263d9980714de79fc51926fc6b3eff9538be6539beacea1f6b71644546564f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a7395b77eeb1a0509d56db1d014e998cee2da6666366134e91f608a48cae7cf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94bf7552667bd8fc4f86244a388a0095b3c7315a9a23efd89eb5ec326ce7477f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d34c2f7559e109eebf1c9fb9defdd0d7bf801db87c06c67e9d32d41027db5ba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dafbadfa47972d371f8519f91157ce51d44f4eaa635a86f9f6fd69a82e5343c5(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be1b042034f3ddf8d8ceb4767013de549ce0e2b389f1d744846aac41cd128c9c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa7496d62934e8102301b3aeb79095478e90c80ab3551e47460bc21c7a9c098e(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    data_source_id: builtins.str,
    name: builtins.str,
    query: builtins.str,
    created_at: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    parameter: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[SqlQueryParameter, typing.Dict[builtins.str, typing.Any]]]]] = None,
    parent: typing.Optional[builtins.str] = None,
    run_as_role: typing.Optional[builtins.str] = None,
    schedule: typing.Optional[typing.Union[SqlQuerySchedule, typing.Dict[builtins.str, typing.Any]]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    updated_at: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0347eb58b4f36ddaf88cb73b2e45fee12f3c767a2fabc79a99151c050bb2c968(
    *,
    name: builtins.str,
    date: typing.Optional[typing.Union[SqlQueryParameterDate, typing.Dict[builtins.str, typing.Any]]] = None,
    date_range: typing.Optional[typing.Union[SqlQueryParameterDateRange, typing.Dict[builtins.str, typing.Any]]] = None,
    datetime: typing.Optional[typing.Union[SqlQueryParameterDatetime, typing.Dict[builtins.str, typing.Any]]] = None,
    datetime_range: typing.Optional[typing.Union[SqlQueryParameterDatetimeRange, typing.Dict[builtins.str, typing.Any]]] = None,
    datetimesec: typing.Optional[typing.Union[SqlQueryParameterDatetimesec, typing.Dict[builtins.str, typing.Any]]] = None,
    datetimesec_range: typing.Optional[typing.Union[SqlQueryParameterDatetimesecRange, typing.Dict[builtins.str, typing.Any]]] = None,
    enum: typing.Optional[typing.Union[SqlQueryParameterEnum, typing.Dict[builtins.str, typing.Any]]] = None,
    number: typing.Optional[typing.Union[SqlQueryParameterNumber, typing.Dict[builtins.str, typing.Any]]] = None,
    query: typing.Optional[typing.Union[SqlQueryParameterQuery, typing.Dict[builtins.str, typing.Any]]] = None,
    text: typing.Optional[typing.Union[SqlQueryParameterText, typing.Dict[builtins.str, typing.Any]]] = None,
    title: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf146c0521f6254bda9c6e968492f515fe6d99984e63d6cb1dc6c8f3afdf847e(
    *,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e77f05f7e83b878cb0984d9d20a5561b04d040d88072e5fc1d772866496ec56(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0baf03565e745355e3f3a3871b59ffa1ed3c54bd1fab034618935cbffdd8ea8a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e6e58fabdcf81fc880cba49d3519eddae369788e7a6e2a960bfdde2034936f6(
    value: typing.Optional[SqlQueryParameterDate],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e22f85eaf6f5a586dbad434431028633d1fd6153460a62bf1c6f8160bffcbd00(
    *,
    range: typing.Optional[typing.Union[SqlQueryParameterDateRangeRange, typing.Dict[builtins.str, typing.Any]]] = None,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__444ec5e0e9e05ba51f98000245d246e6e13465ab0e21d795f7dd6b6481a22aa9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eea95a1a7a6072c29099708bfaba6284408483d8b4ce9df8ef57a2624c5c814a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33708275fae3e14d6351d6613dd060052f1dda11b819f21447df810f2fc06d22(
    value: typing.Optional[SqlQueryParameterDateRange],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8eba84bb02fd70ce89222e5576fce94541cd8ac7022ec2652ec828d939763293(
    *,
    end: builtins.str,
    start: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9178ea3b6d50c679ce6c505844b40229df8c90bfd34b527fda1f585bdae5a92f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8896b1f03759ce27f0a36284dd1aaced423d260efc35f981911b74725fd7871c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebf21e054fed09e3108d29f334bb0874aaa3ac37cb45f1b9d7e2f7a1ca77d168(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4719a117e56efc00055e0353051a3427db22b18d8c53820bcd35b2b56d38ac8(
    value: typing.Optional[SqlQueryParameterDateRangeRange],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__026a4754efa6d7c0bcca18a4215f8202964071f651ca33312fb4143a2f6301d1(
    *,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a1b7abeb75e9fab6678284ddb2dd19026dd7bfbed3373d193f69b7166552bda(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3469a227037e33c8408125cce17dc394d7b2291e9291b755c0d50e876c4a135d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e600ddcfd19771e9ad434d0e454528c3623e22b9afb4ef34cc5eccdc5bed9c26(
    value: typing.Optional[SqlQueryParameterDatetime],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d48e61c95ad0f50d69f39712a514b95d6751735ac098e4dbb0eaa777d9e31ca(
    *,
    range: typing.Optional[typing.Union[SqlQueryParameterDatetimeRangeRange, typing.Dict[builtins.str, typing.Any]]] = None,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__852150fd54e372e93c9495c0e9e42c00a6b9f7caf2e64d40a91269ca97d42aad(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28f3d16de9193a48b738ea44b2bb0a148ae9e732a64d7db6dbc025e6a06e4560(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__908e522295073a7919fc72f9bd086ee1a207ad7f3878f3144bfe4c5d5e79cd47(
    value: typing.Optional[SqlQueryParameterDatetimeRange],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5244fd1ccda7611eea1bd8801b96151c1f41757acbc14703385313e0a8820715(
    *,
    end: builtins.str,
    start: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4eb5b6a4b0b3c2d6ffd44df370b8d3d9706e84ea6863a9bff91545e9007d789(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fd415bf08ff08863a94431619379916fcfdd2cd9b514df0192d35d9a19605f4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccff14d67440c4114936eccbd19be3d8a5f501a61cf54d47d33e79828b664afe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a7b7c5051f6118b94c0f066c1832049fa2b5c2631a1743d8b897ac97af80764(
    value: typing.Optional[SqlQueryParameterDatetimeRangeRange],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2be8018a3f054e991eb612b9098a16106380fa5750ad9b3ecbe9f10746903b3f(
    *,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3fe084d6a9ffba8957c7271effd038d90745be857d507bb33fce3941570ccf0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad0267b6fa861da429258bbc1fdfff4ad412d231c9758bce3d7ae1f05cdf160c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca79157ff45803bb0db91f193f7b0b697aec693e930f87629bc043e05c5426b1(
    value: typing.Optional[SqlQueryParameterDatetimesec],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fbb4fdb9ec4403b5582a8d27b2164222f07f3897b0b4d3986df7a1d13bd8c95(
    *,
    range: typing.Optional[typing.Union[SqlQueryParameterDatetimesecRangeRange, typing.Dict[builtins.str, typing.Any]]] = None,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7ac632d5d0b057ff23179c522f343e148d102a6c054c589e4318713a2848979(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b1c5926db5d2a5a720024d1d9f62259533344865f29ec2e1e21dcbc31d0ea81(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75994c3de13f97afdd3a5241b8cbb67227bdb28dff5befe17ce4079a8f6c92ed(
    value: typing.Optional[SqlQueryParameterDatetimesecRange],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ae87a0b9d8aed199eff7056984574daa166b7810bb08b12761c09e9854c8c63(
    *,
    end: builtins.str,
    start: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09f87226bf3ea6cb2dd2e5cf9c83896da0efb0705637c96b33217cb9d41aa94d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dac2a8053eb879f18ede5d42f33d01ebed9493813113f39aaf07d5675ebc89a7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6859c0a7e820b0ada3395ae50a17fda92a1074fc5362f6c6053ebade3a990ce8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec13f69815ef1bb2500dcdaff56791dc410dc3454e7ab0ae6fa331ee8a825014(
    value: typing.Optional[SqlQueryParameterDatetimesecRangeRange],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27f4b45f14d5762ae6661fd865d998aa0923ae369e23e89b96eb3bc000665037(
    *,
    options: typing.Sequence[builtins.str],
    multiple: typing.Optional[typing.Union[SqlQueryParameterEnumMultiple, typing.Dict[builtins.str, typing.Any]]] = None,
    value: typing.Optional[builtins.str] = None,
    values: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81e1895124837d67e9f036b3f2458dbd0a96b584a57989cd0b407a947d7fad34(
    *,
    separator: builtins.str,
    prefix: typing.Optional[builtins.str] = None,
    suffix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c1a4afe02fbb9de03b4dccf350792319b4a3ee23368ea63199494a41e948971(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b88b0f13a230cc2a5f12b108b7465fc8d064b9f9b6588d47df2415c4a57aef92(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f80358e8d06acec0e2c3e44a52debff52c5bc1153531783983688d6fda02da2f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81e843c15e47a6032b8a68e637de6be8fdd601a5faf3bb3966fe303e397e1874(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a6d1fbf61f008caa25fa07e96db273d25637435bbf71e4d59982fdb820df2a3(
    value: typing.Optional[SqlQueryParameterEnumMultiple],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f00e14c20c0e88831582caad8644472a93f69137e447258e7ec0dff0e6efd89(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57e563bf810fb6fd6d3b0ed9a3d66de97bf9a1dfa1f33e1681f3b88bf64be79b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b9cd0c26fe90f609e4d9955ed3cd3cbb69880e0956340201680a0dfc24c490c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__827ea4c64db089a768cb797d9c5e8b2dffa11a4f2e8f28c68659e98186b966f4(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35f172f346caa41a942775a61e00c93f4b85dbc5c32ece65b89790462b2ad916(
    value: typing.Optional[SqlQueryParameterEnum],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__338e4e803938f0687ee90a2b311455c23bdb61fbde749e7e0a5b38ec9cc739c7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5850df8fa525b259541b38a52b53e78003e6e497e5b2c4454e5ff816d185e8b(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7f0fddff3539cb31d78654935ea423b2578d4d157453f678608bc1ca0c79a07(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5750b1a79f712e0bcc5d76d42423b72350d4bfb0347840ee74e150a7ed52f8f9(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04f05e31e58dd8065372faa1625729e788bf7058f96e4cac0e8d3f68c3b71379(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__164b0948943f22bff3a7b28b6dd74a90f5a390b5d42a99551161a42ec4f6f59a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[SqlQueryParameter]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95f9fb77d8f72fbfbd338ca93eccd980d77ca89155b20cadc629363156413342(
    *,
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d758c27f894e92bdae2e2e24a5be347b32651dc16ab51c0bdd3123e5102147ab(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78223e165799e817973ada1d13ce908d4360c59014446391fcf559a2114c7a84(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58290e4f5e931d75646a0cc3053de79cad3ae4f6b80aacab18568fe7d47a086e(
    value: typing.Optional[SqlQueryParameterNumber],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__293548e368b2b9a5e7624309e573b93126b637ebf9850cad8d0e6a63930ce54b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62092ae9591109c5c45ac157f07be82b2838bff3589719bb02680732f0b5ce97(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dac72c08f42d37e373120f8a2faffc7a052fb4f8009812ebf490fa9e2dd4e092(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6554320435ca9aa14cbe306670b69867bb5cd5ed0c09e52a3cb88016f2aacb04(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SqlQueryParameter]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8e2b5f947ed9fc6a447b08a812d48ae5c9156e9e0eddac29b2fcef36777c38e(
    *,
    query_id: builtins.str,
    multiple: typing.Optional[typing.Union[SqlQueryParameterQueryMultiple, typing.Dict[builtins.str, typing.Any]]] = None,
    value: typing.Optional[builtins.str] = None,
    values: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6043a233f169b277af0bd5385752a715f5ea51d40f44967d3a661706b4f42758(
    *,
    separator: builtins.str,
    prefix: typing.Optional[builtins.str] = None,
    suffix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b71243a774c0c375691078935c47aad26077374b096cd04aa578616b75d91d4c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__310a8478c150458de9b7b336e92dd2609c8c42c64fa31fed5db8dcb3485a716e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4152f0af7d9f8bd00858561ed884c47477d8ef983b8cc338cb0e42621326fc10(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__947d3bdffc88663783283741b83acd3bc834f3a78ea1fb21b98b137ebebdd804(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e18ae8b38561bc8e17f83ccce02faffd3493bdb0c9f389556220025228d254ca(
    value: typing.Optional[SqlQueryParameterQueryMultiple],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a2961ebc20eeef593dd1f7cb2c95ad89b05de0f804b4e55b2d1231029731c2e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96f15e7a41bc4867025cda18536efde79879d17ab6a3bf35800a9f14135dba2c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cb78864c89a84c1017beb4754c84a98db8f9d7cd6b9bee60be6b5a014b82bb1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10ee5b4c051d15ea4aaf710117d24717137d26024e2ca24c68f706b2242c36ed(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db9290a4b0f41ff306ceaf8a584ca887bef1bbe7aae4d6d07e63c82fd5e19a7c(
    value: typing.Optional[SqlQueryParameterQuery],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c69a585e6156e2d172caba6f0a1ec2532d58e14965eacc8a488588e82ef5e53c(
    *,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89e3d3ac9cb100cadda8919f2319d18ee27719299b78a4d34ed73d23939b9f63(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d69e6198da0286b2e0dd0684f9ab7c8ab877c1d4c6e4c3a2d31c6e5a46abea45(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e006cae5ed549ed666a4e83159bb94918687db05960e3fb1ce97e816e240f756(
    value: typing.Optional[SqlQueryParameterText],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__196cbe3b5841d0707b7b58d9a8b59a53645fd0d6aa82376c59f580f2d997e8f6(
    *,
    continuous: typing.Optional[typing.Union[SqlQueryScheduleContinuous, typing.Dict[builtins.str, typing.Any]]] = None,
    daily: typing.Optional[typing.Union[SqlQueryScheduleDaily, typing.Dict[builtins.str, typing.Any]]] = None,
    weekly: typing.Optional[typing.Union[SqlQueryScheduleWeekly, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9d05fd1ed96d3d1a095d9e60fc4074542262251d1c8fe152159abe86cffb0b1(
    *,
    interval_seconds: jsii.Number,
    until_date: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9a5030edbafed43d18cbfb9e5d429c794089332802a3f34c4b312c89b93259f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4386c21450a59e16ade5388c748e97138d9e66d770ec3875f1c1dd17f19a7247(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2f7c2b42caf175be078a0acccc369a4c8fb5c2aaa89440bdde6ad8bee055203(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__213f69924ca3a06944562a46b2888bbd66b36489032572aae576096f9aa1952d(
    value: typing.Optional[SqlQueryScheduleContinuous],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01c1068332cb1e8e24d320e347dd3765a35703e32608c75f40f4e77101f53eb1(
    *,
    interval_days: jsii.Number,
    time_of_day: builtins.str,
    until_date: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0972a399436449e71732130daa5a3769c52868b9fb9a86a1ad0d352731f0eda1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19b89ae7fb34a25d2ca39402a9f98a733cbbd3c722c36dcbd1f7367cbd37da8b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9743d833944299586b6da489a819b2fafb81c0389d69b614dfa7056b352ba40(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d753f65785537aee819176a7bd4f00fe95c755c3a726444523776b4bd9bcb3c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d096c325f45db1ff0b644dd468cf9f8f564102f2d4608127998f0bf1b1c3560(
    value: typing.Optional[SqlQueryScheduleDaily],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea1631a1f985c9822ad50a38f47ef62800871f771a6f8d7c2692a6c6975e956d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8214772b14edbc9e6a761a9ad757072370c69dd62de6def404f4e4ab5086c7db(
    value: typing.Optional[SqlQuerySchedule],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf65635a3685101330be6e83bd0567c2c6b427255dcaef0fcb94ffdf93cbfa1b(
    *,
    day_of_week: builtins.str,
    interval_weeks: jsii.Number,
    time_of_day: builtins.str,
    until_date: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a660d3530e12f067581024cbd38f401d9c23a020718398f1b530a4642e1d3984(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cf589f5b3d87290941df9d84af33f60dc9d4929fa4138fc763157f351f806f5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e42ff4c206de92fb3a3e70c3f424533ff43c3c63c630e114d0e793f41eb50a5(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__979823d27b505754f30b98cd5c34fed2d8cf0b5ac50e2a2ccdb2166a72c9293e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81df11da1792f86ca2acaf3f9642d65e5445e1998040146b83a361442d10eeca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c9d183d69bda62fe0dd8f0165e84aa3a591847eeb19ded8e55e31518bedc7e7(
    value: typing.Optional[SqlQueryScheduleWeekly],
) -> None:
    """Type checking stubs"""
    pass
