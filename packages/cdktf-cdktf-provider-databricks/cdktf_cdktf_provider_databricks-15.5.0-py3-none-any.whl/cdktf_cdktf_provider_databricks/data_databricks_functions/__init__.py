r'''
# `data_databricks_functions`

Refer to the Terraform Registry for docs: [`data_databricks_functions`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions).
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


class DataDatabricksFunctions(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksFunctions.DataDatabricksFunctions",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions databricks_functions}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        catalog_name: builtins.str,
        schema_name: builtins.str,
        functions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksFunctionsFunctions", typing.Dict[builtins.str, typing.Any]]]]] = None,
        include_browse: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions databricks_functions} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param catalog_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#catalog_name DataDatabricksFunctions#catalog_name}.
        :param schema_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#schema_name DataDatabricksFunctions#schema_name}.
        :param functions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#functions DataDatabricksFunctions#functions}.
        :param include_browse: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#include_browse DataDatabricksFunctions#include_browse}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d2e4df42b578602016352031cb9ffedb715044dfb99f86fd5d826bbc0bce894)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataDatabricksFunctionsConfig(
            catalog_name=catalog_name,
            schema_name=schema_name,
            functions=functions,
            include_browse=include_browse,
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
        '''Generates CDKTF code for importing a DataDatabricksFunctions resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDatabricksFunctions to import.
        :param import_from_id: The id of the existing DataDatabricksFunctions that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDatabricksFunctions to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64566aed2b3945590967ad8ebb6ff5620a819537f87f01e8f531518f50b60933)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putFunctions")
    def put_functions(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksFunctionsFunctions", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be8315555557cdf16893e0a68644cf3e5de92241561b195b5d5c46b3cdf872de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putFunctions", [value]))

    @jsii.member(jsii_name="resetFunctions")
    def reset_functions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFunctions", []))

    @jsii.member(jsii_name="resetIncludeBrowse")
    def reset_include_browse(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeBrowse", []))

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
    @jsii.member(jsii_name="functions")
    def functions(self) -> "DataDatabricksFunctionsFunctionsList":
        return typing.cast("DataDatabricksFunctionsFunctionsList", jsii.get(self, "functions"))

    @builtins.property
    @jsii.member(jsii_name="catalogNameInput")
    def catalog_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "catalogNameInput"))

    @builtins.property
    @jsii.member(jsii_name="functionsInput")
    def functions_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksFunctionsFunctions"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksFunctionsFunctions"]]], jsii.get(self, "functionsInput"))

    @builtins.property
    @jsii.member(jsii_name="includeBrowseInput")
    def include_browse_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "includeBrowseInput"))

    @builtins.property
    @jsii.member(jsii_name="schemaNameInput")
    def schema_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schemaNameInput"))

    @builtins.property
    @jsii.member(jsii_name="catalogName")
    def catalog_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "catalogName"))

    @catalog_name.setter
    def catalog_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9614ee4dde73595e4567caf7193d3aea26fb147a3658a08129b69171bafc8bbe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "catalogName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="includeBrowse")
    def include_browse(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "includeBrowse"))

    @include_browse.setter
    def include_browse(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83990dc67f05707bb4d0713fdb7d969f849e7f8a8d8fe689d76a80a32e5a0e4e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "includeBrowse", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="schemaName")
    def schema_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schemaName"))

    @schema_name.setter
    def schema_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9c5e0581233d96bc77844fbaa4866586b2b4d9b61521174566d66d6fac3acc6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "schemaName", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksFunctions.DataDatabricksFunctionsConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "catalog_name": "catalogName",
        "schema_name": "schemaName",
        "functions": "functions",
        "include_browse": "includeBrowse",
    },
)
class DataDatabricksFunctionsConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        catalog_name: builtins.str,
        schema_name: builtins.str,
        functions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksFunctionsFunctions", typing.Dict[builtins.str, typing.Any]]]]] = None,
        include_browse: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param catalog_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#catalog_name DataDatabricksFunctions#catalog_name}.
        :param schema_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#schema_name DataDatabricksFunctions#schema_name}.
        :param functions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#functions DataDatabricksFunctions#functions}.
        :param include_browse: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#include_browse DataDatabricksFunctions#include_browse}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c090a204515d727101661784bfda9f542f3eb99b5c2739f73bb3605a6e57f59)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument catalog_name", value=catalog_name, expected_type=type_hints["catalog_name"])
            check_type(argname="argument schema_name", value=schema_name, expected_type=type_hints["schema_name"])
            check_type(argname="argument functions", value=functions, expected_type=type_hints["functions"])
            check_type(argname="argument include_browse", value=include_browse, expected_type=type_hints["include_browse"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "catalog_name": catalog_name,
            "schema_name": schema_name,
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
        if functions is not None:
            self._values["functions"] = functions
        if include_browse is not None:
            self._values["include_browse"] = include_browse

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
    def catalog_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#catalog_name DataDatabricksFunctions#catalog_name}.'''
        result = self._values.get("catalog_name")
        assert result is not None, "Required property 'catalog_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def schema_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#schema_name DataDatabricksFunctions#schema_name}.'''
        result = self._values.get("schema_name")
        assert result is not None, "Required property 'schema_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def functions(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksFunctionsFunctions"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#functions DataDatabricksFunctions#functions}.'''
        result = self._values.get("functions")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksFunctionsFunctions"]]], result)

    @builtins.property
    def include_browse(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#include_browse DataDatabricksFunctions#include_browse}.'''
        result = self._values.get("include_browse")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksFunctionsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksFunctions.DataDatabricksFunctionsFunctions",
    jsii_struct_bases=[],
    name_mapping={
        "browse_only": "browseOnly",
        "catalog_name": "catalogName",
        "comment": "comment",
        "created_at": "createdAt",
        "created_by": "createdBy",
        "data_type": "dataType",
        "external_language": "externalLanguage",
        "external_name": "externalName",
        "full_data_type": "fullDataType",
        "full_name": "fullName",
        "function_id": "functionId",
        "input_params": "inputParams",
        "is_deterministic": "isDeterministic",
        "is_null_call": "isNullCall",
        "metastore_id": "metastoreId",
        "name": "name",
        "owner": "owner",
        "parameter_style": "parameterStyle",
        "properties": "properties",
        "return_params": "returnParams",
        "routine_body": "routineBody",
        "routine_definition": "routineDefinition",
        "routine_dependencies": "routineDependencies",
        "schema_name": "schemaName",
        "security_type": "securityType",
        "specific_name": "specificName",
        "sql_data_access": "sqlDataAccess",
        "sql_path": "sqlPath",
        "updated_at": "updatedAt",
        "updated_by": "updatedBy",
    },
)
class DataDatabricksFunctionsFunctions:
    def __init__(
        self,
        *,
        browse_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        catalog_name: typing.Optional[builtins.str] = None,
        comment: typing.Optional[builtins.str] = None,
        created_at: typing.Optional[jsii.Number] = None,
        created_by: typing.Optional[builtins.str] = None,
        data_type: typing.Optional[builtins.str] = None,
        external_language: typing.Optional[builtins.str] = None,
        external_name: typing.Optional[builtins.str] = None,
        full_data_type: typing.Optional[builtins.str] = None,
        full_name: typing.Optional[builtins.str] = None,
        function_id: typing.Optional[builtins.str] = None,
        input_params: typing.Optional[typing.Union["DataDatabricksFunctionsFunctionsInputParams", typing.Dict[builtins.str, typing.Any]]] = None,
        is_deterministic: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        is_null_call: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        metastore_id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
        parameter_style: typing.Optional[builtins.str] = None,
        properties: typing.Optional[builtins.str] = None,
        return_params: typing.Optional[typing.Union["DataDatabricksFunctionsFunctionsReturnParams", typing.Dict[builtins.str, typing.Any]]] = None,
        routine_body: typing.Optional[builtins.str] = None,
        routine_definition: typing.Optional[builtins.str] = None,
        routine_dependencies: typing.Optional[typing.Union["DataDatabricksFunctionsFunctionsRoutineDependencies", typing.Dict[builtins.str, typing.Any]]] = None,
        schema_name: typing.Optional[builtins.str] = None,
        security_type: typing.Optional[builtins.str] = None,
        specific_name: typing.Optional[builtins.str] = None,
        sql_data_access: typing.Optional[builtins.str] = None,
        sql_path: typing.Optional[builtins.str] = None,
        updated_at: typing.Optional[jsii.Number] = None,
        updated_by: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param browse_only: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#browse_only DataDatabricksFunctions#browse_only}.
        :param catalog_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#catalog_name DataDatabricksFunctions#catalog_name}.
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#comment DataDatabricksFunctions#comment}.
        :param created_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#created_at DataDatabricksFunctions#created_at}.
        :param created_by: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#created_by DataDatabricksFunctions#created_by}.
        :param data_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#data_type DataDatabricksFunctions#data_type}.
        :param external_language: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#external_language DataDatabricksFunctions#external_language}.
        :param external_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#external_name DataDatabricksFunctions#external_name}.
        :param full_data_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#full_data_type DataDatabricksFunctions#full_data_type}.
        :param full_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#full_name DataDatabricksFunctions#full_name}.
        :param function_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#function_id DataDatabricksFunctions#function_id}.
        :param input_params: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#input_params DataDatabricksFunctions#input_params}.
        :param is_deterministic: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#is_deterministic DataDatabricksFunctions#is_deterministic}.
        :param is_null_call: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#is_null_call DataDatabricksFunctions#is_null_call}.
        :param metastore_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#metastore_id DataDatabricksFunctions#metastore_id}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#name DataDatabricksFunctions#name}.
        :param owner: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#owner DataDatabricksFunctions#owner}.
        :param parameter_style: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#parameter_style DataDatabricksFunctions#parameter_style}.
        :param properties: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#properties DataDatabricksFunctions#properties}.
        :param return_params: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#return_params DataDatabricksFunctions#return_params}.
        :param routine_body: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#routine_body DataDatabricksFunctions#routine_body}.
        :param routine_definition: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#routine_definition DataDatabricksFunctions#routine_definition}.
        :param routine_dependencies: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#routine_dependencies DataDatabricksFunctions#routine_dependencies}.
        :param schema_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#schema_name DataDatabricksFunctions#schema_name}.
        :param security_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#security_type DataDatabricksFunctions#security_type}.
        :param specific_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#specific_name DataDatabricksFunctions#specific_name}.
        :param sql_data_access: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#sql_data_access DataDatabricksFunctions#sql_data_access}.
        :param sql_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#sql_path DataDatabricksFunctions#sql_path}.
        :param updated_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#updated_at DataDatabricksFunctions#updated_at}.
        :param updated_by: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#updated_by DataDatabricksFunctions#updated_by}.
        '''
        if isinstance(input_params, dict):
            input_params = DataDatabricksFunctionsFunctionsInputParams(**input_params)
        if isinstance(return_params, dict):
            return_params = DataDatabricksFunctionsFunctionsReturnParams(**return_params)
        if isinstance(routine_dependencies, dict):
            routine_dependencies = DataDatabricksFunctionsFunctionsRoutineDependencies(**routine_dependencies)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e607b59531791ae2f0325effe6c2759c9d847b9e7f1e03f0fff2a4141c07b14)
            check_type(argname="argument browse_only", value=browse_only, expected_type=type_hints["browse_only"])
            check_type(argname="argument catalog_name", value=catalog_name, expected_type=type_hints["catalog_name"])
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument created_at", value=created_at, expected_type=type_hints["created_at"])
            check_type(argname="argument created_by", value=created_by, expected_type=type_hints["created_by"])
            check_type(argname="argument data_type", value=data_type, expected_type=type_hints["data_type"])
            check_type(argname="argument external_language", value=external_language, expected_type=type_hints["external_language"])
            check_type(argname="argument external_name", value=external_name, expected_type=type_hints["external_name"])
            check_type(argname="argument full_data_type", value=full_data_type, expected_type=type_hints["full_data_type"])
            check_type(argname="argument full_name", value=full_name, expected_type=type_hints["full_name"])
            check_type(argname="argument function_id", value=function_id, expected_type=type_hints["function_id"])
            check_type(argname="argument input_params", value=input_params, expected_type=type_hints["input_params"])
            check_type(argname="argument is_deterministic", value=is_deterministic, expected_type=type_hints["is_deterministic"])
            check_type(argname="argument is_null_call", value=is_null_call, expected_type=type_hints["is_null_call"])
            check_type(argname="argument metastore_id", value=metastore_id, expected_type=type_hints["metastore_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument owner", value=owner, expected_type=type_hints["owner"])
            check_type(argname="argument parameter_style", value=parameter_style, expected_type=type_hints["parameter_style"])
            check_type(argname="argument properties", value=properties, expected_type=type_hints["properties"])
            check_type(argname="argument return_params", value=return_params, expected_type=type_hints["return_params"])
            check_type(argname="argument routine_body", value=routine_body, expected_type=type_hints["routine_body"])
            check_type(argname="argument routine_definition", value=routine_definition, expected_type=type_hints["routine_definition"])
            check_type(argname="argument routine_dependencies", value=routine_dependencies, expected_type=type_hints["routine_dependencies"])
            check_type(argname="argument schema_name", value=schema_name, expected_type=type_hints["schema_name"])
            check_type(argname="argument security_type", value=security_type, expected_type=type_hints["security_type"])
            check_type(argname="argument specific_name", value=specific_name, expected_type=type_hints["specific_name"])
            check_type(argname="argument sql_data_access", value=sql_data_access, expected_type=type_hints["sql_data_access"])
            check_type(argname="argument sql_path", value=sql_path, expected_type=type_hints["sql_path"])
            check_type(argname="argument updated_at", value=updated_at, expected_type=type_hints["updated_at"])
            check_type(argname="argument updated_by", value=updated_by, expected_type=type_hints["updated_by"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if browse_only is not None:
            self._values["browse_only"] = browse_only
        if catalog_name is not None:
            self._values["catalog_name"] = catalog_name
        if comment is not None:
            self._values["comment"] = comment
        if created_at is not None:
            self._values["created_at"] = created_at
        if created_by is not None:
            self._values["created_by"] = created_by
        if data_type is not None:
            self._values["data_type"] = data_type
        if external_language is not None:
            self._values["external_language"] = external_language
        if external_name is not None:
            self._values["external_name"] = external_name
        if full_data_type is not None:
            self._values["full_data_type"] = full_data_type
        if full_name is not None:
            self._values["full_name"] = full_name
        if function_id is not None:
            self._values["function_id"] = function_id
        if input_params is not None:
            self._values["input_params"] = input_params
        if is_deterministic is not None:
            self._values["is_deterministic"] = is_deterministic
        if is_null_call is not None:
            self._values["is_null_call"] = is_null_call
        if metastore_id is not None:
            self._values["metastore_id"] = metastore_id
        if name is not None:
            self._values["name"] = name
        if owner is not None:
            self._values["owner"] = owner
        if parameter_style is not None:
            self._values["parameter_style"] = parameter_style
        if properties is not None:
            self._values["properties"] = properties
        if return_params is not None:
            self._values["return_params"] = return_params
        if routine_body is not None:
            self._values["routine_body"] = routine_body
        if routine_definition is not None:
            self._values["routine_definition"] = routine_definition
        if routine_dependencies is not None:
            self._values["routine_dependencies"] = routine_dependencies
        if schema_name is not None:
            self._values["schema_name"] = schema_name
        if security_type is not None:
            self._values["security_type"] = security_type
        if specific_name is not None:
            self._values["specific_name"] = specific_name
        if sql_data_access is not None:
            self._values["sql_data_access"] = sql_data_access
        if sql_path is not None:
            self._values["sql_path"] = sql_path
        if updated_at is not None:
            self._values["updated_at"] = updated_at
        if updated_by is not None:
            self._values["updated_by"] = updated_by

    @builtins.property
    def browse_only(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#browse_only DataDatabricksFunctions#browse_only}.'''
        result = self._values.get("browse_only")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def catalog_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#catalog_name DataDatabricksFunctions#catalog_name}.'''
        result = self._values.get("catalog_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#comment DataDatabricksFunctions#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def created_at(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#created_at DataDatabricksFunctions#created_at}.'''
        result = self._values.get("created_at")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def created_by(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#created_by DataDatabricksFunctions#created_by}.'''
        result = self._values.get("created_by")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def data_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#data_type DataDatabricksFunctions#data_type}.'''
        result = self._values.get("data_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def external_language(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#external_language DataDatabricksFunctions#external_language}.'''
        result = self._values.get("external_language")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def external_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#external_name DataDatabricksFunctions#external_name}.'''
        result = self._values.get("external_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def full_data_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#full_data_type DataDatabricksFunctions#full_data_type}.'''
        result = self._values.get("full_data_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def full_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#full_name DataDatabricksFunctions#full_name}.'''
        result = self._values.get("full_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def function_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#function_id DataDatabricksFunctions#function_id}.'''
        result = self._values.get("function_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def input_params(
        self,
    ) -> typing.Optional["DataDatabricksFunctionsFunctionsInputParams"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#input_params DataDatabricksFunctions#input_params}.'''
        result = self._values.get("input_params")
        return typing.cast(typing.Optional["DataDatabricksFunctionsFunctionsInputParams"], result)

    @builtins.property
    def is_deterministic(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#is_deterministic DataDatabricksFunctions#is_deterministic}.'''
        result = self._values.get("is_deterministic")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def is_null_call(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#is_null_call DataDatabricksFunctions#is_null_call}.'''
        result = self._values.get("is_null_call")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def metastore_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#metastore_id DataDatabricksFunctions#metastore_id}.'''
        result = self._values.get("metastore_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#name DataDatabricksFunctions#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def owner(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#owner DataDatabricksFunctions#owner}.'''
        result = self._values.get("owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameter_style(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#parameter_style DataDatabricksFunctions#parameter_style}.'''
        result = self._values.get("parameter_style")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def properties(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#properties DataDatabricksFunctions#properties}.'''
        result = self._values.get("properties")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def return_params(
        self,
    ) -> typing.Optional["DataDatabricksFunctionsFunctionsReturnParams"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#return_params DataDatabricksFunctions#return_params}.'''
        result = self._values.get("return_params")
        return typing.cast(typing.Optional["DataDatabricksFunctionsFunctionsReturnParams"], result)

    @builtins.property
    def routine_body(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#routine_body DataDatabricksFunctions#routine_body}.'''
        result = self._values.get("routine_body")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def routine_definition(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#routine_definition DataDatabricksFunctions#routine_definition}.'''
        result = self._values.get("routine_definition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def routine_dependencies(
        self,
    ) -> typing.Optional["DataDatabricksFunctionsFunctionsRoutineDependencies"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#routine_dependencies DataDatabricksFunctions#routine_dependencies}.'''
        result = self._values.get("routine_dependencies")
        return typing.cast(typing.Optional["DataDatabricksFunctionsFunctionsRoutineDependencies"], result)

    @builtins.property
    def schema_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#schema_name DataDatabricksFunctions#schema_name}.'''
        result = self._values.get("schema_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#security_type DataDatabricksFunctions#security_type}.'''
        result = self._values.get("security_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def specific_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#specific_name DataDatabricksFunctions#specific_name}.'''
        result = self._values.get("specific_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sql_data_access(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#sql_data_access DataDatabricksFunctions#sql_data_access}.'''
        result = self._values.get("sql_data_access")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sql_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#sql_path DataDatabricksFunctions#sql_path}.'''
        result = self._values.get("sql_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def updated_at(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#updated_at DataDatabricksFunctions#updated_at}.'''
        result = self._values.get("updated_at")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def updated_by(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#updated_by DataDatabricksFunctions#updated_by}.'''
        result = self._values.get("updated_by")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksFunctionsFunctions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksFunctions.DataDatabricksFunctionsFunctionsInputParams",
    jsii_struct_bases=[],
    name_mapping={"parameters": "parameters"},
)
class DataDatabricksFunctionsFunctionsInputParams:
    def __init__(
        self,
        *,
        parameters: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksFunctionsFunctionsInputParamsParameters", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param parameters: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#parameters DataDatabricksFunctions#parameters}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be9c13e16d7906d1fea60aa1741103114223405c391769eede8757bf0065f291)
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if parameters is not None:
            self._values["parameters"] = parameters

    @builtins.property
    def parameters(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksFunctionsFunctionsInputParamsParameters"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#parameters DataDatabricksFunctions#parameters}.'''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksFunctionsFunctionsInputParamsParameters"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksFunctionsFunctionsInputParams(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksFunctionsFunctionsInputParamsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksFunctions.DataDatabricksFunctionsFunctionsInputParamsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7df60c33a02aae813b90db4530ff6e33220e5e9126c0b62b7e28a08211320b7c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putParameters")
    def put_parameters(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksFunctionsFunctionsInputParamsParameters", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4841e2b31e87bd42a460cf5b74f8a453cd88aedebc50f72597f864a7836ba54f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putParameters", [value]))

    @jsii.member(jsii_name="resetParameters")
    def reset_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameters", []))

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> "DataDatabricksFunctionsFunctionsInputParamsParametersList":
        return typing.cast("DataDatabricksFunctionsFunctionsInputParamsParametersList", jsii.get(self, "parameters"))

    @builtins.property
    @jsii.member(jsii_name="parametersInput")
    def parameters_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksFunctionsFunctionsInputParamsParameters"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksFunctionsFunctionsInputParamsParameters"]]], jsii.get(self, "parametersInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsInputParams]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsInputParams]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsInputParams]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a4c0c4e0953022ba9b43db162e855120dbb2be759c64d41b170c4c4a365d6c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksFunctions.DataDatabricksFunctionsFunctionsInputParamsParameters",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "position": "position",
        "type_name": "typeName",
        "type_text": "typeText",
        "comment": "comment",
        "parameter_default": "parameterDefault",
        "parameter_mode": "parameterMode",
        "parameter_type": "parameterType",
        "type_interval_type": "typeIntervalType",
        "type_json": "typeJson",
        "type_precision": "typePrecision",
        "type_scale": "typeScale",
    },
)
class DataDatabricksFunctionsFunctionsInputParamsParameters:
    def __init__(
        self,
        *,
        name: builtins.str,
        position: jsii.Number,
        type_name: builtins.str,
        type_text: builtins.str,
        comment: typing.Optional[builtins.str] = None,
        parameter_default: typing.Optional[builtins.str] = None,
        parameter_mode: typing.Optional[builtins.str] = None,
        parameter_type: typing.Optional[builtins.str] = None,
        type_interval_type: typing.Optional[builtins.str] = None,
        type_json: typing.Optional[builtins.str] = None,
        type_precision: typing.Optional[jsii.Number] = None,
        type_scale: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#name DataDatabricksFunctions#name}.
        :param position: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#position DataDatabricksFunctions#position}.
        :param type_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#type_name DataDatabricksFunctions#type_name}.
        :param type_text: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#type_text DataDatabricksFunctions#type_text}.
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#comment DataDatabricksFunctions#comment}.
        :param parameter_default: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#parameter_default DataDatabricksFunctions#parameter_default}.
        :param parameter_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#parameter_mode DataDatabricksFunctions#parameter_mode}.
        :param parameter_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#parameter_type DataDatabricksFunctions#parameter_type}.
        :param type_interval_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#type_interval_type DataDatabricksFunctions#type_interval_type}.
        :param type_json: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#type_json DataDatabricksFunctions#type_json}.
        :param type_precision: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#type_precision DataDatabricksFunctions#type_precision}.
        :param type_scale: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#type_scale DataDatabricksFunctions#type_scale}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ed24a14cb2a970ce00d3176490657682087a073cc448f0ec26a41799a5f2884)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument position", value=position, expected_type=type_hints["position"])
            check_type(argname="argument type_name", value=type_name, expected_type=type_hints["type_name"])
            check_type(argname="argument type_text", value=type_text, expected_type=type_hints["type_text"])
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument parameter_default", value=parameter_default, expected_type=type_hints["parameter_default"])
            check_type(argname="argument parameter_mode", value=parameter_mode, expected_type=type_hints["parameter_mode"])
            check_type(argname="argument parameter_type", value=parameter_type, expected_type=type_hints["parameter_type"])
            check_type(argname="argument type_interval_type", value=type_interval_type, expected_type=type_hints["type_interval_type"])
            check_type(argname="argument type_json", value=type_json, expected_type=type_hints["type_json"])
            check_type(argname="argument type_precision", value=type_precision, expected_type=type_hints["type_precision"])
            check_type(argname="argument type_scale", value=type_scale, expected_type=type_hints["type_scale"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "position": position,
            "type_name": type_name,
            "type_text": type_text,
        }
        if comment is not None:
            self._values["comment"] = comment
        if parameter_default is not None:
            self._values["parameter_default"] = parameter_default
        if parameter_mode is not None:
            self._values["parameter_mode"] = parameter_mode
        if parameter_type is not None:
            self._values["parameter_type"] = parameter_type
        if type_interval_type is not None:
            self._values["type_interval_type"] = type_interval_type
        if type_json is not None:
            self._values["type_json"] = type_json
        if type_precision is not None:
            self._values["type_precision"] = type_precision
        if type_scale is not None:
            self._values["type_scale"] = type_scale

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#name DataDatabricksFunctions#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def position(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#position DataDatabricksFunctions#position}.'''
        result = self._values.get("position")
        assert result is not None, "Required property 'position' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def type_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#type_name DataDatabricksFunctions#type_name}.'''
        result = self._values.get("type_name")
        assert result is not None, "Required property 'type_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type_text(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#type_text DataDatabricksFunctions#type_text}.'''
        result = self._values.get("type_text")
        assert result is not None, "Required property 'type_text' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#comment DataDatabricksFunctions#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameter_default(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#parameter_default DataDatabricksFunctions#parameter_default}.'''
        result = self._values.get("parameter_default")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameter_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#parameter_mode DataDatabricksFunctions#parameter_mode}.'''
        result = self._values.get("parameter_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameter_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#parameter_type DataDatabricksFunctions#parameter_type}.'''
        result = self._values.get("parameter_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_interval_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#type_interval_type DataDatabricksFunctions#type_interval_type}.'''
        result = self._values.get("type_interval_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#type_json DataDatabricksFunctions#type_json}.'''
        result = self._values.get("type_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_precision(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#type_precision DataDatabricksFunctions#type_precision}.'''
        result = self._values.get("type_precision")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_scale(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#type_scale DataDatabricksFunctions#type_scale}.'''
        result = self._values.get("type_scale")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksFunctionsFunctionsInputParamsParameters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksFunctionsFunctionsInputParamsParametersList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksFunctions.DataDatabricksFunctionsFunctionsInputParamsParametersList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1ce05d5d787b4358e225264118db072ebc194ffdff37d68d73de966df45a0462)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksFunctionsFunctionsInputParamsParametersOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3dffb7875b1df7c34b70068a2a9c2eec8c9db22c534d23f4863fbf7d6caa4316)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksFunctionsFunctionsInputParamsParametersOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa955a29aed720e824ecbc4d97a5db41d09fc7e148138dabe0fab2afe61cd12e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e2949ba6df062be2e72045f9ba2e65ba500cbe01bbba14eb2d2e728c7d9a2c86)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b7d28db4a599367ea8c6cddde1d21b6a8a5ce130e3a77a760e6c3d2614a58eaf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksFunctionsFunctionsInputParamsParameters]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksFunctionsFunctionsInputParamsParameters]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksFunctionsFunctionsInputParamsParameters]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__542ac03a6d56e17de18216c8e8f869a7bc446d677f8b2415e13d52089d69106f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksFunctionsFunctionsInputParamsParametersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksFunctions.DataDatabricksFunctionsFunctionsInputParamsParametersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7362f2bafb4c71813b11080f9cacd55484de8079cc92a4cb7ccafbfd530ca0cd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="resetParameterDefault")
    def reset_parameter_default(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameterDefault", []))

    @jsii.member(jsii_name="resetParameterMode")
    def reset_parameter_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameterMode", []))

    @jsii.member(jsii_name="resetParameterType")
    def reset_parameter_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameterType", []))

    @jsii.member(jsii_name="resetTypeIntervalType")
    def reset_type_interval_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTypeIntervalType", []))

    @jsii.member(jsii_name="resetTypeJson")
    def reset_type_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTypeJson", []))

    @jsii.member(jsii_name="resetTypePrecision")
    def reset_type_precision(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTypePrecision", []))

    @jsii.member(jsii_name="resetTypeScale")
    def reset_type_scale(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTypeScale", []))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="parameterDefaultInput")
    def parameter_default_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parameterDefaultInput"))

    @builtins.property
    @jsii.member(jsii_name="parameterModeInput")
    def parameter_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parameterModeInput"))

    @builtins.property
    @jsii.member(jsii_name="parameterTypeInput")
    def parameter_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parameterTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="positionInput")
    def position_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "positionInput"))

    @builtins.property
    @jsii.member(jsii_name="typeIntervalTypeInput")
    def type_interval_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeIntervalTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="typeJsonInput")
    def type_json_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeJsonInput"))

    @builtins.property
    @jsii.member(jsii_name="typeNameInput")
    def type_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeNameInput"))

    @builtins.property
    @jsii.member(jsii_name="typePrecisionInput")
    def type_precision_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "typePrecisionInput"))

    @builtins.property
    @jsii.member(jsii_name="typeScaleInput")
    def type_scale_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "typeScaleInput"))

    @builtins.property
    @jsii.member(jsii_name="typeTextInput")
    def type_text_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeTextInput"))

    @builtins.property
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea5e50c834e8547320011a4dcf0b706be6d822a36cf67d6f45a77a2f5fa4888f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bd50e243697cfcf0aa0ced77cc60f25113e4316f554fb7624cbbd02502b1a65)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parameterDefault")
    def parameter_default(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parameterDefault"))

    @parameter_default.setter
    def parameter_default(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2da6199cc373c19de2b9d2a0fffb920a9c460c856d6ee1571add458ca46eab10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameterDefault", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parameterMode")
    def parameter_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parameterMode"))

    @parameter_mode.setter
    def parameter_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d99ffecbe49d64a40c458eca4e11c003bf7f21c077adfea58fa0af39fdfd363)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameterMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parameterType")
    def parameter_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parameterType"))

    @parameter_type.setter
    def parameter_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d0c9247eb490ca7ae259582a4451f8fb2f31c2723dcfe46d42fea812d597664)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameterType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="position")
    def position(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "position"))

    @position.setter
    def position(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c58cb3dda78a85a452f725b47be01190505afe57986cb0f869f9386da2047407)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "position", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeIntervalType")
    def type_interval_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeIntervalType"))

    @type_interval_type.setter
    def type_interval_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8df9e3738bad6f13e21cc4dabcb61841d7f883048578d67e7aebb551db12d8a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeIntervalType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeJson")
    def type_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeJson"))

    @type_json.setter
    def type_json(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e90f3dbc28e6aaace2e4f685e518971fad7b39ff2a704e79ab8c6e73c9afa41)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeJson", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeName")
    def type_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeName"))

    @type_name.setter
    def type_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5b8f38cc44fb29d904477f8f5dafdab8d1d02a202fe616101e7b68165236916)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typePrecision")
    def type_precision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "typePrecision"))

    @type_precision.setter
    def type_precision(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42e3d8880a2095c1012bb3ee4719eff6a23498cd6daec6bdca562d7b5cf04032)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typePrecision", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeScale")
    def type_scale(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "typeScale"))

    @type_scale.setter
    def type_scale(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37d2d9cf4f77e628df13cf9f1a6d4499bddfcf46b4831bb12dbb291cbdce79e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeScale", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeText")
    def type_text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeText"))

    @type_text.setter
    def type_text(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9e6c8f97598ff0c0e168ee5869f4e3423ea80d9da33237441b4e5ee3acade7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeText", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsInputParamsParameters]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsInputParamsParameters]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsInputParamsParameters]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ba76736b007d507b35954a61cbc932831f9797e6b24cbfa7279a54677eba2ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksFunctionsFunctionsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksFunctions.DataDatabricksFunctionsFunctionsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__18a3ac77f06b3c3af779aa168b97bb7315bb70aa69d469249a2cb48995a9418d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksFunctionsFunctionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76e24f8b19be3bddb75a79facfcc33c4fa7fd373dcf1e1426823d650f11bc3a0)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksFunctionsFunctionsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5869a1bd860dd86e48dba4efc7f898d59c2f21839acc6cba70224d0e66ea1bce)
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
            type_hints = typing.get_type_hints(_typecheckingstub__971a62130f3a98030f1575c12072ca5ffdbc94a0807bbf8d764cf1e0de07117c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2ed465a34457cea749d76f9448fd65ca9e1ddd6bade638a0f722ba4e719be90f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksFunctionsFunctions]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksFunctionsFunctions]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksFunctionsFunctions]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c561d074192b500b8767ddbb3d30e171704015e6e76b558954262b63437de106)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksFunctionsFunctionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksFunctions.DataDatabricksFunctionsFunctionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__11ee9a88f1fca1544fb5d2705087734b23abcb33713048ecd95219d01bd9fba2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putInputParams")
    def put_input_params(
        self,
        *,
        parameters: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksFunctionsFunctionsInputParamsParameters, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param parameters: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#parameters DataDatabricksFunctions#parameters}.
        '''
        value = DataDatabricksFunctionsFunctionsInputParams(parameters=parameters)

        return typing.cast(None, jsii.invoke(self, "putInputParams", [value]))

    @jsii.member(jsii_name="putReturnParams")
    def put_return_params(
        self,
        *,
        parameters: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksFunctionsFunctionsReturnParamsParameters", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param parameters: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#parameters DataDatabricksFunctions#parameters}.
        '''
        value = DataDatabricksFunctionsFunctionsReturnParams(parameters=parameters)

        return typing.cast(None, jsii.invoke(self, "putReturnParams", [value]))

    @jsii.member(jsii_name="putRoutineDependencies")
    def put_routine_dependencies(
        self,
        *,
        dependencies: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksFunctionsFunctionsRoutineDependenciesDependencies", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param dependencies: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#dependencies DataDatabricksFunctions#dependencies}.
        '''
        value = DataDatabricksFunctionsFunctionsRoutineDependencies(
            dependencies=dependencies
        )

        return typing.cast(None, jsii.invoke(self, "putRoutineDependencies", [value]))

    @jsii.member(jsii_name="resetBrowseOnly")
    def reset_browse_only(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBrowseOnly", []))

    @jsii.member(jsii_name="resetCatalogName")
    def reset_catalog_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCatalogName", []))

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="resetCreatedAt")
    def reset_created_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatedAt", []))

    @jsii.member(jsii_name="resetCreatedBy")
    def reset_created_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatedBy", []))

    @jsii.member(jsii_name="resetDataType")
    def reset_data_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataType", []))

    @jsii.member(jsii_name="resetExternalLanguage")
    def reset_external_language(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExternalLanguage", []))

    @jsii.member(jsii_name="resetExternalName")
    def reset_external_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExternalName", []))

    @jsii.member(jsii_name="resetFullDataType")
    def reset_full_data_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFullDataType", []))

    @jsii.member(jsii_name="resetFullName")
    def reset_full_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFullName", []))

    @jsii.member(jsii_name="resetFunctionId")
    def reset_function_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFunctionId", []))

    @jsii.member(jsii_name="resetInputParams")
    def reset_input_params(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInputParams", []))

    @jsii.member(jsii_name="resetIsDeterministic")
    def reset_is_deterministic(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsDeterministic", []))

    @jsii.member(jsii_name="resetIsNullCall")
    def reset_is_null_call(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsNullCall", []))

    @jsii.member(jsii_name="resetMetastoreId")
    def reset_metastore_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetastoreId", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetOwner")
    def reset_owner(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOwner", []))

    @jsii.member(jsii_name="resetParameterStyle")
    def reset_parameter_style(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameterStyle", []))

    @jsii.member(jsii_name="resetProperties")
    def reset_properties(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProperties", []))

    @jsii.member(jsii_name="resetReturnParams")
    def reset_return_params(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReturnParams", []))

    @jsii.member(jsii_name="resetRoutineBody")
    def reset_routine_body(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoutineBody", []))

    @jsii.member(jsii_name="resetRoutineDefinition")
    def reset_routine_definition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoutineDefinition", []))

    @jsii.member(jsii_name="resetRoutineDependencies")
    def reset_routine_dependencies(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoutineDependencies", []))

    @jsii.member(jsii_name="resetSchemaName")
    def reset_schema_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchemaName", []))

    @jsii.member(jsii_name="resetSecurityType")
    def reset_security_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityType", []))

    @jsii.member(jsii_name="resetSpecificName")
    def reset_specific_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpecificName", []))

    @jsii.member(jsii_name="resetSqlDataAccess")
    def reset_sql_data_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSqlDataAccess", []))

    @jsii.member(jsii_name="resetSqlPath")
    def reset_sql_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSqlPath", []))

    @jsii.member(jsii_name="resetUpdatedAt")
    def reset_updated_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdatedAt", []))

    @jsii.member(jsii_name="resetUpdatedBy")
    def reset_updated_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdatedBy", []))

    @builtins.property
    @jsii.member(jsii_name="inputParams")
    def input_params(
        self,
    ) -> DataDatabricksFunctionsFunctionsInputParamsOutputReference:
        return typing.cast(DataDatabricksFunctionsFunctionsInputParamsOutputReference, jsii.get(self, "inputParams"))

    @builtins.property
    @jsii.member(jsii_name="returnParams")
    def return_params(
        self,
    ) -> "DataDatabricksFunctionsFunctionsReturnParamsOutputReference":
        return typing.cast("DataDatabricksFunctionsFunctionsReturnParamsOutputReference", jsii.get(self, "returnParams"))

    @builtins.property
    @jsii.member(jsii_name="routineDependencies")
    def routine_dependencies(
        self,
    ) -> "DataDatabricksFunctionsFunctionsRoutineDependenciesOutputReference":
        return typing.cast("DataDatabricksFunctionsFunctionsRoutineDependenciesOutputReference", jsii.get(self, "routineDependencies"))

    @builtins.property
    @jsii.member(jsii_name="browseOnlyInput")
    def browse_only_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "browseOnlyInput"))

    @builtins.property
    @jsii.member(jsii_name="catalogNameInput")
    def catalog_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "catalogNameInput"))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="createdAtInput")
    def created_at_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "createdAtInput"))

    @builtins.property
    @jsii.member(jsii_name="createdByInput")
    def created_by_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdByInput"))

    @builtins.property
    @jsii.member(jsii_name="dataTypeInput")
    def data_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="externalLanguageInput")
    def external_language_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "externalLanguageInput"))

    @builtins.property
    @jsii.member(jsii_name="externalNameInput")
    def external_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "externalNameInput"))

    @builtins.property
    @jsii.member(jsii_name="fullDataTypeInput")
    def full_data_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fullDataTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="fullNameInput")
    def full_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fullNameInput"))

    @builtins.property
    @jsii.member(jsii_name="functionIdInput")
    def function_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionIdInput"))

    @builtins.property
    @jsii.member(jsii_name="inputParamsInput")
    def input_params_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsInputParams]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsInputParams]], jsii.get(self, "inputParamsInput"))

    @builtins.property
    @jsii.member(jsii_name="isDeterministicInput")
    def is_deterministic_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isDeterministicInput"))

    @builtins.property
    @jsii.member(jsii_name="isNullCallInput")
    def is_null_call_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isNullCallInput"))

    @builtins.property
    @jsii.member(jsii_name="metastoreIdInput")
    def metastore_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metastoreIdInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="ownerInput")
    def owner_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ownerInput"))

    @builtins.property
    @jsii.member(jsii_name="parameterStyleInput")
    def parameter_style_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parameterStyleInput"))

    @builtins.property
    @jsii.member(jsii_name="propertiesInput")
    def properties_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "propertiesInput"))

    @builtins.property
    @jsii.member(jsii_name="returnParamsInput")
    def return_params_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksFunctionsFunctionsReturnParams"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksFunctionsFunctionsReturnParams"]], jsii.get(self, "returnParamsInput"))

    @builtins.property
    @jsii.member(jsii_name="routineBodyInput")
    def routine_body_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "routineBodyInput"))

    @builtins.property
    @jsii.member(jsii_name="routineDefinitionInput")
    def routine_definition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "routineDefinitionInput"))

    @builtins.property
    @jsii.member(jsii_name="routineDependenciesInput")
    def routine_dependencies_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksFunctionsFunctionsRoutineDependencies"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksFunctionsFunctionsRoutineDependencies"]], jsii.get(self, "routineDependenciesInput"))

    @builtins.property
    @jsii.member(jsii_name="schemaNameInput")
    def schema_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schemaNameInput"))

    @builtins.property
    @jsii.member(jsii_name="securityTypeInput")
    def security_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "securityTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="specificNameInput")
    def specific_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "specificNameInput"))

    @builtins.property
    @jsii.member(jsii_name="sqlDataAccessInput")
    def sql_data_access_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sqlDataAccessInput"))

    @builtins.property
    @jsii.member(jsii_name="sqlPathInput")
    def sql_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sqlPathInput"))

    @builtins.property
    @jsii.member(jsii_name="updatedAtInput")
    def updated_at_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "updatedAtInput"))

    @builtins.property
    @jsii.member(jsii_name="updatedByInput")
    def updated_by_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updatedByInput"))

    @builtins.property
    @jsii.member(jsii_name="browseOnly")
    def browse_only(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "browseOnly"))

    @browse_only.setter
    def browse_only(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__896285b7eba52bf0607466c5eb3ac2544ac2da8a21b8dcb528aade55b484a4bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "browseOnly", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="catalogName")
    def catalog_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "catalogName"))

    @catalog_name.setter
    def catalog_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afe0ef01f349ca72e0f0266e421d53c46ace27ad5af6fd321f37880c9f90d02d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "catalogName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6b77eef9e7c50c514932a7ce45cf1797c33449a40bd280f385cb323483707ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "createdAt"))

    @created_at.setter
    def created_at(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__135eff0da066a8b53b963bf3654e5780a84a9bf4dccfb48bcd9af8590ea6966d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="createdBy")
    def created_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdBy"))

    @created_by.setter
    def created_by(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df9c388ead60fdbe80609bfbaee17f2ccdb2ff561efc71813cc88a894a91e66c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdBy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dataType")
    def data_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataType"))

    @data_type.setter
    def data_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19d9b1426948c39c1aa28868da18c9c617070a50f79912a267ad02c0e967bbb9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="externalLanguage")
    def external_language(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "externalLanguage"))

    @external_language.setter
    def external_language(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__883388ce52644d85f2758a489d845b834afe713236b7a37531d95d46d07f284f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "externalLanguage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="externalName")
    def external_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "externalName"))

    @external_name.setter
    def external_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__279347d0c0ce6d8f0a2d374c93e453c444656598f2538c6adf3084fc8f0f064f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "externalName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="fullDataType")
    def full_data_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fullDataType"))

    @full_data_type.setter
    def full_data_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0d71dc5e705c949ff336cebff6f544e449707c9583ad518b6588cd6d8475077)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fullDataType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="fullName")
    def full_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fullName"))

    @full_name.setter
    def full_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ec4762e63845fde3ea2ca528992ade9fb43014a640411432427c569543bedb9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fullName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="functionId")
    def function_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionId"))

    @function_id.setter
    def function_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b307d859ae31ffd6741c9bcc19c778bbc5deae52525dcb75a176016ad285e1fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "functionId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isDeterministic")
    def is_deterministic(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isDeterministic"))

    @is_deterministic.setter
    def is_deterministic(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f95b66516e1b7f5c883a81d0bc9bb05aa5146bd5bfe246de662fdbe67890758a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isDeterministic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isNullCall")
    def is_null_call(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isNullCall"))

    @is_null_call.setter
    def is_null_call(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc0b58174b84afa21dc9381f4acf872061efe31c865762f823e2c799864d9483)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isNullCall", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="metastoreId")
    def metastore_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metastoreId"))

    @metastore_id.setter
    def metastore_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efae769af038363c58dfcbda35fbeb5266660e3c81f1f2cd9d78e23987dedd5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metastoreId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f19c403e2716a7581391b7b9abfc7001c91e193dcdde1c00a1fd416d4f2bf716)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @owner.setter
    def owner(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76c7f1c947759d1fe2ab8def0321ed34a828c800d7c29ee642faf90751b776fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "owner", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parameterStyle")
    def parameter_style(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parameterStyle"))

    @parameter_style.setter
    def parameter_style(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f4a0f75f148fc538d17deef195d2e73670d2179338d4bd44de9d3aa9b4428e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameterStyle", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="properties")
    def properties(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "properties"))

    @properties.setter
    def properties(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__edf05dbf1e42b7ea369000b6a6b32f546403b8a31dba07d546475c0fe974e113)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "properties", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="routineBody")
    def routine_body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "routineBody"))

    @routine_body.setter
    def routine_body(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0bf142931c05f6928ef9736a3bec953dc2befabe4fd5339f553e374f2a996a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "routineBody", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="routineDefinition")
    def routine_definition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "routineDefinition"))

    @routine_definition.setter
    def routine_definition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba64db537a74dda4334fbbeef526a3ce375c047197f39407e5b4c2d519f4f3c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "routineDefinition", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="schemaName")
    def schema_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schemaName"))

    @schema_name.setter
    def schema_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eec88c2c15f67a3feeb5996e179658b872400a09fa4dcfbcf55776a6f444ec2d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "schemaName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="securityType")
    def security_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "securityType"))

    @security_type.setter
    def security_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4259c25d4d080d448c2542f5812fcb9cdcfffea3dfd9f8f9719d3e93d1a915c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "securityType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="specificName")
    def specific_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "specificName"))

    @specific_name.setter
    def specific_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b269782603b7859eaac64ab498d9cbf6d94113fd255f5166930d040d5cf4ca2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "specificName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sqlDataAccess")
    def sql_data_access(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sqlDataAccess"))

    @sql_data_access.setter
    def sql_data_access(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81d91b6232e345edfdb92f393a34716dc5ce2c2e85b32b98e6c993c5129aed73)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sqlDataAccess", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sqlPath")
    def sql_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sqlPath"))

    @sql_path.setter
    def sql_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bafc7c080be9f7d5f4a72bb01bc9b49853edfb59535b40446211023ea6f85746)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sqlPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "updatedAt"))

    @updated_at.setter
    def updated_at(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8b6ef4e3a2aa9602a866603dbf2ff8fbb27e80c5b59477d199aef23dfaa8627)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "updatedAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="updatedBy")
    def updated_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedBy"))

    @updated_by.setter
    def updated_by(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33cf00ff2abba74b6c3e3f6613ef6af246d74872b25e79a94cdafa32bcf33f38)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "updatedBy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctions]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctions]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctions]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a5c31b5871e56dd91088f6de5db705a9a5c373b8f1a57fedd0e5084ff50c5bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksFunctions.DataDatabricksFunctionsFunctionsReturnParams",
    jsii_struct_bases=[],
    name_mapping={"parameters": "parameters"},
)
class DataDatabricksFunctionsFunctionsReturnParams:
    def __init__(
        self,
        *,
        parameters: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksFunctionsFunctionsReturnParamsParameters", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param parameters: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#parameters DataDatabricksFunctions#parameters}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dace5bc2bb5fec9736c18e1b9f0baaddc52ccd912ed1ea93a32f43b4e0e6eca5)
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if parameters is not None:
            self._values["parameters"] = parameters

    @builtins.property
    def parameters(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksFunctionsFunctionsReturnParamsParameters"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#parameters DataDatabricksFunctions#parameters}.'''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksFunctionsFunctionsReturnParamsParameters"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksFunctionsFunctionsReturnParams(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksFunctionsFunctionsReturnParamsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksFunctions.DataDatabricksFunctionsFunctionsReturnParamsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0eeeba2468bc315c5ddf92662ccf6df42013613b28685d57319804a517087e67)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putParameters")
    def put_parameters(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksFunctionsFunctionsReturnParamsParameters", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf32178f095a3bd492bb21b92a685d28b27585bbc725276073950b969e9f36e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putParameters", [value]))

    @jsii.member(jsii_name="resetParameters")
    def reset_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameters", []))

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(
        self,
    ) -> "DataDatabricksFunctionsFunctionsReturnParamsParametersList":
        return typing.cast("DataDatabricksFunctionsFunctionsReturnParamsParametersList", jsii.get(self, "parameters"))

    @builtins.property
    @jsii.member(jsii_name="parametersInput")
    def parameters_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksFunctionsFunctionsReturnParamsParameters"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksFunctionsFunctionsReturnParamsParameters"]]], jsii.get(self, "parametersInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsReturnParams]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsReturnParams]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsReturnParams]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7b0fb311efc4354af14587ef7a5ad002e63a7a5feda8cb8d86cfd6a2b8b3f2b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksFunctions.DataDatabricksFunctionsFunctionsReturnParamsParameters",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "position": "position",
        "type_name": "typeName",
        "type_text": "typeText",
        "comment": "comment",
        "parameter_default": "parameterDefault",
        "parameter_mode": "parameterMode",
        "parameter_type": "parameterType",
        "type_interval_type": "typeIntervalType",
        "type_json": "typeJson",
        "type_precision": "typePrecision",
        "type_scale": "typeScale",
    },
)
class DataDatabricksFunctionsFunctionsReturnParamsParameters:
    def __init__(
        self,
        *,
        name: builtins.str,
        position: jsii.Number,
        type_name: builtins.str,
        type_text: builtins.str,
        comment: typing.Optional[builtins.str] = None,
        parameter_default: typing.Optional[builtins.str] = None,
        parameter_mode: typing.Optional[builtins.str] = None,
        parameter_type: typing.Optional[builtins.str] = None,
        type_interval_type: typing.Optional[builtins.str] = None,
        type_json: typing.Optional[builtins.str] = None,
        type_precision: typing.Optional[jsii.Number] = None,
        type_scale: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#name DataDatabricksFunctions#name}.
        :param position: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#position DataDatabricksFunctions#position}.
        :param type_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#type_name DataDatabricksFunctions#type_name}.
        :param type_text: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#type_text DataDatabricksFunctions#type_text}.
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#comment DataDatabricksFunctions#comment}.
        :param parameter_default: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#parameter_default DataDatabricksFunctions#parameter_default}.
        :param parameter_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#parameter_mode DataDatabricksFunctions#parameter_mode}.
        :param parameter_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#parameter_type DataDatabricksFunctions#parameter_type}.
        :param type_interval_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#type_interval_type DataDatabricksFunctions#type_interval_type}.
        :param type_json: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#type_json DataDatabricksFunctions#type_json}.
        :param type_precision: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#type_precision DataDatabricksFunctions#type_precision}.
        :param type_scale: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#type_scale DataDatabricksFunctions#type_scale}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae3a0b43f87a338a98506b8f17ad48daedeb2382f25ed7d814d4b1b61f0124a3)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument position", value=position, expected_type=type_hints["position"])
            check_type(argname="argument type_name", value=type_name, expected_type=type_hints["type_name"])
            check_type(argname="argument type_text", value=type_text, expected_type=type_hints["type_text"])
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument parameter_default", value=parameter_default, expected_type=type_hints["parameter_default"])
            check_type(argname="argument parameter_mode", value=parameter_mode, expected_type=type_hints["parameter_mode"])
            check_type(argname="argument parameter_type", value=parameter_type, expected_type=type_hints["parameter_type"])
            check_type(argname="argument type_interval_type", value=type_interval_type, expected_type=type_hints["type_interval_type"])
            check_type(argname="argument type_json", value=type_json, expected_type=type_hints["type_json"])
            check_type(argname="argument type_precision", value=type_precision, expected_type=type_hints["type_precision"])
            check_type(argname="argument type_scale", value=type_scale, expected_type=type_hints["type_scale"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "position": position,
            "type_name": type_name,
            "type_text": type_text,
        }
        if comment is not None:
            self._values["comment"] = comment
        if parameter_default is not None:
            self._values["parameter_default"] = parameter_default
        if parameter_mode is not None:
            self._values["parameter_mode"] = parameter_mode
        if parameter_type is not None:
            self._values["parameter_type"] = parameter_type
        if type_interval_type is not None:
            self._values["type_interval_type"] = type_interval_type
        if type_json is not None:
            self._values["type_json"] = type_json
        if type_precision is not None:
            self._values["type_precision"] = type_precision
        if type_scale is not None:
            self._values["type_scale"] = type_scale

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#name DataDatabricksFunctions#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def position(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#position DataDatabricksFunctions#position}.'''
        result = self._values.get("position")
        assert result is not None, "Required property 'position' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def type_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#type_name DataDatabricksFunctions#type_name}.'''
        result = self._values.get("type_name")
        assert result is not None, "Required property 'type_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type_text(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#type_text DataDatabricksFunctions#type_text}.'''
        result = self._values.get("type_text")
        assert result is not None, "Required property 'type_text' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#comment DataDatabricksFunctions#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameter_default(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#parameter_default DataDatabricksFunctions#parameter_default}.'''
        result = self._values.get("parameter_default")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameter_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#parameter_mode DataDatabricksFunctions#parameter_mode}.'''
        result = self._values.get("parameter_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameter_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#parameter_type DataDatabricksFunctions#parameter_type}.'''
        result = self._values.get("parameter_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_interval_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#type_interval_type DataDatabricksFunctions#type_interval_type}.'''
        result = self._values.get("type_interval_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#type_json DataDatabricksFunctions#type_json}.'''
        result = self._values.get("type_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_precision(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#type_precision DataDatabricksFunctions#type_precision}.'''
        result = self._values.get("type_precision")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_scale(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#type_scale DataDatabricksFunctions#type_scale}.'''
        result = self._values.get("type_scale")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksFunctionsFunctionsReturnParamsParameters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksFunctionsFunctionsReturnParamsParametersList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksFunctions.DataDatabricksFunctionsFunctionsReturnParamsParametersList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b90eb1274bf96efbc82ef99d43284da194351787a33ae986cb00acfdc1c3ec2c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksFunctionsFunctionsReturnParamsParametersOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__758f33cdfc468205478761961eff4150cb11ab3f8e8ed1e2379dcafff1ac27cf)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksFunctionsFunctionsReturnParamsParametersOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ac61c0eec6b80ac3b005509ff2fbcc3a65c703644270cd083f399b48e986681)
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
            type_hints = typing.get_type_hints(_typecheckingstub__310ebb06a3b5e9a5ba9a99f0021afd36c72c631e6631603af890dd7b6a6fbfc2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a0f28ac8d9cc6c6680e1b03f029bb31dabf05be26e5cc43300f8670d6ccb3a50)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksFunctionsFunctionsReturnParamsParameters]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksFunctionsFunctionsReturnParamsParameters]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksFunctionsFunctionsReturnParamsParameters]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__913bb15f76a74a502460a3291a13a6170805104190e1be335d126c338aa4b840)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksFunctionsFunctionsReturnParamsParametersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksFunctions.DataDatabricksFunctionsFunctionsReturnParamsParametersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8c6c3da04361090eaf47d4583ceb33ec7898c801e642d60a67dcea606d692519)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="resetParameterDefault")
    def reset_parameter_default(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameterDefault", []))

    @jsii.member(jsii_name="resetParameterMode")
    def reset_parameter_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameterMode", []))

    @jsii.member(jsii_name="resetParameterType")
    def reset_parameter_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameterType", []))

    @jsii.member(jsii_name="resetTypeIntervalType")
    def reset_type_interval_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTypeIntervalType", []))

    @jsii.member(jsii_name="resetTypeJson")
    def reset_type_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTypeJson", []))

    @jsii.member(jsii_name="resetTypePrecision")
    def reset_type_precision(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTypePrecision", []))

    @jsii.member(jsii_name="resetTypeScale")
    def reset_type_scale(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTypeScale", []))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="parameterDefaultInput")
    def parameter_default_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parameterDefaultInput"))

    @builtins.property
    @jsii.member(jsii_name="parameterModeInput")
    def parameter_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parameterModeInput"))

    @builtins.property
    @jsii.member(jsii_name="parameterTypeInput")
    def parameter_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parameterTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="positionInput")
    def position_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "positionInput"))

    @builtins.property
    @jsii.member(jsii_name="typeIntervalTypeInput")
    def type_interval_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeIntervalTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="typeJsonInput")
    def type_json_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeJsonInput"))

    @builtins.property
    @jsii.member(jsii_name="typeNameInput")
    def type_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeNameInput"))

    @builtins.property
    @jsii.member(jsii_name="typePrecisionInput")
    def type_precision_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "typePrecisionInput"))

    @builtins.property
    @jsii.member(jsii_name="typeScaleInput")
    def type_scale_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "typeScaleInput"))

    @builtins.property
    @jsii.member(jsii_name="typeTextInput")
    def type_text_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeTextInput"))

    @builtins.property
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c648d1b7b64d560e1e856e59afb8fd0ce485762a6db719366c5f67bead9847c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__657328708c8c2daf6765d92a8a9cee901f2d13ea35ce8c6b1e3d81b13ca89ed9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parameterDefault")
    def parameter_default(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parameterDefault"))

    @parameter_default.setter
    def parameter_default(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a4f182f1ae3f6ef74565c9fefe12db31c710971f8bc128bccb299e2f128c8fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameterDefault", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parameterMode")
    def parameter_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parameterMode"))

    @parameter_mode.setter
    def parameter_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12c9c9ec270be6dd6160c4b3de0d7fc6e6628ec360dd77e326884be17d67560a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameterMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parameterType")
    def parameter_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parameterType"))

    @parameter_type.setter
    def parameter_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7670a05f94be3d17366ee9fbebd7206cffb41d9e6a8f8ca6507adcf000892587)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameterType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="position")
    def position(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "position"))

    @position.setter
    def position(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7250f44ad45870b83c9610064ed7d98ec3b7742dd51f8e45d59ce3f257f70f5e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "position", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeIntervalType")
    def type_interval_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeIntervalType"))

    @type_interval_type.setter
    def type_interval_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89295c1481c3b8f69e8a70ac26437ffd6a4878a9a2a13fdbdc01ad7f9f0041fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeIntervalType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeJson")
    def type_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeJson"))

    @type_json.setter
    def type_json(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7aef7a4141f2c8c97550a42e5a9d92ecc8211b8847eeef8ae11552e66f0b7af2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeJson", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeName")
    def type_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeName"))

    @type_name.setter
    def type_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f4184591f861d1599c74b7167efcd32827c78a0682fe6ac85151ba56785c261)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typePrecision")
    def type_precision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "typePrecision"))

    @type_precision.setter
    def type_precision(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec78b6a43fc423f9e225d23b1654e8d7af253826dcf84a44392b797fdaa12237)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typePrecision", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeScale")
    def type_scale(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "typeScale"))

    @type_scale.setter
    def type_scale(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82bd9ffbb0b45abc9a0a4c96440f3937327f69d3fcb6e6db2e9ce2c3cdd4c318)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeScale", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeText")
    def type_text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeText"))

    @type_text.setter
    def type_text(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cfbc005afbbe937487df54108436288b0880b7fa18a161957b0af1142dcb33a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeText", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsReturnParamsParameters]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsReturnParamsParameters]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsReturnParamsParameters]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__460603481e95a0c7ab17aba0913eeb113e89898836c0062c2b855f2749527d87)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksFunctions.DataDatabricksFunctionsFunctionsRoutineDependencies",
    jsii_struct_bases=[],
    name_mapping={"dependencies": "dependencies"},
)
class DataDatabricksFunctionsFunctionsRoutineDependencies:
    def __init__(
        self,
        *,
        dependencies: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksFunctionsFunctionsRoutineDependenciesDependencies", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param dependencies: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#dependencies DataDatabricksFunctions#dependencies}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38c70cb6598fe868db6d1d739a9885998ef7b3ccebcd97f33258bfa81ab7fdd5)
            check_type(argname="argument dependencies", value=dependencies, expected_type=type_hints["dependencies"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dependencies is not None:
            self._values["dependencies"] = dependencies

    @builtins.property
    def dependencies(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksFunctionsFunctionsRoutineDependenciesDependencies"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#dependencies DataDatabricksFunctions#dependencies}.'''
        result = self._values.get("dependencies")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksFunctionsFunctionsRoutineDependenciesDependencies"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksFunctionsFunctionsRoutineDependencies(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksFunctions.DataDatabricksFunctionsFunctionsRoutineDependenciesDependencies",
    jsii_struct_bases=[],
    name_mapping={
        "connection": "connection",
        "credential": "credential",
        "function": "function",
        "table": "table",
    },
)
class DataDatabricksFunctionsFunctionsRoutineDependenciesDependencies:
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union["DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesConnection", typing.Dict[builtins.str, typing.Any]]] = None,
        credential: typing.Optional[typing.Union["DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesCredential", typing.Dict[builtins.str, typing.Any]]] = None,
        function: typing.Optional[typing.Union["DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesFunction", typing.Dict[builtins.str, typing.Any]]] = None,
        table: typing.Optional[typing.Union["DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesTable", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#connection DataDatabricksFunctions#connection}.
        :param credential: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#credential DataDatabricksFunctions#credential}.
        :param function: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#function DataDatabricksFunctions#function}.
        :param table: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#table DataDatabricksFunctions#table}.
        '''
        if isinstance(connection, dict):
            connection = DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesConnection(**connection)
        if isinstance(credential, dict):
            credential = DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesCredential(**credential)
        if isinstance(function, dict):
            function = DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesFunction(**function)
        if isinstance(table, dict):
            table = DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesTable(**table)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3407e5328ce63d069c070e4759fd8640767b85aba913f4541d9af756b935b06)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument credential", value=credential, expected_type=type_hints["credential"])
            check_type(argname="argument function", value=function, expected_type=type_hints["function"])
            check_type(argname="argument table", value=table, expected_type=type_hints["table"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if connection is not None:
            self._values["connection"] = connection
        if credential is not None:
            self._values["credential"] = credential
        if function is not None:
            self._values["function"] = function
        if table is not None:
            self._values["table"] = table

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional["DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesConnection"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#connection DataDatabricksFunctions#connection}.'''
        result = self._values.get("connection")
        return typing.cast(typing.Optional["DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesConnection"], result)

    @builtins.property
    def credential(
        self,
    ) -> typing.Optional["DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesCredential"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#credential DataDatabricksFunctions#credential}.'''
        result = self._values.get("credential")
        return typing.cast(typing.Optional["DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesCredential"], result)

    @builtins.property
    def function(
        self,
    ) -> typing.Optional["DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesFunction"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#function DataDatabricksFunctions#function}.'''
        result = self._values.get("function")
        return typing.cast(typing.Optional["DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesFunction"], result)

    @builtins.property
    def table(
        self,
    ) -> typing.Optional["DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesTable"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#table DataDatabricksFunctions#table}.'''
        result = self._values.get("table")
        return typing.cast(typing.Optional["DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesTable"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksFunctionsFunctionsRoutineDependenciesDependencies(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksFunctions.DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesConnection",
    jsii_struct_bases=[],
    name_mapping={"connection_name": "connectionName"},
)
class DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesConnection:
    def __init__(
        self,
        *,
        connection_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#connection_name DataDatabricksFunctions#connection_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c7c1a8b1088b3e557c11aab29ba91f01b5009fe83e030d7a0046099d0fad73e)
            check_type(argname="argument connection_name", value=connection_name, expected_type=type_hints["connection_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if connection_name is not None:
            self._values["connection_name"] = connection_name

    @builtins.property
    def connection_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#connection_name DataDatabricksFunctions#connection_name}.'''
        result = self._values.get("connection_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesConnection(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesConnectionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksFunctions.DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesConnectionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c307f7f217ee66041a5ca0ca0ae51433c35f6af881e23ea1d3f44653118adec6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetConnectionName")
    def reset_connection_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectionName", []))

    @builtins.property
    @jsii.member(jsii_name="connectionNameInput")
    def connection_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionNameInput"))

    @builtins.property
    @jsii.member(jsii_name="connectionName")
    def connection_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectionName"))

    @connection_name.setter
    def connection_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc5178223208d822dd9e76fec09d3d2c0a733d11d72806a782e4237815a0314d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesConnection]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesConnection]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesConnection]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b2c939a96992bc0c5586d7e19b9157845e6c7ecc60d3317c0ef0dd45a26fec4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksFunctions.DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesCredential",
    jsii_struct_bases=[],
    name_mapping={"credential_name": "credentialName"},
)
class DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesCredential:
    def __init__(
        self,
        *,
        credential_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param credential_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#credential_name DataDatabricksFunctions#credential_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae71fc2ed7f8ab97b3bae1cdb431d3caf0141157107b1349c81dd440a0769ee6)
            check_type(argname="argument credential_name", value=credential_name, expected_type=type_hints["credential_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if credential_name is not None:
            self._values["credential_name"] = credential_name

    @builtins.property
    def credential_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#credential_name DataDatabricksFunctions#credential_name}.'''
        result = self._values.get("credential_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesCredential(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesCredentialOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksFunctions.DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesCredentialOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5c8c5e63937a479116a17eddb6d6cd88631d0df7cc225b5ba4dcb9ef98dca22a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCredentialName")
    def reset_credential_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCredentialName", []))

    @builtins.property
    @jsii.member(jsii_name="credentialNameInput")
    def credential_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "credentialNameInput"))

    @builtins.property
    @jsii.member(jsii_name="credentialName")
    def credential_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "credentialName"))

    @credential_name.setter
    def credential_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a22a912cdcb1a519a31670c4ad1b23fde0e3d184c988dae99b921f5da77d7d3c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "credentialName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesCredential]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesCredential]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesCredential]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae1f7dc9f578118d87a2fe1fc77d13f46fa2c6f098aa26a260824732ebc9fbec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksFunctions.DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesFunction",
    jsii_struct_bases=[],
    name_mapping={"function_full_name": "functionFullName"},
)
class DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesFunction:
    def __init__(self, *, function_full_name: builtins.str) -> None:
        '''
        :param function_full_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#function_full_name DataDatabricksFunctions#function_full_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01472f8b4299a8188c8ec36e7849616390600b170364caff0627c92296970c16)
            check_type(argname="argument function_full_name", value=function_full_name, expected_type=type_hints["function_full_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "function_full_name": function_full_name,
        }

    @builtins.property
    def function_full_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#function_full_name DataDatabricksFunctions#function_full_name}.'''
        result = self._values.get("function_full_name")
        assert result is not None, "Required property 'function_full_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesFunction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesFunctionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksFunctions.DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesFunctionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__caef3584220d5beb63cca2260fcbbbe769126c55e87e1c3338608237ebbe1dd4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="functionFullNameInput")
    def function_full_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionFullNameInput"))

    @builtins.property
    @jsii.member(jsii_name="functionFullName")
    def function_full_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionFullName"))

    @function_full_name.setter
    def function_full_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ba4d699b86f86d96760f474e11cde7a11617fc09ac9e4a79bae452530a7e034)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "functionFullName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesFunction]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesFunction]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesFunction]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c5337f24aff57b2aefa83d3bc822caec01262599fc192e2a24e165ef975d426)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksFunctions.DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4cd00af95f7ab8f02978262d59d3ded621ddce753a04d266dcdcdefbf3daf6bc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__967bd430f9dbe4d788493473b6a890bb29065460d0f68d2277454fa44ec2fcd9)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e8f1c2e5dd6ae6f649fd38d6fc4203058208e94d2cce0052794f9c6cfe5d632)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9409de77b4a7295f7b6f8b5f27558cada1e5eaa035507c6e4d768558c6694f1a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e8d1f9a929db2e0bf7fecc3339af2565cfb7a6d2143946cd7505f76c45450e5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksFunctionsFunctionsRoutineDependenciesDependencies]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksFunctionsFunctionsRoutineDependenciesDependencies]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksFunctionsFunctionsRoutineDependenciesDependencies]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fee847093f5eb6ea7bcaebaf5ed01f4cab8574558c9a9db5c2b70f572fc50f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksFunctions.DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1d5a771bdbfca9471a9f196b232e30435d38dd4e7d1d18625df489d983c0674b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putConnection")
    def put_connection(
        self,
        *,
        connection_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#connection_name DataDatabricksFunctions#connection_name}.
        '''
        value = DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesConnection(
            connection_name=connection_name
        )

        return typing.cast(None, jsii.invoke(self, "putConnection", [value]))

    @jsii.member(jsii_name="putCredential")
    def put_credential(
        self,
        *,
        credential_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param credential_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#credential_name DataDatabricksFunctions#credential_name}.
        '''
        value = DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesCredential(
            credential_name=credential_name
        )

        return typing.cast(None, jsii.invoke(self, "putCredential", [value]))

    @jsii.member(jsii_name="putFunction")
    def put_function(self, *, function_full_name: builtins.str) -> None:
        '''
        :param function_full_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#function_full_name DataDatabricksFunctions#function_full_name}.
        '''
        value = DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesFunction(
            function_full_name=function_full_name
        )

        return typing.cast(None, jsii.invoke(self, "putFunction", [value]))

    @jsii.member(jsii_name="putTable")
    def put_table(self, *, table_full_name: builtins.str) -> None:
        '''
        :param table_full_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#table_full_name DataDatabricksFunctions#table_full_name}.
        '''
        value = DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesTable(
            table_full_name=table_full_name
        )

        return typing.cast(None, jsii.invoke(self, "putTable", [value]))

    @jsii.member(jsii_name="resetConnection")
    def reset_connection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnection", []))

    @jsii.member(jsii_name="resetCredential")
    def reset_credential(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCredential", []))

    @jsii.member(jsii_name="resetFunction")
    def reset_function(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFunction", []))

    @jsii.member(jsii_name="resetTable")
    def reset_table(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTable", []))

    @builtins.property
    @jsii.member(jsii_name="connection")
    def connection(
        self,
    ) -> DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesConnectionOutputReference:
        return typing.cast(DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesConnectionOutputReference, jsii.get(self, "connection"))

    @builtins.property
    @jsii.member(jsii_name="credential")
    def credential(
        self,
    ) -> DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesCredentialOutputReference:
        return typing.cast(DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesCredentialOutputReference, jsii.get(self, "credential"))

    @builtins.property
    @jsii.member(jsii_name="function")
    def function(
        self,
    ) -> DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesFunctionOutputReference:
        return typing.cast(DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesFunctionOutputReference, jsii.get(self, "function"))

    @builtins.property
    @jsii.member(jsii_name="table")
    def table(
        self,
    ) -> "DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesTableOutputReference":
        return typing.cast("DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesTableOutputReference", jsii.get(self, "table"))

    @builtins.property
    @jsii.member(jsii_name="connectionInput")
    def connection_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesConnection]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesConnection]], jsii.get(self, "connectionInput"))

    @builtins.property
    @jsii.member(jsii_name="credentialInput")
    def credential_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesCredential]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesCredential]], jsii.get(self, "credentialInput"))

    @builtins.property
    @jsii.member(jsii_name="functionInput")
    def function_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesFunction]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesFunction]], jsii.get(self, "functionInput"))

    @builtins.property
    @jsii.member(jsii_name="tableInput")
    def table_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesTable"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesTable"]], jsii.get(self, "tableInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependenciesDependencies]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependenciesDependencies]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependenciesDependencies]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b09d8da19159d42c9119ff33fc4532b21c0198b93f3a7a97cd3b369f25b0b319)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksFunctions.DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesTable",
    jsii_struct_bases=[],
    name_mapping={"table_full_name": "tableFullName"},
)
class DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesTable:
    def __init__(self, *, table_full_name: builtins.str) -> None:
        '''
        :param table_full_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#table_full_name DataDatabricksFunctions#table_full_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6167266455294ec7b667a912dda2af379f115436836e57193b1ddc66b467f0e6)
            check_type(argname="argument table_full_name", value=table_full_name, expected_type=type_hints["table_full_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "table_full_name": table_full_name,
        }

    @builtins.property
    def table_full_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/functions#table_full_name DataDatabricksFunctions#table_full_name}.'''
        result = self._values.get("table_full_name")
        assert result is not None, "Required property 'table_full_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesTable(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesTableOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksFunctions.DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesTableOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__101f9d486702b5e9d599fc2c57c2942ade1d1eab089cf21e1aa1303fb2d7d2f0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="tableFullNameInput")
    def table_full_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tableFullNameInput"))

    @builtins.property
    @jsii.member(jsii_name="tableFullName")
    def table_full_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tableFullName"))

    @table_full_name.setter
    def table_full_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3076a61da83894c58c2940c2a3b1eda12ba83e4cf720a678060bf91ecc474416)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tableFullName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesTable]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesTable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesTable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36f42b47461a1e4462a83f04f0e06e0d90d8d42d2a20ec66160f03830be24010)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksFunctionsFunctionsRoutineDependenciesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksFunctions.DataDatabricksFunctionsFunctionsRoutineDependenciesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__45d2ecf9c7203df13b082a7736df0c078a49d554a79f5a5a317edb2053b6d2b7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putDependencies")
    def put_dependencies(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksFunctionsFunctionsRoutineDependenciesDependencies, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d272cfa850855f91b21d1f55fa779f53978633f61975a9f90f5fbc00430e57d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDependencies", [value]))

    @jsii.member(jsii_name="resetDependencies")
    def reset_dependencies(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDependencies", []))

    @builtins.property
    @jsii.member(jsii_name="dependencies")
    def dependencies(
        self,
    ) -> DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesList:
        return typing.cast(DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesList, jsii.get(self, "dependencies"))

    @builtins.property
    @jsii.member(jsii_name="dependenciesInput")
    def dependencies_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksFunctionsFunctionsRoutineDependenciesDependencies]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksFunctionsFunctionsRoutineDependenciesDependencies]]], jsii.get(self, "dependenciesInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependencies]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependencies]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependencies]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91d1829748a9a869fb6569299f53e49dafb16dcfa38fb6d87c4cb91c24b5cd77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataDatabricksFunctions",
    "DataDatabricksFunctionsConfig",
    "DataDatabricksFunctionsFunctions",
    "DataDatabricksFunctionsFunctionsInputParams",
    "DataDatabricksFunctionsFunctionsInputParamsOutputReference",
    "DataDatabricksFunctionsFunctionsInputParamsParameters",
    "DataDatabricksFunctionsFunctionsInputParamsParametersList",
    "DataDatabricksFunctionsFunctionsInputParamsParametersOutputReference",
    "DataDatabricksFunctionsFunctionsList",
    "DataDatabricksFunctionsFunctionsOutputReference",
    "DataDatabricksFunctionsFunctionsReturnParams",
    "DataDatabricksFunctionsFunctionsReturnParamsOutputReference",
    "DataDatabricksFunctionsFunctionsReturnParamsParameters",
    "DataDatabricksFunctionsFunctionsReturnParamsParametersList",
    "DataDatabricksFunctionsFunctionsReturnParamsParametersOutputReference",
    "DataDatabricksFunctionsFunctionsRoutineDependencies",
    "DataDatabricksFunctionsFunctionsRoutineDependenciesDependencies",
    "DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesConnection",
    "DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesConnectionOutputReference",
    "DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesCredential",
    "DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesCredentialOutputReference",
    "DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesFunction",
    "DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesFunctionOutputReference",
    "DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesList",
    "DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesOutputReference",
    "DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesTable",
    "DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesTableOutputReference",
    "DataDatabricksFunctionsFunctionsRoutineDependenciesOutputReference",
]

