r'''
# `data_databricks_database_instance`

Refer to the Terraform Registry for docs: [`data_databricks_database_instance`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance).
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


class DataDatabricksDatabaseInstance(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseInstance.DataDatabricksDatabaseInstance",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance databricks_database_instance}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        capacity: typing.Optional[builtins.str] = None,
        enable_pg_native_login: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_readable_secondaries: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        node_count: typing.Optional[jsii.Number] = None,
        parent_instance_ref: typing.Optional[typing.Union["DataDatabricksDatabaseInstanceParentInstanceRef", typing.Dict[builtins.str, typing.Any]]] = None,
        retention_window_in_days: typing.Optional[jsii.Number] = None,
        stopped: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        workspace_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance databricks_database_instance} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#name DataDatabricksDatabaseInstance#name}.
        :param capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#capacity DataDatabricksDatabaseInstance#capacity}.
        :param enable_pg_native_login: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#enable_pg_native_login DataDatabricksDatabaseInstance#enable_pg_native_login}.
        :param enable_readable_secondaries: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#enable_readable_secondaries DataDatabricksDatabaseInstance#enable_readable_secondaries}.
        :param node_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#node_count DataDatabricksDatabaseInstance#node_count}.
        :param parent_instance_ref: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#parent_instance_ref DataDatabricksDatabaseInstance#parent_instance_ref}.
        :param retention_window_in_days: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#retention_window_in_days DataDatabricksDatabaseInstance#retention_window_in_days}.
        :param stopped: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#stopped DataDatabricksDatabaseInstance#stopped}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#workspace_id DataDatabricksDatabaseInstance#workspace_id}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d938b865b258cce04340eb05c9e90f5fb200489bdad9c80c392c14a255902d2a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataDatabricksDatabaseInstanceConfig(
            name=name,
            capacity=capacity,
            enable_pg_native_login=enable_pg_native_login,
            enable_readable_secondaries=enable_readable_secondaries,
            node_count=node_count,
            parent_instance_ref=parent_instance_ref,
            retention_window_in_days=retention_window_in_days,
            stopped=stopped,
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
        '''Generates CDKTF code for importing a DataDatabricksDatabaseInstance resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDatabricksDatabaseInstance to import.
        :param import_from_id: The id of the existing DataDatabricksDatabaseInstance that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDatabricksDatabaseInstance to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c546786fbfa13177934b50fd3c1e699ff19d469ea7b781bec138149cd184efd0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putParentInstanceRef")
    def put_parent_instance_ref(
        self,
        *,
        branch_time: typing.Optional[builtins.str] = None,
        lsn: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param branch_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#branch_time DataDatabricksDatabaseInstance#branch_time}.
        :param lsn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#lsn DataDatabricksDatabaseInstance#lsn}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#name DataDatabricksDatabaseInstance#name}.
        '''
        value = DataDatabricksDatabaseInstanceParentInstanceRef(
            branch_time=branch_time, lsn=lsn, name=name
        )

        return typing.cast(None, jsii.invoke(self, "putParentInstanceRef", [value]))

    @jsii.member(jsii_name="resetCapacity")
    def reset_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCapacity", []))

    @jsii.member(jsii_name="resetEnablePgNativeLogin")
    def reset_enable_pg_native_login(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnablePgNativeLogin", []))

    @jsii.member(jsii_name="resetEnableReadableSecondaries")
    def reset_enable_readable_secondaries(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableReadableSecondaries", []))

    @jsii.member(jsii_name="resetNodeCount")
    def reset_node_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodeCount", []))

    @jsii.member(jsii_name="resetParentInstanceRef")
    def reset_parent_instance_ref(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParentInstanceRef", []))

    @jsii.member(jsii_name="resetRetentionWindowInDays")
    def reset_retention_window_in_days(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetentionWindowInDays", []))

    @jsii.member(jsii_name="resetStopped")
    def reset_stopped(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStopped", []))

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
    @jsii.member(jsii_name="childInstanceRefs")
    def child_instance_refs(
        self,
    ) -> "DataDatabricksDatabaseInstanceChildInstanceRefsList":
        return typing.cast("DataDatabricksDatabaseInstanceChildInstanceRefsList", jsii.get(self, "childInstanceRefs"))

    @builtins.property
    @jsii.member(jsii_name="creationTime")
    def creation_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creationTime"))

    @builtins.property
    @jsii.member(jsii_name="creator")
    def creator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creator"))

    @builtins.property
    @jsii.member(jsii_name="effectiveEnablePgNativeLogin")
    def effective_enable_pg_native_login(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "effectiveEnablePgNativeLogin"))

    @builtins.property
    @jsii.member(jsii_name="effectiveEnableReadableSecondaries")
    def effective_enable_readable_secondaries(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "effectiveEnableReadableSecondaries"))

    @builtins.property
    @jsii.member(jsii_name="effectiveNodeCount")
    def effective_node_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "effectiveNodeCount"))

    @builtins.property
    @jsii.member(jsii_name="effectiveRetentionWindowInDays")
    def effective_retention_window_in_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "effectiveRetentionWindowInDays"))

    @builtins.property
    @jsii.member(jsii_name="effectiveStopped")
    def effective_stopped(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "effectiveStopped"))

    @builtins.property
    @jsii.member(jsii_name="parentInstanceRef")
    def parent_instance_ref(
        self,
    ) -> "DataDatabricksDatabaseInstanceParentInstanceRefOutputReference":
        return typing.cast("DataDatabricksDatabaseInstanceParentInstanceRefOutputReference", jsii.get(self, "parentInstanceRef"))

    @builtins.property
    @jsii.member(jsii_name="pgVersion")
    def pg_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pgVersion"))

    @builtins.property
    @jsii.member(jsii_name="readOnlyDns")
    def read_only_dns(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "readOnlyDns"))

    @builtins.property
    @jsii.member(jsii_name="readWriteDns")
    def read_write_dns(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "readWriteDns"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="uid")
    def uid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uid"))

    @builtins.property
    @jsii.member(jsii_name="capacityInput")
    def capacity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "capacityInput"))

    @builtins.property
    @jsii.member(jsii_name="enablePgNativeLoginInput")
    def enable_pg_native_login_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enablePgNativeLoginInput"))

    @builtins.property
    @jsii.member(jsii_name="enableReadableSecondariesInput")
    def enable_readable_secondaries_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableReadableSecondariesInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="nodeCountInput")
    def node_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "nodeCountInput"))

    @builtins.property
    @jsii.member(jsii_name="parentInstanceRefInput")
    def parent_instance_ref_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksDatabaseInstanceParentInstanceRef"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksDatabaseInstanceParentInstanceRef"]], jsii.get(self, "parentInstanceRefInput"))

    @builtins.property
    @jsii.member(jsii_name="retentionWindowInDaysInput")
    def retention_window_in_days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retentionWindowInDaysInput"))

    @builtins.property
    @jsii.member(jsii_name="stoppedInput")
    def stopped_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "stoppedInput"))

    @builtins.property
    @jsii.member(jsii_name="workspaceIdInput")
    def workspace_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workspaceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="capacity")
    def capacity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "capacity"))

    @capacity.setter
    def capacity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e934d4d680179e26842507b86cb2327577f5f7e2d92df672488841aef3abfbcb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "capacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enablePgNativeLogin")
    def enable_pg_native_login(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enablePgNativeLogin"))

    @enable_pg_native_login.setter
    def enable_pg_native_login(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73ad286140e93206752818166e57e6882eb8dcba2a8de8e0d0f85131796abf2d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enablePgNativeLogin", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableReadableSecondaries")
    def enable_readable_secondaries(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableReadableSecondaries"))

    @enable_readable_secondaries.setter
    def enable_readable_secondaries(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c53aff4a52642d960015fd00c2cc30018ce5602a78905188882e3eddd44db3a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableReadableSecondaries", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02b76281c149ddf94221ff852944b8fd30f584b71d4a03f33701f50f8814b575)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nodeCount")
    def node_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "nodeCount"))

    @node_count.setter
    def node_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__574709e028dff51c29d16140ce1178a0161789480678379cce12c036fb4d616e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nodeCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retentionWindowInDays")
    def retention_window_in_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retentionWindowInDays"))

    @retention_window_in_days.setter
    def retention_window_in_days(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c2b858cac371cd97f93bf2bbb12901e0a746b943f7ec03f2fe494aa994f1479)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retentionWindowInDays", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stopped")
    def stopped(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "stopped"))

    @stopped.setter
    def stopped(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a012498e0a9ad00f704626aff8c4e06d99889be5002def3fe5aff3af2f3b31ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stopped", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workspaceId")
    def workspace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceId"))

    @workspace_id.setter
    def workspace_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d8e9c297dbcee6c4026187fa0b2def2c2d64d131d9a68e0fb43460b2cd18544)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workspaceId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseInstance.DataDatabricksDatabaseInstanceChildInstanceRefs",
    jsii_struct_bases=[],
    name_mapping={"branch_time": "branchTime", "lsn": "lsn", "name": "name"},
)
class DataDatabricksDatabaseInstanceChildInstanceRefs:
    def __init__(
        self,
        *,
        branch_time: typing.Optional[builtins.str] = None,
        lsn: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param branch_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#branch_time DataDatabricksDatabaseInstance#branch_time}.
        :param lsn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#lsn DataDatabricksDatabaseInstance#lsn}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#name DataDatabricksDatabaseInstance#name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e50aa8353d490e9c21060a282276ea622669487496be23e7bdb235e9de58a3f3)
            check_type(argname="argument branch_time", value=branch_time, expected_type=type_hints["branch_time"])
            check_type(argname="argument lsn", value=lsn, expected_type=type_hints["lsn"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if branch_time is not None:
            self._values["branch_time"] = branch_time
        if lsn is not None:
            self._values["lsn"] = lsn
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def branch_time(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#branch_time DataDatabricksDatabaseInstance#branch_time}.'''
        result = self._values.get("branch_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lsn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#lsn DataDatabricksDatabaseInstance#lsn}.'''
        result = self._values.get("lsn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#name DataDatabricksDatabaseInstance#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseInstanceChildInstanceRefs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksDatabaseInstanceChildInstanceRefsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseInstance.DataDatabricksDatabaseInstanceChildInstanceRefsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f78f2a3c753b4f7df5f08eeb97ff1b125678e20e091e2cd9f7cc2824cba92bc5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksDatabaseInstanceChildInstanceRefsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce6b89fecad1ef04e38a4f69c22051b7c66fa718cf9414bda3a52ec7c506646a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksDatabaseInstanceChildInstanceRefsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d1672145716da37458c21d8e839847f4e1bc4e3dbe0c1383e1141629ce34554)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bbf0b47d092834bc85b427b51b03e7fdef783c2e8889913f28dc469a8f6cfcaf)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c8945bc01073e6d2772cf2272df6236dd1fc7973d4805de138126fdf0b385c43)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksDatabaseInstanceChildInstanceRefs]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksDatabaseInstanceChildInstanceRefs]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksDatabaseInstanceChildInstanceRefs]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c2757c1b23431ef0b36945b87334c377803b76288575f89660f4b406ec136f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksDatabaseInstanceChildInstanceRefsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseInstance.DataDatabricksDatabaseInstanceChildInstanceRefsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a8ff24382f983ece3c591548bf31e10c79f9608cf8647e36d8eb28875b156389)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetBranchTime")
    def reset_branch_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBranchTime", []))

    @jsii.member(jsii_name="resetLsn")
    def reset_lsn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLsn", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @builtins.property
    @jsii.member(jsii_name="effectiveLsn")
    def effective_lsn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "effectiveLsn"))

    @builtins.property
    @jsii.member(jsii_name="uid")
    def uid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uid"))

    @builtins.property
    @jsii.member(jsii_name="branchTimeInput")
    def branch_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "branchTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="lsnInput")
    def lsn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lsnInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="branchTime")
    def branch_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "branchTime"))

    @branch_time.setter
    def branch_time(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__999ca9459b2a22ba610cea9dcf2f95dad0fb4fa81b1dcc1a2dfc7cc3eebbb864)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "branchTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lsn")
    def lsn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lsn"))

    @lsn.setter
    def lsn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af38fb8e5bf981fad0f254b130fec4536c3a834b595d960b6939126369a06951)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lsn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f1d2af8e5194b0e30455e0b6a4117bc18bddba24a8910d58bfa2d37f686c3a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksDatabaseInstanceChildInstanceRefs]:
        return typing.cast(typing.Optional[DataDatabricksDatabaseInstanceChildInstanceRefs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksDatabaseInstanceChildInstanceRefs],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff538f30da47e47d6a8013873dc816cf2c7acc30e373826e4e395026208f824d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseInstance.DataDatabricksDatabaseInstanceConfig",
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
        "capacity": "capacity",
        "enable_pg_native_login": "enablePgNativeLogin",
        "enable_readable_secondaries": "enableReadableSecondaries",
        "node_count": "nodeCount",
        "parent_instance_ref": "parentInstanceRef",
        "retention_window_in_days": "retentionWindowInDays",
        "stopped": "stopped",
        "workspace_id": "workspaceId",
    },
)
class DataDatabricksDatabaseInstanceConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        capacity: typing.Optional[builtins.str] = None,
        enable_pg_native_login: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_readable_secondaries: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        node_count: typing.Optional[jsii.Number] = None,
        parent_instance_ref: typing.Optional[typing.Union["DataDatabricksDatabaseInstanceParentInstanceRef", typing.Dict[builtins.str, typing.Any]]] = None,
        retention_window_in_days: typing.Optional[jsii.Number] = None,
        stopped: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#name DataDatabricksDatabaseInstance#name}.
        :param capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#capacity DataDatabricksDatabaseInstance#capacity}.
        :param enable_pg_native_login: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#enable_pg_native_login DataDatabricksDatabaseInstance#enable_pg_native_login}.
        :param enable_readable_secondaries: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#enable_readable_secondaries DataDatabricksDatabaseInstance#enable_readable_secondaries}.
        :param node_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#node_count DataDatabricksDatabaseInstance#node_count}.
        :param parent_instance_ref: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#parent_instance_ref DataDatabricksDatabaseInstance#parent_instance_ref}.
        :param retention_window_in_days: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#retention_window_in_days DataDatabricksDatabaseInstance#retention_window_in_days}.
        :param stopped: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#stopped DataDatabricksDatabaseInstance#stopped}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#workspace_id DataDatabricksDatabaseInstance#workspace_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(parent_instance_ref, dict):
            parent_instance_ref = DataDatabricksDatabaseInstanceParentInstanceRef(**parent_instance_ref)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8b841c08122822ce16a0039337a7e21f9b97728a2f006ac703b8841eacc21bc)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument capacity", value=capacity, expected_type=type_hints["capacity"])
            check_type(argname="argument enable_pg_native_login", value=enable_pg_native_login, expected_type=type_hints["enable_pg_native_login"])
            check_type(argname="argument enable_readable_secondaries", value=enable_readable_secondaries, expected_type=type_hints["enable_readable_secondaries"])
            check_type(argname="argument node_count", value=node_count, expected_type=type_hints["node_count"])
            check_type(argname="argument parent_instance_ref", value=parent_instance_ref, expected_type=type_hints["parent_instance_ref"])
            check_type(argname="argument retention_window_in_days", value=retention_window_in_days, expected_type=type_hints["retention_window_in_days"])
            check_type(argname="argument stopped", value=stopped, expected_type=type_hints["stopped"])
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
        if capacity is not None:
            self._values["capacity"] = capacity
        if enable_pg_native_login is not None:
            self._values["enable_pg_native_login"] = enable_pg_native_login
        if enable_readable_secondaries is not None:
            self._values["enable_readable_secondaries"] = enable_readable_secondaries
        if node_count is not None:
            self._values["node_count"] = node_count
        if parent_instance_ref is not None:
            self._values["parent_instance_ref"] = parent_instance_ref
        if retention_window_in_days is not None:
            self._values["retention_window_in_days"] = retention_window_in_days
        if stopped is not None:
            self._values["stopped"] = stopped
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#name DataDatabricksDatabaseInstance#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def capacity(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#capacity DataDatabricksDatabaseInstance#capacity}.'''
        result = self._values.get("capacity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_pg_native_login(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#enable_pg_native_login DataDatabricksDatabaseInstance#enable_pg_native_login}.'''
        result = self._values.get("enable_pg_native_login")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enable_readable_secondaries(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#enable_readable_secondaries DataDatabricksDatabaseInstance#enable_readable_secondaries}.'''
        result = self._values.get("enable_readable_secondaries")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def node_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#node_count DataDatabricksDatabaseInstance#node_count}.'''
        result = self._values.get("node_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def parent_instance_ref(
        self,
    ) -> typing.Optional["DataDatabricksDatabaseInstanceParentInstanceRef"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#parent_instance_ref DataDatabricksDatabaseInstance#parent_instance_ref}.'''
        result = self._values.get("parent_instance_ref")
        return typing.cast(typing.Optional["DataDatabricksDatabaseInstanceParentInstanceRef"], result)

    @builtins.property
    def retention_window_in_days(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#retention_window_in_days DataDatabricksDatabaseInstance#retention_window_in_days}.'''
        result = self._values.get("retention_window_in_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def stopped(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#stopped DataDatabricksDatabaseInstance#stopped}.'''
        result = self._values.get("stopped")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def workspace_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#workspace_id DataDatabricksDatabaseInstance#workspace_id}.'''
        result = self._values.get("workspace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseInstanceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseInstance.DataDatabricksDatabaseInstanceParentInstanceRef",
    jsii_struct_bases=[],
    name_mapping={"branch_time": "branchTime", "lsn": "lsn", "name": "name"},
)
class DataDatabricksDatabaseInstanceParentInstanceRef:
    def __init__(
        self,
        *,
        branch_time: typing.Optional[builtins.str] = None,
        lsn: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param branch_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#branch_time DataDatabricksDatabaseInstance#branch_time}.
        :param lsn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#lsn DataDatabricksDatabaseInstance#lsn}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#name DataDatabricksDatabaseInstance#name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77ad157d97826ec7900c2ef901e954723cb17fccfe3f06eac7913a8ff55cac8b)
            check_type(argname="argument branch_time", value=branch_time, expected_type=type_hints["branch_time"])
            check_type(argname="argument lsn", value=lsn, expected_type=type_hints["lsn"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if branch_time is not None:
            self._values["branch_time"] = branch_time
        if lsn is not None:
            self._values["lsn"] = lsn
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def branch_time(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#branch_time DataDatabricksDatabaseInstance#branch_time}.'''
        result = self._values.get("branch_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lsn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#lsn DataDatabricksDatabaseInstance#lsn}.'''
        result = self._values.get("lsn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/database_instance#name DataDatabricksDatabaseInstance#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksDatabaseInstanceParentInstanceRef(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksDatabaseInstanceParentInstanceRefOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksDatabaseInstance.DataDatabricksDatabaseInstanceParentInstanceRefOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6b3e4f29ace6947e0b45c0e8aed5995fd19ee79461f0d23635ff21e9d47b09b0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetBranchTime")
    def reset_branch_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBranchTime", []))

    @jsii.member(jsii_name="resetLsn")
    def reset_lsn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLsn", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @builtins.property
    @jsii.member(jsii_name="effectiveLsn")
    def effective_lsn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "effectiveLsn"))

    @builtins.property
    @jsii.member(jsii_name="uid")
    def uid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uid"))

    @builtins.property
    @jsii.member(jsii_name="branchTimeInput")
    def branch_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "branchTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="lsnInput")
    def lsn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lsnInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="branchTime")
    def branch_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "branchTime"))

    @branch_time.setter
    def branch_time(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6ed4add913c3b4e3abf788971fc9bdf9e7e0f69d8911c8ea5f8023f165ce534)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "branchTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lsn")
    def lsn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lsn"))

    @lsn.setter
    def lsn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a674a8c46c21ffecb326d01d9716dfbd3fd9e943e704f1f9a96c5e75cd9a7847)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lsn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__795ace2feb7bfd0bde6cf1a63bd6405ab29cad71f351f55916b37579cdbdd9cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseInstanceParentInstanceRef]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseInstanceParentInstanceRef]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseInstanceParentInstanceRef]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99488bceb08e542224b6c49b206e72ec73813d1b294512255b5adab70d1e5732)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataDatabricksDatabaseInstance",
    "DataDatabricksDatabaseInstanceChildInstanceRefs",
    "DataDatabricksDatabaseInstanceChildInstanceRefsList",
    "DataDatabricksDatabaseInstanceChildInstanceRefsOutputReference",
    "DataDatabricksDatabaseInstanceConfig",
    "DataDatabricksDatabaseInstanceParentInstanceRef",
    "DataDatabricksDatabaseInstanceParentInstanceRefOutputReference",
]

