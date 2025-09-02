r'''
# `data_databricks_table`

Refer to the Terraform Registry for docs: [`data_databricks_table`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table).
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


class DataDatabricksTable(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTable",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table databricks_table}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        table_info: typing.Optional[typing.Union["DataDatabricksTableTableInfo", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table databricks_table} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#name DataDatabricksTable#name}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#id DataDatabricksTable#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param table_info: table_info block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#table_info DataDatabricksTable#table_info}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08f897014853759e0010e7d51b826b5f68d7ed1ca7a826e4b46f482bba830824)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataDatabricksTableConfig(
            name=name,
            id=id,
            table_info=table_info,
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
        '''Generates CDKTF code for importing a DataDatabricksTable resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDatabricksTable to import.
        :param import_from_id: The id of the existing DataDatabricksTable that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDatabricksTable to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7b713457b82b6a8a3c46328d78c9954b5144755786b7957004b053f42676b30)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putTableInfo")
    def put_table_info(
        self,
        *,
        access_point: typing.Optional[builtins.str] = None,
        browse_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        catalog_name: typing.Optional[builtins.str] = None,
        columns: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksTableTableInfoColumns", typing.Dict[builtins.str, typing.Any]]]]] = None,
        comment: typing.Optional[builtins.str] = None,
        created_at: typing.Optional[jsii.Number] = None,
        created_by: typing.Optional[builtins.str] = None,
        data_access_configuration_id: typing.Optional[builtins.str] = None,
        data_source_format: typing.Optional[builtins.str] = None,
        deleted_at: typing.Optional[jsii.Number] = None,
        delta_runtime_properties_kvpairs: typing.Optional[typing.Union["DataDatabricksTableTableInfoDeltaRuntimePropertiesKvpairs", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_predictive_optimization_flag: typing.Optional[typing.Union["DataDatabricksTableTableInfoEffectivePredictiveOptimizationFlag", typing.Dict[builtins.str, typing.Any]]] = None,
        enable_predictive_optimization: typing.Optional[builtins.str] = None,
        encryption_details: typing.Optional[typing.Union["DataDatabricksTableTableInfoEncryptionDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        full_name: typing.Optional[builtins.str] = None,
        metastore_id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
        pipeline_id: typing.Optional[builtins.str] = None,
        properties: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        row_filter: typing.Optional[typing.Union["DataDatabricksTableTableInfoRowFilter", typing.Dict[builtins.str, typing.Any]]] = None,
        schema_name: typing.Optional[builtins.str] = None,
        securable_kind_manifest: typing.Optional[typing.Union["DataDatabricksTableTableInfoSecurableKindManifest", typing.Dict[builtins.str, typing.Any]]] = None,
        sql_path: typing.Optional[builtins.str] = None,
        storage_credential_name: typing.Optional[builtins.str] = None,
        storage_location: typing.Optional[builtins.str] = None,
        table_constraints: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksTableTableInfoTableConstraints", typing.Dict[builtins.str, typing.Any]]]]] = None,
        table_id: typing.Optional[builtins.str] = None,
        table_type: typing.Optional[builtins.str] = None,
        updated_at: typing.Optional[jsii.Number] = None,
        updated_by: typing.Optional[builtins.str] = None,
        view_definition: typing.Optional[builtins.str] = None,
        view_dependencies: typing.Optional[typing.Union["DataDatabricksTableTableInfoViewDependencies", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param access_point: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#access_point DataDatabricksTable#access_point}.
        :param browse_only: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#browse_only DataDatabricksTable#browse_only}.
        :param catalog_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#catalog_name DataDatabricksTable#catalog_name}.
        :param columns: columns block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#columns DataDatabricksTable#columns}
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#comment DataDatabricksTable#comment}.
        :param created_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#created_at DataDatabricksTable#created_at}.
        :param created_by: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#created_by DataDatabricksTable#created_by}.
        :param data_access_configuration_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#data_access_configuration_id DataDatabricksTable#data_access_configuration_id}.
        :param data_source_format: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#data_source_format DataDatabricksTable#data_source_format}.
        :param deleted_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#deleted_at DataDatabricksTable#deleted_at}.
        :param delta_runtime_properties_kvpairs: delta_runtime_properties_kvpairs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#delta_runtime_properties_kvpairs DataDatabricksTable#delta_runtime_properties_kvpairs}
        :param effective_predictive_optimization_flag: effective_predictive_optimization_flag block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#effective_predictive_optimization_flag DataDatabricksTable#effective_predictive_optimization_flag}
        :param enable_predictive_optimization: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#enable_predictive_optimization DataDatabricksTable#enable_predictive_optimization}.
        :param encryption_details: encryption_details block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#encryption_details DataDatabricksTable#encryption_details}
        :param full_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#full_name DataDatabricksTable#full_name}.
        :param metastore_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#metastore_id DataDatabricksTable#metastore_id}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#name DataDatabricksTable#name}.
        :param owner: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#owner DataDatabricksTable#owner}.
        :param pipeline_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#pipeline_id DataDatabricksTable#pipeline_id}.
        :param properties: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#properties DataDatabricksTable#properties}.
        :param row_filter: row_filter block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#row_filter DataDatabricksTable#row_filter}
        :param schema_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#schema_name DataDatabricksTable#schema_name}.
        :param securable_kind_manifest: securable_kind_manifest block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#securable_kind_manifest DataDatabricksTable#securable_kind_manifest}
        :param sql_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#sql_path DataDatabricksTable#sql_path}.
        :param storage_credential_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#storage_credential_name DataDatabricksTable#storage_credential_name}.
        :param storage_location: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#storage_location DataDatabricksTable#storage_location}.
        :param table_constraints: table_constraints block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#table_constraints DataDatabricksTable#table_constraints}
        :param table_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#table_id DataDatabricksTable#table_id}.
        :param table_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#table_type DataDatabricksTable#table_type}.
        :param updated_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#updated_at DataDatabricksTable#updated_at}.
        :param updated_by: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#updated_by DataDatabricksTable#updated_by}.
        :param view_definition: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#view_definition DataDatabricksTable#view_definition}.
        :param view_dependencies: view_dependencies block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#view_dependencies DataDatabricksTable#view_dependencies}
        '''
        value = DataDatabricksTableTableInfo(
            access_point=access_point,
            browse_only=browse_only,
            catalog_name=catalog_name,
            columns=columns,
            comment=comment,
            created_at=created_at,
            created_by=created_by,
            data_access_configuration_id=data_access_configuration_id,
            data_source_format=data_source_format,
            deleted_at=deleted_at,
            delta_runtime_properties_kvpairs=delta_runtime_properties_kvpairs,
            effective_predictive_optimization_flag=effective_predictive_optimization_flag,
            enable_predictive_optimization=enable_predictive_optimization,
            encryption_details=encryption_details,
            full_name=full_name,
            metastore_id=metastore_id,
            name=name,
            owner=owner,
            pipeline_id=pipeline_id,
            properties=properties,
            row_filter=row_filter,
            schema_name=schema_name,
            securable_kind_manifest=securable_kind_manifest,
            sql_path=sql_path,
            storage_credential_name=storage_credential_name,
            storage_location=storage_location,
            table_constraints=table_constraints,
            table_id=table_id,
            table_type=table_type,
            updated_at=updated_at,
            updated_by=updated_by,
            view_definition=view_definition,
            view_dependencies=view_dependencies,
        )

        return typing.cast(None, jsii.invoke(self, "putTableInfo", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetTableInfo")
    def reset_table_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTableInfo", []))

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
    @jsii.member(jsii_name="tableInfo")
    def table_info(self) -> "DataDatabricksTableTableInfoOutputReference":
        return typing.cast("DataDatabricksTableTableInfoOutputReference", jsii.get(self, "tableInfo"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="tableInfoInput")
    def table_info_input(self) -> typing.Optional["DataDatabricksTableTableInfo"]:
        return typing.cast(typing.Optional["DataDatabricksTableTableInfo"], jsii.get(self, "tableInfoInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7a964ebb33d4aff11008e0c4bec73fe0754ab87d7a608856ffdfc205e862e8f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__234395ebe7a7792b8ac3bccf7c0a6a388ca7626cf784f6138d0f1c34beec1745)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableConfig",
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
        "id": "id",
        "table_info": "tableInfo",
    },
)
class DataDatabricksTableConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        id: typing.Optional[builtins.str] = None,
        table_info: typing.Optional[typing.Union["DataDatabricksTableTableInfo", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#name DataDatabricksTable#name}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#id DataDatabricksTable#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param table_info: table_info block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#table_info DataDatabricksTable#table_info}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(table_info, dict):
            table_info = DataDatabricksTableTableInfo(**table_info)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c88dc6eb23145ea0377c19e5f27afc0450b3ba85ddedae46ce25b34752f5e7aa)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument table_info", value=table_info, expected_type=type_hints["table_info"])
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
        if id is not None:
            self._values["id"] = id
        if table_info is not None:
            self._values["table_info"] = table_info

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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#name DataDatabricksTable#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#id DataDatabricksTable#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def table_info(self) -> typing.Optional["DataDatabricksTableTableInfo"]:
        '''table_info block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#table_info DataDatabricksTable#table_info}
        '''
        result = self._values.get("table_info")
        return typing.cast(typing.Optional["DataDatabricksTableTableInfo"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksTableConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfo",
    jsii_struct_bases=[],
    name_mapping={
        "access_point": "accessPoint",
        "browse_only": "browseOnly",
        "catalog_name": "catalogName",
        "columns": "columns",
        "comment": "comment",
        "created_at": "createdAt",
        "created_by": "createdBy",
        "data_access_configuration_id": "dataAccessConfigurationId",
        "data_source_format": "dataSourceFormat",
        "deleted_at": "deletedAt",
        "delta_runtime_properties_kvpairs": "deltaRuntimePropertiesKvpairs",
        "effective_predictive_optimization_flag": "effectivePredictiveOptimizationFlag",
        "enable_predictive_optimization": "enablePredictiveOptimization",
        "encryption_details": "encryptionDetails",
        "full_name": "fullName",
        "metastore_id": "metastoreId",
        "name": "name",
        "owner": "owner",
        "pipeline_id": "pipelineId",
        "properties": "properties",
        "row_filter": "rowFilter",
        "schema_name": "schemaName",
        "securable_kind_manifest": "securableKindManifest",
        "sql_path": "sqlPath",
        "storage_credential_name": "storageCredentialName",
        "storage_location": "storageLocation",
        "table_constraints": "tableConstraints",
        "table_id": "tableId",
        "table_type": "tableType",
        "updated_at": "updatedAt",
        "updated_by": "updatedBy",
        "view_definition": "viewDefinition",
        "view_dependencies": "viewDependencies",
    },
)
class DataDatabricksTableTableInfo:
    def __init__(
        self,
        *,
        access_point: typing.Optional[builtins.str] = None,
        browse_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        catalog_name: typing.Optional[builtins.str] = None,
        columns: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksTableTableInfoColumns", typing.Dict[builtins.str, typing.Any]]]]] = None,
        comment: typing.Optional[builtins.str] = None,
        created_at: typing.Optional[jsii.Number] = None,
        created_by: typing.Optional[builtins.str] = None,
        data_access_configuration_id: typing.Optional[builtins.str] = None,
        data_source_format: typing.Optional[builtins.str] = None,
        deleted_at: typing.Optional[jsii.Number] = None,
        delta_runtime_properties_kvpairs: typing.Optional[typing.Union["DataDatabricksTableTableInfoDeltaRuntimePropertiesKvpairs", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_predictive_optimization_flag: typing.Optional[typing.Union["DataDatabricksTableTableInfoEffectivePredictiveOptimizationFlag", typing.Dict[builtins.str, typing.Any]]] = None,
        enable_predictive_optimization: typing.Optional[builtins.str] = None,
        encryption_details: typing.Optional[typing.Union["DataDatabricksTableTableInfoEncryptionDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        full_name: typing.Optional[builtins.str] = None,
        metastore_id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
        pipeline_id: typing.Optional[builtins.str] = None,
        properties: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        row_filter: typing.Optional[typing.Union["DataDatabricksTableTableInfoRowFilter", typing.Dict[builtins.str, typing.Any]]] = None,
        schema_name: typing.Optional[builtins.str] = None,
        securable_kind_manifest: typing.Optional[typing.Union["DataDatabricksTableTableInfoSecurableKindManifest", typing.Dict[builtins.str, typing.Any]]] = None,
        sql_path: typing.Optional[builtins.str] = None,
        storage_credential_name: typing.Optional[builtins.str] = None,
        storage_location: typing.Optional[builtins.str] = None,
        table_constraints: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksTableTableInfoTableConstraints", typing.Dict[builtins.str, typing.Any]]]]] = None,
        table_id: typing.Optional[builtins.str] = None,
        table_type: typing.Optional[builtins.str] = None,
        updated_at: typing.Optional[jsii.Number] = None,
        updated_by: typing.Optional[builtins.str] = None,
        view_definition: typing.Optional[builtins.str] = None,
        view_dependencies: typing.Optional[typing.Union["DataDatabricksTableTableInfoViewDependencies", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param access_point: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#access_point DataDatabricksTable#access_point}.
        :param browse_only: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#browse_only DataDatabricksTable#browse_only}.
        :param catalog_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#catalog_name DataDatabricksTable#catalog_name}.
        :param columns: columns block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#columns DataDatabricksTable#columns}
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#comment DataDatabricksTable#comment}.
        :param created_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#created_at DataDatabricksTable#created_at}.
        :param created_by: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#created_by DataDatabricksTable#created_by}.
        :param data_access_configuration_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#data_access_configuration_id DataDatabricksTable#data_access_configuration_id}.
        :param data_source_format: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#data_source_format DataDatabricksTable#data_source_format}.
        :param deleted_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#deleted_at DataDatabricksTable#deleted_at}.
        :param delta_runtime_properties_kvpairs: delta_runtime_properties_kvpairs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#delta_runtime_properties_kvpairs DataDatabricksTable#delta_runtime_properties_kvpairs}
        :param effective_predictive_optimization_flag: effective_predictive_optimization_flag block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#effective_predictive_optimization_flag DataDatabricksTable#effective_predictive_optimization_flag}
        :param enable_predictive_optimization: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#enable_predictive_optimization DataDatabricksTable#enable_predictive_optimization}.
        :param encryption_details: encryption_details block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#encryption_details DataDatabricksTable#encryption_details}
        :param full_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#full_name DataDatabricksTable#full_name}.
        :param metastore_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#metastore_id DataDatabricksTable#metastore_id}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#name DataDatabricksTable#name}.
        :param owner: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#owner DataDatabricksTable#owner}.
        :param pipeline_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#pipeline_id DataDatabricksTable#pipeline_id}.
        :param properties: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#properties DataDatabricksTable#properties}.
        :param row_filter: row_filter block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#row_filter DataDatabricksTable#row_filter}
        :param schema_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#schema_name DataDatabricksTable#schema_name}.
        :param securable_kind_manifest: securable_kind_manifest block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#securable_kind_manifest DataDatabricksTable#securable_kind_manifest}
        :param sql_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#sql_path DataDatabricksTable#sql_path}.
        :param storage_credential_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#storage_credential_name DataDatabricksTable#storage_credential_name}.
        :param storage_location: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#storage_location DataDatabricksTable#storage_location}.
        :param table_constraints: table_constraints block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#table_constraints DataDatabricksTable#table_constraints}
        :param table_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#table_id DataDatabricksTable#table_id}.
        :param table_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#table_type DataDatabricksTable#table_type}.
        :param updated_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#updated_at DataDatabricksTable#updated_at}.
        :param updated_by: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#updated_by DataDatabricksTable#updated_by}.
        :param view_definition: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#view_definition DataDatabricksTable#view_definition}.
        :param view_dependencies: view_dependencies block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#view_dependencies DataDatabricksTable#view_dependencies}
        '''
        if isinstance(delta_runtime_properties_kvpairs, dict):
            delta_runtime_properties_kvpairs = DataDatabricksTableTableInfoDeltaRuntimePropertiesKvpairs(**delta_runtime_properties_kvpairs)
        if isinstance(effective_predictive_optimization_flag, dict):
            effective_predictive_optimization_flag = DataDatabricksTableTableInfoEffectivePredictiveOptimizationFlag(**effective_predictive_optimization_flag)
        if isinstance(encryption_details, dict):
            encryption_details = DataDatabricksTableTableInfoEncryptionDetails(**encryption_details)
        if isinstance(row_filter, dict):
            row_filter = DataDatabricksTableTableInfoRowFilter(**row_filter)
        if isinstance(securable_kind_manifest, dict):
            securable_kind_manifest = DataDatabricksTableTableInfoSecurableKindManifest(**securable_kind_manifest)
        if isinstance(view_dependencies, dict):
            view_dependencies = DataDatabricksTableTableInfoViewDependencies(**view_dependencies)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d1c70959089ece59fe8eb37c1418abbc1f9df1affcc2543df88d188f30a2b8e)
            check_type(argname="argument access_point", value=access_point, expected_type=type_hints["access_point"])
            check_type(argname="argument browse_only", value=browse_only, expected_type=type_hints["browse_only"])
            check_type(argname="argument catalog_name", value=catalog_name, expected_type=type_hints["catalog_name"])
            check_type(argname="argument columns", value=columns, expected_type=type_hints["columns"])
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument created_at", value=created_at, expected_type=type_hints["created_at"])
            check_type(argname="argument created_by", value=created_by, expected_type=type_hints["created_by"])
            check_type(argname="argument data_access_configuration_id", value=data_access_configuration_id, expected_type=type_hints["data_access_configuration_id"])
            check_type(argname="argument data_source_format", value=data_source_format, expected_type=type_hints["data_source_format"])
            check_type(argname="argument deleted_at", value=deleted_at, expected_type=type_hints["deleted_at"])
            check_type(argname="argument delta_runtime_properties_kvpairs", value=delta_runtime_properties_kvpairs, expected_type=type_hints["delta_runtime_properties_kvpairs"])
            check_type(argname="argument effective_predictive_optimization_flag", value=effective_predictive_optimization_flag, expected_type=type_hints["effective_predictive_optimization_flag"])
            check_type(argname="argument enable_predictive_optimization", value=enable_predictive_optimization, expected_type=type_hints["enable_predictive_optimization"])
            check_type(argname="argument encryption_details", value=encryption_details, expected_type=type_hints["encryption_details"])
            check_type(argname="argument full_name", value=full_name, expected_type=type_hints["full_name"])
            check_type(argname="argument metastore_id", value=metastore_id, expected_type=type_hints["metastore_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument owner", value=owner, expected_type=type_hints["owner"])
            check_type(argname="argument pipeline_id", value=pipeline_id, expected_type=type_hints["pipeline_id"])
            check_type(argname="argument properties", value=properties, expected_type=type_hints["properties"])
            check_type(argname="argument row_filter", value=row_filter, expected_type=type_hints["row_filter"])
            check_type(argname="argument schema_name", value=schema_name, expected_type=type_hints["schema_name"])
            check_type(argname="argument securable_kind_manifest", value=securable_kind_manifest, expected_type=type_hints["securable_kind_manifest"])
            check_type(argname="argument sql_path", value=sql_path, expected_type=type_hints["sql_path"])
            check_type(argname="argument storage_credential_name", value=storage_credential_name, expected_type=type_hints["storage_credential_name"])
            check_type(argname="argument storage_location", value=storage_location, expected_type=type_hints["storage_location"])
            check_type(argname="argument table_constraints", value=table_constraints, expected_type=type_hints["table_constraints"])
            check_type(argname="argument table_id", value=table_id, expected_type=type_hints["table_id"])
            check_type(argname="argument table_type", value=table_type, expected_type=type_hints["table_type"])
            check_type(argname="argument updated_at", value=updated_at, expected_type=type_hints["updated_at"])
            check_type(argname="argument updated_by", value=updated_by, expected_type=type_hints["updated_by"])
            check_type(argname="argument view_definition", value=view_definition, expected_type=type_hints["view_definition"])
            check_type(argname="argument view_dependencies", value=view_dependencies, expected_type=type_hints["view_dependencies"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if access_point is not None:
            self._values["access_point"] = access_point
        if browse_only is not None:
            self._values["browse_only"] = browse_only
        if catalog_name is not None:
            self._values["catalog_name"] = catalog_name
        if columns is not None:
            self._values["columns"] = columns
        if comment is not None:
            self._values["comment"] = comment
        if created_at is not None:
            self._values["created_at"] = created_at
        if created_by is not None:
            self._values["created_by"] = created_by
        if data_access_configuration_id is not None:
            self._values["data_access_configuration_id"] = data_access_configuration_id
        if data_source_format is not None:
            self._values["data_source_format"] = data_source_format
        if deleted_at is not None:
            self._values["deleted_at"] = deleted_at
        if delta_runtime_properties_kvpairs is not None:
            self._values["delta_runtime_properties_kvpairs"] = delta_runtime_properties_kvpairs
        if effective_predictive_optimization_flag is not None:
            self._values["effective_predictive_optimization_flag"] = effective_predictive_optimization_flag
        if enable_predictive_optimization is not None:
            self._values["enable_predictive_optimization"] = enable_predictive_optimization
        if encryption_details is not None:
            self._values["encryption_details"] = encryption_details
        if full_name is not None:
            self._values["full_name"] = full_name
        if metastore_id is not None:
            self._values["metastore_id"] = metastore_id
        if name is not None:
            self._values["name"] = name
        if owner is not None:
            self._values["owner"] = owner
        if pipeline_id is not None:
            self._values["pipeline_id"] = pipeline_id
        if properties is not None:
            self._values["properties"] = properties
        if row_filter is not None:
            self._values["row_filter"] = row_filter
        if schema_name is not None:
            self._values["schema_name"] = schema_name
        if securable_kind_manifest is not None:
            self._values["securable_kind_manifest"] = securable_kind_manifest
        if sql_path is not None:
            self._values["sql_path"] = sql_path
        if storage_credential_name is not None:
            self._values["storage_credential_name"] = storage_credential_name
        if storage_location is not None:
            self._values["storage_location"] = storage_location
        if table_constraints is not None:
            self._values["table_constraints"] = table_constraints
        if table_id is not None:
            self._values["table_id"] = table_id
        if table_type is not None:
            self._values["table_type"] = table_type
        if updated_at is not None:
            self._values["updated_at"] = updated_at
        if updated_by is not None:
            self._values["updated_by"] = updated_by
        if view_definition is not None:
            self._values["view_definition"] = view_definition
        if view_dependencies is not None:
            self._values["view_dependencies"] = view_dependencies

    @builtins.property
    def access_point(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#access_point DataDatabricksTable#access_point}.'''
        result = self._values.get("access_point")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def browse_only(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#browse_only DataDatabricksTable#browse_only}.'''
        result = self._values.get("browse_only")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def catalog_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#catalog_name DataDatabricksTable#catalog_name}.'''
        result = self._values.get("catalog_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def columns(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksTableTableInfoColumns"]]]:
        '''columns block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#columns DataDatabricksTable#columns}
        '''
        result = self._values.get("columns")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksTableTableInfoColumns"]]], result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#comment DataDatabricksTable#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def created_at(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#created_at DataDatabricksTable#created_at}.'''
        result = self._values.get("created_at")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def created_by(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#created_by DataDatabricksTable#created_by}.'''
        result = self._values.get("created_by")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def data_access_configuration_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#data_access_configuration_id DataDatabricksTable#data_access_configuration_id}.'''
        result = self._values.get("data_access_configuration_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def data_source_format(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#data_source_format DataDatabricksTable#data_source_format}.'''
        result = self._values.get("data_source_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def deleted_at(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#deleted_at DataDatabricksTable#deleted_at}.'''
        result = self._values.get("deleted_at")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def delta_runtime_properties_kvpairs(
        self,
    ) -> typing.Optional["DataDatabricksTableTableInfoDeltaRuntimePropertiesKvpairs"]:
        '''delta_runtime_properties_kvpairs block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#delta_runtime_properties_kvpairs DataDatabricksTable#delta_runtime_properties_kvpairs}
        '''
        result = self._values.get("delta_runtime_properties_kvpairs")
        return typing.cast(typing.Optional["DataDatabricksTableTableInfoDeltaRuntimePropertiesKvpairs"], result)

    @builtins.property
    def effective_predictive_optimization_flag(
        self,
    ) -> typing.Optional["DataDatabricksTableTableInfoEffectivePredictiveOptimizationFlag"]:
        '''effective_predictive_optimization_flag block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#effective_predictive_optimization_flag DataDatabricksTable#effective_predictive_optimization_flag}
        '''
        result = self._values.get("effective_predictive_optimization_flag")
        return typing.cast(typing.Optional["DataDatabricksTableTableInfoEffectivePredictiveOptimizationFlag"], result)

    @builtins.property
    def enable_predictive_optimization(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#enable_predictive_optimization DataDatabricksTable#enable_predictive_optimization}.'''
        result = self._values.get("enable_predictive_optimization")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_details(
        self,
    ) -> typing.Optional["DataDatabricksTableTableInfoEncryptionDetails"]:
        '''encryption_details block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#encryption_details DataDatabricksTable#encryption_details}
        '''
        result = self._values.get("encryption_details")
        return typing.cast(typing.Optional["DataDatabricksTableTableInfoEncryptionDetails"], result)

    @builtins.property
    def full_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#full_name DataDatabricksTable#full_name}.'''
        result = self._values.get("full_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metastore_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#metastore_id DataDatabricksTable#metastore_id}.'''
        result = self._values.get("metastore_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#name DataDatabricksTable#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def owner(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#owner DataDatabricksTable#owner}.'''
        result = self._values.get("owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pipeline_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#pipeline_id DataDatabricksTable#pipeline_id}.'''
        result = self._values.get("pipeline_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def properties(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#properties DataDatabricksTable#properties}.'''
        result = self._values.get("properties")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def row_filter(self) -> typing.Optional["DataDatabricksTableTableInfoRowFilter"]:
        '''row_filter block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#row_filter DataDatabricksTable#row_filter}
        '''
        result = self._values.get("row_filter")
        return typing.cast(typing.Optional["DataDatabricksTableTableInfoRowFilter"], result)

    @builtins.property
    def schema_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#schema_name DataDatabricksTable#schema_name}.'''
        result = self._values.get("schema_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def securable_kind_manifest(
        self,
    ) -> typing.Optional["DataDatabricksTableTableInfoSecurableKindManifest"]:
        '''securable_kind_manifest block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#securable_kind_manifest DataDatabricksTable#securable_kind_manifest}
        '''
        result = self._values.get("securable_kind_manifest")
        return typing.cast(typing.Optional["DataDatabricksTableTableInfoSecurableKindManifest"], result)

    @builtins.property
    def sql_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#sql_path DataDatabricksTable#sql_path}.'''
        result = self._values.get("sql_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def storage_credential_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#storage_credential_name DataDatabricksTable#storage_credential_name}.'''
        result = self._values.get("storage_credential_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def storage_location(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#storage_location DataDatabricksTable#storage_location}.'''
        result = self._values.get("storage_location")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def table_constraints(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksTableTableInfoTableConstraints"]]]:
        '''table_constraints block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#table_constraints DataDatabricksTable#table_constraints}
        '''
        result = self._values.get("table_constraints")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksTableTableInfoTableConstraints"]]], result)

    @builtins.property
    def table_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#table_id DataDatabricksTable#table_id}.'''
        result = self._values.get("table_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def table_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#table_type DataDatabricksTable#table_type}.'''
        result = self._values.get("table_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def updated_at(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#updated_at DataDatabricksTable#updated_at}.'''
        result = self._values.get("updated_at")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def updated_by(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#updated_by DataDatabricksTable#updated_by}.'''
        result = self._values.get("updated_by")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def view_definition(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#view_definition DataDatabricksTable#view_definition}.'''
        result = self._values.get("view_definition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def view_dependencies(
        self,
    ) -> typing.Optional["DataDatabricksTableTableInfoViewDependencies"]:
        '''view_dependencies block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#view_dependencies DataDatabricksTable#view_dependencies}
        '''
        result = self._values.get("view_dependencies")
        return typing.cast(typing.Optional["DataDatabricksTableTableInfoViewDependencies"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksTableTableInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoColumns",
    jsii_struct_bases=[],
    name_mapping={
        "comment": "comment",
        "mask": "mask",
        "name": "name",
        "nullable": "nullable",
        "partition_index": "partitionIndex",
        "position": "position",
        "type_interval_type": "typeIntervalType",
        "type_json": "typeJson",
        "type_name": "typeName",
        "type_precision": "typePrecision",
        "type_scale": "typeScale",
        "type_text": "typeText",
    },
)
class DataDatabricksTableTableInfoColumns:
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        mask: typing.Optional[typing.Union["DataDatabricksTableTableInfoColumnsMask", typing.Dict[builtins.str, typing.Any]]] = None,
        name: typing.Optional[builtins.str] = None,
        nullable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        partition_index: typing.Optional[jsii.Number] = None,
        position: typing.Optional[jsii.Number] = None,
        type_interval_type: typing.Optional[builtins.str] = None,
        type_json: typing.Optional[builtins.str] = None,
        type_name: typing.Optional[builtins.str] = None,
        type_precision: typing.Optional[jsii.Number] = None,
        type_scale: typing.Optional[jsii.Number] = None,
        type_text: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#comment DataDatabricksTable#comment}.
        :param mask: mask block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#mask DataDatabricksTable#mask}
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#name DataDatabricksTable#name}.
        :param nullable: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#nullable DataDatabricksTable#nullable}.
        :param partition_index: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#partition_index DataDatabricksTable#partition_index}.
        :param position: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#position DataDatabricksTable#position}.
        :param type_interval_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#type_interval_type DataDatabricksTable#type_interval_type}.
        :param type_json: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#type_json DataDatabricksTable#type_json}.
        :param type_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#type_name DataDatabricksTable#type_name}.
        :param type_precision: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#type_precision DataDatabricksTable#type_precision}.
        :param type_scale: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#type_scale DataDatabricksTable#type_scale}.
        :param type_text: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#type_text DataDatabricksTable#type_text}.
        '''
        if isinstance(mask, dict):
            mask = DataDatabricksTableTableInfoColumnsMask(**mask)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54254b1f3ae0fe9723095869ac9bf419f23838171f757ed525563ea41ef68017)
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument mask", value=mask, expected_type=type_hints["mask"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument nullable", value=nullable, expected_type=type_hints["nullable"])
            check_type(argname="argument partition_index", value=partition_index, expected_type=type_hints["partition_index"])
            check_type(argname="argument position", value=position, expected_type=type_hints["position"])
            check_type(argname="argument type_interval_type", value=type_interval_type, expected_type=type_hints["type_interval_type"])
            check_type(argname="argument type_json", value=type_json, expected_type=type_hints["type_json"])
            check_type(argname="argument type_name", value=type_name, expected_type=type_hints["type_name"])
            check_type(argname="argument type_precision", value=type_precision, expected_type=type_hints["type_precision"])
            check_type(argname="argument type_scale", value=type_scale, expected_type=type_hints["type_scale"])
            check_type(argname="argument type_text", value=type_text, expected_type=type_hints["type_text"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if comment is not None:
            self._values["comment"] = comment
        if mask is not None:
            self._values["mask"] = mask
        if name is not None:
            self._values["name"] = name
        if nullable is not None:
            self._values["nullable"] = nullable
        if partition_index is not None:
            self._values["partition_index"] = partition_index
        if position is not None:
            self._values["position"] = position
        if type_interval_type is not None:
            self._values["type_interval_type"] = type_interval_type
        if type_json is not None:
            self._values["type_json"] = type_json
        if type_name is not None:
            self._values["type_name"] = type_name
        if type_precision is not None:
            self._values["type_precision"] = type_precision
        if type_scale is not None:
            self._values["type_scale"] = type_scale
        if type_text is not None:
            self._values["type_text"] = type_text

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#comment DataDatabricksTable#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mask(self) -> typing.Optional["DataDatabricksTableTableInfoColumnsMask"]:
        '''mask block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#mask DataDatabricksTable#mask}
        '''
        result = self._values.get("mask")
        return typing.cast(typing.Optional["DataDatabricksTableTableInfoColumnsMask"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#name DataDatabricksTable#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nullable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#nullable DataDatabricksTable#nullable}.'''
        result = self._values.get("nullable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def partition_index(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#partition_index DataDatabricksTable#partition_index}.'''
        result = self._values.get("partition_index")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def position(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#position DataDatabricksTable#position}.'''
        result = self._values.get("position")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_interval_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#type_interval_type DataDatabricksTable#type_interval_type}.'''
        result = self._values.get("type_interval_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#type_json DataDatabricksTable#type_json}.'''
        result = self._values.get("type_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#type_name DataDatabricksTable#type_name}.'''
        result = self._values.get("type_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_precision(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#type_precision DataDatabricksTable#type_precision}.'''
        result = self._values.get("type_precision")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_scale(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#type_scale DataDatabricksTable#type_scale}.'''
        result = self._values.get("type_scale")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_text(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#type_text DataDatabricksTable#type_text}.'''
        result = self._values.get("type_text")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksTableTableInfoColumns(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksTableTableInfoColumnsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoColumnsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cdf3838c76d526149330d6c206eed8a75a256a9f6ffbbfde41861b37b2c2c8f7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksTableTableInfoColumnsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff3e691186410b26e3846e6733c389fa0a3492f801fef55e16cd609f671f743b)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksTableTableInfoColumnsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cfc4d6a9ae88a4c3e68d49a1c16c66339ae18fe194857245e625f49cb79bc24)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c24d65ad65444c636b315c8429acb8ca782d0b5dcf80ee93bba6391d346909db)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5ed58a4911268ed789617a2e34ab65a5873d8084237fbc0cbc9b878857a12808)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksTableTableInfoColumns]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksTableTableInfoColumns]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksTableTableInfoColumns]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9132e65bcf74fb0f846efaba6bbb534eb4bbbec608249406098f40b4149414d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoColumnsMask",
    jsii_struct_bases=[],
    name_mapping={
        "function_name": "functionName",
        "using_column_names": "usingColumnNames",
    },
)
class DataDatabricksTableTableInfoColumnsMask:
    def __init__(
        self,
        *,
        function_name: typing.Optional[builtins.str] = None,
        using_column_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#function_name DataDatabricksTable#function_name}.
        :param using_column_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#using_column_names DataDatabricksTable#using_column_names}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d538ed698c2eef70b99839317b1012ae9d1a81bb86381dc31b5f9be98d20fd6a)
            check_type(argname="argument function_name", value=function_name, expected_type=type_hints["function_name"])
            check_type(argname="argument using_column_names", value=using_column_names, expected_type=type_hints["using_column_names"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if function_name is not None:
            self._values["function_name"] = function_name
        if using_column_names is not None:
            self._values["using_column_names"] = using_column_names

    @builtins.property
    def function_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#function_name DataDatabricksTable#function_name}.'''
        result = self._values.get("function_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def using_column_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#using_column_names DataDatabricksTable#using_column_names}.'''
        result = self._values.get("using_column_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksTableTableInfoColumnsMask(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksTableTableInfoColumnsMaskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoColumnsMaskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__951343289d6c6349b42bd5745ec76151d8f35d1c5c502074732c22dd27397135)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetFunctionName")
    def reset_function_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFunctionName", []))

    @jsii.member(jsii_name="resetUsingColumnNames")
    def reset_using_column_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsingColumnNames", []))

    @builtins.property
    @jsii.member(jsii_name="functionNameInput")
    def function_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionNameInput"))

    @builtins.property
    @jsii.member(jsii_name="usingColumnNamesInput")
    def using_column_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "usingColumnNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionName"))

    @function_name.setter
    def function_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d57670a92bf6cd9ae52e32282da9ad4f5c54c71dedf2ab81208703d03b22ef29)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "functionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usingColumnNames")
    def using_column_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "usingColumnNames"))

    @using_column_names.setter
    def using_column_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fbe2b816b129d828bfb33da9b2943427658b238c2424580cc3c5c1df9df6675)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usingColumnNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksTableTableInfoColumnsMask]:
        return typing.cast(typing.Optional[DataDatabricksTableTableInfoColumnsMask], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksTableTableInfoColumnsMask],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c149bbed22050a94368e59e1bd9109dbdf721a49ccea3ecad9c3139812e4f2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksTableTableInfoColumnsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoColumnsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__863fd40b07f6cf7ab7b89160c05e783b630a51b1964e71c124e9f4968f5d3b3d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putMask")
    def put_mask(
        self,
        *,
        function_name: typing.Optional[builtins.str] = None,
        using_column_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#function_name DataDatabricksTable#function_name}.
        :param using_column_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#using_column_names DataDatabricksTable#using_column_names}.
        '''
        value = DataDatabricksTableTableInfoColumnsMask(
            function_name=function_name, using_column_names=using_column_names
        )

        return typing.cast(None, jsii.invoke(self, "putMask", [value]))

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="resetMask")
    def reset_mask(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMask", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNullable")
    def reset_nullable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNullable", []))

    @jsii.member(jsii_name="resetPartitionIndex")
    def reset_partition_index(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPartitionIndex", []))

    @jsii.member(jsii_name="resetPosition")
    def reset_position(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPosition", []))

    @jsii.member(jsii_name="resetTypeIntervalType")
    def reset_type_interval_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTypeIntervalType", []))

    @jsii.member(jsii_name="resetTypeJson")
    def reset_type_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTypeJson", []))

    @jsii.member(jsii_name="resetTypeName")
    def reset_type_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTypeName", []))

    @jsii.member(jsii_name="resetTypePrecision")
    def reset_type_precision(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTypePrecision", []))

    @jsii.member(jsii_name="resetTypeScale")
    def reset_type_scale(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTypeScale", []))

    @jsii.member(jsii_name="resetTypeText")
    def reset_type_text(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTypeText", []))

    @builtins.property
    @jsii.member(jsii_name="mask")
    def mask(self) -> DataDatabricksTableTableInfoColumnsMaskOutputReference:
        return typing.cast(DataDatabricksTableTableInfoColumnsMaskOutputReference, jsii.get(self, "mask"))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="maskInput")
    def mask_input(self) -> typing.Optional[DataDatabricksTableTableInfoColumnsMask]:
        return typing.cast(typing.Optional[DataDatabricksTableTableInfoColumnsMask], jsii.get(self, "maskInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="nullableInput")
    def nullable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "nullableInput"))

    @builtins.property
    @jsii.member(jsii_name="partitionIndexInput")
    def partition_index_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "partitionIndexInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__53577afd12301aa3b7dec1f67e1964af881f1358f7aa5f24637f0697d56b2b30)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4175e64795fba90fe66db889f39ddb3857c988aa3eeb1866fa23c1c81b710f82)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nullable")
    def nullable(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "nullable"))

    @nullable.setter
    def nullable(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26a11d2138f50110c02aad9aef76f39fc9b13fea44d318ca896ce44167781aaa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nullable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="partitionIndex")
    def partition_index(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "partitionIndex"))

    @partition_index.setter
    def partition_index(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d101bef0403d84abb60bd826f378ddc91a2d43bf37e698a82d07dda657a8950e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "partitionIndex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="position")
    def position(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "position"))

    @position.setter
    def position(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b84aebbd51f4007a324fafaae3ecabaff462dcde753485d25d5ae639f9bec334)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "position", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeIntervalType")
    def type_interval_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeIntervalType"))

    @type_interval_type.setter
    def type_interval_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6797e8366e92cc9fad54ebb4f2ff7dc59fe42a88947c23882bf6e0fc3e19ff2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeIntervalType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeJson")
    def type_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeJson"))

    @type_json.setter
    def type_json(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc95da90e1d59eaad91c212a6361810423bdc8b5567486b9f9db7c64bd17229e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeJson", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeName")
    def type_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeName"))

    @type_name.setter
    def type_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84c0d1f109cd54c23680e7bb714eac4ccf663caaaf2287571a0719038b4d3f55)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typePrecision")
    def type_precision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "typePrecision"))

    @type_precision.setter
    def type_precision(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a21123a2e44bd63577822808d32736eba91b1410e85f9ac189c4c1b4b217f6df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typePrecision", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeScale")
    def type_scale(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "typeScale"))

    @type_scale.setter
    def type_scale(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e865a79f06e059a2a6bc6a51f82d44140e10c4c0eda5b0257007e67746e2a4b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeScale", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeText")
    def type_text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeText"))

    @type_text.setter
    def type_text(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31690075c154652848954e81902d6be584a0214aa29e9828e077e8cea28ff5c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeText", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksTableTableInfoColumns]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksTableTableInfoColumns]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksTableTableInfoColumns]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8ec06988b1d3ebbcb2004cfeacc24a6381746110cf448edbf7d560c4c4c92e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoDeltaRuntimePropertiesKvpairs",
    jsii_struct_bases=[],
    name_mapping={"delta_runtime_properties": "deltaRuntimeProperties"},
)
class DataDatabricksTableTableInfoDeltaRuntimePropertiesKvpairs:
    def __init__(
        self,
        *,
        delta_runtime_properties: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        '''
        :param delta_runtime_properties: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#delta_runtime_properties DataDatabricksTable#delta_runtime_properties}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20d7e82a071a5fb6bbc27028508fc4558ab3488621f60c01249b5d7619ef70c9)
            check_type(argname="argument delta_runtime_properties", value=delta_runtime_properties, expected_type=type_hints["delta_runtime_properties"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "delta_runtime_properties": delta_runtime_properties,
        }

    @builtins.property
    def delta_runtime_properties(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#delta_runtime_properties DataDatabricksTable#delta_runtime_properties}.'''
        result = self._values.get("delta_runtime_properties")
        assert result is not None, "Required property 'delta_runtime_properties' is missing"
        return typing.cast(typing.Mapping[builtins.str, builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksTableTableInfoDeltaRuntimePropertiesKvpairs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksTableTableInfoDeltaRuntimePropertiesKvpairsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoDeltaRuntimePropertiesKvpairsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b6af1a76556950fb03132493bafb8d48de2e3b985e692fe43fc68a0519669626)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="deltaRuntimePropertiesInput")
    def delta_runtime_properties_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "deltaRuntimePropertiesInput"))

    @builtins.property
    @jsii.member(jsii_name="deltaRuntimeProperties")
    def delta_runtime_properties(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "deltaRuntimeProperties"))

    @delta_runtime_properties.setter
    def delta_runtime_properties(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cc3bf06b2f242771225068c17f57758839bc6e75284cc1373b2a0819d1754f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deltaRuntimeProperties", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksTableTableInfoDeltaRuntimePropertiesKvpairs]:
        return typing.cast(typing.Optional[DataDatabricksTableTableInfoDeltaRuntimePropertiesKvpairs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksTableTableInfoDeltaRuntimePropertiesKvpairs],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c011a30b82885068d08bd6de251b0884677aefe68f1c0b20f27094e9a4574fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoEffectivePredictiveOptimizationFlag",
    jsii_struct_bases=[],
    name_mapping={
        "value": "value",
        "inherited_from_name": "inheritedFromName",
        "inherited_from_type": "inheritedFromType",
    },
)
class DataDatabricksTableTableInfoEffectivePredictiveOptimizationFlag:
    def __init__(
        self,
        *,
        value: builtins.str,
        inherited_from_name: typing.Optional[builtins.str] = None,
        inherited_from_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#value DataDatabricksTable#value}.
        :param inherited_from_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#inherited_from_name DataDatabricksTable#inherited_from_name}.
        :param inherited_from_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#inherited_from_type DataDatabricksTable#inherited_from_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3cb97e6fbd513b31f4a50a82091c9e5bf1fb366217f2a044b086d2fbb96774b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
            check_type(argname="argument inherited_from_name", value=inherited_from_name, expected_type=type_hints["inherited_from_name"])
            check_type(argname="argument inherited_from_type", value=inherited_from_type, expected_type=type_hints["inherited_from_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "value": value,
        }
        if inherited_from_name is not None:
            self._values["inherited_from_name"] = inherited_from_name
        if inherited_from_type is not None:
            self._values["inherited_from_type"] = inherited_from_type

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#value DataDatabricksTable#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def inherited_from_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#inherited_from_name DataDatabricksTable#inherited_from_name}.'''
        result = self._values.get("inherited_from_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def inherited_from_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#inherited_from_type DataDatabricksTable#inherited_from_type}.'''
        result = self._values.get("inherited_from_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksTableTableInfoEffectivePredictiveOptimizationFlag(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksTableTableInfoEffectivePredictiveOptimizationFlagOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoEffectivePredictiveOptimizationFlagOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0e3a04ca19c89208976b6950db308b04c832b896127c82df792328e2263416d9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetInheritedFromName")
    def reset_inherited_from_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInheritedFromName", []))

    @jsii.member(jsii_name="resetInheritedFromType")
    def reset_inherited_from_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInheritedFromType", []))

    @builtins.property
    @jsii.member(jsii_name="inheritedFromNameInput")
    def inherited_from_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "inheritedFromNameInput"))

    @builtins.property
    @jsii.member(jsii_name="inheritedFromTypeInput")
    def inherited_from_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "inheritedFromTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="inheritedFromName")
    def inherited_from_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "inheritedFromName"))

    @inherited_from_name.setter
    def inherited_from_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c1655e53f9b0a9a0322a705275a912d11fbabf77784a7bc4a1985a3b739f728)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inheritedFromName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="inheritedFromType")
    def inherited_from_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "inheritedFromType"))

    @inherited_from_type.setter
    def inherited_from_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7389b7aa650a07b503e03ca4068e0d53316ae0855bdcad3133e16743c3517cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inheritedFromType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de36031fc1016557473aad611db4eb7e8eecff43ad06ee2511c831ddcbccf051)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksTableTableInfoEffectivePredictiveOptimizationFlag]:
        return typing.cast(typing.Optional[DataDatabricksTableTableInfoEffectivePredictiveOptimizationFlag], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksTableTableInfoEffectivePredictiveOptimizationFlag],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2dc7c9e30f9f332158dca68da650e652cbeb6a21e2346f56d02cc1d6a9049d5e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoEncryptionDetails",
    jsii_struct_bases=[],
    name_mapping={"sse_encryption_details": "sseEncryptionDetails"},
)
class DataDatabricksTableTableInfoEncryptionDetails:
    def __init__(
        self,
        *,
        sse_encryption_details: typing.Optional[typing.Union["DataDatabricksTableTableInfoEncryptionDetailsSseEncryptionDetails", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param sse_encryption_details: sse_encryption_details block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#sse_encryption_details DataDatabricksTable#sse_encryption_details}
        '''
        if isinstance(sse_encryption_details, dict):
            sse_encryption_details = DataDatabricksTableTableInfoEncryptionDetailsSseEncryptionDetails(**sse_encryption_details)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7492ae8e8b8f5f2703b4177c5449a08c3b7921c3e4f2ee01bda078a95db984e8)
            check_type(argname="argument sse_encryption_details", value=sse_encryption_details, expected_type=type_hints["sse_encryption_details"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if sse_encryption_details is not None:
            self._values["sse_encryption_details"] = sse_encryption_details

    @builtins.property
    def sse_encryption_details(
        self,
    ) -> typing.Optional["DataDatabricksTableTableInfoEncryptionDetailsSseEncryptionDetails"]:
        '''sse_encryption_details block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#sse_encryption_details DataDatabricksTable#sse_encryption_details}
        '''
        result = self._values.get("sse_encryption_details")
        return typing.cast(typing.Optional["DataDatabricksTableTableInfoEncryptionDetailsSseEncryptionDetails"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksTableTableInfoEncryptionDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksTableTableInfoEncryptionDetailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoEncryptionDetailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__eecf59b5ab93cc46f1f2fc8747e67eda635c432b16cce15a19a25cf5823a33fd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putSseEncryptionDetails")
    def put_sse_encryption_details(
        self,
        *,
        algorithm: typing.Optional[builtins.str] = None,
        aws_kms_key_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param algorithm: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#algorithm DataDatabricksTable#algorithm}.
        :param aws_kms_key_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#aws_kms_key_arn DataDatabricksTable#aws_kms_key_arn}.
        '''
        value = DataDatabricksTableTableInfoEncryptionDetailsSseEncryptionDetails(
            algorithm=algorithm, aws_kms_key_arn=aws_kms_key_arn
        )

        return typing.cast(None, jsii.invoke(self, "putSseEncryptionDetails", [value]))

    @jsii.member(jsii_name="resetSseEncryptionDetails")
    def reset_sse_encryption_details(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSseEncryptionDetails", []))

    @builtins.property
    @jsii.member(jsii_name="sseEncryptionDetails")
    def sse_encryption_details(
        self,
    ) -> "DataDatabricksTableTableInfoEncryptionDetailsSseEncryptionDetailsOutputReference":
        return typing.cast("DataDatabricksTableTableInfoEncryptionDetailsSseEncryptionDetailsOutputReference", jsii.get(self, "sseEncryptionDetails"))

    @builtins.property
    @jsii.member(jsii_name="sseEncryptionDetailsInput")
    def sse_encryption_details_input(
        self,
    ) -> typing.Optional["DataDatabricksTableTableInfoEncryptionDetailsSseEncryptionDetails"]:
        return typing.cast(typing.Optional["DataDatabricksTableTableInfoEncryptionDetailsSseEncryptionDetails"], jsii.get(self, "sseEncryptionDetailsInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksTableTableInfoEncryptionDetails]:
        return typing.cast(typing.Optional[DataDatabricksTableTableInfoEncryptionDetails], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksTableTableInfoEncryptionDetails],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86c39c0ba6d42d6942c4bb605656e6014c6b3b40d659ab4afa6a87e066b0a6b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoEncryptionDetailsSseEncryptionDetails",
    jsii_struct_bases=[],
    name_mapping={"algorithm": "algorithm", "aws_kms_key_arn": "awsKmsKeyArn"},
)
class DataDatabricksTableTableInfoEncryptionDetailsSseEncryptionDetails:
    def __init__(
        self,
        *,
        algorithm: typing.Optional[builtins.str] = None,
        aws_kms_key_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param algorithm: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#algorithm DataDatabricksTable#algorithm}.
        :param aws_kms_key_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#aws_kms_key_arn DataDatabricksTable#aws_kms_key_arn}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64a76fcc34d6297f78d253b0ce083331589f4ce3f2efdae4f944eb89074887f8)
            check_type(argname="argument algorithm", value=algorithm, expected_type=type_hints["algorithm"])
            check_type(argname="argument aws_kms_key_arn", value=aws_kms_key_arn, expected_type=type_hints["aws_kms_key_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if algorithm is not None:
            self._values["algorithm"] = algorithm
        if aws_kms_key_arn is not None:
            self._values["aws_kms_key_arn"] = aws_kms_key_arn

    @builtins.property
    def algorithm(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#algorithm DataDatabricksTable#algorithm}.'''
        result = self._values.get("algorithm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_kms_key_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#aws_kms_key_arn DataDatabricksTable#aws_kms_key_arn}.'''
        result = self._values.get("aws_kms_key_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksTableTableInfoEncryptionDetailsSseEncryptionDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksTableTableInfoEncryptionDetailsSseEncryptionDetailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoEncryptionDetailsSseEncryptionDetailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__93e48ada4ca2f74ad97f1f983711bf55a30af1830e3e2353741a9f95545f078a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAlgorithm")
    def reset_algorithm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlgorithm", []))

    @jsii.member(jsii_name="resetAwsKmsKeyArn")
    def reset_aws_kms_key_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsKmsKeyArn", []))

    @builtins.property
    @jsii.member(jsii_name="algorithmInput")
    def algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "algorithmInput"))

    @builtins.property
    @jsii.member(jsii_name="awsKmsKeyArnInput")
    def aws_kms_key_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsKmsKeyArnInput"))

    @builtins.property
    @jsii.member(jsii_name="algorithm")
    def algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "algorithm"))

    @algorithm.setter
    def algorithm(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__464b696be504cadd711df94518bd9216329e48d4f6c478b0eb1667ec33b86fd6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "algorithm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="awsKmsKeyArn")
    def aws_kms_key_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsKmsKeyArn"))

    @aws_kms_key_arn.setter
    def aws_kms_key_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91a6c10e1899b85d922efd07fdce3b75698e5bf3682844b9d7d5aa2af104a852)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsKmsKeyArn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksTableTableInfoEncryptionDetailsSseEncryptionDetails]:
        return typing.cast(typing.Optional[DataDatabricksTableTableInfoEncryptionDetailsSseEncryptionDetails], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksTableTableInfoEncryptionDetailsSseEncryptionDetails],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c40fb3921c8ca95ab94c1f37a6df9222b2de42a40aa7789b140bc3c2704e5cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksTableTableInfoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7b30280e1a8d263b50a18c395b588870bc07ac4089d2852737a9456f4bb4fe07)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putColumns")
    def put_columns(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksTableTableInfoColumns, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a7c634d0f7e179cd1d42c46b1bee773bd50feda3da2ae307b27ffc3b313b07f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putColumns", [value]))

    @jsii.member(jsii_name="putDeltaRuntimePropertiesKvpairs")
    def put_delta_runtime_properties_kvpairs(
        self,
        *,
        delta_runtime_properties: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        '''
        :param delta_runtime_properties: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#delta_runtime_properties DataDatabricksTable#delta_runtime_properties}.
        '''
        value = DataDatabricksTableTableInfoDeltaRuntimePropertiesKvpairs(
            delta_runtime_properties=delta_runtime_properties
        )

        return typing.cast(None, jsii.invoke(self, "putDeltaRuntimePropertiesKvpairs", [value]))

    @jsii.member(jsii_name="putEffectivePredictiveOptimizationFlag")
    def put_effective_predictive_optimization_flag(
        self,
        *,
        value: builtins.str,
        inherited_from_name: typing.Optional[builtins.str] = None,
        inherited_from_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#value DataDatabricksTable#value}.
        :param inherited_from_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#inherited_from_name DataDatabricksTable#inherited_from_name}.
        :param inherited_from_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#inherited_from_type DataDatabricksTable#inherited_from_type}.
        '''
        value_ = DataDatabricksTableTableInfoEffectivePredictiveOptimizationFlag(
            value=value,
            inherited_from_name=inherited_from_name,
            inherited_from_type=inherited_from_type,
        )

        return typing.cast(None, jsii.invoke(self, "putEffectivePredictiveOptimizationFlag", [value_]))

    @jsii.member(jsii_name="putEncryptionDetails")
    def put_encryption_details(
        self,
        *,
        sse_encryption_details: typing.Optional[typing.Union[DataDatabricksTableTableInfoEncryptionDetailsSseEncryptionDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param sse_encryption_details: sse_encryption_details block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#sse_encryption_details DataDatabricksTable#sse_encryption_details}
        '''
        value = DataDatabricksTableTableInfoEncryptionDetails(
            sse_encryption_details=sse_encryption_details
        )

        return typing.cast(None, jsii.invoke(self, "putEncryptionDetails", [value]))

    @jsii.member(jsii_name="putRowFilter")
    def put_row_filter(
        self,
        *,
        function_name: builtins.str,
        input_column_names: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#function_name DataDatabricksTable#function_name}.
        :param input_column_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#input_column_names DataDatabricksTable#input_column_names}.
        '''
        value = DataDatabricksTableTableInfoRowFilter(
            function_name=function_name, input_column_names=input_column_names
        )

        return typing.cast(None, jsii.invoke(self, "putRowFilter", [value]))

    @jsii.member(jsii_name="putSecurableKindManifest")
    def put_securable_kind_manifest(
        self,
        *,
        assignable_privileges: typing.Optional[typing.Sequence[builtins.str]] = None,
        capabilities: typing.Optional[typing.Sequence[builtins.str]] = None,
        options: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksTableTableInfoSecurableKindManifestOptions", typing.Dict[builtins.str, typing.Any]]]]] = None,
        securable_kind: typing.Optional[builtins.str] = None,
        securable_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param assignable_privileges: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#assignable_privileges DataDatabricksTable#assignable_privileges}.
        :param capabilities: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#capabilities DataDatabricksTable#capabilities}.
        :param options: options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#options DataDatabricksTable#options}
        :param securable_kind: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#securable_kind DataDatabricksTable#securable_kind}.
        :param securable_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#securable_type DataDatabricksTable#securable_type}.
        '''
        value = DataDatabricksTableTableInfoSecurableKindManifest(
            assignable_privileges=assignable_privileges,
            capabilities=capabilities,
            options=options,
            securable_kind=securable_kind,
            securable_type=securable_type,
        )

        return typing.cast(None, jsii.invoke(self, "putSecurableKindManifest", [value]))

    @jsii.member(jsii_name="putTableConstraints")
    def put_table_constraints(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksTableTableInfoTableConstraints", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3cc36fddf6e8fd49d538195acd24e6e66039e65b8556c2e3b643a5f3abc5a9b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTableConstraints", [value]))

    @jsii.member(jsii_name="putViewDependencies")
    def put_view_dependencies(
        self,
        *,
        dependencies: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksTableTableInfoViewDependenciesDependencies", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param dependencies: dependencies block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#dependencies DataDatabricksTable#dependencies}
        '''
        value = DataDatabricksTableTableInfoViewDependencies(dependencies=dependencies)

        return typing.cast(None, jsii.invoke(self, "putViewDependencies", [value]))

    @jsii.member(jsii_name="resetAccessPoint")
    def reset_access_point(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessPoint", []))

    @jsii.member(jsii_name="resetBrowseOnly")
    def reset_browse_only(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBrowseOnly", []))

    @jsii.member(jsii_name="resetCatalogName")
    def reset_catalog_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCatalogName", []))

    @jsii.member(jsii_name="resetColumns")
    def reset_columns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetColumns", []))

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="resetCreatedAt")
    def reset_created_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatedAt", []))

    @jsii.member(jsii_name="resetCreatedBy")
    def reset_created_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatedBy", []))

    @jsii.member(jsii_name="resetDataAccessConfigurationId")
    def reset_data_access_configuration_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataAccessConfigurationId", []))

    @jsii.member(jsii_name="resetDataSourceFormat")
    def reset_data_source_format(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataSourceFormat", []))

    @jsii.member(jsii_name="resetDeletedAt")
    def reset_deleted_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeletedAt", []))

    @jsii.member(jsii_name="resetDeltaRuntimePropertiesKvpairs")
    def reset_delta_runtime_properties_kvpairs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeltaRuntimePropertiesKvpairs", []))

    @jsii.member(jsii_name="resetEffectivePredictiveOptimizationFlag")
    def reset_effective_predictive_optimization_flag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEffectivePredictiveOptimizationFlag", []))

    @jsii.member(jsii_name="resetEnablePredictiveOptimization")
    def reset_enable_predictive_optimization(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnablePredictiveOptimization", []))

    @jsii.member(jsii_name="resetEncryptionDetails")
    def reset_encryption_details(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionDetails", []))

    @jsii.member(jsii_name="resetFullName")
    def reset_full_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFullName", []))

    @jsii.member(jsii_name="resetMetastoreId")
    def reset_metastore_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetastoreId", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetOwner")
    def reset_owner(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOwner", []))

    @jsii.member(jsii_name="resetPipelineId")
    def reset_pipeline_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPipelineId", []))

    @jsii.member(jsii_name="resetProperties")
    def reset_properties(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProperties", []))

    @jsii.member(jsii_name="resetRowFilter")
    def reset_row_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRowFilter", []))

    @jsii.member(jsii_name="resetSchemaName")
    def reset_schema_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchemaName", []))

    @jsii.member(jsii_name="resetSecurableKindManifest")
    def reset_securable_kind_manifest(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurableKindManifest", []))

    @jsii.member(jsii_name="resetSqlPath")
    def reset_sql_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSqlPath", []))

    @jsii.member(jsii_name="resetStorageCredentialName")
    def reset_storage_credential_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageCredentialName", []))

    @jsii.member(jsii_name="resetStorageLocation")
    def reset_storage_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageLocation", []))

    @jsii.member(jsii_name="resetTableConstraints")
    def reset_table_constraints(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTableConstraints", []))

    @jsii.member(jsii_name="resetTableId")
    def reset_table_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTableId", []))

    @jsii.member(jsii_name="resetTableType")
    def reset_table_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTableType", []))

    @jsii.member(jsii_name="resetUpdatedAt")
    def reset_updated_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdatedAt", []))

    @jsii.member(jsii_name="resetUpdatedBy")
    def reset_updated_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdatedBy", []))

    @jsii.member(jsii_name="resetViewDefinition")
    def reset_view_definition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetViewDefinition", []))

    @jsii.member(jsii_name="resetViewDependencies")
    def reset_view_dependencies(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetViewDependencies", []))

    @builtins.property
    @jsii.member(jsii_name="columns")
    def columns(self) -> DataDatabricksTableTableInfoColumnsList:
        return typing.cast(DataDatabricksTableTableInfoColumnsList, jsii.get(self, "columns"))

    @builtins.property
    @jsii.member(jsii_name="deltaRuntimePropertiesKvpairs")
    def delta_runtime_properties_kvpairs(
        self,
    ) -> DataDatabricksTableTableInfoDeltaRuntimePropertiesKvpairsOutputReference:
        return typing.cast(DataDatabricksTableTableInfoDeltaRuntimePropertiesKvpairsOutputReference, jsii.get(self, "deltaRuntimePropertiesKvpairs"))

    @builtins.property
    @jsii.member(jsii_name="effectivePredictiveOptimizationFlag")
    def effective_predictive_optimization_flag(
        self,
    ) -> DataDatabricksTableTableInfoEffectivePredictiveOptimizationFlagOutputReference:
        return typing.cast(DataDatabricksTableTableInfoEffectivePredictiveOptimizationFlagOutputReference, jsii.get(self, "effectivePredictiveOptimizationFlag"))

    @builtins.property
    @jsii.member(jsii_name="encryptionDetails")
    def encryption_details(
        self,
    ) -> DataDatabricksTableTableInfoEncryptionDetailsOutputReference:
        return typing.cast(DataDatabricksTableTableInfoEncryptionDetailsOutputReference, jsii.get(self, "encryptionDetails"))

    @builtins.property
    @jsii.member(jsii_name="rowFilter")
    def row_filter(self) -> "DataDatabricksTableTableInfoRowFilterOutputReference":
        return typing.cast("DataDatabricksTableTableInfoRowFilterOutputReference", jsii.get(self, "rowFilter"))

    @builtins.property
    @jsii.member(jsii_name="securableKindManifest")
    def securable_kind_manifest(
        self,
    ) -> "DataDatabricksTableTableInfoSecurableKindManifestOutputReference":
        return typing.cast("DataDatabricksTableTableInfoSecurableKindManifestOutputReference", jsii.get(self, "securableKindManifest"))

    @builtins.property
    @jsii.member(jsii_name="tableConstraints")
    def table_constraints(self) -> "DataDatabricksTableTableInfoTableConstraintsList":
        return typing.cast("DataDatabricksTableTableInfoTableConstraintsList", jsii.get(self, "tableConstraints"))

    @builtins.property
    @jsii.member(jsii_name="viewDependencies")
    def view_dependencies(
        self,
    ) -> "DataDatabricksTableTableInfoViewDependenciesOutputReference":
        return typing.cast("DataDatabricksTableTableInfoViewDependenciesOutputReference", jsii.get(self, "viewDependencies"))

    @builtins.property
    @jsii.member(jsii_name="accessPointInput")
    def access_point_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessPointInput"))

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
    @jsii.member(jsii_name="columnsInput")
    def columns_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksTableTableInfoColumns]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksTableTableInfoColumns]]], jsii.get(self, "columnsInput"))

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
    @jsii.member(jsii_name="dataAccessConfigurationIdInput")
    def data_access_configuration_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataAccessConfigurationIdInput"))

    @builtins.property
    @jsii.member(jsii_name="dataSourceFormatInput")
    def data_source_format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataSourceFormatInput"))

    @builtins.property
    @jsii.member(jsii_name="deletedAtInput")
    def deleted_at_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "deletedAtInput"))

    @builtins.property
    @jsii.member(jsii_name="deltaRuntimePropertiesKvpairsInput")
    def delta_runtime_properties_kvpairs_input(
        self,
    ) -> typing.Optional[DataDatabricksTableTableInfoDeltaRuntimePropertiesKvpairs]:
        return typing.cast(typing.Optional[DataDatabricksTableTableInfoDeltaRuntimePropertiesKvpairs], jsii.get(self, "deltaRuntimePropertiesKvpairsInput"))

    @builtins.property
    @jsii.member(jsii_name="effectivePredictiveOptimizationFlagInput")
    def effective_predictive_optimization_flag_input(
        self,
    ) -> typing.Optional[DataDatabricksTableTableInfoEffectivePredictiveOptimizationFlag]:
        return typing.cast(typing.Optional[DataDatabricksTableTableInfoEffectivePredictiveOptimizationFlag], jsii.get(self, "effectivePredictiveOptimizationFlagInput"))

    @builtins.property
    @jsii.member(jsii_name="enablePredictiveOptimizationInput")
    def enable_predictive_optimization_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "enablePredictiveOptimizationInput"))

    @builtins.property
    @jsii.member(jsii_name="encryptionDetailsInput")
    def encryption_details_input(
        self,
    ) -> typing.Optional[DataDatabricksTableTableInfoEncryptionDetails]:
        return typing.cast(typing.Optional[DataDatabricksTableTableInfoEncryptionDetails], jsii.get(self, "encryptionDetailsInput"))

    @builtins.property
    @jsii.member(jsii_name="fullNameInput")
    def full_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fullNameInput"))

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
    @jsii.member(jsii_name="pipelineIdInput")
    def pipeline_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pipelineIdInput"))

    @builtins.property
    @jsii.member(jsii_name="propertiesInput")
    def properties_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "propertiesInput"))

    @builtins.property
    @jsii.member(jsii_name="rowFilterInput")
    def row_filter_input(
        self,
    ) -> typing.Optional["DataDatabricksTableTableInfoRowFilter"]:
        return typing.cast(typing.Optional["DataDatabricksTableTableInfoRowFilter"], jsii.get(self, "rowFilterInput"))

    @builtins.property
    @jsii.member(jsii_name="schemaNameInput")
    def schema_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schemaNameInput"))

    @builtins.property
    @jsii.member(jsii_name="securableKindManifestInput")
    def securable_kind_manifest_input(
        self,
    ) -> typing.Optional["DataDatabricksTableTableInfoSecurableKindManifest"]:
        return typing.cast(typing.Optional["DataDatabricksTableTableInfoSecurableKindManifest"], jsii.get(self, "securableKindManifestInput"))

    @builtins.property
    @jsii.member(jsii_name="sqlPathInput")
    def sql_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sqlPathInput"))

    @builtins.property
    @jsii.member(jsii_name="storageCredentialNameInput")
    def storage_credential_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageCredentialNameInput"))

    @builtins.property
    @jsii.member(jsii_name="storageLocationInput")
    def storage_location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageLocationInput"))

    @builtins.property
    @jsii.member(jsii_name="tableConstraintsInput")
    def table_constraints_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksTableTableInfoTableConstraints"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksTableTableInfoTableConstraints"]]], jsii.get(self, "tableConstraintsInput"))

    @builtins.property
    @jsii.member(jsii_name="tableIdInput")
    def table_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tableIdInput"))

    @builtins.property
    @jsii.member(jsii_name="tableTypeInput")
    def table_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tableTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="updatedAtInput")
    def updated_at_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "updatedAtInput"))

    @builtins.property
    @jsii.member(jsii_name="updatedByInput")
    def updated_by_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updatedByInput"))

    @builtins.property
    @jsii.member(jsii_name="viewDefinitionInput")
    def view_definition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "viewDefinitionInput"))

    @builtins.property
    @jsii.member(jsii_name="viewDependenciesInput")
    def view_dependencies_input(
        self,
    ) -> typing.Optional["DataDatabricksTableTableInfoViewDependencies"]:
        return typing.cast(typing.Optional["DataDatabricksTableTableInfoViewDependencies"], jsii.get(self, "viewDependenciesInput"))

    @builtins.property
    @jsii.member(jsii_name="accessPoint")
    def access_point(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessPoint"))

    @access_point.setter
    def access_point(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6549b72513dde0e699a6385344924fcd8788f311ceaecec89a0622d81a3636cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessPoint", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__0157366097f312ca68dabda844382288aa1f1a501b35be45bed4b0df7e7be045)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "browseOnly", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="catalogName")
    def catalog_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "catalogName"))

    @catalog_name.setter
    def catalog_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aec9c8bf6f2da33bda31ba265151d12234392bf728397bf899c163dcbc6eeda1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "catalogName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1bda6813b9b476f78b9f9dc9221380eef3f02f4b1f4a28f9b2faa1c501ad2cdc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "createdAt"))

    @created_at.setter
    def created_at(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de7a48b94616c8636aa63695b84a56198360461ddbdc4024540b4d5f9b548846)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="createdBy")
    def created_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdBy"))

    @created_by.setter
    def created_by(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84403c02724f58eb512e0c1c925fad710191257a660a0f73ddbd9029289fc6c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdBy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dataAccessConfigurationId")
    def data_access_configuration_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataAccessConfigurationId"))

    @data_access_configuration_id.setter
    def data_access_configuration_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6cb63301c69b0ce09fed583d8c9b31426b4b898bb95745f637fe10ddfca0281e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataAccessConfigurationId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dataSourceFormat")
    def data_source_format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataSourceFormat"))

    @data_source_format.setter
    def data_source_format(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8ba54c836299c70f221452c59302558a6cf68d91df5317e59066e2e2ed26dab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataSourceFormat", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deletedAt")
    def deleted_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "deletedAt"))

    @deleted_at.setter
    def deleted_at(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2293e2d1ab3b7e2dad7af5e5f89e3338b24c271fca02f92152deb841a03422d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deletedAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enablePredictiveOptimization")
    def enable_predictive_optimization(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "enablePredictiveOptimization"))

    @enable_predictive_optimization.setter
    def enable_predictive_optimization(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ba50314750c45cf417af54f43e922c6c6a9194d129499c5aaddddc7533c8197)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enablePredictiveOptimization", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="fullName")
    def full_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fullName"))

    @full_name.setter
    def full_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb412ad93d2975f1acfcb92611dfbf20fd70bc9458bd1f0a829d92f1f5e7db8f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fullName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="metastoreId")
    def metastore_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metastoreId"))

    @metastore_id.setter
    def metastore_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f4e730b6d7c9aff6de82f10c7ad57cc2f0e473583378ffe2a84ec578c4352a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metastoreId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__078452f61bc7211c9beefeade7b6de996071924bcf772412ff5919348dd8d3d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @owner.setter
    def owner(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51d4f03bb09c5c3b050c3a29b9de6b4b9990266a1db258d8398ea9e49a306a90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "owner", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pipelineId")
    def pipeline_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pipelineId"))

    @pipeline_id.setter
    def pipeline_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__adaac1e0ac4d3f46df860f27b7ef0b5b533253f7310360215351eb5803983136)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pipelineId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="properties")
    def properties(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "properties"))

    @properties.setter
    def properties(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc11f519dff6af270acfe130a63eb5136e78638bb6cde0695675b9fd5cc9c772)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "properties", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="schemaName")
    def schema_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schemaName"))

    @schema_name.setter
    def schema_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b92fbd2f1e91e6bb0b99f97ee8a14597854b5127c9afe27508032c518d024b9a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "schemaName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sqlPath")
    def sql_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sqlPath"))

    @sql_path.setter
    def sql_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fbe0c385c4b377f85d5fe0009158d1ff4a36cf23f10f4807c6ca5391de7cf72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sqlPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storageCredentialName")
    def storage_credential_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageCredentialName"))

    @storage_credential_name.setter
    def storage_credential_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a74fca918ce8d19cd50e570090ddcbbfdfb3673b5d08422ceec8e6aff15edcaa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageCredentialName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storageLocation")
    def storage_location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageLocation"))

    @storage_location.setter
    def storage_location(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d9937f7d96737d7d2b5360cfa58d89e08a5e3a5237a6551c28daa43502ea90d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageLocation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tableId")
    def table_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tableId"))

    @table_id.setter
    def table_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df04bfda1d2127d78ed7d805f3c755792fad96cf1afc0a8efa7d3ba848f0d18e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tableId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tableType")
    def table_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tableType"))

    @table_type.setter
    def table_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd3556a987608c9621cf8f9801baf316e34aa35e0d7167d32f3e578b41c8f322)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tableType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "updatedAt"))

    @updated_at.setter
    def updated_at(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74cab1fe84bd8ca7d77ac6f7024deb54abd1e3aa2bc2b5d684f16a3b4460b580)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "updatedAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="updatedBy")
    def updated_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedBy"))

    @updated_by.setter
    def updated_by(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb4d5c5e0ec4557aed127738cddca1a5c8bea820e21c7ac5578344130d95bd25)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "updatedBy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="viewDefinition")
    def view_definition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "viewDefinition"))

    @view_definition.setter
    def view_definition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__246c3f8bf7538d1bdef082f11941005b5ec5efedd89c0e45d7e7b193accfa89c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "viewDefinition", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataDatabricksTableTableInfo]:
        return typing.cast(typing.Optional[DataDatabricksTableTableInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksTableTableInfo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50f8177c283eb8988c1090f9d960c9285b44f1b87f501b060bfb9b59bad4a217)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoRowFilter",
    jsii_struct_bases=[],
    name_mapping={
        "function_name": "functionName",
        "input_column_names": "inputColumnNames",
    },
)
class DataDatabricksTableTableInfoRowFilter:
    def __init__(
        self,
        *,
        function_name: builtins.str,
        input_column_names: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#function_name DataDatabricksTable#function_name}.
        :param input_column_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#input_column_names DataDatabricksTable#input_column_names}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08eb34e37b1818bb07b2085db0a91a3ff163ca1ccfe1593510b5a847b0993a54)
            check_type(argname="argument function_name", value=function_name, expected_type=type_hints["function_name"])
            check_type(argname="argument input_column_names", value=input_column_names, expected_type=type_hints["input_column_names"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "function_name": function_name,
            "input_column_names": input_column_names,
        }

    @builtins.property
    def function_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#function_name DataDatabricksTable#function_name}.'''
        result = self._values.get("function_name")
        assert result is not None, "Required property 'function_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def input_column_names(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#input_column_names DataDatabricksTable#input_column_names}.'''
        result = self._values.get("input_column_names")
        assert result is not None, "Required property 'input_column_names' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksTableTableInfoRowFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksTableTableInfoRowFilterOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoRowFilterOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fb7c685ea7b59fc30a670a62396829845f05ed4e7475263d505421a5e139535c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="functionNameInput")
    def function_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionNameInput"))

    @builtins.property
    @jsii.member(jsii_name="inputColumnNamesInput")
    def input_column_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "inputColumnNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionName"))

    @function_name.setter
    def function_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__422602cabb9d96d7137712bb9a72eb2a74c8d94d372660342dd15c566ac5bcad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "functionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="inputColumnNames")
    def input_column_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "inputColumnNames"))

    @input_column_names.setter
    def input_column_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15f23ba59fd4f9aa517e9fde2b7b6ce3b04eaec8760786a62420a2bb5b08bb08)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inputColumnNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataDatabricksTableTableInfoRowFilter]:
        return typing.cast(typing.Optional[DataDatabricksTableTableInfoRowFilter], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksTableTableInfoRowFilter],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fc01730dfe751b7c83c623fce2f4153c14ecd6314f0fd9445705d67d46409d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoSecurableKindManifest",
    jsii_struct_bases=[],
    name_mapping={
        "assignable_privileges": "assignablePrivileges",
        "capabilities": "capabilities",
        "options": "options",
        "securable_kind": "securableKind",
        "securable_type": "securableType",
    },
)
class DataDatabricksTableTableInfoSecurableKindManifest:
    def __init__(
        self,
        *,
        assignable_privileges: typing.Optional[typing.Sequence[builtins.str]] = None,
        capabilities: typing.Optional[typing.Sequence[builtins.str]] = None,
        options: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksTableTableInfoSecurableKindManifestOptions", typing.Dict[builtins.str, typing.Any]]]]] = None,
        securable_kind: typing.Optional[builtins.str] = None,
        securable_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param assignable_privileges: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#assignable_privileges DataDatabricksTable#assignable_privileges}.
        :param capabilities: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#capabilities DataDatabricksTable#capabilities}.
        :param options: options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#options DataDatabricksTable#options}
        :param securable_kind: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#securable_kind DataDatabricksTable#securable_kind}.
        :param securable_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#securable_type DataDatabricksTable#securable_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc00711557de7593a3c9bffecfea89f1b515a4373919e34d2e0b158af721ccf9)
            check_type(argname="argument assignable_privileges", value=assignable_privileges, expected_type=type_hints["assignable_privileges"])
            check_type(argname="argument capabilities", value=capabilities, expected_type=type_hints["capabilities"])
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
            check_type(argname="argument securable_kind", value=securable_kind, expected_type=type_hints["securable_kind"])
            check_type(argname="argument securable_type", value=securable_type, expected_type=type_hints["securable_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if assignable_privileges is not None:
            self._values["assignable_privileges"] = assignable_privileges
        if capabilities is not None:
            self._values["capabilities"] = capabilities
        if options is not None:
            self._values["options"] = options
        if securable_kind is not None:
            self._values["securable_kind"] = securable_kind
        if securable_type is not None:
            self._values["securable_type"] = securable_type

    @builtins.property
    def assignable_privileges(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#assignable_privileges DataDatabricksTable#assignable_privileges}.'''
        result = self._values.get("assignable_privileges")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def capabilities(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#capabilities DataDatabricksTable#capabilities}.'''
        result = self._values.get("capabilities")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def options(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksTableTableInfoSecurableKindManifestOptions"]]]:
        '''options block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#options DataDatabricksTable#options}
        '''
        result = self._values.get("options")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksTableTableInfoSecurableKindManifestOptions"]]], result)

    @builtins.property
    def securable_kind(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#securable_kind DataDatabricksTable#securable_kind}.'''
        result = self._values.get("securable_kind")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def securable_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#securable_type DataDatabricksTable#securable_type}.'''
        result = self._values.get("securable_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksTableTableInfoSecurableKindManifest(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoSecurableKindManifestOptions",
    jsii_struct_bases=[],
    name_mapping={
        "allowed_values": "allowedValues",
        "default_value": "defaultValue",
        "description": "description",
        "hint": "hint",
        "is_copiable": "isCopiable",
        "is_creatable": "isCreatable",
        "is_hidden": "isHidden",
        "is_loggable": "isLoggable",
        "is_required": "isRequired",
        "is_secret": "isSecret",
        "is_updatable": "isUpdatable",
        "name": "name",
        "oauth_stage": "oauthStage",
        "type": "type",
    },
)
class DataDatabricksTableTableInfoSecurableKindManifestOptions:
    def __init__(
        self,
        *,
        allowed_values: typing.Optional[typing.Sequence[builtins.str]] = None,
        default_value: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        hint: typing.Optional[builtins.str] = None,
        is_copiable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        is_creatable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        is_hidden: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        is_loggable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        is_required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        is_secret: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        is_updatable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        name: typing.Optional[builtins.str] = None,
        oauth_stage: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param allowed_values: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#allowed_values DataDatabricksTable#allowed_values}.
        :param default_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#default_value DataDatabricksTable#default_value}.
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#description DataDatabricksTable#description}.
        :param hint: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#hint DataDatabricksTable#hint}.
        :param is_copiable: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#is_copiable DataDatabricksTable#is_copiable}.
        :param is_creatable: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#is_creatable DataDatabricksTable#is_creatable}.
        :param is_hidden: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#is_hidden DataDatabricksTable#is_hidden}.
        :param is_loggable: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#is_loggable DataDatabricksTable#is_loggable}.
        :param is_required: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#is_required DataDatabricksTable#is_required}.
        :param is_secret: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#is_secret DataDatabricksTable#is_secret}.
        :param is_updatable: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#is_updatable DataDatabricksTable#is_updatable}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#name DataDatabricksTable#name}.
        :param oauth_stage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#oauth_stage DataDatabricksTable#oauth_stage}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#type DataDatabricksTable#type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a8c0997ad652b953c8168a737f6f6277e45ccbcc2704c3bc302cded095d1b06)
            check_type(argname="argument allowed_values", value=allowed_values, expected_type=type_hints["allowed_values"])
            check_type(argname="argument default_value", value=default_value, expected_type=type_hints["default_value"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument hint", value=hint, expected_type=type_hints["hint"])
            check_type(argname="argument is_copiable", value=is_copiable, expected_type=type_hints["is_copiable"])
            check_type(argname="argument is_creatable", value=is_creatable, expected_type=type_hints["is_creatable"])
            check_type(argname="argument is_hidden", value=is_hidden, expected_type=type_hints["is_hidden"])
            check_type(argname="argument is_loggable", value=is_loggable, expected_type=type_hints["is_loggable"])
            check_type(argname="argument is_required", value=is_required, expected_type=type_hints["is_required"])
            check_type(argname="argument is_secret", value=is_secret, expected_type=type_hints["is_secret"])
            check_type(argname="argument is_updatable", value=is_updatable, expected_type=type_hints["is_updatable"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument oauth_stage", value=oauth_stage, expected_type=type_hints["oauth_stage"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if allowed_values is not None:
            self._values["allowed_values"] = allowed_values
        if default_value is not None:
            self._values["default_value"] = default_value
        if description is not None:
            self._values["description"] = description
        if hint is not None:
            self._values["hint"] = hint
        if is_copiable is not None:
            self._values["is_copiable"] = is_copiable
        if is_creatable is not None:
            self._values["is_creatable"] = is_creatable
        if is_hidden is not None:
            self._values["is_hidden"] = is_hidden
        if is_loggable is not None:
            self._values["is_loggable"] = is_loggable
        if is_required is not None:
            self._values["is_required"] = is_required
        if is_secret is not None:
            self._values["is_secret"] = is_secret
        if is_updatable is not None:
            self._values["is_updatable"] = is_updatable
        if name is not None:
            self._values["name"] = name
        if oauth_stage is not None:
            self._values["oauth_stage"] = oauth_stage
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def allowed_values(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#allowed_values DataDatabricksTable#allowed_values}.'''
        result = self._values.get("allowed_values")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def default_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#default_value DataDatabricksTable#default_value}.'''
        result = self._values.get("default_value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#description DataDatabricksTable#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hint(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#hint DataDatabricksTable#hint}.'''
        result = self._values.get("hint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_copiable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#is_copiable DataDatabricksTable#is_copiable}.'''
        result = self._values.get("is_copiable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def is_creatable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#is_creatable DataDatabricksTable#is_creatable}.'''
        result = self._values.get("is_creatable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def is_hidden(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#is_hidden DataDatabricksTable#is_hidden}.'''
        result = self._values.get("is_hidden")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def is_loggable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#is_loggable DataDatabricksTable#is_loggable}.'''
        result = self._values.get("is_loggable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def is_required(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#is_required DataDatabricksTable#is_required}.'''
        result = self._values.get("is_required")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def is_secret(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#is_secret DataDatabricksTable#is_secret}.'''
        result = self._values.get("is_secret")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def is_updatable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#is_updatable DataDatabricksTable#is_updatable}.'''
        result = self._values.get("is_updatable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#name DataDatabricksTable#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oauth_stage(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#oauth_stage DataDatabricksTable#oauth_stage}.'''
        result = self._values.get("oauth_stage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#type DataDatabricksTable#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksTableTableInfoSecurableKindManifestOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksTableTableInfoSecurableKindManifestOptionsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoSecurableKindManifestOptionsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6e1fed7e84f1d9a25a9631df67192fb04f85c53f0a0ea22bfbfb8618c26806dd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksTableTableInfoSecurableKindManifestOptionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18913a49cb6fa28da1be489bc25ac98532429304565f74564adc22ff907bee69)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksTableTableInfoSecurableKindManifestOptionsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__013a4af3b97708e033fb87754432c269ca923788a223255d6ab65b4cb6a83ccb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9ce679b9c10869fb77510cd22dbc97afc1416b62c9a6671e87cab7e3f6219d56)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1c6cba332a045edbe479c6d8003f70c0270f4b6313016c323ac6b304199836d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksTableTableInfoSecurableKindManifestOptions]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksTableTableInfoSecurableKindManifestOptions]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksTableTableInfoSecurableKindManifestOptions]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e77da4b4e3c036e174aaed1959f802b87e11b1fb091fba50847813f9dcce25f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksTableTableInfoSecurableKindManifestOptionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoSecurableKindManifestOptionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1bad7f0b33d9cf62bfa62c0e25e2fb5ad6571dbddf914e5dadfca81d85b0c1a2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAllowedValues")
    def reset_allowed_values(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedValues", []))

    @jsii.member(jsii_name="resetDefaultValue")
    def reset_default_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultValue", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetHint")
    def reset_hint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHint", []))

    @jsii.member(jsii_name="resetIsCopiable")
    def reset_is_copiable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsCopiable", []))

    @jsii.member(jsii_name="resetIsCreatable")
    def reset_is_creatable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsCreatable", []))

    @jsii.member(jsii_name="resetIsHidden")
    def reset_is_hidden(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsHidden", []))

    @jsii.member(jsii_name="resetIsLoggable")
    def reset_is_loggable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsLoggable", []))

    @jsii.member(jsii_name="resetIsRequired")
    def reset_is_required(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsRequired", []))

    @jsii.member(jsii_name="resetIsSecret")
    def reset_is_secret(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsSecret", []))

    @jsii.member(jsii_name="resetIsUpdatable")
    def reset_is_updatable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsUpdatable", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetOauthStage")
    def reset_oauth_stage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOauthStage", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @builtins.property
    @jsii.member(jsii_name="allowedValuesInput")
    def allowed_values_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedValuesInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultValueInput")
    def default_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultValueInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="hintInput")
    def hint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hintInput"))

    @builtins.property
    @jsii.member(jsii_name="isCopiableInput")
    def is_copiable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isCopiableInput"))

    @builtins.property
    @jsii.member(jsii_name="isCreatableInput")
    def is_creatable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isCreatableInput"))

    @builtins.property
    @jsii.member(jsii_name="isHiddenInput")
    def is_hidden_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isHiddenInput"))

    @builtins.property
    @jsii.member(jsii_name="isLoggableInput")
    def is_loggable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isLoggableInput"))

    @builtins.property
    @jsii.member(jsii_name="isRequiredInput")
    def is_required_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isRequiredInput"))

    @builtins.property
    @jsii.member(jsii_name="isSecretInput")
    def is_secret_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isSecretInput"))

    @builtins.property
    @jsii.member(jsii_name="isUpdatableInput")
    def is_updatable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isUpdatableInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="oauthStageInput")
    def oauth_stage_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oauthStageInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedValues")
    def allowed_values(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedValues"))

    @allowed_values.setter
    def allowed_values(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20088996aa5a89d036ab148dfa6fb33e89b84f6bfe575b42ed573a460cb20870)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedValues", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultValue")
    def default_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultValue"))

    @default_value.setter
    def default_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37a9a197b1663e7b76bffc0bfc80431e236a3735a3324f253100aa5465d17931)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0da089b9ab1514892e1314725b68332aaaa0f8dc3529df191ccaa4ae2647269)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hint")
    def hint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hint"))

    @hint.setter
    def hint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78cbdb326521be6c718f228de708c154814fd4a4b0ba95f0dbd06b117f4296cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hint", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isCopiable")
    def is_copiable(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isCopiable"))

    @is_copiable.setter
    def is_copiable(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3c3744106e3db91679b5d55157b33b00a7991f51267f94427ac43b6f31c7c42)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isCopiable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isCreatable")
    def is_creatable(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isCreatable"))

    @is_creatable.setter
    def is_creatable(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afccaf95ade2e28be31b52058e7daef2d5e3e391dc8ecada967050aa9c8576cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isCreatable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isHidden")
    def is_hidden(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isHidden"))

    @is_hidden.setter
    def is_hidden(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5363f1bbb987b6516d9f422177ff8191404022b0b67bdbbab9ac9f6dbdb0863)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isHidden", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isLoggable")
    def is_loggable(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isLoggable"))

    @is_loggable.setter
    def is_loggable(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0ad5f03a07a5d05a8f6f58b4ec6ba01a8bb9270c99ef8e191d2ab71187aa22f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isLoggable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isRequired")
    def is_required(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isRequired"))

    @is_required.setter
    def is_required(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c433b8169b9ca65db4af73ad35080a8aaa0ef0b13cd829953fd3070eca5d9d0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isRequired", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isSecret")
    def is_secret(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isSecret"))

    @is_secret.setter
    def is_secret(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc7423eb0ee5f850323c74bb79587fc15af15cd6f65bb73e28c8831d8ef4d8e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isSecret", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isUpdatable")
    def is_updatable(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isUpdatable"))

    @is_updatable.setter
    def is_updatable(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f1cfbaa757ca25372fa07860abd555607ab6d5e9314f3ca3d1a6d7fa3d6efe9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isUpdatable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64df3bd27f0918cf7db20684215a283302a307deda9776a31db874412a4271ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oauthStage")
    def oauth_stage(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oauthStage"))

    @oauth_stage.setter
    def oauth_stage(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cbc893e533390c83ffa6196b38e25ab5b567919dcc005c698e8cbbd5d24ca2bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oauthStage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb5cdecdafde74ff30ee5e20303548c538e492384070fa5d1ac2708eeb5ed35b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksTableTableInfoSecurableKindManifestOptions]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksTableTableInfoSecurableKindManifestOptions]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksTableTableInfoSecurableKindManifestOptions]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64070fe32657f41765cabe595a79eebed1bff7e7a413ab1ce95195104b792460)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksTableTableInfoSecurableKindManifestOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoSecurableKindManifestOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e2f42b0adf33eb87092336780dbd15475ccd6a3adc2d1a61c7d71fd85cc7877c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putOptions")
    def put_options(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksTableTableInfoSecurableKindManifestOptions, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01024e6a0c85154fdd04b84a0cd9cec78399db4220ba90c690f2e59350f8c1e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putOptions", [value]))

    @jsii.member(jsii_name="resetAssignablePrivileges")
    def reset_assignable_privileges(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAssignablePrivileges", []))

    @jsii.member(jsii_name="resetCapabilities")
    def reset_capabilities(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCapabilities", []))

    @jsii.member(jsii_name="resetOptions")
    def reset_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOptions", []))

    @jsii.member(jsii_name="resetSecurableKind")
    def reset_securable_kind(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurableKind", []))

    @jsii.member(jsii_name="resetSecurableType")
    def reset_securable_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurableType", []))

    @builtins.property
    @jsii.member(jsii_name="options")
    def options(self) -> DataDatabricksTableTableInfoSecurableKindManifestOptionsList:
        return typing.cast(DataDatabricksTableTableInfoSecurableKindManifestOptionsList, jsii.get(self, "options"))

    @builtins.property
    @jsii.member(jsii_name="assignablePrivilegesInput")
    def assignable_privileges_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "assignablePrivilegesInput"))

    @builtins.property
    @jsii.member(jsii_name="capabilitiesInput")
    def capabilities_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "capabilitiesInput"))

    @builtins.property
    @jsii.member(jsii_name="optionsInput")
    def options_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksTableTableInfoSecurableKindManifestOptions]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksTableTableInfoSecurableKindManifestOptions]]], jsii.get(self, "optionsInput"))

    @builtins.property
    @jsii.member(jsii_name="securableKindInput")
    def securable_kind_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "securableKindInput"))

    @builtins.property
    @jsii.member(jsii_name="securableTypeInput")
    def securable_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "securableTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="assignablePrivileges")
    def assignable_privileges(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "assignablePrivileges"))

    @assignable_privileges.setter
    def assignable_privileges(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__980e945d23c1ebf4100485380161166fb09c1b87506c29cd0b6e1c2b69600e09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "assignablePrivileges", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="capabilities")
    def capabilities(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "capabilities"))

    @capabilities.setter
    def capabilities(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6aeb555cb6d14221403989b98c4fff65833034f8a7682e5e70c50254f0be753)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "capabilities", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="securableKind")
    def securable_kind(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "securableKind"))

    @securable_kind.setter
    def securable_kind(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__869611d08d005ca0339ba335d1d8044f51534b13089a188d026ef3158e1d3f38)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "securableKind", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="securableType")
    def securable_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "securableType"))

    @securable_type.setter
    def securable_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__094ae80a248f84c530c61e7a100777a61675e7debdd4746cf3beb5988e8ebbb6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "securableType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksTableTableInfoSecurableKindManifest]:
        return typing.cast(typing.Optional[DataDatabricksTableTableInfoSecurableKindManifest], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksTableTableInfoSecurableKindManifest],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c7e10fee52891a4df339ee543a8ec07f0914a4329ffc55235e7f96a1c707754)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoTableConstraints",
    jsii_struct_bases=[],
    name_mapping={
        "foreign_key_constraint": "foreignKeyConstraint",
        "named_table_constraint": "namedTableConstraint",
        "primary_key_constraint": "primaryKeyConstraint",
    },
)
class DataDatabricksTableTableInfoTableConstraints:
    def __init__(
        self,
        *,
        foreign_key_constraint: typing.Optional[typing.Union["DataDatabricksTableTableInfoTableConstraintsForeignKeyConstraint", typing.Dict[builtins.str, typing.Any]]] = None,
        named_table_constraint: typing.Optional[typing.Union["DataDatabricksTableTableInfoTableConstraintsNamedTableConstraint", typing.Dict[builtins.str, typing.Any]]] = None,
        primary_key_constraint: typing.Optional[typing.Union["DataDatabricksTableTableInfoTableConstraintsPrimaryKeyConstraint", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param foreign_key_constraint: foreign_key_constraint block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#foreign_key_constraint DataDatabricksTable#foreign_key_constraint}
        :param named_table_constraint: named_table_constraint block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#named_table_constraint DataDatabricksTable#named_table_constraint}
        :param primary_key_constraint: primary_key_constraint block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#primary_key_constraint DataDatabricksTable#primary_key_constraint}
        '''
        if isinstance(foreign_key_constraint, dict):
            foreign_key_constraint = DataDatabricksTableTableInfoTableConstraintsForeignKeyConstraint(**foreign_key_constraint)
        if isinstance(named_table_constraint, dict):
            named_table_constraint = DataDatabricksTableTableInfoTableConstraintsNamedTableConstraint(**named_table_constraint)
        if isinstance(primary_key_constraint, dict):
            primary_key_constraint = DataDatabricksTableTableInfoTableConstraintsPrimaryKeyConstraint(**primary_key_constraint)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4b77325ec695169b5edd62915971ea07f33d88e05ac33a9cddbaa7c26da68d1)
            check_type(argname="argument foreign_key_constraint", value=foreign_key_constraint, expected_type=type_hints["foreign_key_constraint"])
            check_type(argname="argument named_table_constraint", value=named_table_constraint, expected_type=type_hints["named_table_constraint"])
            check_type(argname="argument primary_key_constraint", value=primary_key_constraint, expected_type=type_hints["primary_key_constraint"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if foreign_key_constraint is not None:
            self._values["foreign_key_constraint"] = foreign_key_constraint
        if named_table_constraint is not None:
            self._values["named_table_constraint"] = named_table_constraint
        if primary_key_constraint is not None:
            self._values["primary_key_constraint"] = primary_key_constraint

    @builtins.property
    def foreign_key_constraint(
        self,
    ) -> typing.Optional["DataDatabricksTableTableInfoTableConstraintsForeignKeyConstraint"]:
        '''foreign_key_constraint block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#foreign_key_constraint DataDatabricksTable#foreign_key_constraint}
        '''
        result = self._values.get("foreign_key_constraint")
        return typing.cast(typing.Optional["DataDatabricksTableTableInfoTableConstraintsForeignKeyConstraint"], result)

    @builtins.property
    def named_table_constraint(
        self,
    ) -> typing.Optional["DataDatabricksTableTableInfoTableConstraintsNamedTableConstraint"]:
        '''named_table_constraint block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#named_table_constraint DataDatabricksTable#named_table_constraint}
        '''
        result = self._values.get("named_table_constraint")
        return typing.cast(typing.Optional["DataDatabricksTableTableInfoTableConstraintsNamedTableConstraint"], result)

    @builtins.property
    def primary_key_constraint(
        self,
    ) -> typing.Optional["DataDatabricksTableTableInfoTableConstraintsPrimaryKeyConstraint"]:
        '''primary_key_constraint block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#primary_key_constraint DataDatabricksTable#primary_key_constraint}
        '''
        result = self._values.get("primary_key_constraint")
        return typing.cast(typing.Optional["DataDatabricksTableTableInfoTableConstraintsPrimaryKeyConstraint"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksTableTableInfoTableConstraints(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoTableConstraintsForeignKeyConstraint",
    jsii_struct_bases=[],
    name_mapping={
        "child_columns": "childColumns",
        "name": "name",
        "parent_columns": "parentColumns",
        "parent_table": "parentTable",
        "rely": "rely",
    },
)
class DataDatabricksTableTableInfoTableConstraintsForeignKeyConstraint:
    def __init__(
        self,
        *,
        child_columns: typing.Sequence[builtins.str],
        name: builtins.str,
        parent_columns: typing.Sequence[builtins.str],
        parent_table: builtins.str,
        rely: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param child_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#child_columns DataDatabricksTable#child_columns}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#name DataDatabricksTable#name}.
        :param parent_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#parent_columns DataDatabricksTable#parent_columns}.
        :param parent_table: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#parent_table DataDatabricksTable#parent_table}.
        :param rely: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#rely DataDatabricksTable#rely}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a8e6a508893a90c45d8fd1730542fc306236bec83459913b9c30e40660653d8)
            check_type(argname="argument child_columns", value=child_columns, expected_type=type_hints["child_columns"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument parent_columns", value=parent_columns, expected_type=type_hints["parent_columns"])
            check_type(argname="argument parent_table", value=parent_table, expected_type=type_hints["parent_table"])
            check_type(argname="argument rely", value=rely, expected_type=type_hints["rely"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "child_columns": child_columns,
            "name": name,
            "parent_columns": parent_columns,
            "parent_table": parent_table,
        }
        if rely is not None:
            self._values["rely"] = rely

    @builtins.property
    def child_columns(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#child_columns DataDatabricksTable#child_columns}.'''
        result = self._values.get("child_columns")
        assert result is not None, "Required property 'child_columns' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#name DataDatabricksTable#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parent_columns(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#parent_columns DataDatabricksTable#parent_columns}.'''
        result = self._values.get("parent_columns")
        assert result is not None, "Required property 'parent_columns' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def parent_table(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#parent_table DataDatabricksTable#parent_table}.'''
        result = self._values.get("parent_table")
        assert result is not None, "Required property 'parent_table' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rely(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#rely DataDatabricksTable#rely}.'''
        result = self._values.get("rely")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksTableTableInfoTableConstraintsForeignKeyConstraint(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksTableTableInfoTableConstraintsForeignKeyConstraintOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoTableConstraintsForeignKeyConstraintOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b36c8d84b3560bffcf24afda080666db7a963534cb9ce32f91c5bd18a2b09d13)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetRely")
    def reset_rely(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRely", []))

    @builtins.property
    @jsii.member(jsii_name="childColumnsInput")
    def child_columns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "childColumnsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="parentColumnsInput")
    def parent_columns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "parentColumnsInput"))

    @builtins.property
    @jsii.member(jsii_name="parentTableInput")
    def parent_table_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parentTableInput"))

    @builtins.property
    @jsii.member(jsii_name="relyInput")
    def rely_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "relyInput"))

    @builtins.property
    @jsii.member(jsii_name="childColumns")
    def child_columns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "childColumns"))

    @child_columns.setter
    def child_columns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66b2db471bf5694dc6f6bee73f2e877080bae607099160c978ac4d307e873adc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "childColumns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51667a39e84b9d606d56b2aa842bd6662853d4d80090432bced3593da1443a23)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parentColumns")
    def parent_columns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "parentColumns"))

    @parent_columns.setter
    def parent_columns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4756aeebd3137e5946875d5c7e7b392699608c0188dac3b95a07c9b1d5c52ad8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parentColumns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parentTable")
    def parent_table(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parentTable"))

    @parent_table.setter
    def parent_table(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5c42fa00046f49af55e38a54b4b4a82086fe16058f4654d2f52790c4d0ff3cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parentTable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rely")
    def rely(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "rely"))

    @rely.setter
    def rely(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9aad7e24c244b50d7977f96685120bdf26ff727312ed87b1a8a8aeb045551d2c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rely", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksTableTableInfoTableConstraintsForeignKeyConstraint]:
        return typing.cast(typing.Optional[DataDatabricksTableTableInfoTableConstraintsForeignKeyConstraint], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksTableTableInfoTableConstraintsForeignKeyConstraint],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0661c07cbc90e0c61d373a26d0094213146baafdaf5b5d79bee03b59c66c8b59)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksTableTableInfoTableConstraintsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoTableConstraintsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e4209b14a293e6cd799981d6024aab0995728f51a43dd81888bd442eca525f9f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksTableTableInfoTableConstraintsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b79b03c2e6b42cbc6860183723256b466854b8fa7ade5acff0d6000ebd2a6cf9)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksTableTableInfoTableConstraintsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f63bb041f940325b499ebd71081c3dbdda182508e306c488e3373231bfdc1e8d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ec08e9e92b0f27dae9935176bd24f16ceb81245e7e66aac238baf2173da00b4b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b3aa6377e8f73479df01757905411580cabaf986df6204557d1440dd0609596e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksTableTableInfoTableConstraints]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksTableTableInfoTableConstraints]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksTableTableInfoTableConstraints]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3560698466bf94174ee89e7775125cd4015721c7a6d80699d3841125f4fe8b63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoTableConstraintsNamedTableConstraint",
    jsii_struct_bases=[],
    name_mapping={"name": "name"},
)
class DataDatabricksTableTableInfoTableConstraintsNamedTableConstraint:
    def __init__(self, *, name: builtins.str) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#name DataDatabricksTable#name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e589f43d813ea14b7469eec1b1db7f931d71c3cecd842fe9f821ddd051da184)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#name DataDatabricksTable#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksTableTableInfoTableConstraintsNamedTableConstraint(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksTableTableInfoTableConstraintsNamedTableConstraintOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoTableConstraintsNamedTableConstraintOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__aa530eb4f98b672d0fd1eaafc0154eae72faed5a7c53503d2b11087e47237b79)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5b0a7f616dcf8187f292e4b9c9f53fdcbbcba452fde279705caf1f51df11350a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksTableTableInfoTableConstraintsNamedTableConstraint]:
        return typing.cast(typing.Optional[DataDatabricksTableTableInfoTableConstraintsNamedTableConstraint], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksTableTableInfoTableConstraintsNamedTableConstraint],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92066c1d425d989611bd2f31cffa1c28e753d6139ddf199d0c44a5b08c9da480)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksTableTableInfoTableConstraintsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoTableConstraintsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8c5a70d9cebc86f3917232d042f6237cb58123c58d025e93f5ddd52a3bd3c30e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putForeignKeyConstraint")
    def put_foreign_key_constraint(
        self,
        *,
        child_columns: typing.Sequence[builtins.str],
        name: builtins.str,
        parent_columns: typing.Sequence[builtins.str],
        parent_table: builtins.str,
        rely: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param child_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#child_columns DataDatabricksTable#child_columns}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#name DataDatabricksTable#name}.
        :param parent_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#parent_columns DataDatabricksTable#parent_columns}.
        :param parent_table: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#parent_table DataDatabricksTable#parent_table}.
        :param rely: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#rely DataDatabricksTable#rely}.
        '''
        value = DataDatabricksTableTableInfoTableConstraintsForeignKeyConstraint(
            child_columns=child_columns,
            name=name,
            parent_columns=parent_columns,
            parent_table=parent_table,
            rely=rely,
        )

        return typing.cast(None, jsii.invoke(self, "putForeignKeyConstraint", [value]))

    @jsii.member(jsii_name="putNamedTableConstraint")
    def put_named_table_constraint(self, *, name: builtins.str) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#name DataDatabricksTable#name}.
        '''
        value = DataDatabricksTableTableInfoTableConstraintsNamedTableConstraint(
            name=name
        )

        return typing.cast(None, jsii.invoke(self, "putNamedTableConstraint", [value]))

    @jsii.member(jsii_name="putPrimaryKeyConstraint")
    def put_primary_key_constraint(
        self,
        *,
        child_columns: typing.Sequence[builtins.str],
        name: builtins.str,
        rely: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        timeseries_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param child_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#child_columns DataDatabricksTable#child_columns}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#name DataDatabricksTable#name}.
        :param rely: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#rely DataDatabricksTable#rely}.
        :param timeseries_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#timeseries_columns DataDatabricksTable#timeseries_columns}.
        '''
        value = DataDatabricksTableTableInfoTableConstraintsPrimaryKeyConstraint(
            child_columns=child_columns,
            name=name,
            rely=rely,
            timeseries_columns=timeseries_columns,
        )

        return typing.cast(None, jsii.invoke(self, "putPrimaryKeyConstraint", [value]))

    @jsii.member(jsii_name="resetForeignKeyConstraint")
    def reset_foreign_key_constraint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForeignKeyConstraint", []))

    @jsii.member(jsii_name="resetNamedTableConstraint")
    def reset_named_table_constraint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamedTableConstraint", []))

    @jsii.member(jsii_name="resetPrimaryKeyConstraint")
    def reset_primary_key_constraint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrimaryKeyConstraint", []))

    @builtins.property
    @jsii.member(jsii_name="foreignKeyConstraint")
    def foreign_key_constraint(
        self,
    ) -> DataDatabricksTableTableInfoTableConstraintsForeignKeyConstraintOutputReference:
        return typing.cast(DataDatabricksTableTableInfoTableConstraintsForeignKeyConstraintOutputReference, jsii.get(self, "foreignKeyConstraint"))

    @builtins.property
    @jsii.member(jsii_name="namedTableConstraint")
    def named_table_constraint(
        self,
    ) -> DataDatabricksTableTableInfoTableConstraintsNamedTableConstraintOutputReference:
        return typing.cast(DataDatabricksTableTableInfoTableConstraintsNamedTableConstraintOutputReference, jsii.get(self, "namedTableConstraint"))

    @builtins.property
    @jsii.member(jsii_name="primaryKeyConstraint")
    def primary_key_constraint(
        self,
    ) -> "DataDatabricksTableTableInfoTableConstraintsPrimaryKeyConstraintOutputReference":
        return typing.cast("DataDatabricksTableTableInfoTableConstraintsPrimaryKeyConstraintOutputReference", jsii.get(self, "primaryKeyConstraint"))

    @builtins.property
    @jsii.member(jsii_name="foreignKeyConstraintInput")
    def foreign_key_constraint_input(
        self,
    ) -> typing.Optional[DataDatabricksTableTableInfoTableConstraintsForeignKeyConstraint]:
        return typing.cast(typing.Optional[DataDatabricksTableTableInfoTableConstraintsForeignKeyConstraint], jsii.get(self, "foreignKeyConstraintInput"))

    @builtins.property
    @jsii.member(jsii_name="namedTableConstraintInput")
    def named_table_constraint_input(
        self,
    ) -> typing.Optional[DataDatabricksTableTableInfoTableConstraintsNamedTableConstraint]:
        return typing.cast(typing.Optional[DataDatabricksTableTableInfoTableConstraintsNamedTableConstraint], jsii.get(self, "namedTableConstraintInput"))

    @builtins.property
    @jsii.member(jsii_name="primaryKeyConstraintInput")
    def primary_key_constraint_input(
        self,
    ) -> typing.Optional["DataDatabricksTableTableInfoTableConstraintsPrimaryKeyConstraint"]:
        return typing.cast(typing.Optional["DataDatabricksTableTableInfoTableConstraintsPrimaryKeyConstraint"], jsii.get(self, "primaryKeyConstraintInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksTableTableInfoTableConstraints]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksTableTableInfoTableConstraints]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksTableTableInfoTableConstraints]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d27130809c870da1dda1cac79e44d6c97599ba185973a5f569d60b1ac00bc29f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoTableConstraintsPrimaryKeyConstraint",
    jsii_struct_bases=[],
    name_mapping={
        "child_columns": "childColumns",
        "name": "name",
        "rely": "rely",
        "timeseries_columns": "timeseriesColumns",
    },
)
class DataDatabricksTableTableInfoTableConstraintsPrimaryKeyConstraint:
    def __init__(
        self,
        *,
        child_columns: typing.Sequence[builtins.str],
        name: builtins.str,
        rely: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        timeseries_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param child_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#child_columns DataDatabricksTable#child_columns}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#name DataDatabricksTable#name}.
        :param rely: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#rely DataDatabricksTable#rely}.
        :param timeseries_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#timeseries_columns DataDatabricksTable#timeseries_columns}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48b3e0e1b359ba7651372e753bee520750202c65b67f9f776fc12de31402d237)
            check_type(argname="argument child_columns", value=child_columns, expected_type=type_hints["child_columns"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument rely", value=rely, expected_type=type_hints["rely"])
            check_type(argname="argument timeseries_columns", value=timeseries_columns, expected_type=type_hints["timeseries_columns"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "child_columns": child_columns,
            "name": name,
        }
        if rely is not None:
            self._values["rely"] = rely
        if timeseries_columns is not None:
            self._values["timeseries_columns"] = timeseries_columns

    @builtins.property
    def child_columns(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#child_columns DataDatabricksTable#child_columns}.'''
        result = self._values.get("child_columns")
        assert result is not None, "Required property 'child_columns' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#name DataDatabricksTable#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rely(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#rely DataDatabricksTable#rely}.'''
        result = self._values.get("rely")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def timeseries_columns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#timeseries_columns DataDatabricksTable#timeseries_columns}.'''
        result = self._values.get("timeseries_columns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksTableTableInfoTableConstraintsPrimaryKeyConstraint(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksTableTableInfoTableConstraintsPrimaryKeyConstraintOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoTableConstraintsPrimaryKeyConstraintOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a9c573f4a6f99ce1127efad7814bcca9c7dab55da4e9bc3c1a1ba299bbbc2b15)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetRely")
    def reset_rely(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRely", []))

    @jsii.member(jsii_name="resetTimeseriesColumns")
    def reset_timeseries_columns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeseriesColumns", []))

    @builtins.property
    @jsii.member(jsii_name="childColumnsInput")
    def child_columns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "childColumnsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="relyInput")
    def rely_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "relyInput"))

    @builtins.property
    @jsii.member(jsii_name="timeseriesColumnsInput")
    def timeseries_columns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "timeseriesColumnsInput"))

    @builtins.property
    @jsii.member(jsii_name="childColumns")
    def child_columns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "childColumns"))

    @child_columns.setter
    def child_columns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6578187eb0fa2fb01bb9e2d82db81e3e0c586bf0cd08362ce7f55aa11746481)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "childColumns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56df88d04b11646489828ffccc209b2bcff73ca1f612d97c4fe7a92074cfcbcb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rely")
    def rely(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "rely"))

    @rely.setter
    def rely(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca1cd7429b199350cb9690863b795a3c2e21d11aefb6f393b25748d9628fb97e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rely", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeseriesColumns")
    def timeseries_columns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "timeseriesColumns"))

    @timeseries_columns.setter
    def timeseries_columns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b24d7c2b18751092ec5e6078d5dce597443678f74b1c67f5d874345d24bc22a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeseriesColumns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksTableTableInfoTableConstraintsPrimaryKeyConstraint]:
        return typing.cast(typing.Optional[DataDatabricksTableTableInfoTableConstraintsPrimaryKeyConstraint], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksTableTableInfoTableConstraintsPrimaryKeyConstraint],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e82cd0ddc24f9d0272cdffac0668f70a8d2504f28dac54f859ccf2ddb6ad4fba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoViewDependencies",
    jsii_struct_bases=[],
    name_mapping={"dependencies": "dependencies"},
)
class DataDatabricksTableTableInfoViewDependencies:
    def __init__(
        self,
        *,
        dependencies: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksTableTableInfoViewDependenciesDependencies", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param dependencies: dependencies block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#dependencies DataDatabricksTable#dependencies}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2fd3887adbe9bf747d9386579c61002e3d65a751cf41e56ff3f730ec3f0c029)
            check_type(argname="argument dependencies", value=dependencies, expected_type=type_hints["dependencies"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dependencies is not None:
            self._values["dependencies"] = dependencies

    @builtins.property
    def dependencies(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksTableTableInfoViewDependenciesDependencies"]]]:
        '''dependencies block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#dependencies DataDatabricksTable#dependencies}
        '''
        result = self._values.get("dependencies")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksTableTableInfoViewDependenciesDependencies"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksTableTableInfoViewDependencies(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoViewDependenciesDependencies",
    jsii_struct_bases=[],
    name_mapping={
        "connection": "connection",
        "credential": "credential",
        "function": "function",
        "table": "table",
    },
)
class DataDatabricksTableTableInfoViewDependenciesDependencies:
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union["DataDatabricksTableTableInfoViewDependenciesDependenciesConnection", typing.Dict[builtins.str, typing.Any]]] = None,
        credential: typing.Optional[typing.Union["DataDatabricksTableTableInfoViewDependenciesDependenciesCredential", typing.Dict[builtins.str, typing.Any]]] = None,
        function: typing.Optional[typing.Union["DataDatabricksTableTableInfoViewDependenciesDependenciesFunction", typing.Dict[builtins.str, typing.Any]]] = None,
        table: typing.Optional[typing.Union["DataDatabricksTableTableInfoViewDependenciesDependenciesTable", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: connection block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#connection DataDatabricksTable#connection}
        :param credential: credential block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#credential DataDatabricksTable#credential}
        :param function: function block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#function DataDatabricksTable#function}
        :param table: table block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#table DataDatabricksTable#table}
        '''
        if isinstance(connection, dict):
            connection = DataDatabricksTableTableInfoViewDependenciesDependenciesConnection(**connection)
        if isinstance(credential, dict):
            credential = DataDatabricksTableTableInfoViewDependenciesDependenciesCredential(**credential)
        if isinstance(function, dict):
            function = DataDatabricksTableTableInfoViewDependenciesDependenciesFunction(**function)
        if isinstance(table, dict):
            table = DataDatabricksTableTableInfoViewDependenciesDependenciesTable(**table)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cce868b624e5b5a5d30d9ec95598e1e10868fd072654deb8c3d879309cea011)
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
    ) -> typing.Optional["DataDatabricksTableTableInfoViewDependenciesDependenciesConnection"]:
        '''connection block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#connection DataDatabricksTable#connection}
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional["DataDatabricksTableTableInfoViewDependenciesDependenciesConnection"], result)

    @builtins.property
    def credential(
        self,
    ) -> typing.Optional["DataDatabricksTableTableInfoViewDependenciesDependenciesCredential"]:
        '''credential block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#credential DataDatabricksTable#credential}
        '''
        result = self._values.get("credential")
        return typing.cast(typing.Optional["DataDatabricksTableTableInfoViewDependenciesDependenciesCredential"], result)

    @builtins.property
    def function(
        self,
    ) -> typing.Optional["DataDatabricksTableTableInfoViewDependenciesDependenciesFunction"]:
        '''function block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#function DataDatabricksTable#function}
        '''
        result = self._values.get("function")
        return typing.cast(typing.Optional["DataDatabricksTableTableInfoViewDependenciesDependenciesFunction"], result)

    @builtins.property
    def table(
        self,
    ) -> typing.Optional["DataDatabricksTableTableInfoViewDependenciesDependenciesTable"]:
        '''table block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#table DataDatabricksTable#table}
        '''
        result = self._values.get("table")
        return typing.cast(typing.Optional["DataDatabricksTableTableInfoViewDependenciesDependenciesTable"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksTableTableInfoViewDependenciesDependencies(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoViewDependenciesDependenciesConnection",
    jsii_struct_bases=[],
    name_mapping={"connection_name": "connectionName"},
)
class DataDatabricksTableTableInfoViewDependenciesDependenciesConnection:
    def __init__(
        self,
        *,
        connection_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#connection_name DataDatabricksTable#connection_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44694cdc34cfb46c5d55ee806c5d702a1828d92f652f5284833209e408fabd24)
            check_type(argname="argument connection_name", value=connection_name, expected_type=type_hints["connection_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if connection_name is not None:
            self._values["connection_name"] = connection_name

    @builtins.property
    def connection_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#connection_name DataDatabricksTable#connection_name}.'''
        result = self._values.get("connection_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksTableTableInfoViewDependenciesDependenciesConnection(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksTableTableInfoViewDependenciesDependenciesConnectionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoViewDependenciesDependenciesConnectionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d11eb57942a8302e196f0b49d682338f587a6d25202a794b03a40612d81c4da1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1ba1299a592fda4904d87528d52a4529bfb2ced1c9430c2d1ae2b69f349ed3b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksTableTableInfoViewDependenciesDependenciesConnection]:
        return typing.cast(typing.Optional[DataDatabricksTableTableInfoViewDependenciesDependenciesConnection], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksTableTableInfoViewDependenciesDependenciesConnection],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a49921e3d5fa8ad689bc64c36ea5dc94118dbc951eb25f79e298a55ed5a041a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoViewDependenciesDependenciesCredential",
    jsii_struct_bases=[],
    name_mapping={"credential_name": "credentialName"},
)
class DataDatabricksTableTableInfoViewDependenciesDependenciesCredential:
    def __init__(
        self,
        *,
        credential_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param credential_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#credential_name DataDatabricksTable#credential_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c19308480a5b68a2e72f6873d69e443a572d1a62ceab4e681ba24c65ffe8bfd3)
            check_type(argname="argument credential_name", value=credential_name, expected_type=type_hints["credential_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if credential_name is not None:
            self._values["credential_name"] = credential_name

    @builtins.property
    def credential_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#credential_name DataDatabricksTable#credential_name}.'''
        result = self._values.get("credential_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksTableTableInfoViewDependenciesDependenciesCredential(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksTableTableInfoViewDependenciesDependenciesCredentialOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoViewDependenciesDependenciesCredentialOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9900f14a1fb99b6b99419bc5cd88b2ed7da8e08821e139a98ab0b39909869f4a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5b7aa85c23f1e46968241e161fb8915b2a3d35767a3269237159f5c46020d782)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "credentialName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksTableTableInfoViewDependenciesDependenciesCredential]:
        return typing.cast(typing.Optional[DataDatabricksTableTableInfoViewDependenciesDependenciesCredential], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksTableTableInfoViewDependenciesDependenciesCredential],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4145d1e02d2691c8697cf000af601138c8166f4375eaf6d9a8ee957a1acb889)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoViewDependenciesDependenciesFunction",
    jsii_struct_bases=[],
    name_mapping={"function_full_name": "functionFullName"},
)
class DataDatabricksTableTableInfoViewDependenciesDependenciesFunction:
    def __init__(self, *, function_full_name: builtins.str) -> None:
        '''
        :param function_full_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#function_full_name DataDatabricksTable#function_full_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2682171d2da687bd8d536f338bcba376cdd8451059af8fe909cd5cbc35795ebc)
            check_type(argname="argument function_full_name", value=function_full_name, expected_type=type_hints["function_full_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "function_full_name": function_full_name,
        }

    @builtins.property
    def function_full_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#function_full_name DataDatabricksTable#function_full_name}.'''
        result = self._values.get("function_full_name")
        assert result is not None, "Required property 'function_full_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksTableTableInfoViewDependenciesDependenciesFunction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksTableTableInfoViewDependenciesDependenciesFunctionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoViewDependenciesDependenciesFunctionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e936f4c092af7d9fa5b17fc361012493de5cb3c3fa9da5a6e7024931304e4ab1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a8057f11912c1245a66eefe7c62b5e1dffe7adb930221750aadf07f29a778324)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "functionFullName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksTableTableInfoViewDependenciesDependenciesFunction]:
        return typing.cast(typing.Optional[DataDatabricksTableTableInfoViewDependenciesDependenciesFunction], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksTableTableInfoViewDependenciesDependenciesFunction],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b38b055fd5c2b4684035fd2da6d92e2d6183ea127f77b0181482c9c143062ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksTableTableInfoViewDependenciesDependenciesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoViewDependenciesDependenciesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1fecdf80b23d48e508f0787920442a838a65c25e7c0099d81ee41c77576fdb42)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksTableTableInfoViewDependenciesDependenciesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a624d54f5632321d4220ac41bdd90a662caa6ca44b6792abc6162c37ebbaafd8)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksTableTableInfoViewDependenciesDependenciesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7337f0f7a91b7e8148950d94f20c862a8a10c3f446b6092252a846a7002bab43)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cd615ebad8eccb0865e920bc7f6c804da4389e1cfc106706a73adec65191228d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__60e79bce4e12abc22a721232cad085cbb2315b3abfdbb774e3e5697359d45f3f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksTableTableInfoViewDependenciesDependencies]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksTableTableInfoViewDependenciesDependencies]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksTableTableInfoViewDependenciesDependencies]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5186418e5b1952c8a9befc7fb3f3b3fd35fe320f28284d964f8646d80864aea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksTableTableInfoViewDependenciesDependenciesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoViewDependenciesDependenciesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cc5d240fa77acddbbe6e425cc8c07fcb3dc9bdff53963e5bb76a83a854040e29)
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
        :param connection_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#connection_name DataDatabricksTable#connection_name}.
        '''
        value = DataDatabricksTableTableInfoViewDependenciesDependenciesConnection(
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
        :param credential_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#credential_name DataDatabricksTable#credential_name}.
        '''
        value = DataDatabricksTableTableInfoViewDependenciesDependenciesCredential(
            credential_name=credential_name
        )

        return typing.cast(None, jsii.invoke(self, "putCredential", [value]))

    @jsii.member(jsii_name="putFunction")
    def put_function(self, *, function_full_name: builtins.str) -> None:
        '''
        :param function_full_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#function_full_name DataDatabricksTable#function_full_name}.
        '''
        value = DataDatabricksTableTableInfoViewDependenciesDependenciesFunction(
            function_full_name=function_full_name
        )

        return typing.cast(None, jsii.invoke(self, "putFunction", [value]))

    @jsii.member(jsii_name="putTable")
    def put_table(self, *, table_full_name: builtins.str) -> None:
        '''
        :param table_full_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#table_full_name DataDatabricksTable#table_full_name}.
        '''
        value = DataDatabricksTableTableInfoViewDependenciesDependenciesTable(
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
    ) -> DataDatabricksTableTableInfoViewDependenciesDependenciesConnectionOutputReference:
        return typing.cast(DataDatabricksTableTableInfoViewDependenciesDependenciesConnectionOutputReference, jsii.get(self, "connection"))

    @builtins.property
    @jsii.member(jsii_name="credential")
    def credential(
        self,
    ) -> DataDatabricksTableTableInfoViewDependenciesDependenciesCredentialOutputReference:
        return typing.cast(DataDatabricksTableTableInfoViewDependenciesDependenciesCredentialOutputReference, jsii.get(self, "credential"))

    @builtins.property
    @jsii.member(jsii_name="function")
    def function(
        self,
    ) -> DataDatabricksTableTableInfoViewDependenciesDependenciesFunctionOutputReference:
        return typing.cast(DataDatabricksTableTableInfoViewDependenciesDependenciesFunctionOutputReference, jsii.get(self, "function"))

    @builtins.property
    @jsii.member(jsii_name="table")
    def table(
        self,
    ) -> "DataDatabricksTableTableInfoViewDependenciesDependenciesTableOutputReference":
        return typing.cast("DataDatabricksTableTableInfoViewDependenciesDependenciesTableOutputReference", jsii.get(self, "table"))

    @builtins.property
    @jsii.member(jsii_name="connectionInput")
    def connection_input(
        self,
    ) -> typing.Optional[DataDatabricksTableTableInfoViewDependenciesDependenciesConnection]:
        return typing.cast(typing.Optional[DataDatabricksTableTableInfoViewDependenciesDependenciesConnection], jsii.get(self, "connectionInput"))

    @builtins.property
    @jsii.member(jsii_name="credentialInput")
    def credential_input(
        self,
    ) -> typing.Optional[DataDatabricksTableTableInfoViewDependenciesDependenciesCredential]:
        return typing.cast(typing.Optional[DataDatabricksTableTableInfoViewDependenciesDependenciesCredential], jsii.get(self, "credentialInput"))

    @builtins.property
    @jsii.member(jsii_name="functionInput")
    def function_input(
        self,
    ) -> typing.Optional[DataDatabricksTableTableInfoViewDependenciesDependenciesFunction]:
        return typing.cast(typing.Optional[DataDatabricksTableTableInfoViewDependenciesDependenciesFunction], jsii.get(self, "functionInput"))

    @builtins.property
    @jsii.member(jsii_name="tableInput")
    def table_input(
        self,
    ) -> typing.Optional["DataDatabricksTableTableInfoViewDependenciesDependenciesTable"]:
        return typing.cast(typing.Optional["DataDatabricksTableTableInfoViewDependenciesDependenciesTable"], jsii.get(self, "tableInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksTableTableInfoViewDependenciesDependencies]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksTableTableInfoViewDependenciesDependencies]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksTableTableInfoViewDependenciesDependencies]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebd399e6a0bbd540a38c75461fd2895230e45789d4837433cf37af8339d7bb9d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoViewDependenciesDependenciesTable",
    jsii_struct_bases=[],
    name_mapping={"table_full_name": "tableFullName"},
)
class DataDatabricksTableTableInfoViewDependenciesDependenciesTable:
    def __init__(self, *, table_full_name: builtins.str) -> None:
        '''
        :param table_full_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#table_full_name DataDatabricksTable#table_full_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebb2dae672aaa98c37cc02d0bba18e1a5ee5b76aad22efc50030860da0312e7e)
            check_type(argname="argument table_full_name", value=table_full_name, expected_type=type_hints["table_full_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "table_full_name": table_full_name,
        }

    @builtins.property
    def table_full_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/table#table_full_name DataDatabricksTable#table_full_name}.'''
        result = self._values.get("table_full_name")
        assert result is not None, "Required property 'table_full_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksTableTableInfoViewDependenciesDependenciesTable(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksTableTableInfoViewDependenciesDependenciesTableOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoViewDependenciesDependenciesTableOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__55ab997492bcb55a8ab98f8af1c0c0935c002c379931f33cd5136474e88c9a6a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__459681f89374929d2e3ee40f13c62c5921712659eeceafb576c6340b46c816f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tableFullName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksTableTableInfoViewDependenciesDependenciesTable]:
        return typing.cast(typing.Optional[DataDatabricksTableTableInfoViewDependenciesDependenciesTable], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksTableTableInfoViewDependenciesDependenciesTable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__498bd55828df79f10f138bb5cf0f8df6105a2083d6aa079f5c9152e9ad222330)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksTableTableInfoViewDependenciesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksTable.DataDatabricksTableTableInfoViewDependenciesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__394714fdf28588e8d0415d17e3e2c8d3e921bef36d2890269652a4c240cbd422)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putDependencies")
    def put_dependencies(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksTableTableInfoViewDependenciesDependencies, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08c21e9575fd9c3fee2cc1dee2aaa0a9a93acb8eebeee5d27226075075a998be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDependencies", [value]))

    @jsii.member(jsii_name="resetDependencies")
    def reset_dependencies(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDependencies", []))

    @builtins.property
    @jsii.member(jsii_name="dependencies")
    def dependencies(
        self,
    ) -> DataDatabricksTableTableInfoViewDependenciesDependenciesList:
        return typing.cast(DataDatabricksTableTableInfoViewDependenciesDependenciesList, jsii.get(self, "dependencies"))

    @builtins.property
    @jsii.member(jsii_name="dependenciesInput")
    def dependencies_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksTableTableInfoViewDependenciesDependencies]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksTableTableInfoViewDependenciesDependencies]]], jsii.get(self, "dependenciesInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksTableTableInfoViewDependencies]:
        return typing.cast(typing.Optional[DataDatabricksTableTableInfoViewDependencies], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksTableTableInfoViewDependencies],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eebdff3e00d58bbf49817405b262997806167808fa1cecf194439bddfb7ae16c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataDatabricksTable",
    "DataDatabricksTableConfig",
    "DataDatabricksTableTableInfo",
    "DataDatabricksTableTableInfoColumns",
    "DataDatabricksTableTableInfoColumnsList",
    "DataDatabricksTableTableInfoColumnsMask",
    "DataDatabricksTableTableInfoColumnsMaskOutputReference",
    "DataDatabricksTableTableInfoColumnsOutputReference",
    "DataDatabricksTableTableInfoDeltaRuntimePropertiesKvpairs",
    "DataDatabricksTableTableInfoDeltaRuntimePropertiesKvpairsOutputReference",
    "DataDatabricksTableTableInfoEffectivePredictiveOptimizationFlag",
    "DataDatabricksTableTableInfoEffectivePredictiveOptimizationFlagOutputReference",
    "DataDatabricksTableTableInfoEncryptionDetails",
    "DataDatabricksTableTableInfoEncryptionDetailsOutputReference",
    "DataDatabricksTableTableInfoEncryptionDetailsSseEncryptionDetails",
    "DataDatabricksTableTableInfoEncryptionDetailsSseEncryptionDetailsOutputReference",
    "DataDatabricksTableTableInfoOutputReference",
    "DataDatabricksTableTableInfoRowFilter",
    "DataDatabricksTableTableInfoRowFilterOutputReference",
    "DataDatabricksTableTableInfoSecurableKindManifest",
    "DataDatabricksTableTableInfoSecurableKindManifestOptions",
    "DataDatabricksTableTableInfoSecurableKindManifestOptionsList",
    "DataDatabricksTableTableInfoSecurableKindManifestOptionsOutputReference",
    "DataDatabricksTableTableInfoSecurableKindManifestOutputReference",
    "DataDatabricksTableTableInfoTableConstraints",
    "DataDatabricksTableTableInfoTableConstraintsForeignKeyConstraint",
    "DataDatabricksTableTableInfoTableConstraintsForeignKeyConstraintOutputReference",
    "DataDatabricksTableTableInfoTableConstraintsList",
    "DataDatabricksTableTableInfoTableConstraintsNamedTableConstraint",
    "DataDatabricksTableTableInfoTableConstraintsNamedTableConstraintOutputReference",
    "DataDatabricksTableTableInfoTableConstraintsOutputReference",
    "DataDatabricksTableTableInfoTableConstraintsPrimaryKeyConstraint",
    "DataDatabricksTableTableInfoTableConstraintsPrimaryKeyConstraintOutputReference",
    "DataDatabricksTableTableInfoViewDependencies",
    "DataDatabricksTableTableInfoViewDependenciesDependencies",
    "DataDatabricksTableTableInfoViewDependenciesDependenciesConnection",
    "DataDatabricksTableTableInfoViewDependenciesDependenciesConnectionOutputReference",
    "DataDatabricksTableTableInfoViewDependenciesDependenciesCredential",
    "DataDatabricksTableTableInfoViewDependenciesDependenciesCredentialOutputReference",
    "DataDatabricksTableTableInfoViewDependenciesDependenciesFunction",
    "DataDatabricksTableTableInfoViewDependenciesDependenciesFunctionOutputReference",
    "DataDatabricksTableTableInfoViewDependenciesDependenciesList",
    "DataDatabricksTableTableInfoViewDependenciesDependenciesOutputReference",
    "DataDatabricksTableTableInfoViewDependenciesDependenciesTable",
    "DataDatabricksTableTableInfoViewDependenciesDependenciesTableOutputReference",
    "DataDatabricksTableTableInfoViewDependenciesOutputReference",
]

publication.publish()

def _typecheckingstub__08f897014853759e0010e7d51b826b5f68d7ed1ca7a826e4b46f482bba830824(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    id: typing.Optional[builtins.str] = None,
    table_info: typing.Optional[typing.Union[DataDatabricksTableTableInfo, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__a7b713457b82b6a8a3c46328d78c9954b5144755786b7957004b053f42676b30(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7a964ebb33d4aff11008e0c4bec73fe0754ab87d7a608856ffdfc205e862e8f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__234395ebe7a7792b8ac3bccf7c0a6a388ca7626cf784f6138d0f1c34beec1745(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c88dc6eb23145ea0377c19e5f27afc0450b3ba85ddedae46ce25b34752f5e7aa(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    id: typing.Optional[builtins.str] = None,
    table_info: typing.Optional[typing.Union[DataDatabricksTableTableInfo, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d1c70959089ece59fe8eb37c1418abbc1f9df1affcc2543df88d188f30a2b8e(
    *,
    access_point: typing.Optional[builtins.str] = None,
    browse_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    catalog_name: typing.Optional[builtins.str] = None,
    columns: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksTableTableInfoColumns, typing.Dict[builtins.str, typing.Any]]]]] = None,
    comment: typing.Optional[builtins.str] = None,
    created_at: typing.Optional[jsii.Number] = None,
    created_by: typing.Optional[builtins.str] = None,
    data_access_configuration_id: typing.Optional[builtins.str] = None,
    data_source_format: typing.Optional[builtins.str] = None,
    deleted_at: typing.Optional[jsii.Number] = None,
    delta_runtime_properties_kvpairs: typing.Optional[typing.Union[DataDatabricksTableTableInfoDeltaRuntimePropertiesKvpairs, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_predictive_optimization_flag: typing.Optional[typing.Union[DataDatabricksTableTableInfoEffectivePredictiveOptimizationFlag, typing.Dict[builtins.str, typing.Any]]] = None,
    enable_predictive_optimization: typing.Optional[builtins.str] = None,
    encryption_details: typing.Optional[typing.Union[DataDatabricksTableTableInfoEncryptionDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    full_name: typing.Optional[builtins.str] = None,
    metastore_id: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    owner: typing.Optional[builtins.str] = None,
    pipeline_id: typing.Optional[builtins.str] = None,
    properties: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    row_filter: typing.Optional[typing.Union[DataDatabricksTableTableInfoRowFilter, typing.Dict[builtins.str, typing.Any]]] = None,
    schema_name: typing.Optional[builtins.str] = None,
    securable_kind_manifest: typing.Optional[typing.Union[DataDatabricksTableTableInfoSecurableKindManifest, typing.Dict[builtins.str, typing.Any]]] = None,
    sql_path: typing.Optional[builtins.str] = None,
    storage_credential_name: typing.Optional[builtins.str] = None,
    storage_location: typing.Optional[builtins.str] = None,
    table_constraints: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksTableTableInfoTableConstraints, typing.Dict[builtins.str, typing.Any]]]]] = None,
    table_id: typing.Optional[builtins.str] = None,
    table_type: typing.Optional[builtins.str] = None,
    updated_at: typing.Optional[jsii.Number] = None,
    updated_by: typing.Optional[builtins.str] = None,
    view_definition: typing.Optional[builtins.str] = None,
    view_dependencies: typing.Optional[typing.Union[DataDatabricksTableTableInfoViewDependencies, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54254b1f3ae0fe9723095869ac9bf419f23838171f757ed525563ea41ef68017(
    *,
    comment: typing.Optional[builtins.str] = None,
    mask: typing.Optional[typing.Union[DataDatabricksTableTableInfoColumnsMask, typing.Dict[builtins.str, typing.Any]]] = None,
    name: typing.Optional[builtins.str] = None,
    nullable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    partition_index: typing.Optional[jsii.Number] = None,
    position: typing.Optional[jsii.Number] = None,
    type_interval_type: typing.Optional[builtins.str] = None,
    type_json: typing.Optional[builtins.str] = None,
    type_name: typing.Optional[builtins.str] = None,
    type_precision: typing.Optional[jsii.Number] = None,
    type_scale: typing.Optional[jsii.Number] = None,
    type_text: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdf3838c76d526149330d6c206eed8a75a256a9f6ffbbfde41861b37b2c2c8f7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff3e691186410b26e3846e6733c389fa0a3492f801fef55e16cd609f671f743b(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cfc4d6a9ae88a4c3e68d49a1c16c66339ae18fe194857245e625f49cb79bc24(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c24d65ad65444c636b315c8429acb8ca782d0b5dcf80ee93bba6391d346909db(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ed58a4911268ed789617a2e34ab65a5873d8084237fbc0cbc9b878857a12808(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9132e65bcf74fb0f846efaba6bbb534eb4bbbec608249406098f40b4149414d6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksTableTableInfoColumns]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d538ed698c2eef70b99839317b1012ae9d1a81bb86381dc31b5f9be98d20fd6a(
    *,
    function_name: typing.Optional[builtins.str] = None,
    using_column_names: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__951343289d6c6349b42bd5745ec76151d8f35d1c5c502074732c22dd27397135(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d57670a92bf6cd9ae52e32282da9ad4f5c54c71dedf2ab81208703d03b22ef29(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fbe2b816b129d828bfb33da9b2943427658b238c2424580cc3c5c1df9df6675(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c149bbed22050a94368e59e1bd9109dbdf721a49ccea3ecad9c3139812e4f2a(
    value: typing.Optional[DataDatabricksTableTableInfoColumnsMask],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__863fd40b07f6cf7ab7b89160c05e783b630a51b1964e71c124e9f4968f5d3b3d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53577afd12301aa3b7dec1f67e1964af881f1358f7aa5f24637f0697d56b2b30(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4175e64795fba90fe66db889f39ddb3857c988aa3eeb1866fa23c1c81b710f82(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26a11d2138f50110c02aad9aef76f39fc9b13fea44d318ca896ce44167781aaa(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d101bef0403d84abb60bd826f378ddc91a2d43bf37e698a82d07dda657a8950e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b84aebbd51f4007a324fafaae3ecabaff462dcde753485d25d5ae639f9bec334(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6797e8366e92cc9fad54ebb4f2ff7dc59fe42a88947c23882bf6e0fc3e19ff2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc95da90e1d59eaad91c212a6361810423bdc8b5567486b9f9db7c64bd17229e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84c0d1f109cd54c23680e7bb714eac4ccf663caaaf2287571a0719038b4d3f55(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a21123a2e44bd63577822808d32736eba91b1410e85f9ac189c4c1b4b217f6df(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e865a79f06e059a2a6bc6a51f82d44140e10c4c0eda5b0257007e67746e2a4b1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31690075c154652848954e81902d6be584a0214aa29e9828e077e8cea28ff5c2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8ec06988b1d3ebbcb2004cfeacc24a6381746110cf448edbf7d560c4c4c92e2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksTableTableInfoColumns]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20d7e82a071a5fb6bbc27028508fc4558ab3488621f60c01249b5d7619ef70c9(
    *,
    delta_runtime_properties: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6af1a76556950fb03132493bafb8d48de2e3b985e692fe43fc68a0519669626(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cc3bf06b2f242771225068c17f57758839bc6e75284cc1373b2a0819d1754f3(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c011a30b82885068d08bd6de251b0884677aefe68f1c0b20f27094e9a4574fc(
    value: typing.Optional[DataDatabricksTableTableInfoDeltaRuntimePropertiesKvpairs],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3cb97e6fbd513b31f4a50a82091c9e5bf1fb366217f2a044b086d2fbb96774b(
    *,
    value: builtins.str,
    inherited_from_name: typing.Optional[builtins.str] = None,
    inherited_from_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e3a04ca19c89208976b6950db308b04c832b896127c82df792328e2263416d9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c1655e53f9b0a9a0322a705275a912d11fbabf77784a7bc4a1985a3b739f728(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7389b7aa650a07b503e03ca4068e0d53316ae0855bdcad3133e16743c3517cb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de36031fc1016557473aad611db4eb7e8eecff43ad06ee2511c831ddcbccf051(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2dc7c9e30f9f332158dca68da650e652cbeb6a21e2346f56d02cc1d6a9049d5e(
    value: typing.Optional[DataDatabricksTableTableInfoEffectivePredictiveOptimizationFlag],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7492ae8e8b8f5f2703b4177c5449a08c3b7921c3e4f2ee01bda078a95db984e8(
    *,
    sse_encryption_details: typing.Optional[typing.Union[DataDatabricksTableTableInfoEncryptionDetailsSseEncryptionDetails, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eecf59b5ab93cc46f1f2fc8747e67eda635c432b16cce15a19a25cf5823a33fd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86c39c0ba6d42d6942c4bb605656e6014c6b3b40d659ab4afa6a87e066b0a6b7(
    value: typing.Optional[DataDatabricksTableTableInfoEncryptionDetails],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64a76fcc34d6297f78d253b0ce083331589f4ce3f2efdae4f944eb89074887f8(
    *,
    algorithm: typing.Optional[builtins.str] = None,
    aws_kms_key_arn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93e48ada4ca2f74ad97f1f983711bf55a30af1830e3e2353741a9f95545f078a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__464b696be504cadd711df94518bd9216329e48d4f6c478b0eb1667ec33b86fd6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91a6c10e1899b85d922efd07fdce3b75698e5bf3682844b9d7d5aa2af104a852(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c40fb3921c8ca95ab94c1f37a6df9222b2de42a40aa7789b140bc3c2704e5cc(
    value: typing.Optional[DataDatabricksTableTableInfoEncryptionDetailsSseEncryptionDetails],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b30280e1a8d263b50a18c395b588870bc07ac4089d2852737a9456f4bb4fe07(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a7c634d0f7e179cd1d42c46b1bee773bd50feda3da2ae307b27ffc3b313b07f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksTableTableInfoColumns, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cc36fddf6e8fd49d538195acd24e6e66039e65b8556c2e3b643a5f3abc5a9b6(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksTableTableInfoTableConstraints, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6549b72513dde0e699a6385344924fcd8788f311ceaecec89a0622d81a3636cc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0157366097f312ca68dabda844382288aa1f1a501b35be45bed4b0df7e7be045(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aec9c8bf6f2da33bda31ba265151d12234392bf728397bf899c163dcbc6eeda1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1bda6813b9b476f78b9f9dc9221380eef3f02f4b1f4a28f9b2faa1c501ad2cdc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de7a48b94616c8636aa63695b84a56198360461ddbdc4024540b4d5f9b548846(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84403c02724f58eb512e0c1c925fad710191257a660a0f73ddbd9029289fc6c9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cb63301c69b0ce09fed583d8c9b31426b4b898bb95745f637fe10ddfca0281e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8ba54c836299c70f221452c59302558a6cf68d91df5317e59066e2e2ed26dab(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2293e2d1ab3b7e2dad7af5e5f89e3338b24c271fca02f92152deb841a03422d6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ba50314750c45cf417af54f43e922c6c6a9194d129499c5aaddddc7533c8197(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb412ad93d2975f1acfcb92611dfbf20fd70bc9458bd1f0a829d92f1f5e7db8f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f4e730b6d7c9aff6de82f10c7ad57cc2f0e473583378ffe2a84ec578c4352a3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__078452f61bc7211c9beefeade7b6de996071924bcf772412ff5919348dd8d3d4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51d4f03bb09c5c3b050c3a29b9de6b4b9990266a1db258d8398ea9e49a306a90(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__adaac1e0ac4d3f46df860f27b7ef0b5b533253f7310360215351eb5803983136(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc11f519dff6af270acfe130a63eb5136e78638bb6cde0695675b9fd5cc9c772(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b92fbd2f1e91e6bb0b99f97ee8a14597854b5127c9afe27508032c518d024b9a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fbe0c385c4b377f85d5fe0009158d1ff4a36cf23f10f4807c6ca5391de7cf72(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a74fca918ce8d19cd50e570090ddcbbfdfb3673b5d08422ceec8e6aff15edcaa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d9937f7d96737d7d2b5360cfa58d89e08a5e3a5237a6551c28daa43502ea90d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df04bfda1d2127d78ed7d805f3c755792fad96cf1afc0a8efa7d3ba848f0d18e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd3556a987608c9621cf8f9801baf316e34aa35e0d7167d32f3e578b41c8f322(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74cab1fe84bd8ca7d77ac6f7024deb54abd1e3aa2bc2b5d684f16a3b4460b580(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb4d5c5e0ec4557aed127738cddca1a5c8bea820e21c7ac5578344130d95bd25(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__246c3f8bf7538d1bdef082f11941005b5ec5efedd89c0e45d7e7b193accfa89c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50f8177c283eb8988c1090f9d960c9285b44f1b87f501b060bfb9b59bad4a217(
    value: typing.Optional[DataDatabricksTableTableInfo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08eb34e37b1818bb07b2085db0a91a3ff163ca1ccfe1593510b5a847b0993a54(
    *,
    function_name: builtins.str,
    input_column_names: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb7c685ea7b59fc30a670a62396829845f05ed4e7475263d505421a5e139535c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__422602cabb9d96d7137712bb9a72eb2a74c8d94d372660342dd15c566ac5bcad(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15f23ba59fd4f9aa517e9fde2b7b6ce3b04eaec8760786a62420a2bb5b08bb08(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fc01730dfe751b7c83c623fce2f4153c14ecd6314f0fd9445705d67d46409d8(
    value: typing.Optional[DataDatabricksTableTableInfoRowFilter],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc00711557de7593a3c9bffecfea89f1b515a4373919e34d2e0b158af721ccf9(
    *,
    assignable_privileges: typing.Optional[typing.Sequence[builtins.str]] = None,
    capabilities: typing.Optional[typing.Sequence[builtins.str]] = None,
    options: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksTableTableInfoSecurableKindManifestOptions, typing.Dict[builtins.str, typing.Any]]]]] = None,
    securable_kind: typing.Optional[builtins.str] = None,
    securable_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a8c0997ad652b953c8168a737f6f6277e45ccbcc2704c3bc302cded095d1b06(
    *,
    allowed_values: typing.Optional[typing.Sequence[builtins.str]] = None,
    default_value: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    hint: typing.Optional[builtins.str] = None,
    is_copiable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    is_creatable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    is_hidden: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    is_loggable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    is_required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    is_secret: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    is_updatable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    name: typing.Optional[builtins.str] = None,
    oauth_stage: typing.Optional[builtins.str] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e1fed7e84f1d9a25a9631df67192fb04f85c53f0a0ea22bfbfb8618c26806dd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18913a49cb6fa28da1be489bc25ac98532429304565f74564adc22ff907bee69(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__013a4af3b97708e033fb87754432c269ca923788a223255d6ab65b4cb6a83ccb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ce679b9c10869fb77510cd22dbc97afc1416b62c9a6671e87cab7e3f6219d56(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c6cba332a045edbe479c6d8003f70c0270f4b6313016c323ac6b304199836d1(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e77da4b4e3c036e174aaed1959f802b87e11b1fb091fba50847813f9dcce25f9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksTableTableInfoSecurableKindManifestOptions]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1bad7f0b33d9cf62bfa62c0e25e2fb5ad6571dbddf914e5dadfca81d85b0c1a2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20088996aa5a89d036ab148dfa6fb33e89b84f6bfe575b42ed573a460cb20870(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37a9a197b1663e7b76bffc0bfc80431e236a3735a3324f253100aa5465d17931(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0da089b9ab1514892e1314725b68332aaaa0f8dc3529df191ccaa4ae2647269(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78cbdb326521be6c718f228de708c154814fd4a4b0ba95f0dbd06b117f4296cb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3c3744106e3db91679b5d55157b33b00a7991f51267f94427ac43b6f31c7c42(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afccaf95ade2e28be31b52058e7daef2d5e3e391dc8ecada967050aa9c8576cf(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5363f1bbb987b6516d9f422177ff8191404022b0b67bdbbab9ac9f6dbdb0863(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0ad5f03a07a5d05a8f6f58b4ec6ba01a8bb9270c99ef8e191d2ab71187aa22f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c433b8169b9ca65db4af73ad35080a8aaa0ef0b13cd829953fd3070eca5d9d0b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc7423eb0ee5f850323c74bb79587fc15af15cd6f65bb73e28c8831d8ef4d8e7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f1cfbaa757ca25372fa07860abd555607ab6d5e9314f3ca3d1a6d7fa3d6efe9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64df3bd27f0918cf7db20684215a283302a307deda9776a31db874412a4271ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbc893e533390c83ffa6196b38e25ab5b567919dcc005c698e8cbbd5d24ca2bc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb5cdecdafde74ff30ee5e20303548c538e492384070fa5d1ac2708eeb5ed35b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64070fe32657f41765cabe595a79eebed1bff7e7a413ab1ce95195104b792460(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksTableTableInfoSecurableKindManifestOptions]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2f42b0adf33eb87092336780dbd15475ccd6a3adc2d1a61c7d71fd85cc7877c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01024e6a0c85154fdd04b84a0cd9cec78399db4220ba90c690f2e59350f8c1e8(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksTableTableInfoSecurableKindManifestOptions, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__980e945d23c1ebf4100485380161166fb09c1b87506c29cd0b6e1c2b69600e09(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6aeb555cb6d14221403989b98c4fff65833034f8a7682e5e70c50254f0be753(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__869611d08d005ca0339ba335d1d8044f51534b13089a188d026ef3158e1d3f38(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__094ae80a248f84c530c61e7a100777a61675e7debdd4746cf3beb5988e8ebbb6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c7e10fee52891a4df339ee543a8ec07f0914a4329ffc55235e7f96a1c707754(
    value: typing.Optional[DataDatabricksTableTableInfoSecurableKindManifest],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4b77325ec695169b5edd62915971ea07f33d88e05ac33a9cddbaa7c26da68d1(
    *,
    foreign_key_constraint: typing.Optional[typing.Union[DataDatabricksTableTableInfoTableConstraintsForeignKeyConstraint, typing.Dict[builtins.str, typing.Any]]] = None,
    named_table_constraint: typing.Optional[typing.Union[DataDatabricksTableTableInfoTableConstraintsNamedTableConstraint, typing.Dict[builtins.str, typing.Any]]] = None,
    primary_key_constraint: typing.Optional[typing.Union[DataDatabricksTableTableInfoTableConstraintsPrimaryKeyConstraint, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a8e6a508893a90c45d8fd1730542fc306236bec83459913b9c30e40660653d8(
    *,
    child_columns: typing.Sequence[builtins.str],
    name: builtins.str,
    parent_columns: typing.Sequence[builtins.str],
    parent_table: builtins.str,
    rely: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b36c8d84b3560bffcf24afda080666db7a963534cb9ce32f91c5bd18a2b09d13(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66b2db471bf5694dc6f6bee73f2e877080bae607099160c978ac4d307e873adc(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51667a39e84b9d606d56b2aa842bd6662853d4d80090432bced3593da1443a23(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4756aeebd3137e5946875d5c7e7b392699608c0188dac3b95a07c9b1d5c52ad8(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5c42fa00046f49af55e38a54b4b4a82086fe16058f4654d2f52790c4d0ff3cc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9aad7e24c244b50d7977f96685120bdf26ff727312ed87b1a8a8aeb045551d2c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0661c07cbc90e0c61d373a26d0094213146baafdaf5b5d79bee03b59c66c8b59(
    value: typing.Optional[DataDatabricksTableTableInfoTableConstraintsForeignKeyConstraint],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4209b14a293e6cd799981d6024aab0995728f51a43dd81888bd442eca525f9f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b79b03c2e6b42cbc6860183723256b466854b8fa7ade5acff0d6000ebd2a6cf9(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f63bb041f940325b499ebd71081c3dbdda182508e306c488e3373231bfdc1e8d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec08e9e92b0f27dae9935176bd24f16ceb81245e7e66aac238baf2173da00b4b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3aa6377e8f73479df01757905411580cabaf986df6204557d1440dd0609596e(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3560698466bf94174ee89e7775125cd4015721c7a6d80699d3841125f4fe8b63(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksTableTableInfoTableConstraints]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e589f43d813ea14b7469eec1b1db7f931d71c3cecd842fe9f821ddd051da184(
    *,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa530eb4f98b672d0fd1eaafc0154eae72faed5a7c53503d2b11087e47237b79(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b0a7f616dcf8187f292e4b9c9f53fdcbbcba452fde279705caf1f51df11350a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92066c1d425d989611bd2f31cffa1c28e753d6139ddf199d0c44a5b08c9da480(
    value: typing.Optional[DataDatabricksTableTableInfoTableConstraintsNamedTableConstraint],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c5a70d9cebc86f3917232d042f6237cb58123c58d025e93f5ddd52a3bd3c30e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d27130809c870da1dda1cac79e44d6c97599ba185973a5f569d60b1ac00bc29f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksTableTableInfoTableConstraints]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48b3e0e1b359ba7651372e753bee520750202c65b67f9f776fc12de31402d237(
    *,
    child_columns: typing.Sequence[builtins.str],
    name: builtins.str,
    rely: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    timeseries_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9c573f4a6f99ce1127efad7814bcca9c7dab55da4e9bc3c1a1ba299bbbc2b15(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6578187eb0fa2fb01bb9e2d82db81e3e0c586bf0cd08362ce7f55aa11746481(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56df88d04b11646489828ffccc209b2bcff73ca1f612d97c4fe7a92074cfcbcb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca1cd7429b199350cb9690863b795a3c2e21d11aefb6f393b25748d9628fb97e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b24d7c2b18751092ec5e6078d5dce597443678f74b1c67f5d874345d24bc22a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e82cd0ddc24f9d0272cdffac0668f70a8d2504f28dac54f859ccf2ddb6ad4fba(
    value: typing.Optional[DataDatabricksTableTableInfoTableConstraintsPrimaryKeyConstraint],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2fd3887adbe9bf747d9386579c61002e3d65a751cf41e56ff3f730ec3f0c029(
    *,
    dependencies: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksTableTableInfoViewDependenciesDependencies, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cce868b624e5b5a5d30d9ec95598e1e10868fd072654deb8c3d879309cea011(
    *,
    connection: typing.Optional[typing.Union[DataDatabricksTableTableInfoViewDependenciesDependenciesConnection, typing.Dict[builtins.str, typing.Any]]] = None,
    credential: typing.Optional[typing.Union[DataDatabricksTableTableInfoViewDependenciesDependenciesCredential, typing.Dict[builtins.str, typing.Any]]] = None,
    function: typing.Optional[typing.Union[DataDatabricksTableTableInfoViewDependenciesDependenciesFunction, typing.Dict[builtins.str, typing.Any]]] = None,
    table: typing.Optional[typing.Union[DataDatabricksTableTableInfoViewDependenciesDependenciesTable, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44694cdc34cfb46c5d55ee806c5d702a1828d92f652f5284833209e408fabd24(
    *,
    connection_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d11eb57942a8302e196f0b49d682338f587a6d25202a794b03a40612d81c4da1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ba1299a592fda4904d87528d52a4529bfb2ced1c9430c2d1ae2b69f349ed3b2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a49921e3d5fa8ad689bc64c36ea5dc94118dbc951eb25f79e298a55ed5a041a2(
    value: typing.Optional[DataDatabricksTableTableInfoViewDependenciesDependenciesConnection],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c19308480a5b68a2e72f6873d69e443a572d1a62ceab4e681ba24c65ffe8bfd3(
    *,
    credential_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9900f14a1fb99b6b99419bc5cd88b2ed7da8e08821e139a98ab0b39909869f4a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b7aa85c23f1e46968241e161fb8915b2a3d35767a3269237159f5c46020d782(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4145d1e02d2691c8697cf000af601138c8166f4375eaf6d9a8ee957a1acb889(
    value: typing.Optional[DataDatabricksTableTableInfoViewDependenciesDependenciesCredential],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2682171d2da687bd8d536f338bcba376cdd8451059af8fe909cd5cbc35795ebc(
    *,
    function_full_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e936f4c092af7d9fa5b17fc361012493de5cb3c3fa9da5a6e7024931304e4ab1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8057f11912c1245a66eefe7c62b5e1dffe7adb930221750aadf07f29a778324(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b38b055fd5c2b4684035fd2da6d92e2d6183ea127f77b0181482c9c143062ee(
    value: typing.Optional[DataDatabricksTableTableInfoViewDependenciesDependenciesFunction],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fecdf80b23d48e508f0787920442a838a65c25e7c0099d81ee41c77576fdb42(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a624d54f5632321d4220ac41bdd90a662caa6ca44b6792abc6162c37ebbaafd8(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7337f0f7a91b7e8148950d94f20c862a8a10c3f446b6092252a846a7002bab43(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd615ebad8eccb0865e920bc7f6c804da4389e1cfc106706a73adec65191228d(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60e79bce4e12abc22a721232cad085cbb2315b3abfdbb774e3e5697359d45f3f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5186418e5b1952c8a9befc7fb3f3b3fd35fe320f28284d964f8646d80864aea(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksTableTableInfoViewDependenciesDependencies]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc5d240fa77acddbbe6e425cc8c07fcb3dc9bdff53963e5bb76a83a854040e29(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebd399e6a0bbd540a38c75461fd2895230e45789d4837433cf37af8339d7bb9d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksTableTableInfoViewDependenciesDependencies]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebb2dae672aaa98c37cc02d0bba18e1a5ee5b76aad22efc50030860da0312e7e(
    *,
    table_full_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55ab997492bcb55a8ab98f8af1c0c0935c002c379931f33cd5136474e88c9a6a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__459681f89374929d2e3ee40f13c62c5921712659eeceafb576c6340b46c816f4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__498bd55828df79f10f138bb5cf0f8df6105a2083d6aa079f5c9152e9ad222330(
    value: typing.Optional[DataDatabricksTableTableInfoViewDependenciesDependenciesTable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__394714fdf28588e8d0415d17e3e2c8d3e921bef36d2890269652a4c240cbd422(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08c21e9575fd9c3fee2cc1dee2aaa0a9a93acb8eebeee5d27226075075a998be(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksTableTableInfoViewDependenciesDependencies, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eebdff3e00d58bbf49817405b262997806167808fa1cecf194439bddfb7ae16c(
    value: typing.Optional[DataDatabricksTableTableInfoViewDependencies],
) -> None:
    """Type checking stubs"""
    pass