publication.publish()

def _typecheckingstub__1d2e4df42b578602016352031cb9ffedb715044dfb99f86fd5d826bbc0bce894(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    catalog_name: builtins.str,
    schema_name: builtins.str,
    functions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksFunctionsFunctions, typing.Dict[builtins.str, typing.Any]]]]] = None,
    include_browse: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__64566aed2b3945590967ad8ebb6ff5620a819537f87f01e8f531518f50b60933(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be8315555557cdf16893e0a68644cf3e5de92241561b195b5d5c46b3cdf872de(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksFunctionsFunctions, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9614ee4dde73595e4567caf7193d3aea26fb147a3658a08129b69171bafc8bbe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83990dc67f05707bb4d0713fdb7d969f849e7f8a8d8fe689d76a80a32e5a0e4e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9c5e0581233d96bc77844fbaa4866586b2b4d9b61521174566d66d6fac3acc6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c090a204515d727101661784bfda9f542f3eb99b5c2739f73bb3605a6e57f59(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    catalog_name: builtins.str,
    schema_name: builtins.str,
    functions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksFunctionsFunctions, typing.Dict[builtins.str, typing.Any]]]]] = None,
    include_browse: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e607b59531791ae2f0325effe6c2759c9d847b9e7f1e03f0fff2a4141c07b14(
    *,
    browse_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    catalog_name: typing.Optional[builtins.str] = None,
    comment: typing.Optional[builtins.str] = None,
    created_at: typing.Optional[jsii.Number] = None,
    created_by: typing.Optional[builtins.str] = None,
    data_type: typing.Optional[builtins.str] = None,
    external_language: typing.Optional[builtins.str] = None,
    external_name: typing.Optional[builtins.str] = None,
    full_data_type: typing.Optional[builtins.str] = None,
    full_name: typing.Optional[builtins.str] = None,
    function_id: typing.Optional[builtins.str] = None,
    input_params: typing.Optional[typing.Union[DataDatabricksFunctionsFunctionsInputParams, typing.Dict[builtins.str, typing.Any]]] = None,
    is_deterministic: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    is_null_call: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    metastore_id: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    owner: typing.Optional[builtins.str] = None,
    parameter_style: typing.Optional[builtins.str] = None,
    properties: typing.Optional[builtins.str] = None,
    return_params: typing.Optional[typing.Union[DataDatabricksFunctionsFunctionsReturnParams, typing.Dict[builtins.str, typing.Any]]] = None,
    routine_body: typing.Optional[builtins.str] = None,
    routine_definition: typing.Optional[builtins.str] = None,
    routine_dependencies: typing.Optional[typing.Union[DataDatabricksFunctionsFunctionsRoutineDependencies, typing.Dict[builtins.str, typing.Any]]] = None,
    schema_name: typing.Optional[builtins.str] = None,
    security_type: typing.Optional[builtins.str] = None,
    specific_name: typing.Optional[builtins.str] = None,
    sql_data_access: typing.Optional[builtins.str] = None,
    sql_path: typing.Optional[builtins.str] = None,
    updated_at: typing.Optional[jsii.Number] = None,
    updated_by: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be9c13e16d7906d1fea60aa1741103114223405c391769eede8757bf0065f291(
    *,
    parameters: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksFunctionsFunctionsInputParamsParameters, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7df60c33a02aae813b90db4530ff6e33220e5e9126c0b62b7e28a08211320b7c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4841e2b31e87bd42a460cf5b74f8a453cd88aedebc50f72597f864a7836ba54f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksFunctionsFunctionsInputParamsParameters, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a4c0c4e0953022ba9b43db162e855120dbb2be759c64d41b170c4c4a365d6c4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsInputParams]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ed24a14cb2a970ce00d3176490657682087a073cc448f0ec26a41799a5f2884(
    *,
    name: builtins.str,
    position: jsii.Number,
    type_name: builtins.str,
    type_text: builtins.str,
    comment: typing.Optional[builtins.str] = None,
    parameter_default: typing.Optional[builtins.str] = None,
    parameter_mode: typing.Optional[builtins.str] = None,
    parameter_type: typing.Optional[builtins.str] = None,
    type_interval_type: typing.Optional[builtins.str] = None,
    type_json: typing.Optional[builtins.str] = None,
    type_precision: typing.Optional[jsii.Number] = None,
    type_scale: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ce05d5d787b4358e225264118db072ebc194ffdff37d68d73de966df45a0462(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3dffb7875b1df7c34b70068a2a9c2eec8c9db22c534d23f4863fbf7d6caa4316(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa955a29aed720e824ecbc4d97a5db41d09fc7e148138dabe0fab2afe61cd12e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2949ba6df062be2e72045f9ba2e65ba500cbe01bbba14eb2d2e728c7d9a2c86(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7d28db4a599367ea8c6cddde1d21b6a8a5ce130e3a77a760e6c3d2614a58eaf(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__542ac03a6d56e17de18216c8e8f869a7bc446d677f8b2415e13d52089d69106f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksFunctionsFunctionsInputParamsParameters]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7362f2bafb4c71813b11080f9cacd55484de8079cc92a4cb7ccafbfd530ca0cd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea5e50c834e8547320011a4dcf0b706be6d822a36cf67d6f45a77a2f5fa4888f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bd50e243697cfcf0aa0ced77cc60f25113e4316f554fb7624cbbd02502b1a65(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2da6199cc373c19de2b9d2a0fffb920a9c460c856d6ee1571add458ca46eab10(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d99ffecbe49d64a40c458eca4e11c003bf7f21c077adfea58fa0af39fdfd363(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d0c9247eb490ca7ae259582a4451f8fb2f31c2723dcfe46d42fea812d597664(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c58cb3dda78a85a452f725b47be01190505afe57986cb0f869f9386da2047407(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8df9e3738bad6f13e21cc4dabcb61841d7f883048578d67e7aebb551db12d8a9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e90f3dbc28e6aaace2e4f685e518971fad7b39ff2a704e79ab8c6e73c9afa41(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5b8f38cc44fb29d904477f8f5dafdab8d1d02a202fe616101e7b68165236916(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42e3d8880a2095c1012bb3ee4719eff6a23498cd6daec6bdca562d7b5cf04032(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37d2d9cf4f77e628df13cf9f1a6d4499bddfcf46b4831bb12dbb291cbdce79e4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9e6c8f97598ff0c0e168ee5869f4e3423ea80d9da33237441b4e5ee3acade7c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ba76736b007d507b35954a61cbc932831f9797e6b24cbfa7279a54677eba2ae(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsInputParamsParameters]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18a3ac77f06b3c3af779aa168b97bb7315bb70aa69d469249a2cb48995a9418d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76e24f8b19be3bddb75a79facfcc33c4fa7fd373dcf1e1426823d650f11bc3a0(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5869a1bd860dd86e48dba4efc7f898d59c2f21839acc6cba70224d0e66ea1bce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__971a62130f3a98030f1575c12072ca5ffdbc94a0807bbf8d764cf1e0de07117c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ed465a34457cea749d76f9448fd65ca9e1ddd6bade638a0f722ba4e719be90f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c561d074192b500b8767ddbb3d30e171704015e6e76b558954262b63437de106(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksFunctionsFunctions]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11ee9a88f1fca1544fb5d2705087734b23abcb33713048ecd95219d01bd9fba2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__896285b7eba52bf0607466c5eb3ac2544ac2da8a21b8dcb528aade55b484a4bc(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afe0ef01f349ca72e0f0266e421d53c46ace27ad5af6fd321f37880c9f90d02d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6b77eef9e7c50c514932a7ce45cf1797c33449a40bd280f385cb323483707ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__135eff0da066a8b53b963bf3654e5780a84a9bf4dccfb48bcd9af8590ea6966d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df9c388ead60fdbe80609bfbaee17f2ccdb2ff561efc71813cc88a894a91e66c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19d9b1426948c39c1aa28868da18c9c617070a50f79912a267ad02c0e967bbb9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__883388ce52644d85f2758a489d845b834afe713236b7a37531d95d46d07f284f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__279347d0c0ce6d8f0a2d374c93e453c444656598f2538c6adf3084fc8f0f064f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0d71dc5e705c949ff336cebff6f544e449707c9583ad518b6588cd6d8475077(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ec4762e63845fde3ea2ca528992ade9fb43014a640411432427c569543bedb9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b307d859ae31ffd6741c9bcc19c778bbc5deae52525dcb75a176016ad285e1fc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f95b66516e1b7f5c883a81d0bc9bb05aa5146bd5bfe246de662fdbe67890758a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc0b58174b84afa21dc9381f4acf872061efe31c865762f823e2c799864d9483(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efae769af038363c58dfcbda35fbeb5266660e3c81f1f2cd9d78e23987dedd5b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f19c403e2716a7581391b7b9abfc7001c91e193dcdde1c00a1fd416d4f2bf716(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76c7f1c947759d1fe2ab8def0321ed34a828c800d7c29ee642faf90751b776fb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f4a0f75f148fc538d17deef195d2e73670d2179338d4bd44de9d3aa9b4428e8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__edf05dbf1e42b7ea369000b6a6b32f546403b8a31dba07d546475c0fe974e113(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0bf142931c05f6928ef9736a3bec953dc2befabe4fd5339f553e374f2a996a4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba64db537a74dda4334fbbeef526a3ce375c047197f39407e5b4c2d519f4f3c2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eec88c2c15f67a3feeb5996e179658b872400a09fa4dcfbcf55776a6f444ec2d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4259c25d4d080d448c2542f5812fcb9cdcfffea3dfd9f8f9719d3e93d1a915c3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b269782603b7859eaac64ab498d9cbf6d94113fd255f5166930d040d5cf4ca2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81d91b6232e345edfdb92f393a34716dc5ce2c2e85b32b98e6c993c5129aed73(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bafc7c080be9f7d5f4a72bb01bc9b49853edfb59535b40446211023ea6f85746(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8b6ef4e3a2aa9602a866603dbf2ff8fbb27e80c5b59477d199aef23dfaa8627(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33cf00ff2abba74b6c3e3f6613ef6af246d74872b25e79a94cdafa32bcf33f38(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a5c31b5871e56dd91088f6de5db705a9a5c373b8f1a57fedd0e5084ff50c5bc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctions]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dace5bc2bb5fec9736c18e1b9f0baaddc52ccd912ed1ea93a32f43b4e0e6eca5(
    *,
    parameters: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksFunctionsFunctionsReturnParamsParameters, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0eeeba2468bc315c5ddf92662ccf6df42013613b28685d57319804a517087e67(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf32178f095a3bd492bb21b92a685d28b27585bbc725276073950b969e9f36e6(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksFunctionsFunctionsReturnParamsParameters, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7b0fb311efc4354af14587ef7a5ad002e63a7a5feda8cb8d86cfd6a2b8b3f2b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsReturnParams]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae3a0b43f87a338a98506b8f17ad48daedeb2382f25ed7d814d4b1b61f0124a3(
    *,
    name: builtins.str,
    position: jsii.Number,
    type_name: builtins.str,
    type_text: builtins.str,
    comment: typing.Optional[builtins.str] = None,
    parameter_default: typing.Optional[builtins.str] = None,
    parameter_mode: typing.Optional[builtins.str] = None,
    parameter_type: typing.Optional[builtins.str] = None,
    type_interval_type: typing.Optional[builtins.str] = None,
    type_json: typing.Optional[builtins.str] = None,
    type_precision: typing.Optional[jsii.Number] = None,
    type_scale: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b90eb1274bf96efbc82ef99d43284da194351787a33ae986cb00acfdc1c3ec2c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__758f33cdfc468205478761961eff4150cb11ab3f8e8ed1e2379dcafff1ac27cf(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ac61c0eec6b80ac3b005509ff2fbcc3a65c703644270cd083f399b48e986681(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__310ebb06a3b5e9a5ba9a99f0021afd36c72c631e6631603af890dd7b6a6fbfc2(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0f28ac8d9cc6c6680e1b03f029bb31dabf05be26e5cc43300f8670d6ccb3a50(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__913bb15f76a74a502460a3291a13a6170805104190e1be335d126c338aa4b840(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksFunctionsFunctionsReturnParamsParameters]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c6c3da04361090eaf47d4583ceb33ec7898c801e642d60a67dcea606d692519(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c648d1b7b64d560e1e856e59afb8fd0ce485762a6db719366c5f67bead9847c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__657328708c8c2daf6765d92a8a9cee901f2d13ea35ce8c6b1e3d81b13ca89ed9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a4f182f1ae3f6ef74565c9fefe12db31c710971f8bc128bccb299e2f128c8fb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12c9c9ec270be6dd6160c4b3de0d7fc6e6628ec360dd77e326884be17d67560a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7670a05f94be3d17366ee9fbebd7206cffb41d9e6a8f8ca6507adcf000892587(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7250f44ad45870b83c9610064ed7d98ec3b7742dd51f8e45d59ce3f257f70f5e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89295c1481c3b8f69e8a70ac26437ffd6a4878a9a2a13fdbdc01ad7f9f0041fe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7aef7a4141f2c8c97550a42e5a9d92ecc8211b8847eeef8ae11552e66f0b7af2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f4184591f861d1599c74b7167efcd32827c78a0682fe6ac85151ba56785c261(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec78b6a43fc423f9e225d23b1654e8d7af253826dcf84a44392b797fdaa12237(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82bd9ffbb0b45abc9a0a4c96440f3937327f69d3fcb6e6db2e9ce2c3cdd4c318(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cfbc005afbbe937487df54108436288b0880b7fa18a161957b0af1142dcb33a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__460603481e95a0c7ab17aba0913eeb113e89898836c0062c2b855f2749527d87(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsReturnParamsParameters]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38c70cb6598fe868db6d1d739a9885998ef7b3ccebcd97f33258bfa81ab7fdd5(
    *,
    dependencies: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksFunctionsFunctionsRoutineDependenciesDependencies, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3407e5328ce63d069c070e4759fd8640767b85aba913f4541d9af756b935b06(
    *,
    connection: typing.Optional[typing.Union[DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesConnection, typing.Dict[builtins.str, typing.Any]]] = None,
    credential: typing.Optional[typing.Union[DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesCredential, typing.Dict[builtins.str, typing.Any]]] = None,
    function: typing.Optional[typing.Union[DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesFunction, typing.Dict[builtins.str, typing.Any]]] = None,
    table: typing.Optional[typing.Union[DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesTable, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c7c1a8b1088b3e557c11aab29ba91f01b5009fe83e030d7a0046099d0fad73e(
    *,
    connection_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c307f7f217ee66041a5ca0ca0ae51433c35f6af881e23ea1d3f44653118adec6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc5178223208d822dd9e76fec09d3d2c0a733d11d72806a782e4237815a0314d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b2c939a96992bc0c5586d7e19b9157845e6c7ecc60d3317c0ef0dd45a26fec4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesConnection]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae71fc2ed7f8ab97b3bae1cdb431d3caf0141157107b1349c81dd440a0769ee6(
    *,
    credential_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c8c5e63937a479116a17eddb6d6cd88631d0df7cc225b5ba4dcb9ef98dca22a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a22a912cdcb1a519a31670c4ad1b23fde0e3d184c988dae99b921f5da77d7d3c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae1f7dc9f578118d87a2fe1fc77d13f46fa2c6f098aa26a260824732ebc9fbec(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesCredential]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01472f8b4299a8188c8ec36e7849616390600b170364caff0627c92296970c16(
    *,
    function_full_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__caef3584220d5beb63cca2260fcbbbe769126c55e87e1c3338608237ebbe1dd4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ba4d699b86f86d96760f474e11cde7a11617fc09ac9e4a79bae452530a7e034(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c5337f24aff57b2aefa83d3bc822caec01262599fc192e2a24e165ef975d426(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesFunction]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4cd00af95f7ab8f02978262d59d3ded621ddce753a04d266dcdcdefbf3daf6bc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__967bd430f9dbe4d788493473b6a890bb29065460d0f68d2277454fa44ec2fcd9(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e8f1c2e5dd6ae6f649fd38d6fc4203058208e94d2cce0052794f9c6cfe5d632(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9409de77b4a7295f7b6f8b5f27558cada1e5eaa035507c6e4d768558c6694f1a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8d1f9a929db2e0bf7fecc3339af2565cfb7a6d2143946cd7505f76c45450e5b(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fee847093f5eb6ea7bcaebaf5ed01f4cab8574558c9a9db5c2b70f572fc50f5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksFunctionsFunctionsRoutineDependenciesDependencies]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d5a771bdbfca9471a9f196b232e30435d38dd4e7d1d18625df489d983c0674b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b09d8da19159d42c9119ff33fc4532b21c0198b93f3a7a97cd3b369f25b0b319(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependenciesDependencies]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6167266455294ec7b667a912dda2af379f115436836e57193b1ddc66b467f0e6(
    *,
    table_full_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__101f9d486702b5e9d599fc2c57c2942ade1d1eab089cf21e1aa1303fb2d7d2f0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3076a61da83894c58c2940c2a3b1eda12ba83e4cf720a678060bf91ecc474416(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36f42b47461a1e4462a83f04f0e06e0d90d8d42d2a20ec66160f03830be24010(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependenciesDependenciesTable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45d2ecf9c7203df13b082a7736df0c078a49d554a79f5a5a317edb2053b6d2b7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d272cfa850855f91b21d1f55fa779f53978633f61975a9f90f5fbc00430e57d(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksFunctionsFunctionsRoutineDependenciesDependencies, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91d1829748a9a869fb6569299f53e49dafb16dcfa38fb6d87c4cb91c24b5cd77(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksFunctionsFunctionsRoutineDependencies]],
) -> None:
    """Type checking stubs"""
    pass