publication.publish()

def _typecheckingstub__d938b865b258cce04340eb05c9e90f5fb200489bdad9c80c392c14a255902d2a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    name: builtins.str,
    capacity: typing.Optional[builtins.str] = None,
    enable_pg_native_login: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_readable_secondaries: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    node_count: typing.Optional[jsii.Number] = None,
    parent_instance_ref: typing.Optional[typing.Union[DataDatabricksDatabaseInstanceParentInstanceRef, typing.Dict[builtins.str, typing.Any]]] = None,
    retention_window_in_days: typing.Optional[jsii.Number] = None,
    stopped: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__c546786fbfa13177934b50fd3c1e699ff19d469ea7b781bec138149cd184efd0(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e934d4d680179e26842507b86cb2327577f5f7e2d92df672488841aef3abfbcb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73ad286140e93206752818166e57e6882eb8dcba2a8de8e0d0f85131796abf2d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c53aff4a52642d960015fd00c2cc30018ce5602a78905188882e3eddd44db3a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02b76281c149ddf94221ff852944b8fd30f584b71d4a03f33701f50f8814b575(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__574709e028dff51c29d16140ce1178a0161789480678379cce12c036fb4d616e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c2b858cac371cd97f93bf2bbb12901e0a746b943f7ec03f2fe494aa994f1479(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a012498e0a9ad00f704626aff8c4e06d99889be5002def3fe5aff3af2f3b31ae(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d8e9c297dbcee6c4026187fa0b2def2c2d64d131d9a68e0fb43460b2cd18544(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e50aa8353d490e9c21060a282276ea622669487496be23e7bdb235e9de58a3f3(
    *,
    branch_time: typing.Optional[builtins.str] = None,
    lsn: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f78f2a3c753b4f7df5f08eeb97ff1b125678e20e091e2cd9f7cc2824cba92bc5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce6b89fecad1ef04e38a4f69c22051b7c66fa718cf9414bda3a52ec7c506646a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d1672145716da37458c21d8e839847f4e1bc4e3dbe0c1383e1141629ce34554(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbf0b47d092834bc85b427b51b03e7fdef783c2e8889913f28dc469a8f6cfcaf(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8945bc01073e6d2772cf2272df6236dd1fc7973d4805de138126fdf0b385c43(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c2757c1b23431ef0b36945b87334c377803b76288575f89660f4b406ec136f4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksDatabaseInstanceChildInstanceRefs]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8ff24382f983ece3c591548bf31e10c79f9608cf8647e36d8eb28875b156389(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__999ca9459b2a22ba610cea9dcf2f95dad0fb4fa81b1dcc1a2dfc7cc3eebbb864(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af38fb8e5bf981fad0f254b130fec4536c3a834b595d960b6939126369a06951(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f1d2af8e5194b0e30455e0b6a4117bc18bddba24a8910d58bfa2d37f686c3a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff538f30da47e47d6a8013873dc816cf2c7acc30e373826e4e395026208f824d(
    value: typing.Optional[DataDatabricksDatabaseInstanceChildInstanceRefs],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8b841c08122822ce16a0039337a7e21f9b97728a2f006ac703b8841eacc21bc(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    capacity: typing.Optional[builtins.str] = None,
    enable_pg_native_login: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_readable_secondaries: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    node_count: typing.Optional[jsii.Number] = None,
    parent_instance_ref: typing.Optional[typing.Union[DataDatabricksDatabaseInstanceParentInstanceRef, typing.Dict[builtins.str, typing.Any]]] = None,
    retention_window_in_days: typing.Optional[jsii.Number] = None,
    stopped: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    workspace_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77ad157d97826ec7900c2ef901e954723cb17fccfe3f06eac7913a8ff55cac8b(
    *,
    branch_time: typing.Optional[builtins.str] = None,
    lsn: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b3e4f29ace6947e0b45c0e8aed5995fd19ee79461f0d23635ff21e9d47b09b0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6ed4add913c3b4e3abf788971fc9bdf9e7e0f69d8911c8ea5f8023f165ce534(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a674a8c46c21ffecb326d01d9716dfbd3fd9e943e704f1f9a96c5e75cd9a7847(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__795ace2feb7bfd0bde6cf1a63bd6405ab29cad71f351f55916b37579cdbdd9cb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99488bceb08e542224b6c49b206e72ec73813d1b294512255b5adab70d1e5732(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksDatabaseInstanceParentInstanceRef]],
) -> None:
    """Type checking stubs"""
    pass
