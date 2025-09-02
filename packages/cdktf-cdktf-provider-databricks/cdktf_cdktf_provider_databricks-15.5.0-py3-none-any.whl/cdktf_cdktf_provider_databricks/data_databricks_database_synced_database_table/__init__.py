r'''
# `data_databricks_database_synced_database_table`

Refer to the Terraform Registry for docs: [`data_databricks_database_synced_database_table`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table).
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


class DataDatabricksDatabaseSyncedDatabaseTable(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTable.DataDatabricksDatabaseSyncedDatabaseTable",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table databricks_database_synced_database_table}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        database_instance_name: typing.Optional[builtins.str] = None,
        logical_database_name: typing.Optional[builtins.str] = None,
        spec: typing.Optional[typing.Union["DataDatabricksDatabaseSyncedDatabaseTableSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        workspace_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table databricks_database_synced_database_table} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#name DataDatabricksDatabaseSyncedDatabaseTable#name}.
        :param database_instance_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#database_instance_name DataDatabricksDatabaseSyncedDatabaseTable#database_instance_name}.
        :param logical_database_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#logical_database_name DataDatabricksDatabaseSyncedDatabaseTable#logical_database_name}.
        :param spec: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#spec DataDatabricksDatabaseSyncedDatabaseTable#spec}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#workspace_id DataDatabricksDatabaseSyncedDatabaseTable#workspace_id}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4472b494a92532fac707e8b311925bfc9b7d8d08b2332730c59511e1498c78f1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataDatabricksDatabaseSyncedDatabaseTableConfig(
            name=name,
            database_instance_name=database_instance_name,
            logical_database_name=logical_database_name,
            spec=spec,
            workspace_id=workspace_id,
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
        '''Generates CDKTF code for importing a DataDatabricksDatabaseSyncedDatabaseTable resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDatabricksDatabaseSyncedDatabaseTable to import.
        :param import_from_id: The id of the existing DataDatabricksDatabaseSyncedDatabaseTable that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDatabricksDatabaseSyncedDatabaseTable to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1232a6d1956895f94590533edb4f2593604f6962259fcdfa53500a9a6e7d20aa)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putSpec")
    def put_spec(
        self,
        *,
        create_database_objects_if_missing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        existing_pipeline_id: typing.Optional[builtins.str] = None,
        new_pipeline_spec: typing.Optional[typing.Union["DataDatabricksDatabaseSyncedDatabaseTableSpecNewPipelineSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        primary_key_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        scheduling_policy: typing.Optional[builtins.str] = None,
        source_table_full_name: typing.Optional[builtins.str] = None,
        timeseries_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create_database_objects_if_missing: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#create_database_objects_if_missing DataDatabricksDatabaseSyncedDatabaseTable#create_database_objects_if_missing}.
        :param existing_pipeline_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#existing_pipeline_id DataDatabricksDatabaseSyncedDatabaseTable#existing_pipeline_id}.
        :param new_pipeline_spec: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#new_pipeline_spec DataDatabricksDatabaseSyncedDatabaseTable#new_pipeline_spec}.
        :param primary_key_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#primary_key_columns DataDatabricksDatabaseSyncedDatabaseTable#primary_key_columns}.
        :param scheduling_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#scheduling_policy DataDatabricksDatabaseSyncedDatabaseTable#scheduling_policy}.
        :param source_table_full_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#source_table_full_name DataDatabricksDatabaseSyncedDatabaseTable#source_table_full_name}.
        :param timeseries_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#timeseries_key DataDatabricksDatabaseSyncedDatabaseTable#timeseries_key}.
        '''
        value = DataDatabricksDatabaseSyncedDatabaseTableSpec(
            create_database_objects_if_missing=create_database_objects_if_missing,
            existing_pipeline_id=existing_pipeline_id,
            new_pipeline_spec=new_pipeline_spec,
            primary_key_columns=primary_key_columns,
            scheduling_policy=scheduling_policy,
            source_table_full_name=source_table_full_name,
            timeseries_key=timeseries_key,
        )

        return typing.cast(None, jsii.invoke(self, "putSpec", [value]))

    @jsii.member(jsii_name="resetDatabaseInstanceName")
    def reset_database_instance_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatabaseInstanceName", []))

    @jsii.member(jsii_name="resetLogicalDatabaseName")
    def reset_logical_database_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogicalDatabaseName", []))

    @jsii.member(jsii_name="resetSpec")
    def reset_spec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpec", []))

    @jsii.member(jsii_name="resetWorkspaceId")
    def reset_workspace_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkspaceId", []))

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
    @jsii.member(jsii_name="dataSynchronizationStatus")
    def data_synchronization_status(
        self,
    ) -> "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusOutputReference":
        return typing.cast("DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusOutputReference", jsii.get(self, "dataSynchronizationStatus"))

    @builtins.property
    @jsii.member(jsii_name="effectiveDatabaseInstanceName")
    def effective_database_instance_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "effectiveDatabaseInstanceName"))

    @builtins.property
    @jsii.member(jsii_name="effectiveLogicalDatabaseName")
    def effective_logical_database_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "effectiveLogicalDatabaseName"))

    @builtins.property
    @jsii.member(jsii_name="spec")
    def spec(self) -> "DataDatabricksDatabaseSyncedDatabaseTableSpecOutputReference":
        return typing.cast("DataDatabricksDatabaseSyncedDatabaseTableSpecOutputReference", jsii.get(self, "spec"))

    @builtins.property
    @jsii.member(jsii_name="unityCatalogProvisioningState")
    def unity_catalog_provisioning_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unityCatalogProvisioningState"))

    @builtins.property
    @jsii.member(jsii_name="databaseInstanceNameInput")
    def database_instance_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseInstanceNameInput"))

    @builtins.property
    @jsii.member(jsii_name="logicalDatabaseNameInput")
    def logical_database_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logicalDatabaseNameInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="specInput")
    def spec_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksDatabaseSyncedDatabaseTableSpec"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksDatabaseSyncedDatabaseTableSpec"]], jsii.get(self, "specInput"))

    @builtins.property
    @jsii.member(jsii_name="workspaceIdInput")
    def workspace_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workspaceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="databaseInstanceName")
    def database_instance_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "databaseInstanceName"))

    @database_instance_name.setter
    def database_instance_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7472d69dadf74e3c697149265fbf4123dd394d05262406848d58f59f519f4b60)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "databaseInstanceName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logicalDatabaseName")
    def logical_database_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logicalDatabaseName"))

    @logical_database_name.setter
    def logical_database_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48e797388626f07ae6285d1b82877327baebd537f7009aad933d77877d49e6e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logicalDatabaseName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1399e396c9467fe280987667226c81981775af51576ac4b943a8bff4ed061288)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workspaceId")
    def workspace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceId"))

    @workspace_id.setter
    def workspace_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26f1aa8428c6188914cecaf54cb10dcc77460c9eace8266c441c20b47aab54a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workspaceId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTable.DataDatabricksDatabaseSyncedDatabaseTableConfig",
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
        "database_instance_name": "databaseInstanceName",
        "logical_database_name": "logicalDatabaseName",
        "spec": "spec",
        "workspace_id": "workspaceId",
    },
)
class DataDatabricksDatabaseSyncedDatabaseTableConfig(
    _cdktf_9a9027ec.TerraformMetaArguments,
):
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
        database_instance_name: typing.Optional[builtins.str] = None,
        logical_database_name: typing.Optional[builtins.str] = None,
        spec: typing.Optional[typing.Union["DataDatabricksDatabaseSyncedDatabaseTableSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        workspace_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#name DataDatabricksDatabaseSyncedDatabaseTable#name}.
        :param database_instance_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#database_instance_name DataDatabricksDatabaseSyncedDatabaseTable#database_instance_name}.
        :param logical_database_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#logical_database_name DataDatabricksDatabaseSyncedDatabaseTable#logical_database_name}.
        :param spec: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#spec DataDatabricksDatabaseSyncedDatabaseTable#spec}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#workspace_id DataDatabricksDatabaseSyncedDatabaseTable#workspace_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(spec, dict):
            spec = DataDatabricksDatabaseSyncedDatabaseTableSpec(**spec)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__810379cae92934cf1e5cd0aeb78b2ca89efdae9c321ae753aea744c4ef92152f)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument database_instance_name", value=database_instance_name, expected_type=type_hints["database_instance_name"])
            check_type(argname="argument logical_database_name", value=logical_database_name, expected_type=type_hints["logical_database_name"])
            check_type(argname="argument spec", value=spec, expected_type=type_hints["spec"])
            check_type(argname="argument workspace_id", value=workspace_id, expected_type=type_hints["workspace_id"])
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
        if database_instance_name is not None:
            self._values["database_instance_name"] = database_instance_name
        if logical_database_name is not None:
            self._values["logical_database_name"] = logical_database_name
        if spec is not None:
            self._values["spec"] = spec
        if workspace_id is not None:
            self._values["workspace_id"] = workspace_id

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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#name DataDatabricksDatabaseSyncedDatabaseTable#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def database_instance_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#database_instance_name DataDatabricksDatabaseSyncedDatabaseTable#database_instance_name}.'''
        result = self._values.get("database_instance_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def logical_database_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#logical_database_name DataDatabricksDatabaseSyncedDatabaseTable#logical_database_name}.'''
        result = self._values.get("logical_database_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spec(self) -> typing.Optional["DataDatabricksDatabaseSyncedDatabaseTableSpec"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#spec DataDatabricksDatabaseSyncedDatabaseTable#spec}.'''
        result = self._values.get("spec")
        return typing.cast(typing.Optional["DataDatabricksDatabaseSyncedDatabaseTableSpec"], result)

    @builtins.property
    def workspace_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#workspace_id DataDatabricksDatabaseSyncedDatabaseTable#workspace_id}.'''
        result = self._values.get("workspace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseSyncedDatabaseTableConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTable.DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatus",
    jsii_struct_bases=[],
    name_mapping={
        "continuous_update_status": "continuousUpdateStatus",
        "failed_status": "failedStatus",
        "provisioning_status": "provisioningStatus",
        "triggered_update_status": "triggeredUpdateStatus",
    },
)
class DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatus:
    def __init__(
        self,
        *,
        continuous_update_status: typing.Optional[typing.Union["DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus", typing.Dict[builtins.str, typing.Any]]] = None,
        failed_status: typing.Optional[typing.Union["DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus", typing.Dict[builtins.str, typing.Any]]] = None,
        provisioning_status: typing.Optional[typing.Union["DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus", typing.Dict[builtins.str, typing.Any]]] = None,
        triggered_update_status: typing.Optional[typing.Union["DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param continuous_update_status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#continuous_update_status DataDatabricksDatabaseSyncedDatabaseTable#continuous_update_status}.
        :param failed_status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#failed_status DataDatabricksDatabaseSyncedDatabaseTable#failed_status}.
        :param provisioning_status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#provisioning_status DataDatabricksDatabaseSyncedDatabaseTable#provisioning_status}.
        :param triggered_update_status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#triggered_update_status DataDatabricksDatabaseSyncedDatabaseTable#triggered_update_status}.
        '''
        if isinstance(continuous_update_status, dict):
            continuous_update_status = DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus(**continuous_update_status)
        if isinstance(failed_status, dict):
            failed_status = DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus(**failed_status)
        if isinstance(provisioning_status, dict):
            provisioning_status = DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus(**provisioning_status)
        if isinstance(triggered_update_status, dict):
            triggered_update_status = DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus(**triggered_update_status)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91f67e8f73993a78d580b8b941ff38c0575b161d068a50f4badcb2f809bee1f4)
            check_type(argname="argument continuous_update_status", value=continuous_update_status, expected_type=type_hints["continuous_update_status"])
            check_type(argname="argument failed_status", value=failed_status, expected_type=type_hints["failed_status"])
            check_type(argname="argument provisioning_status", value=provisioning_status, expected_type=type_hints["provisioning_status"])
            check_type(argname="argument triggered_update_status", value=triggered_update_status, expected_type=type_hints["triggered_update_status"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if continuous_update_status is not None:
            self._values["continuous_update_status"] = continuous_update_status
        if failed_status is not None:
            self._values["failed_status"] = failed_status
        if provisioning_status is not None:
            self._values["provisioning_status"] = provisioning_status
        if triggered_update_status is not None:
            self._values["triggered_update_status"] = triggered_update_status

    @builtins.property
    def continuous_update_status(
        self,
    ) -> typing.Optional["DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#continuous_update_status DataDatabricksDatabaseSyncedDatabaseTable#continuous_update_status}.'''
        result = self._values.get("continuous_update_status")
        return typing.cast(typing.Optional["DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus"], result)

    @builtins.property
    def failed_status(
        self,
    ) -> typing.Optional["DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#failed_status DataDatabricksDatabaseSyncedDatabaseTable#failed_status}.'''
        result = self._values.get("failed_status")
        return typing.cast(typing.Optional["DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus"], result)

    @builtins.property
    def provisioning_status(
        self,
    ) -> typing.Optional["DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#provisioning_status DataDatabricksDatabaseSyncedDatabaseTable#provisioning_status}.'''
        result = self._values.get("provisioning_status")
        return typing.cast(typing.Optional["DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus"], result)

    @builtins.property
    def triggered_update_status(
        self,
    ) -> typing.Optional["DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#triggered_update_status DataDatabricksDatabaseSyncedDatabaseTable#triggered_update_status}.'''
        result = self._values.get("triggered_update_status")
        return typing.cast(typing.Optional["DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTable.DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTable.DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgress",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgress:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgress(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgressOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTable.DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgressOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__50e8fc0eda4ab316b175f96f506f42b35c38fee9f100add51cd5b0939660b1e4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="estimatedCompletionTimeSeconds")
    def estimated_completion_time_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "estimatedCompletionTimeSeconds"))

    @builtins.property
    @jsii.member(jsii_name="latestVersionCurrentlyProcessing")
    def latest_version_currently_processing(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "latestVersionCurrentlyProcessing"))

    @builtins.property
    @jsii.member(jsii_name="provisioningPhase")
    def provisioning_phase(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "provisioningPhase"))

    @builtins.property
    @jsii.member(jsii_name="syncedRowCount")
    def synced_row_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "syncedRowCount"))

    @builtins.property
    @jsii.member(jsii_name="syncProgressCompletion")
    def sync_progress_completion(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "syncProgressCompletion"))

    @builtins.property
    @jsii.member(jsii_name="totalRowCount")
    def total_row_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "totalRowCount"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgress]:
        return typing.cast(typing.Optional[DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgress], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgress],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d599ceddbd6f50d2212ada0f9862a18a383fae77254bd14b6add6f32148e7f56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTable.DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__631a0d7e90908982b8df4544d837ee555ec4a0a395c62a2e0041990903091f02)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="initialPipelineSyncProgress")
    def initial_pipeline_sync_progress(
        self,
    ) -> DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgressOutputReference:
        return typing.cast(DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgressOutputReference, jsii.get(self, "initialPipelineSyncProgress"))

    @builtins.property
    @jsii.member(jsii_name="lastProcessedCommitVersion")
    def last_processed_commit_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lastProcessedCommitVersion"))

    @builtins.property
    @jsii.member(jsii_name="timestamp")
    def timestamp(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timestamp"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__351307947f4016e42cdbe75ec25e1e94a6f7b6281186a6d62460888c16cc73c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTable.DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTable.DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6dd3848f993f089e21e573eeebff469312e7ba572514a3d3af3cbf6e750d9a82)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="lastProcessedCommitVersion")
    def last_processed_commit_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lastProcessedCommitVersion"))

    @builtins.property
    @jsii.member(jsii_name="timestamp")
    def timestamp(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timestamp"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2e78105d4957fb36e3b1a5a28817e04a3edffeca8f14af23f8b850c2adc7d66)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTable.DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusLastSync",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusLastSync:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusLastSync(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTable.DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncDeltaTableSyncInfo",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncDeltaTableSyncInfo:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncDeltaTableSyncInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncDeltaTableSyncInfoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTable.DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncDeltaTableSyncInfoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a321a6377c24200b4a00b44edd7e2eb6637c5a8ada533f9ff24622d244af4826)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="deltaCommitTimestamp")
    def delta_commit_timestamp(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deltaCommitTimestamp"))

    @builtins.property
    @jsii.member(jsii_name="deltaCommitVersion")
    def delta_commit_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "deltaCommitVersion"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncDeltaTableSyncInfo]:
        return typing.cast(typing.Optional[DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncDeltaTableSyncInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncDeltaTableSyncInfo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dcfb90a7b7c6f5180cf335ea2d8286360d5e6c1fb771bd8b42f83f172ecef15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTable.DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__01a60e808c721943ebca4799d578e4de667596ee8164996541c660ec35c78e8f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="deltaTableSyncInfo")
    def delta_table_sync_info(
        self,
    ) -> DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncDeltaTableSyncInfoOutputReference:
        return typing.cast(DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncDeltaTableSyncInfoOutputReference, jsii.get(self, "deltaTableSyncInfo"))

    @builtins.property
    @jsii.member(jsii_name="syncEndTimestamp")
    def sync_end_timestamp(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "syncEndTimestamp"))

    @builtins.property
    @jsii.member(jsii_name="syncStartTimestamp")
    def sync_start_timestamp(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "syncStartTimestamp"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusLastSync]:
        return typing.cast(typing.Optional[DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusLastSync], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusLastSync],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__834c9490d884ce74ab0fb8d1213d259c2938c604a951cd5dd5dddb46f9637894)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTable.DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__eea0c49580bb1ca57fb4a64e823f195936c38cd2d5a0af4e087a2a730b3a2121)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putContinuousUpdateStatus")
    def put_continuous_update_status(self) -> None:
        value = DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus()

        return typing.cast(None, jsii.invoke(self, "putContinuousUpdateStatus", [value]))

    @jsii.member(jsii_name="putFailedStatus")
    def put_failed_status(self) -> None:
        value = DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus()

        return typing.cast(None, jsii.invoke(self, "putFailedStatus", [value]))

    @jsii.member(jsii_name="putProvisioningStatus")
    def put_provisioning_status(self) -> None:
        value = DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus()

        return typing.cast(None, jsii.invoke(self, "putProvisioningStatus", [value]))

    @jsii.member(jsii_name="putTriggeredUpdateStatus")
    def put_triggered_update_status(self) -> None:
        value = DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus()

        return typing.cast(None, jsii.invoke(self, "putTriggeredUpdateStatus", [value]))

    @jsii.member(jsii_name="resetContinuousUpdateStatus")
    def reset_continuous_update_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContinuousUpdateStatus", []))

    @jsii.member(jsii_name="resetFailedStatus")
    def reset_failed_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFailedStatus", []))

    @jsii.member(jsii_name="resetProvisioningStatus")
    def reset_provisioning_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProvisioningStatus", []))

    @jsii.member(jsii_name="resetTriggeredUpdateStatus")
    def reset_triggered_update_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTriggeredUpdateStatus", []))

    @builtins.property
    @jsii.member(jsii_name="continuousUpdateStatus")
    def continuous_update_status(
        self,
    ) -> DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusOutputReference:
        return typing.cast(DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusOutputReference, jsii.get(self, "continuousUpdateStatus"))

    @builtins.property
    @jsii.member(jsii_name="detailedState")
    def detailed_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "detailedState"))

    @builtins.property
    @jsii.member(jsii_name="failedStatus")
    def failed_status(
        self,
    ) -> DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatusOutputReference:
        return typing.cast(DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatusOutputReference, jsii.get(self, "failedStatus"))

    @builtins.property
    @jsii.member(jsii_name="lastSync")
    def last_sync(
        self,
    ) -> DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncOutputReference:
        return typing.cast(DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncOutputReference, jsii.get(self, "lastSync"))

    @builtins.property
    @jsii.member(jsii_name="message")
    def message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "message"))

    @builtins.property
    @jsii.member(jsii_name="pipelineId")
    def pipeline_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pipelineId"))

    @builtins.property
    @jsii.member(jsii_name="provisioningStatus")
    def provisioning_status(
        self,
    ) -> "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusOutputReference":
        return typing.cast("DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusOutputReference", jsii.get(self, "provisioningStatus"))

    @builtins.property
    @jsii.member(jsii_name="triggeredUpdateStatus")
    def triggered_update_status(
        self,
    ) -> "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusOutputReference":
        return typing.cast("DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusOutputReference", jsii.get(self, "triggeredUpdateStatus"))

    @builtins.property
    @jsii.member(jsii_name="continuousUpdateStatusInput")
    def continuous_update_status_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus]], jsii.get(self, "continuousUpdateStatusInput"))

    @builtins.property
    @jsii.member(jsii_name="failedStatusInput")
    def failed_status_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus]], jsii.get(self, "failedStatusInput"))

    @builtins.property
    @jsii.member(jsii_name="provisioningStatusInput")
    def provisioning_status_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus"]], jsii.get(self, "provisioningStatusInput"))

    @builtins.property
    @jsii.member(jsii_name="triggeredUpdateStatusInput")
    def triggered_update_status_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus"]], jsii.get(self, "triggeredUpdateStatusInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatus]:
        return typing.cast(typing.Optional[DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatus], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatus],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__940803f3ce29ef7becd3b7009a1caa091e079ee33383032fbf2cd6892b51512c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTable.DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTable.DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgress",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgress:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgress(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgressOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTable.DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgressOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a9b921e223bdf2f22120a94586812a3df1d31c541891d395902355a0bc302647)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="estimatedCompletionTimeSeconds")
    def estimated_completion_time_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "estimatedCompletionTimeSeconds"))

    @builtins.property
    @jsii.member(jsii_name="latestVersionCurrentlyProcessing")
    def latest_version_currently_processing(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "latestVersionCurrentlyProcessing"))

    @builtins.property
    @jsii.member(jsii_name="provisioningPhase")
    def provisioning_phase(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "provisioningPhase"))

    @builtins.property
    @jsii.member(jsii_name="syncedRowCount")
    def synced_row_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "syncedRowCount"))

    @builtins.property
    @jsii.member(jsii_name="syncProgressCompletion")
    def sync_progress_completion(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "syncProgressCompletion"))

    @builtins.property
    @jsii.member(jsii_name="totalRowCount")
    def total_row_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "totalRowCount"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgress]:
        return typing.cast(typing.Optional[DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgress], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgress],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7387b8fd8f7ee45bde088e026775916a3b3f3ca49d660b002980c539a9fbaea9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTable.DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0c29ae67b827a9ddc4eef33a759048ad189e115ddfc9ec34e1c95c3a6bc18887)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="initialPipelineSyncProgress")
    def initial_pipeline_sync_progress(
        self,
    ) -> DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgressOutputReference:
        return typing.cast(DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgressOutputReference, jsii.get(self, "initialPipelineSyncProgress"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ef3f2faa995c954761c3ac8b91ffab2f3336fa2c444709d553af02f711183dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTable.DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTable.DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8553c81257713d738edf57d8aae5e34e5c63fa4f58db23f684bc93771e91ffa0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="lastProcessedCommitVersion")
    def last_processed_commit_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lastProcessedCommitVersion"))

    @builtins.property
    @jsii.member(jsii_name="timestamp")
    def timestamp(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timestamp"))

    @builtins.property
    @jsii.member(jsii_name="triggeredUpdateProgress")
    def triggered_update_progress(
        self,
    ) -> "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgressOutputReference":
        return typing.cast("DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgressOutputReference", jsii.get(self, "triggeredUpdateProgress"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3cfad3f80337faa675cd07b419076c9b4fa3b38940425c5be3f48d2426df49c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTable.DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgress",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgress:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgress(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgressOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTable.DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgressOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__811f4f28ab33ab5060cae374b543c39454378df0768b0c62e835baf5d23bd30e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="estimatedCompletionTimeSeconds")
    def estimated_completion_time_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "estimatedCompletionTimeSeconds"))

    @builtins.property
    @jsii.member(jsii_name="latestVersionCurrentlyProcessing")
    def latest_version_currently_processing(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "latestVersionCurrentlyProcessing"))

    @builtins.property
    @jsii.member(jsii_name="provisioningPhase")
    def provisioning_phase(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "provisioningPhase"))

    @builtins.property
    @jsii.member(jsii_name="syncedRowCount")
    def synced_row_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "syncedRowCount"))

    @builtins.property
    @jsii.member(jsii_name="syncProgressCompletion")
    def sync_progress_completion(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "syncProgressCompletion"))

    @builtins.property
    @jsii.member(jsii_name="totalRowCount")
    def total_row_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "totalRowCount"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgress]:
        return typing.cast(typing.Optional[DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgress], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgress],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22981283e54b2d1ce8b8758dd5f51d734ce4e560d5610ff216383cb3af4a179b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTable.DataDatabricksDatabaseSyncedDatabaseTableSpec",
    jsii_struct_bases=[],
    name_mapping={
        "create_database_objects_if_missing": "createDatabaseObjectsIfMissing",
        "existing_pipeline_id": "existingPipelineId",
        "new_pipeline_spec": "newPipelineSpec",
        "primary_key_columns": "primaryKeyColumns",
        "scheduling_policy": "schedulingPolicy",
        "source_table_full_name": "sourceTableFullName",
        "timeseries_key": "timeseriesKey",
    },
)
class DataDatabricksDatabaseSyncedDatabaseTableSpec:
    def __init__(
        self,
        *,
        create_database_objects_if_missing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        existing_pipeline_id: typing.Optional[builtins.str] = None,
        new_pipeline_spec: typing.Optional[typing.Union["DataDatabricksDatabaseSyncedDatabaseTableSpecNewPipelineSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        primary_key_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        scheduling_policy: typing.Optional[builtins.str] = None,
        source_table_full_name: typing.Optional[builtins.str] = None,
        timeseries_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create_database_objects_if_missing: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#create_database_objects_if_missing DataDatabricksDatabaseSyncedDatabaseTable#create_database_objects_if_missing}.
        :param existing_pipeline_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#existing_pipeline_id DataDatabricksDatabaseSyncedDatabaseTable#existing_pipeline_id}.
        :param new_pipeline_spec: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#new_pipeline_spec DataDatabricksDatabaseSyncedDatabaseTable#new_pipeline_spec}.
        :param primary_key_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#primary_key_columns DataDatabricksDatabaseSyncedDatabaseTable#primary_key_columns}.
        :param scheduling_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#scheduling_policy DataDatabricksDatabaseSyncedDatabaseTable#scheduling_policy}.
        :param source_table_full_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#source_table_full_name DataDatabricksDatabaseSyncedDatabaseTable#source_table_full_name}.
        :param timeseries_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#timeseries_key DataDatabricksDatabaseSyncedDatabaseTable#timeseries_key}.
        '''
        if isinstance(new_pipeline_spec, dict):
            new_pipeline_spec = DataDatabricksDatabaseSyncedDatabaseTableSpecNewPipelineSpec(**new_pipeline_spec)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79a5995b6c76d23a5a3edddeddd6b7ce456a5478a0886f297f6f2211d51ad4cf)
            check_type(argname="argument create_database_objects_if_missing", value=create_database_objects_if_missing, expected_type=type_hints["create_database_objects_if_missing"])
            check_type(argname="argument existing_pipeline_id", value=existing_pipeline_id, expected_type=type_hints["existing_pipeline_id"])
            check_type(argname="argument new_pipeline_spec", value=new_pipeline_spec, expected_type=type_hints["new_pipeline_spec"])
            check_type(argname="argument primary_key_columns", value=primary_key_columns, expected_type=type_hints["primary_key_columns"])
            check_type(argname="argument scheduling_policy", value=scheduling_policy, expected_type=type_hints["scheduling_policy"])
            check_type(argname="argument source_table_full_name", value=source_table_full_name, expected_type=type_hints["source_table_full_name"])
            check_type(argname="argument timeseries_key", value=timeseries_key, expected_type=type_hints["timeseries_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if create_database_objects_if_missing is not None:
            self._values["create_database_objects_if_missing"] = create_database_objects_if_missing
        if existing_pipeline_id is not None:
            self._values["existing_pipeline_id"] = existing_pipeline_id
        if new_pipeline_spec is not None:
            self._values["new_pipeline_spec"] = new_pipeline_spec
        if primary_key_columns is not None:
            self._values["primary_key_columns"] = primary_key_columns
        if scheduling_policy is not None:
            self._values["scheduling_policy"] = scheduling_policy
        if source_table_full_name is not None:
            self._values["source_table_full_name"] = source_table_full_name
        if timeseries_key is not None:
            self._values["timeseries_key"] = timeseries_key

    @builtins.property
    def create_database_objects_if_missing(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#create_database_objects_if_missing DataDatabricksDatabaseSyncedDatabaseTable#create_database_objects_if_missing}.'''
        result = self._values.get("create_database_objects_if_missing")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def existing_pipeline_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#existing_pipeline_id DataDatabricksDatabaseSyncedDatabaseTable#existing_pipeline_id}.'''
        result = self._values.get("existing_pipeline_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def new_pipeline_spec(
        self,
    ) -> typing.Optional["DataDatabricksDatabaseSyncedDatabaseTableSpecNewPipelineSpec"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#new_pipeline_spec DataDatabricksDatabaseSyncedDatabaseTable#new_pipeline_spec}.'''
        result = self._values.get("new_pipeline_spec")
        return typing.cast(typing.Optional["DataDatabricksDatabaseSyncedDatabaseTableSpecNewPipelineSpec"], result)

    @builtins.property
    def primary_key_columns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#primary_key_columns DataDatabricksDatabaseSyncedDatabaseTable#primary_key_columns}.'''
        result = self._values.get("primary_key_columns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def scheduling_policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#scheduling_policy DataDatabricksDatabaseSyncedDatabaseTable#scheduling_policy}.'''
        result = self._values.get("scheduling_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_table_full_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#source_table_full_name DataDatabricksDatabaseSyncedDatabaseTable#source_table_full_name}.'''
        result = self._values.get("source_table_full_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeseries_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#timeseries_key DataDatabricksDatabaseSyncedDatabaseTable#timeseries_key}.'''
        result = self._values.get("timeseries_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseSyncedDatabaseTableSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTable.DataDatabricksDatabaseSyncedDatabaseTableSpecNewPipelineSpec",
    jsii_struct_bases=[],
    name_mapping={
        "storage_catalog": "storageCatalog",
        "storage_schema": "storageSchema",
    },
)
class DataDatabricksDatabaseSyncedDatabaseTableSpecNewPipelineSpec:
    def __init__(
        self,
        *,
        storage_catalog: typing.Optional[builtins.str] = None,
        storage_schema: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param storage_catalog: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#storage_catalog DataDatabricksDatabaseSyncedDatabaseTable#storage_catalog}.
        :param storage_schema: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#storage_schema DataDatabricksDatabaseSyncedDatabaseTable#storage_schema}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1a1ce43c50cc24fb16373da2fe3d8352ea83795d40d64a02315ca3b23e24167)
            check_type(argname="argument storage_catalog", value=storage_catalog, expected_type=type_hints["storage_catalog"])
            check_type(argname="argument storage_schema", value=storage_schema, expected_type=type_hints["storage_schema"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if storage_catalog is not None:
            self._values["storage_catalog"] = storage_catalog
        if storage_schema is not None:
            self._values["storage_schema"] = storage_schema

    @builtins.property
    def storage_catalog(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#storage_catalog DataDatabricksDatabaseSyncedDatabaseTable#storage_catalog}.'''
        result = self._values.get("storage_catalog")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def storage_schema(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#storage_schema DataDatabricksDatabaseSyncedDatabaseTable#storage_schema}.'''
        result = self._values.get("storage_schema")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseSyncedDatabaseTableSpecNewPipelineSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksDatabaseSyncedDatabaseTableSpecNewPipelineSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTable.DataDatabricksDatabaseSyncedDatabaseTableSpecNewPipelineSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__848565b01f1b4c04a56e1599bc7b871498cdc410a8f3cc6f6b55e1ad0f9c4998)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetStorageCatalog")
    def reset_storage_catalog(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageCatalog", []))

    @jsii.member(jsii_name="resetStorageSchema")
    def reset_storage_schema(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageSchema", []))

    @builtins.property
    @jsii.member(jsii_name="storageCatalogInput")
    def storage_catalog_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageCatalogInput"))

    @builtins.property
    @jsii.member(jsii_name="storageSchemaInput")
    def storage_schema_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageSchemaInput"))

    @builtins.property
    @jsii.member(jsii_name="storageCatalog")
    def storage_catalog(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageCatalog"))

    @storage_catalog.setter
    def storage_catalog(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b019d4241699bf2148c91ee8d7953425b47d41ae386b800ee7b3611f82d8f244)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageCatalog", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storageSchema")
    def storage_schema(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageSchema"))

    @storage_schema.setter
    def storage_schema(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__338eff623822c42bdb60e102dd6fa4ba289193d8db8b80661bd43c58fd6e5e08)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageSchema", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableSpecNewPipelineSpec]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableSpecNewPipelineSpec]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableSpecNewPipelineSpec]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__466a233f92937b39e6a6309d2bc108f44003e38382ec9f014a8b95d26698915a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksDatabaseSyncedDatabaseTableSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTable.DataDatabricksDatabaseSyncedDatabaseTableSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__df33d2c0039968dd9ad5d47e574fb5be3d2d5ab2eacb949d338722d90c923895)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putNewPipelineSpec")
    def put_new_pipeline_spec(
        self,
        *,
        storage_catalog: typing.Optional[builtins.str] = None,
        storage_schema: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param storage_catalog: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#storage_catalog DataDatabricksDatabaseSyncedDatabaseTable#storage_catalog}.
        :param storage_schema: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_table#storage_schema DataDatabricksDatabaseSyncedDatabaseTable#storage_schema}.
        '''
        value = DataDatabricksDatabaseSyncedDatabaseTableSpecNewPipelineSpec(
            storage_catalog=storage_catalog, storage_schema=storage_schema
        )

        return typing.cast(None, jsii.invoke(self, "putNewPipelineSpec", [value]))

    @jsii.member(jsii_name="resetCreateDatabaseObjectsIfMissing")
    def reset_create_database_objects_if_missing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreateDatabaseObjectsIfMissing", []))

    @jsii.member(jsii_name="resetExistingPipelineId")
    def reset_existing_pipeline_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExistingPipelineId", []))

    @jsii.member(jsii_name="resetNewPipelineSpec")
    def reset_new_pipeline_spec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNewPipelineSpec", []))

    @jsii.member(jsii_name="resetPrimaryKeyColumns")
    def reset_primary_key_columns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrimaryKeyColumns", []))

    @jsii.member(jsii_name="resetSchedulingPolicy")
    def reset_scheduling_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchedulingPolicy", []))

    @jsii.member(jsii_name="resetSourceTableFullName")
    def reset_source_table_full_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceTableFullName", []))

    @jsii.member(jsii_name="resetTimeseriesKey")
    def reset_timeseries_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeseriesKey", []))

    @builtins.property
    @jsii.member(jsii_name="newPipelineSpec")
    def new_pipeline_spec(
        self,
    ) -> DataDatabricksDatabaseSyncedDatabaseTableSpecNewPipelineSpecOutputReference:
        return typing.cast(DataDatabricksDatabaseSyncedDatabaseTableSpecNewPipelineSpecOutputReference, jsii.get(self, "newPipelineSpec"))

    @builtins.property
    @jsii.member(jsii_name="createDatabaseObjectsIfMissingInput")
    def create_database_objects_if_missing_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "createDatabaseObjectsIfMissingInput"))

    @builtins.property
    @jsii.member(jsii_name="existingPipelineIdInput")
    def existing_pipeline_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "existingPipelineIdInput"))

    @builtins.property
    @jsii.member(jsii_name="newPipelineSpecInput")
    def new_pipeline_spec_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableSpecNewPipelineSpec]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableSpecNewPipelineSpec]], jsii.get(self, "newPipelineSpecInput"))

    @builtins.property
    @jsii.member(jsii_name="primaryKeyColumnsInput")
    def primary_key_columns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "primaryKeyColumnsInput"))

    @builtins.property
    @jsii.member(jsii_name="schedulingPolicyInput")
    def scheduling_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schedulingPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceTableFullNameInput")
    def source_table_full_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceTableFullNameInput"))

    @builtins.property
    @jsii.member(jsii_name="timeseriesKeyInput")
    def timeseries_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timeseriesKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="createDatabaseObjectsIfMissing")
    def create_database_objects_if_missing(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "createDatabaseObjectsIfMissing"))

    @create_database_objects_if_missing.setter
    def create_database_objects_if_missing(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42d5bb2d01cbe45662a652338e1306558261086119d34314cd91c6fb1fc42d21)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createDatabaseObjectsIfMissing", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="existingPipelineId")
    def existing_pipeline_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "existingPipelineId"))

    @existing_pipeline_id.setter
    def existing_pipeline_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28dde01044b91a8b789202e04964cfe0b9230c238a7eab96abd32391e6196b0e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "existingPipelineId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="primaryKeyColumns")
    def primary_key_columns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "primaryKeyColumns"))

    @primary_key_columns.setter
    def primary_key_columns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__159fff6e87d2b5d745d2b790f215f8e7544694f96296016a5717e833c0c64fe3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "primaryKeyColumns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="schedulingPolicy")
    def scheduling_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schedulingPolicy"))

    @scheduling_policy.setter
    def scheduling_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c5a5a651e401160e8719a5f54ae1108579bb9d2cae86eb54cd11d0bc79162ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "schedulingPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceTableFullName")
    def source_table_full_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceTableFullName"))

    @source_table_full_name.setter
    def source_table_full_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2de0560c7ca17d8d159834bf4f6ab59c9f830ad483fc632871e477d52802cc81)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceTableFullName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeseriesKey")
    def timeseries_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeseriesKey"))

    @timeseries_key.setter
    def timeseries_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a583a8a856f9918af8cbebedadd37c509eaad91eb9af624a7d54be98ab0dd929)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeseriesKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableSpec]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableSpec]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableSpec]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f37c1d03814172d7e1467d8542f60004d43c59b6698aa1eeb21ec422e2209aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataDatabricksDatabaseSyncedDatabaseTable",
    "DataDatabricksDatabaseSyncedDatabaseTableConfig",
    "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatus",
    "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus",
    "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgress",
    "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgressOutputReference",
    "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusOutputReference",
    "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus",
    "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatusOutputReference",
    "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusLastSync",
    "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncDeltaTableSyncInfo",
    "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncDeltaTableSyncInfoOutputReference",
    "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncOutputReference",
    "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusOutputReference",
    "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus",
    "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgress",
    "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgressOutputReference",
    "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusOutputReference",
    "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus",
    "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusOutputReference",
    "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgress",
    "DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgressOutputReference",
    "DataDatabricksDatabaseSyncedDatabaseTableSpec",
    "DataDatabricksDatabaseSyncedDatabaseTableSpecNewPipelineSpec",
    "DataDatabricksDatabaseSyncedDatabaseTableSpecNewPipelineSpecOutputReference",
    "DataDatabricksDatabaseSyncedDatabaseTableSpecOutputReference",
]

publication.publish()

def _typecheckingstub__4472b494a92532fac707e8b311925bfc9b7d8d08b2332730c59511e1498c78f1(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    name: builtins.str,
    database_instance_name: typing.Optional[builtins.str] = None,
    logical_database_name: typing.Optional[builtins.str] = None,
    spec: typing.Optional[typing.Union[DataDatabricksDatabaseSyncedDatabaseTableSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    workspace_id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__1232a6d1956895f94590533edb4f2593604f6962259fcdfa53500a9a6e7d20aa(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7472d69dadf74e3c697149265fbf4123dd394d05262406848d58f59f519f4b60(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48e797388626f07ae6285d1b82877327baebd537f7009aad933d77877d49e6e6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1399e396c9467fe280987667226c81981775af51576ac4b943a8bff4ed061288(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26f1aa8428c6188914cecaf54cb10dcc77460c9eace8266c441c20b47aab54a1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__810379cae92934cf1e5cd0aeb78b2ca89efdae9c321ae753aea744c4ef92152f(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    database_instance_name: typing.Optional[builtins.str] = None,
    logical_database_name: typing.Optional[builtins.str] = None,
    spec: typing.Optional[typing.Union[DataDatabricksDatabaseSyncedDatabaseTableSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    workspace_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91f67e8f73993a78d580b8b941ff38c0575b161d068a50f4badcb2f809bee1f4(
    *,
    continuous_update_status: typing.Optional[typing.Union[DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus, typing.Dict[builtins.str, typing.Any]]] = None,
    failed_status: typing.Optional[typing.Union[DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus, typing.Dict[builtins.str, typing.Any]]] = None,
    provisioning_status: typing.Optional[typing.Union[DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus, typing.Dict[builtins.str, typing.Any]]] = None,
    triggered_update_status: typing.Optional[typing.Union[DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50e8fc0eda4ab316b175f96f506f42b35c38fee9f100add51cd5b0939660b1e4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d599ceddbd6f50d2212ada0f9862a18a383fae77254bd14b6add6f32148e7f56(
    value: typing.Optional[DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgress],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__631a0d7e90908982b8df4544d837ee555ec4a0a395c62a2e0041990903091f02(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__351307947f4016e42cdbe75ec25e1e94a6f7b6281186a6d62460888c16cc73c5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6dd3848f993f089e21e573eeebff469312e7ba572514a3d3af3cbf6e750d9a82(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2e78105d4957fb36e3b1a5a28817e04a3edffeca8f14af23f8b850c2adc7d66(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a321a6377c24200b4a00b44edd7e2eb6637c5a8ada533f9ff24622d244af4826(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dcfb90a7b7c6f5180cf335ea2d8286360d5e6c1fb771bd8b42f83f172ecef15(
    value: typing.Optional[DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncDeltaTableSyncInfo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01a60e808c721943ebca4799d578e4de667596ee8164996541c660ec35c78e8f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__834c9490d884ce74ab0fb8d1213d259c2938c604a951cd5dd5dddb46f9637894(
    value: typing.Optional[DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusLastSync],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eea0c49580bb1ca57fb4a64e823f195936c38cd2d5a0af4e087a2a730b3a2121(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__940803f3ce29ef7becd3b7009a1caa091e079ee33383032fbf2cd6892b51512c(
    value: typing.Optional[DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatus],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9b921e223bdf2f22120a94586812a3df1d31c541891d395902355a0bc302647(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7387b8fd8f7ee45bde088e026775916a3b3f3ca49d660b002980c539a9fbaea9(
    value: typing.Optional[DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgress],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c29ae67b827a9ddc4eef33a759048ad189e115ddfc9ec34e1c95c3a6bc18887(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ef3f2faa995c954761c3ac8b91ffab2f3336fa2c444709d553af02f711183dc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8553c81257713d738edf57d8aae5e34e5c63fa4f58db23f684bc93771e91ffa0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3cfad3f80337faa675cd07b419076c9b4fa3b38940425c5be3f48d2426df49c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__811f4f28ab33ab5060cae374b543c39454378df0768b0c62e835baf5d23bd30e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22981283e54b2d1ce8b8758dd5f51d734ce4e560d5610ff216383cb3af4a179b(
    value: typing.Optional[DataDatabricksDatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgress],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79a5995b6c76d23a5a3edddeddd6b7ce456a5478a0886f297f6f2211d51ad4cf(
    *,
    create_database_objects_if_missing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    existing_pipeline_id: typing.Optional[builtins.str] = None,
    new_pipeline_spec: typing.Optional[typing.Union[DataDatabricksDatabaseSyncedDatabaseTableSpecNewPipelineSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    primary_key_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
    scheduling_policy: typing.Optional[builtins.str] = None,
    source_table_full_name: typing.Optional[builtins.str] = None,
    timeseries_key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1a1ce43c50cc24fb16373da2fe3d8352ea83795d40d64a02315ca3b23e24167(
    *,
    storage_catalog: typing.Optional[builtins.str] = None,
    storage_schema: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__848565b01f1b4c04a56e1599bc7b871498cdc410a8f3cc6f6b55e1ad0f9c4998(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b019d4241699bf2148c91ee8d7953425b47d41ae386b800ee7b3611f82d8f244(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__338eff623822c42bdb60e102dd6fa4ba289193d8db8b80661bd43c58fd6e5e08(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__466a233f92937b39e6a6309d2bc108f44003e38382ec9f014a8b95d26698915a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableSpecNewPipelineSpec]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df33d2c0039968dd9ad5d47e574fb5be3d2d5ab2eacb949d338722d90c923895(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42d5bb2d01cbe45662a652338e1306558261086119d34314cd91c6fb1fc42d21(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28dde01044b91a8b789202e04964cfe0b9230c238a7eab96abd32391e6196b0e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__159fff6e87d2b5d745d2b790f215f8e7544694f96296016a5717e833c0c64fe3(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c5a5a651e401160e8719a5f54ae1108579bb9d2cae86eb54cd11d0bc79162ae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2de0560c7ca17d8d159834bf4f6ab59c9f830ad483fc632871e477d52802cc81(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a583a8a856f9918af8cbebedadd37c509eaad91eb9af624a7d54be98ab0dd929(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f37c1d03814172d7e1467d8542f60004d43c59b6698aa1eeb21ec422e2209aa(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTableSpec]],
) -> None:
    """Type checking stubs"""
    pass
