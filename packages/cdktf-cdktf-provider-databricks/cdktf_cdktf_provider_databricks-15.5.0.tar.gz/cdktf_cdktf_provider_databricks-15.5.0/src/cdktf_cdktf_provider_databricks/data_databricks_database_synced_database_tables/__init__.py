r'''
# `data_databricks_database_synced_database_tables`

Refer to the Terraform Registry for docs: [`data_databricks_database_synced_database_tables`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables).
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


class DataDatabricksDatabaseSyncedDatabaseTables(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTables.DataDatabricksDatabaseSyncedDatabaseTables",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables databricks_database_synced_database_tables}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        workspace_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables databricks_database_synced_database_tables} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#workspace_id DataDatabricksDatabaseSyncedDatabaseTables#workspace_id}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92b8cfcefc4298989f832cd2f9f62d9e05d01d7e7b50278c22d5a5a66c024398)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataDatabricksDatabaseSyncedDatabaseTablesConfig(
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
        '''Generates CDKTF code for importing a DataDatabricksDatabaseSyncedDatabaseTables resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDatabricksDatabaseSyncedDatabaseTables to import.
        :param import_from_id: The id of the existing DataDatabricksDatabaseSyncedDatabaseTables that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDatabricksDatabaseSyncedDatabaseTables to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6433d77d00ae3aec6e4a465f8d0a7c0701a31836f6585c309ea6cd2b73b1be91)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

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
    @jsii.member(jsii_name="syncedTables")
    def synced_tables(
        self,
    ) -> "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesList":
        return typing.cast("DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesList", jsii.get(self, "syncedTables"))

    @builtins.property
    @jsii.member(jsii_name="workspaceIdInput")
    def workspace_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workspaceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="workspaceId")
    def workspace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceId"))

    @workspace_id.setter
    def workspace_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff785fb08f2b47a020c589aede68ba041f8cd8be06cce09e814bc3c547c1186c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workspaceId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTables.DataDatabricksDatabaseSyncedDatabaseTablesConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "workspace_id": "workspaceId",
    },
)
class DataDatabricksDatabaseSyncedDatabaseTablesConfig(
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
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#workspace_id DataDatabricksDatabaseSyncedDatabaseTables#workspace_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4af4f6f6de6ec338f2dccda5c1719baf885945c806acf2a82191adf2e9080285)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument workspace_id", value=workspace_id, expected_type=type_hints["workspace_id"])
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
    def workspace_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#workspace_id DataDatabricksDatabaseSyncedDatabaseTables#workspace_id}.'''
        result = self._values.get("workspace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseSyncedDatabaseTablesConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTables.DataDatabricksDatabaseSyncedDatabaseTablesSyncedTables",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "database_instance_name": "databaseInstanceName",
        "logical_database_name": "logicalDatabaseName",
        "spec": "spec",
    },
)
class DataDatabricksDatabaseSyncedDatabaseTablesSyncedTables:
    def __init__(
        self,
        *,
        name: builtins.str,
        database_instance_name: typing.Optional[builtins.str] = None,
        logical_database_name: typing.Optional[builtins.str] = None,
        spec: typing.Optional[typing.Union["DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpec", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#name DataDatabricksDatabaseSyncedDatabaseTables#name}.
        :param database_instance_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#database_instance_name DataDatabricksDatabaseSyncedDatabaseTables#database_instance_name}.
        :param logical_database_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#logical_database_name DataDatabricksDatabaseSyncedDatabaseTables#logical_database_name}.
        :param spec: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#spec DataDatabricksDatabaseSyncedDatabaseTables#spec}.
        '''
        if isinstance(spec, dict):
            spec = DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpec(**spec)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__920179304dd3fb777e19363e15e0b0849292d73fe5595b9d02a496d32a27dd7f)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument database_instance_name", value=database_instance_name, expected_type=type_hints["database_instance_name"])
            check_type(argname="argument logical_database_name", value=logical_database_name, expected_type=type_hints["logical_database_name"])
            check_type(argname="argument spec", value=spec, expected_type=type_hints["spec"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if database_instance_name is not None:
            self._values["database_instance_name"] = database_instance_name
        if logical_database_name is not None:
            self._values["logical_database_name"] = logical_database_name
        if spec is not None:
            self._values["spec"] = spec

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#name DataDatabricksDatabaseSyncedDatabaseTables#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def database_instance_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#database_instance_name DataDatabricksDatabaseSyncedDatabaseTables#database_instance_name}.'''
        result = self._values.get("database_instance_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def logical_database_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#logical_database_name DataDatabricksDatabaseSyncedDatabaseTables#logical_database_name}.'''
        result = self._values.get("logical_database_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spec(
        self,
    ) -> typing.Optional["DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpec"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#spec DataDatabricksDatabaseSyncedDatabaseTables#spec}.'''
        result = self._values.get("spec")
        return typing.cast(typing.Optional["DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpec"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTables(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTables.DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatus",
    jsii_struct_bases=[],
    name_mapping={
        "continuous_update_status": "continuousUpdateStatus",
        "failed_status": "failedStatus",
        "provisioning_status": "provisioningStatus",
        "triggered_update_status": "triggeredUpdateStatus",
    },
)
class DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatus:
    def __init__(
        self,
        *,
        continuous_update_status: typing.Optional[typing.Union["DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatus", typing.Dict[builtins.str, typing.Any]]] = None,
        failed_status: typing.Optional[typing.Union["DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusFailedStatus", typing.Dict[builtins.str, typing.Any]]] = None,
        provisioning_status: typing.Optional[typing.Union["DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatus", typing.Dict[builtins.str, typing.Any]]] = None,
        triggered_update_status: typing.Optional[typing.Union["DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatus", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param continuous_update_status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#continuous_update_status DataDatabricksDatabaseSyncedDatabaseTables#continuous_update_status}.
        :param failed_status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#failed_status DataDatabricksDatabaseSyncedDatabaseTables#failed_status}.
        :param provisioning_status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#provisioning_status DataDatabricksDatabaseSyncedDatabaseTables#provisioning_status}.
        :param triggered_update_status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#triggered_update_status DataDatabricksDatabaseSyncedDatabaseTables#triggered_update_status}.
        '''
        if isinstance(continuous_update_status, dict):
            continuous_update_status = DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatus(**continuous_update_status)
        if isinstance(failed_status, dict):
            failed_status = DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusFailedStatus(**failed_status)
        if isinstance(provisioning_status, dict):
            provisioning_status = DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatus(**provisioning_status)
        if isinstance(triggered_update_status, dict):
            triggered_update_status = DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatus(**triggered_update_status)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e82a97e318895968a55cfe64c348b1853160149180ef2b3f35809a216678d1a5)
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
    ) -> typing.Optional["DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatus"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#continuous_update_status DataDatabricksDatabaseSyncedDatabaseTables#continuous_update_status}.'''
        result = self._values.get("continuous_update_status")
        return typing.cast(typing.Optional["DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatus"], result)

    @builtins.property
    def failed_status(
        self,
    ) -> typing.Optional["DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusFailedStatus"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#failed_status DataDatabricksDatabaseSyncedDatabaseTables#failed_status}.'''
        result = self._values.get("failed_status")
        return typing.cast(typing.Optional["DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusFailedStatus"], result)

    @builtins.property
    def provisioning_status(
        self,
    ) -> typing.Optional["DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatus"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#provisioning_status DataDatabricksDatabaseSyncedDatabaseTables#provisioning_status}.'''
        result = self._values.get("provisioning_status")
        return typing.cast(typing.Optional["DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatus"], result)

    @builtins.property
    def triggered_update_status(
        self,
    ) -> typing.Optional["DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatus"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#triggered_update_status DataDatabricksDatabaseSyncedDatabaseTables#triggered_update_status}.'''
        result = self._values.get("triggered_update_status")
        return typing.cast(typing.Optional["DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatus"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTables.DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTables.DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgress",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgress:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgress(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgressOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTables.DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgressOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__83b990665e10fb5cbc3d3855a4e54c9dac7f2dbd57a3825e27c43e5747a2366c)
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
    ) -> typing.Optional[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgress]:
        return typing.cast(typing.Optional[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgress], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgress],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9ca4dda8713bb2c590e5d3d0d897d00135e08bb22b842e011e30f014ac5fe08)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTables.DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dff6b1d5bf141239e80489e00b509f205783e6a4aceaae85d767eee77aefcc4d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="initialPipelineSyncProgress")
    def initial_pipeline_sync_progress(
        self,
    ) -> DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgressOutputReference:
        return typing.cast(DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgressOutputReference, jsii.get(self, "initialPipelineSyncProgress"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatus]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatus]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatus]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d36c8c4b327e707e0143af2c9e6e8df5482ef4adb1293c7cd3b02c29d8dcaecc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTables.DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusFailedStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusFailedStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusFailedStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusFailedStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTables.DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusFailedStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7fe23f004e8c501f0fe59cf1f4c3a3636bc081f56f8f6ebd3c8c4d9bfff7ab99)
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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusFailedStatus]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusFailedStatus]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusFailedStatus]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d343ff33f679bf75242f1c7be350ceac1ae6abe1bdf8946999b7e93fa1a75ca8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTables.DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusLastSync",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusLastSync:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusLastSync(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTables.DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusLastSyncDeltaTableSyncInfo",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusLastSyncDeltaTableSyncInfo:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusLastSyncDeltaTableSyncInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusLastSyncDeltaTableSyncInfoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTables.DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusLastSyncDeltaTableSyncInfoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fddee2db7185a75959dd5b0bc27b9ee3baa983c62cc20307f450627472c30870)
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
    ) -> typing.Optional[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusLastSyncDeltaTableSyncInfo]:
        return typing.cast(typing.Optional[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusLastSyncDeltaTableSyncInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusLastSyncDeltaTableSyncInfo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5e09b0c36ad6b881eede33922915fcabe2afe738a168bba738c0fec602da804)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusLastSyncOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTables.DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusLastSyncOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2d105be8529c4714c7c7b921e8595022fa0654bda9c0e00a6db3d2e13bdb1eec)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="deltaTableSyncInfo")
    def delta_table_sync_info(
        self,
    ) -> DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusLastSyncDeltaTableSyncInfoOutputReference:
        return typing.cast(DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusLastSyncDeltaTableSyncInfoOutputReference, jsii.get(self, "deltaTableSyncInfo"))

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
    ) -> typing.Optional[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusLastSync]:
        return typing.cast(typing.Optional[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusLastSync], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusLastSync],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24d8cf3b1ec6a21a1f3562dd76c2908235bf9cb810bf0dfd728106a5526e4bd2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTables.DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e95902c081a08b023ed48549264b16d5e5349b27a89146880b87379ece2787e7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putContinuousUpdateStatus")
    def put_continuous_update_status(self) -> None:
        value = DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatus()

        return typing.cast(None, jsii.invoke(self, "putContinuousUpdateStatus", [value]))

    @jsii.member(jsii_name="putFailedStatus")
    def put_failed_status(self) -> None:
        value = DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusFailedStatus()

        return typing.cast(None, jsii.invoke(self, "putFailedStatus", [value]))

    @jsii.member(jsii_name="putProvisioningStatus")
    def put_provisioning_status(self) -> None:
        value = DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatus()

        return typing.cast(None, jsii.invoke(self, "putProvisioningStatus", [value]))

    @jsii.member(jsii_name="putTriggeredUpdateStatus")
    def put_triggered_update_status(self) -> None:
        value = DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatus()

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
    ) -> DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatusOutputReference:
        return typing.cast(DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatusOutputReference, jsii.get(self, "continuousUpdateStatus"))

    @builtins.property
    @jsii.member(jsii_name="detailedState")
    def detailed_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "detailedState"))

    @builtins.property
    @jsii.member(jsii_name="failedStatus")
    def failed_status(
        self,
    ) -> DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusFailedStatusOutputReference:
        return typing.cast(DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusFailedStatusOutputReference, jsii.get(self, "failedStatus"))

    @builtins.property
    @jsii.member(jsii_name="lastSync")
    def last_sync(
        self,
    ) -> DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusLastSyncOutputReference:
        return typing.cast(DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusLastSyncOutputReference, jsii.get(self, "lastSync"))

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
    ) -> "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatusOutputReference":
        return typing.cast("DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatusOutputReference", jsii.get(self, "provisioningStatus"))

    @builtins.property
    @jsii.member(jsii_name="triggeredUpdateStatus")
    def triggered_update_status(
        self,
    ) -> "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatusOutputReference":
        return typing.cast("DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatusOutputReference", jsii.get(self, "triggeredUpdateStatus"))

    @builtins.property
    @jsii.member(jsii_name="continuousUpdateStatusInput")
    def continuous_update_status_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatus]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatus]], jsii.get(self, "continuousUpdateStatusInput"))

    @builtins.property
    @jsii.member(jsii_name="failedStatusInput")
    def failed_status_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusFailedStatus]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusFailedStatus]], jsii.get(self, "failedStatusInput"))

    @builtins.property
    @jsii.member(jsii_name="provisioningStatusInput")
    def provisioning_status_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatus"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatus"]], jsii.get(self, "provisioningStatusInput"))

    @builtins.property
    @jsii.member(jsii_name="triggeredUpdateStatusInput")
    def triggered_update_status_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatus"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatus"]], jsii.get(self, "triggeredUpdateStatusInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatus]:
        return typing.cast(typing.Optional[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatus], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatus],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5bfb1af639ebb796e42f8ea971cf2d14ffd7e46b23eec02b956d7aefc98f1d1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTables.DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTables.DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgress",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgress:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgress(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgressOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTables.DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgressOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c26995b6e316af98081e15b7c1e65aefa8777dbca356106ef4df7de71893c702)
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
    ) -> typing.Optional[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgress]:
        return typing.cast(typing.Optional[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgress], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgress],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1f074d01a128c02cad18e8495204509380e217e1de644717f6a9ce464dc6b90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTables.DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d4ad271645849be89255c0639d56c2166d04d766a16134a30c862ee9fe58d09b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="initialPipelineSyncProgress")
    def initial_pipeline_sync_progress(
        self,
    ) -> DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgressOutputReference:
        return typing.cast(DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgressOutputReference, jsii.get(self, "initialPipelineSyncProgress"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatus]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatus]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatus]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2a8bb1c3be832d155b34a4b9e41793f716d1f4cde6adf273e6088518dfa02dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTables.DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTables.DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b5c19b947b4bcd724d872166f6a4627febed7c394b9b0d1593cad4198a912b89)
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
    ) -> "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgressOutputReference":
        return typing.cast("DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgressOutputReference", jsii.get(self, "triggeredUpdateProgress"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatus]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatus]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatus]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d20cfb08028247bcedb8ccec7eea9370ddcafa61d42172254ed3094c4e3627d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTables.DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgress",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgress:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgress(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgressOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTables.DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgressOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f4801d5a490511e3cb824c788af93806b256f0344af165cc40c8aec3ef393b22)
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
    ) -> typing.Optional[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgress]:
        return typing.cast(typing.Optional[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgress], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgress],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d7fc46822ae77d4c4cfaf1497c8d5322d96a25fbec1739a4773399bbe66ed19)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTables.DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f15800ee73768bd6b0363210fa937691fb53186863f0470ad3f76b61906d85a5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a902596bebbd701afa25b4fe5a2c874e618b84e4f72b903586c90a7ed006a29)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b007d6e6e18e76b2931bc86e50f4933b611f60f665e28f792f8f83cff84dc77)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ab57dac407ad79315e38ff74009ce461f26e5c3ab6b845abf6336cae6fd3f8b5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bf8615c463e2b7ed7a9f8349dd0f7e6bcb75c49690204d4f77139642e8a5614e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTables]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTables]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTables]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8d51a6308c4722d1fc0f5cfae6ea9fe75f8304142eb8aa4eb915f1af7159ede)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTables.DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__062aa852751f1b514dbd80c7df7da565a3e2417dc7e40e6745e94ad28eee17b1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putSpec")
    def put_spec(
        self,
        *,
        create_database_objects_if_missing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        existing_pipeline_id: typing.Optional[builtins.str] = None,
        new_pipeline_spec: typing.Optional[typing.Union["DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpecNewPipelineSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        primary_key_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        scheduling_policy: typing.Optional[builtins.str] = None,
        source_table_full_name: typing.Optional[builtins.str] = None,
        timeseries_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create_database_objects_if_missing: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#create_database_objects_if_missing DataDatabricksDatabaseSyncedDatabaseTables#create_database_objects_if_missing}.
        :param existing_pipeline_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#existing_pipeline_id DataDatabricksDatabaseSyncedDatabaseTables#existing_pipeline_id}.
        :param new_pipeline_spec: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#new_pipeline_spec DataDatabricksDatabaseSyncedDatabaseTables#new_pipeline_spec}.
        :param primary_key_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#primary_key_columns DataDatabricksDatabaseSyncedDatabaseTables#primary_key_columns}.
        :param scheduling_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#scheduling_policy DataDatabricksDatabaseSyncedDatabaseTables#scheduling_policy}.
        :param source_table_full_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#source_table_full_name DataDatabricksDatabaseSyncedDatabaseTables#source_table_full_name}.
        :param timeseries_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#timeseries_key DataDatabricksDatabaseSyncedDatabaseTables#timeseries_key}.
        '''
        value = DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpec(
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

    @builtins.property
    @jsii.member(jsii_name="dataSynchronizationStatus")
    def data_synchronization_status(
        self,
    ) -> DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusOutputReference:
        return typing.cast(DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusOutputReference, jsii.get(self, "dataSynchronizationStatus"))

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
    def spec(
        self,
    ) -> "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpecOutputReference":
        return typing.cast("DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpecOutputReference", jsii.get(self, "spec"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpec"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpec"]], jsii.get(self, "specInput"))

    @builtins.property
    @jsii.member(jsii_name="databaseInstanceName")
    def database_instance_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "databaseInstanceName"))

    @database_instance_name.setter
    def database_instance_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57864b08442beb6e4b19f8fa8ce9b965635464c70bb8acb3abe6ee318c626c6f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "databaseInstanceName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logicalDatabaseName")
    def logical_database_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logicalDatabaseName"))

    @logical_database_name.setter
    def logical_database_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4304e3edbda1f5966d8ee9a5bb1bae0649d867c384bc6e90e096c884ad52ddf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logicalDatabaseName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e188016f4b0b60baea560707b658d5420e726283e1853c7b3ee7b9e54a42ecf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTables]:
        return typing.cast(typing.Optional[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTables], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTables],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d9a90532b77e7c765ecb8921bd35b4e1c43cb7cc86b8eb930e0806fed03c100)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTables.DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpec",
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
class DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpec:
    def __init__(
        self,
        *,
        create_database_objects_if_missing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        existing_pipeline_id: typing.Optional[builtins.str] = None,
        new_pipeline_spec: typing.Optional[typing.Union["DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpecNewPipelineSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        primary_key_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        scheduling_policy: typing.Optional[builtins.str] = None,
        source_table_full_name: typing.Optional[builtins.str] = None,
        timeseries_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create_database_objects_if_missing: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#create_database_objects_if_missing DataDatabricksDatabaseSyncedDatabaseTables#create_database_objects_if_missing}.
        :param existing_pipeline_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#existing_pipeline_id DataDatabricksDatabaseSyncedDatabaseTables#existing_pipeline_id}.
        :param new_pipeline_spec: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#new_pipeline_spec DataDatabricksDatabaseSyncedDatabaseTables#new_pipeline_spec}.
        :param primary_key_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#primary_key_columns DataDatabricksDatabaseSyncedDatabaseTables#primary_key_columns}.
        :param scheduling_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#scheduling_policy DataDatabricksDatabaseSyncedDatabaseTables#scheduling_policy}.
        :param source_table_full_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#source_table_full_name DataDatabricksDatabaseSyncedDatabaseTables#source_table_full_name}.
        :param timeseries_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#timeseries_key DataDatabricksDatabaseSyncedDatabaseTables#timeseries_key}.
        '''
        if isinstance(new_pipeline_spec, dict):
            new_pipeline_spec = DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpecNewPipelineSpec(**new_pipeline_spec)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da9388c7bab00bea8824383e6313b86a0bc8c3bbcd3824c2c583ac7d10e1684d)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#create_database_objects_if_missing DataDatabricksDatabaseSyncedDatabaseTables#create_database_objects_if_missing}.'''
        result = self._values.get("create_database_objects_if_missing")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def existing_pipeline_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#existing_pipeline_id DataDatabricksDatabaseSyncedDatabaseTables#existing_pipeline_id}.'''
        result = self._values.get("existing_pipeline_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def new_pipeline_spec(
        self,
    ) -> typing.Optional["DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpecNewPipelineSpec"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#new_pipeline_spec DataDatabricksDatabaseSyncedDatabaseTables#new_pipeline_spec}.'''
        result = self._values.get("new_pipeline_spec")
        return typing.cast(typing.Optional["DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpecNewPipelineSpec"], result)

    @builtins.property
    def primary_key_columns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#primary_key_columns DataDatabricksDatabaseSyncedDatabaseTables#primary_key_columns}.'''
        result = self._values.get("primary_key_columns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def scheduling_policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#scheduling_policy DataDatabricksDatabaseSyncedDatabaseTables#scheduling_policy}.'''
        result = self._values.get("scheduling_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_table_full_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#source_table_full_name DataDatabricksDatabaseSyncedDatabaseTables#source_table_full_name}.'''
        result = self._values.get("source_table_full_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeseries_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#timeseries_key DataDatabricksDatabaseSyncedDatabaseTables#timeseries_key}.'''
        result = self._values.get("timeseries_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTables.DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpecNewPipelineSpec",
    jsii_struct_bases=[],
    name_mapping={
        "storage_catalog": "storageCatalog",
        "storage_schema": "storageSchema",
    },
)
class DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpecNewPipelineSpec:
    def __init__(
        self,
        *,
        storage_catalog: typing.Optional[builtins.str] = None,
        storage_schema: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param storage_catalog: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#storage_catalog DataDatabricksDatabaseSyncedDatabaseTables#storage_catalog}.
        :param storage_schema: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#storage_schema DataDatabricksDatabaseSyncedDatabaseTables#storage_schema}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af1cc2421002f93423a52994a2d61f753dfcd89026c5f497f97de60be2e09bc7)
            check_type(argname="argument storage_catalog", value=storage_catalog, expected_type=type_hints["storage_catalog"])
            check_type(argname="argument storage_schema", value=storage_schema, expected_type=type_hints["storage_schema"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if storage_catalog is not None:
            self._values["storage_catalog"] = storage_catalog
        if storage_schema is not None:
            self._values["storage_schema"] = storage_schema

    @builtins.property
    def storage_catalog(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#storage_catalog DataDatabricksDatabaseSyncedDatabaseTables#storage_catalog}.'''
        result = self._values.get("storage_catalog")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def storage_schema(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#storage_schema DataDatabricksDatabaseSyncedDatabaseTables#storage_schema}.'''
        result = self._values.get("storage_schema")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpecNewPipelineSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpecNewPipelineSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTables.DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpecNewPipelineSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__171c3989e1487cec2ee78c1e5cbe059621545926b31646df3976eea10aee7205)
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
            type_hints = typing.get_type_hints(_typecheckingstub__28866537df3218a32c556f15f44622db5f0d9f583620473185eba2273e32aa31)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageCatalog", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storageSchema")
    def storage_schema(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageSchema"))

    @storage_schema.setter
    def storage_schema(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdff1ad8939824754ff163366b71e246b782e1d4af51b9d0b49fc342355a31f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageSchema", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpecNewPipelineSpec]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpecNewPipelineSpec]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpecNewPipelineSpec]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f3e6f49725a347f2839cc3036422648e515d1cc133286c378828ef8128fbbe5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseSyncedDatabaseTables.DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cff26820617b89935e16bd7e54bf4b1fed6d7c09078884f51410518bc4169cf1)
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
        :param storage_catalog: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#storage_catalog DataDatabricksDatabaseSyncedDatabaseTables#storage_catalog}.
        :param storage_schema: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_synced_database_tables#storage_schema DataDatabricksDatabaseSyncedDatabaseTables#storage_schema}.
        '''
        value = DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpecNewPipelineSpec(
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
    ) -> DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpecNewPipelineSpecOutputReference:
        return typing.cast(DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpecNewPipelineSpecOutputReference, jsii.get(self, "newPipelineSpec"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpecNewPipelineSpec]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpecNewPipelineSpec]], jsii.get(self, "newPipelineSpecInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__ad789fb54db07e485090cc6c187b44085145de2379ec15072403fce868c2886c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createDatabaseObjectsIfMissing", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="existingPipelineId")
    def existing_pipeline_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "existingPipelineId"))

    @existing_pipeline_id.setter
    def existing_pipeline_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a67d2c54b0973dd28d0aac3abe5036342543abc1ec8981a8bfc13f83a4ca7b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "existingPipelineId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="primaryKeyColumns")
    def primary_key_columns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "primaryKeyColumns"))

    @primary_key_columns.setter
    def primary_key_columns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fd39394af57a24e5678b06906cf62842dc8f62710d87c0cf0abcc83db10800d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "primaryKeyColumns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="schedulingPolicy")
    def scheduling_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schedulingPolicy"))

    @scheduling_policy.setter
    def scheduling_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8181e05d698224051d37ae0d06b59e880248703fc98bf08c450dad2e3f280fbb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "schedulingPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceTableFullName")
    def source_table_full_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceTableFullName"))

    @source_table_full_name.setter
    def source_table_full_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1dd4fa2db9ac09332193bedcb29aec7ae3317a8dc49ff200bbe9e1cf9740fa7b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceTableFullName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeseriesKey")
    def timeseries_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeseriesKey"))

    @timeseries_key.setter
    def timeseries_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__751bc4def1adf04382d89ad96613745dbf215dcbca9536b6834eceeddc932251)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeseriesKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpec]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpec]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpec]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e81bf40cc36d45d7a4ff7c394c337f39aee6ff3bb3d655faff5d33ebe4bf658)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataDatabricksDatabaseSyncedDatabaseTables",
    "DataDatabricksDatabaseSyncedDatabaseTablesConfig",
    "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTables",
    "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatus",
    "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatus",
    "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgress",
    "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgressOutputReference",
    "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatusOutputReference",
    "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusFailedStatus",
    "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusFailedStatusOutputReference",
    "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusLastSync",
    "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusLastSyncDeltaTableSyncInfo",
    "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusLastSyncDeltaTableSyncInfoOutputReference",
    "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusLastSyncOutputReference",
    "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusOutputReference",
    "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatus",
    "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgress",
    "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgressOutputReference",
    "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatusOutputReference",
    "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatus",
    "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatusOutputReference",
    "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgress",
    "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgressOutputReference",
    "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesList",
    "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesOutputReference",
    "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpec",
    "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpecNewPipelineSpec",
    "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpecNewPipelineSpecOutputReference",
    "DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpecOutputReference",
]

publication.publish()

def _typecheckingstub__92b8cfcefc4298989f832cd2f9f62d9e05d01d7e7b50278c22d5a5a66c024398(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
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

def _typecheckingstub__6433d77d00ae3aec6e4a465f8d0a7c0701a31836f6585c309ea6cd2b73b1be91(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff785fb08f2b47a020c589aede68ba041f8cd8be06cce09e814bc3c547c1186c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4af4f6f6de6ec338f2dccda5c1719baf885945c806acf2a82191adf2e9080285(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    workspace_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__920179304dd3fb777e19363e15e0b0849292d73fe5595b9d02a496d32a27dd7f(
    *,
    name: builtins.str,
    database_instance_name: typing.Optional[builtins.str] = None,
    logical_database_name: typing.Optional[builtins.str] = None,
    spec: typing.Optional[typing.Union[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpec, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e82a97e318895968a55cfe64c348b1853160149180ef2b3f35809a216678d1a5(
    *,
    continuous_update_status: typing.Optional[typing.Union[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatus, typing.Dict[builtins.str, typing.Any]]] = None,
    failed_status: typing.Optional[typing.Union[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusFailedStatus, typing.Dict[builtins.str, typing.Any]]] = None,
    provisioning_status: typing.Optional[typing.Union[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatus, typing.Dict[builtins.str, typing.Any]]] = None,
    triggered_update_status: typing.Optional[typing.Union[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatus, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83b990665e10fb5cbc3d3855a4e54c9dac7f2dbd57a3825e27c43e5747a2366c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9ca4dda8713bb2c590e5d3d0d897d00135e08bb22b842e011e30f014ac5fe08(
    value: typing.Optional[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatusInitialPipelineSyncProgress],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dff6b1d5bf141239e80489e00b509f205783e6a4aceaae85d767eee77aefcc4d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d36c8c4b327e707e0143af2c9e6e8df5482ef4adb1293c7cd3b02c29d8dcaecc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusContinuousUpdateStatus]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fe23f004e8c501f0fe59cf1f4c3a3636bc081f56f8f6ebd3c8c4d9bfff7ab99(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d343ff33f679bf75242f1c7be350ceac1ae6abe1bdf8946999b7e93fa1a75ca8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusFailedStatus]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fddee2db7185a75959dd5b0bc27b9ee3baa983c62cc20307f450627472c30870(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5e09b0c36ad6b881eede33922915fcabe2afe738a168bba738c0fec602da804(
    value: typing.Optional[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusLastSyncDeltaTableSyncInfo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d105be8529c4714c7c7b921e8595022fa0654bda9c0e00a6db3d2e13bdb1eec(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24d8cf3b1ec6a21a1f3562dd76c2908235bf9cb810bf0dfd728106a5526e4bd2(
    value: typing.Optional[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusLastSync],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e95902c081a08b023ed48549264b16d5e5349b27a89146880b87379ece2787e7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bfb1af639ebb796e42f8ea971cf2d14ffd7e46b23eec02b956d7aefc98f1d1f(
    value: typing.Optional[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatus],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c26995b6e316af98081e15b7c1e65aefa8777dbca356106ef4df7de71893c702(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1f074d01a128c02cad18e8495204509380e217e1de644717f6a9ce464dc6b90(
    value: typing.Optional[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatusInitialPipelineSyncProgress],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4ad271645849be89255c0639d56c2166d04d766a16134a30c862ee9fe58d09b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2a8bb1c3be832d155b34a4b9e41793f716d1f4cde6adf273e6088518dfa02dc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusProvisioningStatus]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5c19b947b4bcd724d872166f6a4627febed7c394b9b0d1593cad4198a912b89(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d20cfb08028247bcedb8ccec7eea9370ddcafa61d42172254ed3094c4e3627d6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatus]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4801d5a490511e3cb824c788af93806b256f0344af165cc40c8aec3ef393b22(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d7fc46822ae77d4c4cfaf1497c8d5322d96a25fbec1739a4773399bbe66ed19(
    value: typing.Optional[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesDataSynchronizationStatusTriggeredUpdateStatusTriggeredUpdateProgress],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f15800ee73768bd6b0363210fa937691fb53186863f0470ad3f76b61906d85a5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a902596bebbd701afa25b4fe5a2c874e618b84e4f72b903586c90a7ed006a29(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b007d6e6e18e76b2931bc86e50f4933b611f60f665e28f792f8f83cff84dc77(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab57dac407ad79315e38ff74009ce461f26e5c3ab6b845abf6336cae6fd3f8b5(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf8615c463e2b7ed7a9f8349dd0f7e6bcb75c49690204d4f77139642e8a5614e(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8d51a6308c4722d1fc0f5cfae6ea9fe75f8304142eb8aa4eb915f1af7159ede(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTables]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__062aa852751f1b514dbd80c7df7da565a3e2417dc7e40e6745e94ad28eee17b1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57864b08442beb6e4b19f8fa8ce9b965635464c70bb8acb3abe6ee318c626c6f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4304e3edbda1f5966d8ee9a5bb1bae0649d867c384bc6e90e096c884ad52ddf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e188016f4b0b60baea560707b658d5420e726283e1853c7b3ee7b9e54a42ecf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d9a90532b77e7c765ecb8921bd35b4e1c43cb7cc86b8eb930e0806fed03c100(
    value: typing.Optional[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTables],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da9388c7bab00bea8824383e6313b86a0bc8c3bbcd3824c2c583ac7d10e1684d(
    *,
    create_database_objects_if_missing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    existing_pipeline_id: typing.Optional[builtins.str] = None,
    new_pipeline_spec: typing.Optional[typing.Union[DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpecNewPipelineSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    primary_key_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
    scheduling_policy: typing.Optional[builtins.str] = None,
    source_table_full_name: typing.Optional[builtins.str] = None,
    timeseries_key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af1cc2421002f93423a52994a2d61f753dfcd89026c5f497f97de60be2e09bc7(
    *,
    storage_catalog: typing.Optional[builtins.str] = None,
    storage_schema: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__171c3989e1487cec2ee78c1e5cbe059621545926b31646df3976eea10aee7205(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28866537df3218a32c556f15f44622db5f0d9f583620473185eba2273e32aa31(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdff1ad8939824754ff163366b71e246b782e1d4af51b9d0b49fc342355a31f5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f3e6f49725a347f2839cc3036422648e515d1cc133286c378828ef8128fbbe5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpecNewPipelineSpec]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cff26820617b89935e16bd7e54bf4b1fed6d7c09078884f51410518bc4169cf1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad789fb54db07e485090cc6c187b44085145de2379ec15072403fce868c2886c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a67d2c54b0973dd28d0aac3abe5036342543abc1ec8981a8bfc13f83a4ca7b7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fd39394af57a24e5678b06906cf62842dc8f62710d87c0cf0abcc83db10800d(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8181e05d698224051d37ae0d06b59e880248703fc98bf08c450dad2e3f280fbb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1dd4fa2db9ac09332193bedcb29aec7ae3317a8dc49ff200bbe9e1cf9740fa7b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__751bc4def1adf04382d89ad96613745dbf215dcbca9536b6834eceeddc932251(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e81bf40cc36d45d7a4ff7c394c337f39aee6ff3bb3d655faff5d33ebe4bf658(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseSyncedDatabaseTablesSyncedTablesSpec]],
) -> None:
    """Type checking stubs"""
    pass
