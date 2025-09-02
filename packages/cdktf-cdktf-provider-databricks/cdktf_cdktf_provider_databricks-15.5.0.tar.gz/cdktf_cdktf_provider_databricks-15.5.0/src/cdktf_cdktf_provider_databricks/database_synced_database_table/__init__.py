r'''
# `databricks_database_synced_database_table`

Refer to the Terraform Registry for docs: [`databricks_database_synced_database_table`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table).
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


class DatabaseSyncedDatabaseTable(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.databaseSyncedDatabaseTable.DatabaseSyncedDatabaseTable",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table databricks_database_synced_database_table}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        database_instance_name: typing.Optional[builtins.str] = None,
        logical_database_name: typing.Optional[builtins.str] = None,
        spec: typing.Optional[typing.Union["DatabaseSyncedDatabaseTableSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        workspace_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table databricks_database_synced_database_table} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#name DatabaseSyncedDatabaseTable#name}.
        :param database_instance_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#database_instance_name DatabaseSyncedDatabaseTable#database_instance_name}.
        :param logical_database_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#logical_database_name DatabaseSyncedDatabaseTable#logical_database_name}.
        :param spec: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#spec DatabaseSyncedDatabaseTable#spec}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#workspace_id DatabaseSyncedDatabaseTable#workspace_id}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9a2a2d4e1c79ca01a2c20667801075779d4257dee88a84e1909c8745d4b43f7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DatabaseSyncedDatabaseTableConfig(
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
        '''Generates CDKTF code for importing a DatabaseSyncedDatabaseTable resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DatabaseSyncedDatabaseTable to import.
        :param import_from_id: The id of the existing DatabaseSyncedDatabaseTable that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DatabaseSyncedDatabaseTable to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__799d85ea782d4c9595f93cb651bd4a758562263e872a019e61daed3bbea834fc)
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
        new_pipeline_spec: typing.Optional[typing.Union["DatabaseSyncedDatabaseTableSpecNewPipelineSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        primary_key_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        scheduling_policy: typing.Optional[builtins.str] = None,
        source_table_full_name: typing.Optional[builtins.str] = None,
        timeseries_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create_database_objects_if_missing: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#create_database_objects_if_missing DatabaseSyncedDatabaseTable#create_database_objects_if_missing}.
        :param existing_pipeline_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#existing_pipeline_id DatabaseSyncedDatabaseTable#existing_pipeline_id}.
        :param new_pipeline_spec: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#new_pipeline_spec DatabaseSyncedDatabaseTable#new_pipeline_spec}.
        :param primary_key_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#primary_key_columns DatabaseSyncedDatabaseTable#primary_key_columns}.
        :param scheduling_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#scheduling_policy DatabaseSyncedDatabaseTable#scheduling_policy}.
        :param source_table_full_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#source_table_full_name DatabaseSyncedDatabaseTable#source_table_full_name}.
        :param timeseries_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#timeseries_key DatabaseSyncedDatabaseTable#timeseries_key}.
        '''
        value = DatabaseSyncedDatabaseTableSpec(
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
    ) -> "DatabaseSyncedDatabaseTableDataSynchronizationStatusOutputReference":
        return typing.cast("DatabaseSyncedDatabaseTableDataSynchronizationStatusOutputReference", jsii.get(self, "dataSynchronizationStatus"))

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
    def spec(self) -> "DatabaseSyncedDatabaseTableSpecOutputReference":
        return typing.cast("DatabaseSyncedDatabaseTableSpecOutputReference", jsii.get(self, "spec"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DatabaseSyncedDatabaseTableSpec"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DatabaseSyncedDatabaseTableSpec"]], jsii.get(self, "specInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__178430953bd9b61fe1ca4eb5be7d3e99a08c3b627140bf07001c7d0b097e8877)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "databaseInstanceName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logicalDatabaseName")
    def logical_database_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logicalDatabaseName"))

    @logical_database_name.setter
    def logical_database_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d4a7c92bb077fa09089a29c04de47c91fa51bf0b9c459b4f88feffe4fee2fcb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logicalDatabaseName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5815aebe8b19a8c53b98ba9dd583c9115430aac5ce875cf929d79bef55dbe412)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workspaceId")
    def workspace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceId"))

    @workspace_id.setter
    def workspace_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aebaf5d744857e3224cd1afd5d5893f159326729e481d673e0f927196c21eae4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workspaceId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.databaseSyncedDatabaseTable.DatabaseSyncedDatabaseTableConfig",
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
class DatabaseSyncedDatabaseTableConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        spec: typing.Optional[typing.Union["DatabaseSyncedDatabaseTableSpec", typing.Dict[builtins.str, typing.Any]]] = None,
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
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#name DatabaseSyncedDatabaseTable#name}.
        :param database_instance_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#database_instance_name DatabaseSyncedDatabaseTable#database_instance_name}.
        :param logical_database_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#logical_database_name DatabaseSyncedDatabaseTable#logical_database_name}.
        :param spec: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#spec DatabaseSyncedDatabaseTable#spec}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#workspace_id DatabaseSyncedDatabaseTable#workspace_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(spec, dict):
            spec = DatabaseSyncedDatabaseTableSpec(**spec)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3e0283b75cb202eb14faff47712778debf12844ac187c3822d5de6082d719fe)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#name DatabaseSyncedDatabaseTable#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def database_instance_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#database_instance_name DatabaseSyncedDatabaseTable#database_instance_name}.'''
        result = self._values.get("database_instance_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def logical_database_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#logical_database_name DatabaseSyncedDatabaseTable#logical_database_name}.'''
        result = self._values.get("logical_database_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spec(self) -> typing.Optional["DatabaseSyncedDatabaseTableSpec"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#spec DatabaseSyncedDatabaseTable#spec}.'''
        result = self._values.get("spec")
        return typing.cast(typing.Optional["DatabaseSyncedDatabaseTableSpec"], result)

    @builtins.property
    def workspace_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#workspace_id DatabaseSyncedDatabaseTable#workspace_id}.'''
        result = self._values.get("workspace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSyncedDatabaseTableConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.databaseSyncedDatabaseTable.DatabaseSyncedDatabaseTableDataSynchronizationStatus",
    jsii_struct_bases=[],
    name_mapping={
        "continuous_update_status": "continuousUpdateStatus",
        "failed_status": "failedStatus",
        "provisioning_status": "provisioningStatus",
        "triggered_update_status": "triggeredUpdateStatus",
    },
)
class DatabaseSyncedDatabaseTableDataSynchronizationStatus:
    def __init__(
        self,
        *,
        continuous_update_status: typing.Optional[typing.Union["DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus", typing.Dict[builtins.str, typing.Any]]] = None,
        failed_status: typing.Optional[typing.Union["DatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus", typing.Dict[builtins.str, typing.Any]]] = None,
        provisioning_status: typing.Optional[typing.Union["DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus", typing.Dict[builtins.str, typing.Any]]] = None,
        triggered_update_status: typing.Optional[typing.Union["DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param continuous_update_status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#continuous_update_status DatabaseSyncedDatabaseTable#continuous_update_status}.
        :param failed_status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#failed_status DatabaseSyncedDatabaseTable#failed_status}.
        :param provisioning_status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#provisioning_status DatabaseSyncedDatabaseTable#provisioning_status}.
        :param triggered_update_status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#triggered_update_status DatabaseSyncedDatabaseTable#triggered_update_status}.
        '''
        if isinstance(continuous_update_status, dict):
            continuous_update_status = DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus(**continuous_update_status)
        if isinstance(failed_status, dict):
            failed_status = DatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus(**failed_status)
        if isinstance(provisioning_status, dict):
            provisioning_status = DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus(**provisioning_status)
        if isinstance(triggered_update_status, dict):
            triggered_update_status = DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus(**triggered_update_status)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdd3c3cb972bdd7488b3179bbfe26cc2eee6e85bd71450afceb0fef46c3a8f74)
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
    ) -> typing.Optional["DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#continuous_update_status DatabaseSyncedDatabaseTable#continuous_update_status}.'''
        result = self._values.get("continuous_update_status")
        return typing.cast(typing.Optional["DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus"], result)

    @builtins.property
    def failed_status(
        self,
    ) -> typing.Optional["DatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#failed_status DatabaseSyncedDatabaseTable#failed_status}.'''
        result = self._values.get("failed_status")
        return typing.cast(typing.Optional["DatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus"], result)

    @builtins.property
    def provisioning_status(
        self,
    ) -> typing.Optional["DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#provisioning_status DatabaseSyncedDatabaseTable#provisioning_status}.'''
        result = self._values.get("provisioning_status")
        return typing.cast(typing.Optional["DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus"], result)

    @builtins.property
    def triggered_update_status(
        self,
    ) -> typing.Optional["DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#triggered_update_status DatabaseSyncedDatabaseTable#triggered_update_status}.'''
        result = self._values.get("triggered_update_status")
        return typing.cast(typing.Optional["DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSyncedDatabaseTableDataSynchronizationStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.databaseSyncedDatabaseTable.DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.databaseSyncedDatabaseTable.DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgress",
    jsii_struct_bases=[],
    name_mapping={},
)
class DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgress:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgress(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgressOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.databaseSyncedDatabaseTable.DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgressOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__65b58d32325a4429b7bfc564fd738d98f700e78dec28e69f7ca03710fbb94745)
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
    ) -> typing.Optional[DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgress]:
        return typing.cast(typing.Optional[DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgress], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgress],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ea981c9a53d882d3fe422bc971c25b8c088152939fc092aa5d1787de5f2433e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.databaseSyncedDatabaseTable.DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d3230bb871225f7cbb7959a3ebef871299aa752b5065d1569ffd88033e20b09e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="initialPipelineSyncProgress")
    def initial_pipeline_sync_progress(
        self,
    ) -> DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgressOutputReference:
        return typing.cast(DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgressOutputReference, jsii.get(self, "initialPipelineSyncProgress"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7b3b3fc4cb9106b2d058ef8f2228883d8350d81baa5fbda0ebc08840e6ff2b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.databaseSyncedDatabaseTable.DatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class DatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.databaseSyncedDatabaseTable.DatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cf2454026343f95a5ef5f9f1e1dd534c0d5d779bc9e98e95d393d660b3abaf5a)
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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7ac98ed9e0b0e2eded533d30b83a42106c5e45b947401605c0b06c78db63367)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.databaseSyncedDatabaseTable.DatabaseSyncedDatabaseTableDataSynchronizationStatusLastSync",
    jsii_struct_bases=[],
    name_mapping={},
)
class DatabaseSyncedDatabaseTableDataSynchronizationStatusLastSync:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSyncedDatabaseTableDataSynchronizationStatusLastSync(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.databaseSyncedDatabaseTable.DatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncDeltaTableSyncInfo",
    jsii_struct_bases=[],
    name_mapping={},
)
class DatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncDeltaTableSyncInfo:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncDeltaTableSyncInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncDeltaTableSyncInfoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.databaseSyncedDatabaseTable.DatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncDeltaTableSyncInfoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b88f6086edd23fa4de3f4dcb572bd0dceaa544c7dac082c01e2b22d400b5b2f6)
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
    ) -> typing.Optional[DatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncDeltaTableSyncInfo]:
        return typing.cast(typing.Optional[DatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncDeltaTableSyncInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncDeltaTableSyncInfo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30b672cc5144a284c08fdc2924d0549b21f265318de75970891a1384ac83d388)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.databaseSyncedDatabaseTable.DatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2453ab90827a47dd8feda5bffd6abe04d414358dd0d2ad4df77e726dd163cd59)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="deltaTableSyncInfo")
    def delta_table_sync_info(
        self,
    ) -> DatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncDeltaTableSyncInfoOutputReference:
        return typing.cast(DatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncDeltaTableSyncInfoOutputReference, jsii.get(self, "deltaTableSyncInfo"))

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
    ) -> typing.Optional[DatabaseSyncedDatabaseTableDataSynchronizationStatusLastSync]:
        return typing.cast(typing.Optional[DatabaseSyncedDatabaseTableDataSynchronizationStatusLastSync], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatabaseSyncedDatabaseTableDataSynchronizationStatusLastSync],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b25d5d11123c0099d8fff2e8e413e89dd8bb61f2ca56bb4028ca1e76e2efc1a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DatabaseSyncedDatabaseTableDataSynchronizationStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.databaseSyncedDatabaseTable.DatabaseSyncedDatabaseTableDataSynchronizationStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3628726f299ddb824311964bc15de43267030cb98d43c5d0658f6d15b8d3f444)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putContinuousUpdateStatus")
    def put_continuous_update_status(self) -> None:
        value = DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus()

        return typing.cast(None, jsii.invoke(self, "putContinuousUpdateStatus", [value]))

    @jsii.member(jsii_name="putFailedStatus")
    def put_failed_status(self) -> None:
        value = DatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus()

        return typing.cast(None, jsii.invoke(self, "putFailedStatus", [value]))

    @jsii.member(jsii_name="putProvisioningStatus")
    def put_provisioning_status(self) -> None:
        value = DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus()

        return typing.cast(None, jsii.invoke(self, "putProvisioningStatus", [value]))

    @jsii.member(jsii_name="putTriggeredUpdateStatus")
    def put_triggered_update_status(self) -> None:
        value = DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus()

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
    ) -> DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusOutputReference:
        return typing.cast(DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusOutputReference, jsii.get(self, "continuousUpdateStatus"))

    @builtins.property
    @jsii.member(jsii_name="detailedState")
    def detailed_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "detailedState"))

    @builtins.property
    @jsii.member(jsii_name="failedStatus")
    def failed_status(
        self,
    ) -> DatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatusOutputReference:
        return typing.cast(DatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatusOutputReference, jsii.get(self, "failedStatus"))

    @builtins.property
    @jsii.member(jsii_name="lastSync")
    def last_sync(
        self,
    ) -> DatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncOutputReference:
        return typing.cast(DatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncOutputReference, jsii.get(self, "lastSync"))

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
    ) -> "DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusOutputReference":
        return typing.cast("DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusOutputReference", jsii.get(self, "provisioningStatus"))

    @builtins.property
    @jsii.member(jsii_name="triggeredUpdateStatus")
    def triggered_update_status(
        self,
    ) -> "DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusOutputReference":
        return typing.cast("DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusOutputReference", jsii.get(self, "triggeredUpdateStatus"))

    @builtins.property
    @jsii.member(jsii_name="continuousUpdateStatusInput")
    def continuous_update_status_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus]], jsii.get(self, "continuousUpdateStatusInput"))

    @builtins.property
    @jsii.member(jsii_name="failedStatusInput")
    def failed_status_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus]], jsii.get(self, "failedStatusInput"))

    @builtins.property
    @jsii.member(jsii_name="provisioningStatusInput")
    def provisioning_status_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus"]], jsii.get(self, "provisioningStatusInput"))

    @builtins.property
    @jsii.member(jsii_name="triggeredUpdateStatusInput")
    def triggered_update_status_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus"]], jsii.get(self, "triggeredUpdateStatusInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DatabaseSyncedDatabaseTableDataSynchronizationStatus]:
        return typing.cast(typing.Optional[DatabaseSyncedDatabaseTableDataSynchronizationStatus], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatabaseSyncedDatabaseTableDataSynchronizationStatus],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6627cccbe027f4811677dd09c31138dd90e9c3bca5a5ca1502236c94529e2d73)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.databaseSyncedDatabaseTable.DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.databaseSyncedDatabaseTable.DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgress",
    jsii_struct_bases=[],
    name_mapping={},
)
class DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgress:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgress(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgressOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.databaseSyncedDatabaseTable.DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgressOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__36c560e1e9e9f58129a721a9205ca09c73d46bf419ef40f986cb7f32235a11a0)
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
    ) -> typing.Optional[DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgress]:
        return typing.cast(typing.Optional[DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgress], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgress],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ab5e2cf988460621306ea4a1b86d78b4f0987c5e7848d06831879596a89bbd9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.databaseSyncedDatabaseTable.DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1adeafb5d4d73b901b1aef16084582d512fb5a1ef362630de552a79cf73a5e77)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="initialPipelineSyncProgress")
    def initial_pipeline_sync_progress(
        self,
    ) -> DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgressOutputReference:
        return typing.cast(DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgressOutputReference, jsii.get(self, "initialPipelineSyncProgress"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d7280bc515a43aa56aa6c812f6ea8bc2213a7c30e4c700ed8accca9f380d23d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.databaseSyncedDatabaseTable.DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.databaseSyncedDatabaseTable.DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__39ca9161b5e2b9588070dbc31ee1350bb037f5f85475ed1d245bb334cd48ae9c)
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
    ) -> "DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgressOutputReference":
        return typing.cast("DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgressOutputReference", jsii.get(self, "triggeredUpdateProgress"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8c37d55bd9ae378c6ae6cc20c98ee6c9be21d8c4fc12532deff0672572ff0f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.databaseSyncedDatabaseTable.DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgress",
    jsii_struct_bases=[],
    name_mapping={},
)
class DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgress:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgress(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgressOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.databaseSyncedDatabaseTable.DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgressOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__51450c86a511dd106bed77d7b721d4bee75bc0da68c050a8d818baf70949d7b0)
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
    ) -> typing.Optional[DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgress]:
        return typing.cast(typing.Optional[DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgress], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgress],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44b58d3360a6233f938ad135e1ac49e7fb98667543954064216b5d9338ba908e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.databaseSyncedDatabaseTable.DatabaseSyncedDatabaseTableSpec",
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
class DatabaseSyncedDatabaseTableSpec:
    def __init__(
        self,
        *,
        create_database_objects_if_missing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        existing_pipeline_id: typing.Optional[builtins.str] = None,
        new_pipeline_spec: typing.Optional[typing.Union["DatabaseSyncedDatabaseTableSpecNewPipelineSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        primary_key_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        scheduling_policy: typing.Optional[builtins.str] = None,
        source_table_full_name: typing.Optional[builtins.str] = None,
        timeseries_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create_database_objects_if_missing: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#create_database_objects_if_missing DatabaseSyncedDatabaseTable#create_database_objects_if_missing}.
        :param existing_pipeline_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#existing_pipeline_id DatabaseSyncedDatabaseTable#existing_pipeline_id}.
        :param new_pipeline_spec: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#new_pipeline_spec DatabaseSyncedDatabaseTable#new_pipeline_spec}.
        :param primary_key_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#primary_key_columns DatabaseSyncedDatabaseTable#primary_key_columns}.
        :param scheduling_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#scheduling_policy DatabaseSyncedDatabaseTable#scheduling_policy}.
        :param source_table_full_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#source_table_full_name DatabaseSyncedDatabaseTable#source_table_full_name}.
        :param timeseries_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#timeseries_key DatabaseSyncedDatabaseTable#timeseries_key}.
        '''
        if isinstance(new_pipeline_spec, dict):
            new_pipeline_spec = DatabaseSyncedDatabaseTableSpecNewPipelineSpec(**new_pipeline_spec)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dda8c33bed79bf44ad0288a3a2d36b68ee5ceaffa8b7d79e8780caa8e955b98f)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#create_database_objects_if_missing DatabaseSyncedDatabaseTable#create_database_objects_if_missing}.'''
        result = self._values.get("create_database_objects_if_missing")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def existing_pipeline_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#existing_pipeline_id DatabaseSyncedDatabaseTable#existing_pipeline_id}.'''
        result = self._values.get("existing_pipeline_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def new_pipeline_spec(
        self,
    ) -> typing.Optional["DatabaseSyncedDatabaseTableSpecNewPipelineSpec"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#new_pipeline_spec DatabaseSyncedDatabaseTable#new_pipeline_spec}.'''
        result = self._values.get("new_pipeline_spec")
        return typing.cast(typing.Optional["DatabaseSyncedDatabaseTableSpecNewPipelineSpec"], result)

    @builtins.property
    def primary_key_columns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#primary_key_columns DatabaseSyncedDatabaseTable#primary_key_columns}.'''
        result = self._values.get("primary_key_columns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def scheduling_policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#scheduling_policy DatabaseSyncedDatabaseTable#scheduling_policy}.'''
        result = self._values.get("scheduling_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_table_full_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#source_table_full_name DatabaseSyncedDatabaseTable#source_table_full_name}.'''
        result = self._values.get("source_table_full_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeseries_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#timeseries_key DatabaseSyncedDatabaseTable#timeseries_key}.'''
        result = self._values.get("timeseries_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSyncedDatabaseTableSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.databaseSyncedDatabaseTable.DatabaseSyncedDatabaseTableSpecNewPipelineSpec",
    jsii_struct_bases=[],
    name_mapping={
        "storage_catalog": "storageCatalog",
        "storage_schema": "storageSchema",
    },
)
class DatabaseSyncedDatabaseTableSpecNewPipelineSpec:
    def __init__(
        self,
        *,
        storage_catalog: typing.Optional[builtins.str] = None,
        storage_schema: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param storage_catalog: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#storage_catalog DatabaseSyncedDatabaseTable#storage_catalog}.
        :param storage_schema: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#storage_schema DatabaseSyncedDatabaseTable#storage_schema}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d8c8331c0e6cf0cc565c6556e2e6ecf35af965d5131603738da546e25f4e8b7)
            check_type(argname="argument storage_catalog", value=storage_catalog, expected_type=type_hints["storage_catalog"])
            check_type(argname="argument storage_schema", value=storage_schema, expected_type=type_hints["storage_schema"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if storage_catalog is not None:
            self._values["storage_catalog"] = storage_catalog
        if storage_schema is not None:
            self._values["storage_schema"] = storage_schema

    @builtins.property
    def storage_catalog(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#storage_catalog DatabaseSyncedDatabaseTable#storage_catalog}.'''
        result = self._values.get("storage_catalog")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def storage_schema(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#storage_schema DatabaseSyncedDatabaseTable#storage_schema}.'''
        result = self._values.get("storage_schema")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSyncedDatabaseTableSpecNewPipelineSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatabaseSyncedDatabaseTableSpecNewPipelineSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.databaseSyncedDatabaseTable.DatabaseSyncedDatabaseTableSpecNewPipelineSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1233b3e904017f9fdc4c6eee87d071f9b261b17919b1bfde8eb5411585e12269)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f494bc0b3360adf3641485b8e6d9c40e75774e900815daf7ce79608e3124054f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageCatalog", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storageSchema")
    def storage_schema(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageSchema"))

    @storage_schema.setter
    def storage_schema(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d43a95206499e51e5439321116508c4960be54d7af89caa9edc1b30964f2e424)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageSchema", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableSpecNewPipelineSpec]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableSpecNewPipelineSpec]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableSpecNewPipelineSpec]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f122c5460cefc866b08b78c58f25cadd7261072715725dc1a98777fcd07422a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DatabaseSyncedDatabaseTableSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.databaseSyncedDatabaseTable.DatabaseSyncedDatabaseTableSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__de68444c436b8cfa4d16586a5371f84093cd3998a4b2fc6ed9bd7a89732881aa)
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
        :param storage_catalog: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#storage_catalog DatabaseSyncedDatabaseTable#storage_catalog}.
        :param storage_schema: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/database_synced_database_table#storage_schema DatabaseSyncedDatabaseTable#storage_schema}.
        '''
        value = DatabaseSyncedDatabaseTableSpecNewPipelineSpec(
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
    ) -> DatabaseSyncedDatabaseTableSpecNewPipelineSpecOutputReference:
        return typing.cast(DatabaseSyncedDatabaseTableSpecNewPipelineSpecOutputReference, jsii.get(self, "newPipelineSpec"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableSpecNewPipelineSpec]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableSpecNewPipelineSpec]], jsii.get(self, "newPipelineSpecInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__19748faef4020ab3e06d10e1edb9e82c154e609062007744b41a3345f77ade1e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createDatabaseObjectsIfMissing", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="existingPipelineId")
    def existing_pipeline_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "existingPipelineId"))

    @existing_pipeline_id.setter
    def existing_pipeline_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98c74dadfc0554e1192e265255878c0b2cf75364539143bcea2beb343ad1a0a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "existingPipelineId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="primaryKeyColumns")
    def primary_key_columns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "primaryKeyColumns"))

    @primary_key_columns.setter
    def primary_key_columns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4c35a129e70e3cd2760e7cbf703578b95860a8ae01ef995045a0118d1738a1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "primaryKeyColumns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="schedulingPolicy")
    def scheduling_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schedulingPolicy"))

    @scheduling_policy.setter
    def scheduling_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86bd52d54c736dd1d3182c529d235e9ec8278b7a54cb2eae72e657954c82dddd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "schedulingPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceTableFullName")
    def source_table_full_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceTableFullName"))

    @source_table_full_name.setter
    def source_table_full_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4caa36b1b1c7b4a29346722b08c518f75fe013ea302b97acf9529ac2f43c0dbd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceTableFullName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeseriesKey")
    def timeseries_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeseriesKey"))

    @timeseries_key.setter
    def timeseries_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0ad0fc72ab70989114edd2ed949d8bc4f656bb3321b3444374af4e6225df7cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeseriesKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableSpec]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableSpec]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableSpec]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e044883885683fdc143bb4edca25dcad3bf1d3aadcfc20c5698e6562b55cc57)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DatabaseSyncedDatabaseTable",
    "DatabaseSyncedDatabaseTableConfig",
    "DatabaseSyncedDatabaseTableDataSynchronizationStatus",
    "DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus",
    "DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgress",
    "DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgressOutputReference",
    "DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusOutputReference",
    "DatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus",
    "DatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatusOutputReference",
    "DatabaseSyncedDatabaseTableDataSynchronizationStatusLastSync",
    "DatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncDeltaTableSyncInfo",
    "DatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncDeltaTableSyncInfoOutputReference",
    "DatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncOutputReference",
    "DatabaseSyncedDatabaseTableDataSynchronizationStatusOutputReference",
    "DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus",
    "DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgress",
    "DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgressOutputReference",
    "DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusOutputReference",
    "DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus",
    "DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusOutputReference",
    "DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgress",
    "DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgressOutputReference",
    "DatabaseSyncedDatabaseTableSpec",
    "DatabaseSyncedDatabaseTableSpecNewPipelineSpec",
    "DatabaseSyncedDatabaseTableSpecNewPipelineSpecOutputReference",
    "DatabaseSyncedDatabaseTableSpecOutputReference",
]

publication.publish()

def _typecheckingstub__b9a2a2d4e1c79ca01a2c20667801075779d4257dee88a84e1909c8745d4b43f7(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    name: builtins.str,
    database_instance_name: typing.Optional[builtins.str] = None,
    logical_database_name: typing.Optional[builtins.str] = None,
    spec: typing.Optional[typing.Union[DatabaseSyncedDatabaseTableSpec, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__799d85ea782d4c9595f93cb651bd4a758562263e872a019e61daed3bbea834fc(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__178430953bd9b61fe1ca4eb5be7d3e99a08c3b627140bf07001c7d0b097e8877(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d4a7c92bb077fa09089a29c04de47c91fa51bf0b9c459b4f88feffe4fee2fcb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5815aebe8b19a8c53b98ba9dd583c9115430aac5ce875cf929d79bef55dbe412(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aebaf5d744857e3224cd1afd5d5893f159326729e481d673e0f927196c21eae4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3e0283b75cb202eb14faff47712778debf12844ac187c3822d5de6082d719fe(
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
    spec: typing.Optional[typing.Union[DatabaseSyncedDatabaseTableSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    workspace_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdd3c3cb972bdd7488b3179bbfe26cc2eee6e85bd71450afceb0fef46c3a8f74(
    *,
    continuous_update_status: typing.Optional[typing.Union[DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus, typing.Dict[builtins.str, typing.Any]]] = None,
    failed_status: typing.Optional[typing.Union[DatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus, typing.Dict[builtins.str, typing.Any]]] = None,
    provisioning_status: typing.Optional[typing.Union[DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus, typing.Dict[builtins.str, typing.Any]]] = None,
    triggered_update_status: typing.Optional[typing.Union[DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65b58d32325a4429b7bfc564fd738d98f700e78dec28e69f7ca03710fbb94745(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ea981c9a53d882d3fe422bc971c25b8c088152939fc092aa5d1787de5f2433e(
    value: typing.Optional[DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgress],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3230bb871225f7cbb7959a3ebef871299aa752b5065d1569ffd88033e20b09e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7b3b3fc4cb9106b2d058ef8f2228883d8350d81baa5fbda0ebc08840e6ff2b8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableDataSynchronizationStatusContinuousUpdateStatus]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf2454026343f95a5ef5f9f1e1dd534c0d5d779bc9e98e95d393d660b3abaf5a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7ac98ed9e0b0e2eded533d30b83a42106c5e45b947401605c0b06c78db63367(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableDataSynchronizationStatusFailedStatus]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b88f6086edd23fa4de3f4dcb572bd0dceaa544c7dac082c01e2b22d400b5b2f6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30b672cc5144a284c08fdc2924d0549b21f265318de75970891a1384ac83d388(
    value: typing.Optional[DatabaseSyncedDatabaseTableDataSynchronizationStatusLastSyncDeltaTableSyncInfo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2453ab90827a47dd8feda5bffd6abe04d414358dd0d2ad4df77e726dd163cd59(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b25d5d11123c0099d8fff2e8e413e89dd8bb61f2ca56bb4028ca1e76e2efc1a(
    value: typing.Optional[DatabaseSyncedDatabaseTableDataSynchronizationStatusLastSync],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3628726f299ddb824311964bc15de43267030cb98d43c5d0658f6d15b8d3f444(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6627cccbe027f4811677dd09c31138dd90e9c3bca5a5ca1502236c94529e2d73(
    value: typing.Optional[DatabaseSyncedDatabaseTableDataSynchronizationStatus],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36c560e1e9e9f58129a721a9205ca09c73d46bf419ef40f986cb7f32235a11a0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ab5e2cf988460621306ea4a1b86d78b4f0987c5e7848d06831879596a89bbd9(
    value: typing.Optional[DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgress],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1adeafb5d4d73b901b1aef16084582d512fb5a1ef362630de552a79cf73a5e77(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d7280bc515a43aa56aa6c812f6ea8bc2213a7c30e4c700ed8accca9f380d23d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableDataSynchronizationStatusProvisioningStatus]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39ca9161b5e2b9588070dbc31ee1350bb037f5f85475ed1d245bb334cd48ae9c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8c37d55bd9ae378c6ae6cc20c98ee6c9be21d8c4fc12532deff0672572ff0f9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatus]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51450c86a511dd106bed77d7b721d4bee75bc0da68c050a8d818baf70949d7b0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44b58d3360a6233f938ad135e1ac49e7fb98667543954064216b5d9338ba908e(
    value: typing.Optional[DatabaseSyncedDatabaseTableDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgress],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dda8c33bed79bf44ad0288a3a2d36b68ee5ceaffa8b7d79e8780caa8e955b98f(
    *,
    create_database_objects_if_missing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    existing_pipeline_id: typing.Optional[builtins.str] = None,
    new_pipeline_spec: typing.Optional[typing.Union[DatabaseSyncedDatabaseTableSpecNewPipelineSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    primary_key_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
    scheduling_policy: typing.Optional[builtins.str] = None,
    source_table_full_name: typing.Optional[builtins.str] = None,
    timeseries_key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d8c8331c0e6cf0cc565c6556e2e6ecf35af965d5131603738da546e25f4e8b7(
    *,
    storage_catalog: typing.Optional[builtins.str] = None,
    storage_schema: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1233b3e904017f9fdc4c6eee87d071f9b261b17919b1bfde8eb5411585e12269(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f494bc0b3360adf3641485b8e6d9c40e75774e900815daf7ce79608e3124054f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d43a95206499e51e5439321116508c4960be54d7af89caa9edc1b30964f2e424(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f122c5460cefc866b08b78c58f25cadd7261072715725dc1a98777fcd07422a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableSpecNewPipelineSpec]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de68444c436b8cfa4d16586a5371f84093cd3998a4b2fc6ed9bd7a89732881aa(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19748faef4020ab3e06d10e1edb9e82c154e609062007744b41a3345f77ade1e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98c74dadfc0554e1192e265255878c0b2cf75364539143bcea2beb343ad1a0a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4c35a129e70e3cd2760e7cbf703578b95860a8ae01ef995045a0118d1738a1c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86bd52d54c736dd1d3182c529d235e9ec8278b7a54cb2eae72e657954c82dddd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4caa36b1b1c7b4a29346722b08c518f75fe013ea302b97acf9529ac2f43c0dbd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0ad0fc72ab70989114edd2ed949d8bc4f656bb3321b3444374af4e6225df7cf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e044883885683fdc143bb4edca25dcad3bf1d3aadcfc20c5698e6562b55cc57(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseSyncedDatabaseTableSpec]],
) -> None:
    """Type checking stubs"""
    pass
