r'''
# `data_databricks_clean_room_assets`

Refer to the Terraform Registry for docs: [`data_databricks_clean_room_assets`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets).
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


class DataDatabricksCleanRoomAssets(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssets",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets databricks_clean_room_assets}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        clean_room_name: builtins.str,
        workspace_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets databricks_clean_room_assets} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param clean_room_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#clean_room_name DataDatabricksCleanRoomAssets#clean_room_name}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#workspace_id DataDatabricksCleanRoomAssets#workspace_id}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d956f34b241a5ed4c8a224d1131b86dfeda714f873a9b29ad425ea3829c670ca)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataDatabricksCleanRoomAssetsConfig(
            clean_room_name=clean_room_name,
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
        '''Generates CDKTF code for importing a DataDatabricksCleanRoomAssets resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDatabricksCleanRoomAssets to import.
        :param import_from_id: The id of the existing DataDatabricksCleanRoomAssets that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDatabricksCleanRoomAssets to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96f4f56b1665d0a2e69be7287dd0322fecfc6e81cc10256f2e78d5d9d8e67528)
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
    @jsii.member(jsii_name="assets")
    def assets(self) -> "DataDatabricksCleanRoomAssetsAssetsList":
        return typing.cast("DataDatabricksCleanRoomAssetsAssetsList", jsii.get(self, "assets"))

    @builtins.property
    @jsii.member(jsii_name="cleanRoomNameInput")
    def clean_room_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cleanRoomNameInput"))

    @builtins.property
    @jsii.member(jsii_name="workspaceIdInput")
    def workspace_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workspaceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="cleanRoomName")
    def clean_room_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cleanRoomName"))

    @clean_room_name.setter
    def clean_room_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df83a8fa4d79fbbe6238ff85e129fcf7ba7b000130552e5b3ce94b733a6f528a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cleanRoomName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workspaceId")
    def workspace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceId"))

    @workspace_id.setter
    def workspace_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2845f8814e0b03a440fc7f86acc15a2c70392fea265021a964ee6219e931ee15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workspaceId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssets",
    jsii_struct_bases=[],
    name_mapping={
        "asset_type": "assetType",
        "name": "name",
        "clean_room_name": "cleanRoomName",
        "foreign_table": "foreignTable",
        "foreign_table_local_details": "foreignTableLocalDetails",
        "notebook": "notebook",
        "table": "table",
        "table_local_details": "tableLocalDetails",
        "view": "view",
        "view_local_details": "viewLocalDetails",
        "volume_local_details": "volumeLocalDetails",
    },
)
class DataDatabricksCleanRoomAssetsAssets:
    def __init__(
        self,
        *,
        asset_type: builtins.str,
        name: builtins.str,
        clean_room_name: typing.Optional[builtins.str] = None,
        foreign_table: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetsAssetsForeignTable", typing.Dict[builtins.str, typing.Any]]] = None,
        foreign_table_local_details: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetsAssetsForeignTableLocalDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        notebook: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetsAssetsNotebook", typing.Dict[builtins.str, typing.Any]]] = None,
        table: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetsAssetsTable", typing.Dict[builtins.str, typing.Any]]] = None,
        table_local_details: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetsAssetsTableLocalDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        view: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetsAssetsView", typing.Dict[builtins.str, typing.Any]]] = None,
        view_local_details: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetsAssetsViewLocalDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        volume_local_details: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetsAssetsVolumeLocalDetails", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param asset_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#asset_type DataDatabricksCleanRoomAssets#asset_type}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#name DataDatabricksCleanRoomAssets#name}.
        :param clean_room_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#clean_room_name DataDatabricksCleanRoomAssets#clean_room_name}.
        :param foreign_table: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#foreign_table DataDatabricksCleanRoomAssets#foreign_table}.
        :param foreign_table_local_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#foreign_table_local_details DataDatabricksCleanRoomAssets#foreign_table_local_details}.
        :param notebook: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#notebook DataDatabricksCleanRoomAssets#notebook}.
        :param table: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#table DataDatabricksCleanRoomAssets#table}.
        :param table_local_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#table_local_details DataDatabricksCleanRoomAssets#table_local_details}.
        :param view: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#view DataDatabricksCleanRoomAssets#view}.
        :param view_local_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#view_local_details DataDatabricksCleanRoomAssets#view_local_details}.
        :param volume_local_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#volume_local_details DataDatabricksCleanRoomAssets#volume_local_details}.
        '''
        if isinstance(foreign_table, dict):
            foreign_table = DataDatabricksCleanRoomAssetsAssetsForeignTable(**foreign_table)
        if isinstance(foreign_table_local_details, dict):
            foreign_table_local_details = DataDatabricksCleanRoomAssetsAssetsForeignTableLocalDetails(**foreign_table_local_details)
        if isinstance(notebook, dict):
            notebook = DataDatabricksCleanRoomAssetsAssetsNotebook(**notebook)
        if isinstance(table, dict):
            table = DataDatabricksCleanRoomAssetsAssetsTable(**table)
        if isinstance(table_local_details, dict):
            table_local_details = DataDatabricksCleanRoomAssetsAssetsTableLocalDetails(**table_local_details)
        if isinstance(view, dict):
            view = DataDatabricksCleanRoomAssetsAssetsView(**view)
        if isinstance(view_local_details, dict):
            view_local_details = DataDatabricksCleanRoomAssetsAssetsViewLocalDetails(**view_local_details)
        if isinstance(volume_local_details, dict):
            volume_local_details = DataDatabricksCleanRoomAssetsAssetsVolumeLocalDetails(**volume_local_details)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a3691e69c31801ce0e43158fe50942cd062b432d7e42e331ef7ac56a9b85b3e)
            check_type(argname="argument asset_type", value=asset_type, expected_type=type_hints["asset_type"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument clean_room_name", value=clean_room_name, expected_type=type_hints["clean_room_name"])
            check_type(argname="argument foreign_table", value=foreign_table, expected_type=type_hints["foreign_table"])
            check_type(argname="argument foreign_table_local_details", value=foreign_table_local_details, expected_type=type_hints["foreign_table_local_details"])
            check_type(argname="argument notebook", value=notebook, expected_type=type_hints["notebook"])
            check_type(argname="argument table", value=table, expected_type=type_hints["table"])
            check_type(argname="argument table_local_details", value=table_local_details, expected_type=type_hints["table_local_details"])
            check_type(argname="argument view", value=view, expected_type=type_hints["view"])
            check_type(argname="argument view_local_details", value=view_local_details, expected_type=type_hints["view_local_details"])
            check_type(argname="argument volume_local_details", value=volume_local_details, expected_type=type_hints["volume_local_details"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "asset_type": asset_type,
            "name": name,
        }
        if clean_room_name is not None:
            self._values["clean_room_name"] = clean_room_name
        if foreign_table is not None:
            self._values["foreign_table"] = foreign_table
        if foreign_table_local_details is not None:
            self._values["foreign_table_local_details"] = foreign_table_local_details
        if notebook is not None:
            self._values["notebook"] = notebook
        if table is not None:
            self._values["table"] = table
        if table_local_details is not None:
            self._values["table_local_details"] = table_local_details
        if view is not None:
            self._values["view"] = view
        if view_local_details is not None:
            self._values["view_local_details"] = view_local_details
        if volume_local_details is not None:
            self._values["volume_local_details"] = volume_local_details

    @builtins.property
    def asset_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#asset_type DataDatabricksCleanRoomAssets#asset_type}.'''
        result = self._values.get("asset_type")
        assert result is not None, "Required property 'asset_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#name DataDatabricksCleanRoomAssets#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def clean_room_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#clean_room_name DataDatabricksCleanRoomAssets#clean_room_name}.'''
        result = self._values.get("clean_room_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def foreign_table(
        self,
    ) -> typing.Optional["DataDatabricksCleanRoomAssetsAssetsForeignTable"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#foreign_table DataDatabricksCleanRoomAssets#foreign_table}.'''
        result = self._values.get("foreign_table")
        return typing.cast(typing.Optional["DataDatabricksCleanRoomAssetsAssetsForeignTable"], result)

    @builtins.property
    def foreign_table_local_details(
        self,
    ) -> typing.Optional["DataDatabricksCleanRoomAssetsAssetsForeignTableLocalDetails"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#foreign_table_local_details DataDatabricksCleanRoomAssets#foreign_table_local_details}.'''
        result = self._values.get("foreign_table_local_details")
        return typing.cast(typing.Optional["DataDatabricksCleanRoomAssetsAssetsForeignTableLocalDetails"], result)

    @builtins.property
    def notebook(
        self,
    ) -> typing.Optional["DataDatabricksCleanRoomAssetsAssetsNotebook"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#notebook DataDatabricksCleanRoomAssets#notebook}.'''
        result = self._values.get("notebook")
        return typing.cast(typing.Optional["DataDatabricksCleanRoomAssetsAssetsNotebook"], result)

    @builtins.property
    def table(self) -> typing.Optional["DataDatabricksCleanRoomAssetsAssetsTable"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#table DataDatabricksCleanRoomAssets#table}.'''
        result = self._values.get("table")
        return typing.cast(typing.Optional["DataDatabricksCleanRoomAssetsAssetsTable"], result)

    @builtins.property
    def table_local_details(
        self,
    ) -> typing.Optional["DataDatabricksCleanRoomAssetsAssetsTableLocalDetails"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#table_local_details DataDatabricksCleanRoomAssets#table_local_details}.'''
        result = self._values.get("table_local_details")
        return typing.cast(typing.Optional["DataDatabricksCleanRoomAssetsAssetsTableLocalDetails"], result)

    @builtins.property
    def view(self) -> typing.Optional["DataDatabricksCleanRoomAssetsAssetsView"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#view DataDatabricksCleanRoomAssets#view}.'''
        result = self._values.get("view")
        return typing.cast(typing.Optional["DataDatabricksCleanRoomAssetsAssetsView"], result)

    @builtins.property
    def view_local_details(
        self,
    ) -> typing.Optional["DataDatabricksCleanRoomAssetsAssetsViewLocalDetails"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#view_local_details DataDatabricksCleanRoomAssets#view_local_details}.'''
        result = self._values.get("view_local_details")
        return typing.cast(typing.Optional["DataDatabricksCleanRoomAssetsAssetsViewLocalDetails"], result)

    @builtins.property
    def volume_local_details(
        self,
    ) -> typing.Optional["DataDatabricksCleanRoomAssetsAssetsVolumeLocalDetails"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#volume_local_details DataDatabricksCleanRoomAssets#volume_local_details}.'''
        result = self._values.get("volume_local_details")
        return typing.cast(typing.Optional["DataDatabricksCleanRoomAssetsAssetsVolumeLocalDetails"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetsAssets(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsForeignTable",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksCleanRoomAssetsAssetsForeignTable:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetsAssetsForeignTable(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsForeignTableColumns",
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
class DataDatabricksCleanRoomAssetsAssetsForeignTableColumns:
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        mask: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsMask", typing.Dict[builtins.str, typing.Any]]] = None,
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
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#comment DataDatabricksCleanRoomAssets#comment}.
        :param mask: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#mask DataDatabricksCleanRoomAssets#mask}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#name DataDatabricksCleanRoomAssets#name}.
        :param nullable: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#nullable DataDatabricksCleanRoomAssets#nullable}.
        :param partition_index: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#partition_index DataDatabricksCleanRoomAssets#partition_index}.
        :param position: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#position DataDatabricksCleanRoomAssets#position}.
        :param type_interval_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_interval_type DataDatabricksCleanRoomAssets#type_interval_type}.
        :param type_json: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_json DataDatabricksCleanRoomAssets#type_json}.
        :param type_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_name DataDatabricksCleanRoomAssets#type_name}.
        :param type_precision: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_precision DataDatabricksCleanRoomAssets#type_precision}.
        :param type_scale: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_scale DataDatabricksCleanRoomAssets#type_scale}.
        :param type_text: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_text DataDatabricksCleanRoomAssets#type_text}.
        '''
        if isinstance(mask, dict):
            mask = DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsMask(**mask)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06ec042b7fc658e6c42efe2c7764c19ba50adf762ef92259001bdf12c3bc0f2f)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#comment DataDatabricksCleanRoomAssets#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mask(
        self,
    ) -> typing.Optional["DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsMask"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#mask DataDatabricksCleanRoomAssets#mask}.'''
        result = self._values.get("mask")
        return typing.cast(typing.Optional["DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsMask"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#name DataDatabricksCleanRoomAssets#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nullable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#nullable DataDatabricksCleanRoomAssets#nullable}.'''
        result = self._values.get("nullable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def partition_index(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#partition_index DataDatabricksCleanRoomAssets#partition_index}.'''
        result = self._values.get("partition_index")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def position(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#position DataDatabricksCleanRoomAssets#position}.'''
        result = self._values.get("position")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_interval_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_interval_type DataDatabricksCleanRoomAssets#type_interval_type}.'''
        result = self._values.get("type_interval_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_json DataDatabricksCleanRoomAssets#type_json}.'''
        result = self._values.get("type_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_name DataDatabricksCleanRoomAssets#type_name}.'''
        result = self._values.get("type_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_precision(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_precision DataDatabricksCleanRoomAssets#type_precision}.'''
        result = self._values.get("type_precision")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_scale(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_scale DataDatabricksCleanRoomAssets#type_scale}.'''
        result = self._values.get("type_scale")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_text(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_text DataDatabricksCleanRoomAssets#type_text}.'''
        result = self._values.get("type_text")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetsAssetsForeignTableColumns(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e1cc0dc53e29a26ed71407d1f6c3abb20713309db1bb5de993aa1ca8842bd702)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d96ecf7785f7ee8f81678dbfa17571e442a6d050744b8a18f00b61db818187fa)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44f6d5ebe020c12f66b9bf570c4110c4b81f70933300bca4785a7564977e06ee)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c36e0bbe44df13a515a7b14944e0fe2ae43a2c2de6d436f6ae3f3f718d1f7a41)
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
            type_hints = typing.get_type_hints(_typecheckingstub__30104ded72b7c2604ba095ea606c5571ec240a168eaae1369271cdac2605251b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetsAssetsForeignTableColumns]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetsAssetsForeignTableColumns]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetsAssetsForeignTableColumns]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47ba5171675711fc95b55fff4bb6966446509f8aefac99ac620c9e3426b00c85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsMask",
    jsii_struct_bases=[],
    name_mapping={
        "function_name": "functionName",
        "using_column_names": "usingColumnNames",
    },
)
class DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsMask:
    def __init__(
        self,
        *,
        function_name: typing.Optional[builtins.str] = None,
        using_column_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#function_name DataDatabricksCleanRoomAssets#function_name}.
        :param using_column_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#using_column_names DataDatabricksCleanRoomAssets#using_column_names}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2d71bce57794f76b780d0a9a0c2306a9f1e4630f42ddbacc7da096a8ffc23fb)
            check_type(argname="argument function_name", value=function_name, expected_type=type_hints["function_name"])
            check_type(argname="argument using_column_names", value=using_column_names, expected_type=type_hints["using_column_names"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if function_name is not None:
            self._values["function_name"] = function_name
        if using_column_names is not None:
            self._values["using_column_names"] = using_column_names

    @builtins.property
    def function_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#function_name DataDatabricksCleanRoomAssets#function_name}.'''
        result = self._values.get("function_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def using_column_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#using_column_names DataDatabricksCleanRoomAssets#using_column_names}.'''
        result = self._values.get("using_column_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsMask(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsMaskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsMaskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__42de93a79e0a909e8ee48883665228d3bbe0183bb53c2a844b69aa20476e1c17)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2d63e97312d30f176d896562b32af07962267d29f4147410b2da0670441f7873)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "functionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usingColumnNames")
    def using_column_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "usingColumnNames"))

    @using_column_names.setter
    def using_column_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78a976e7bd11bd00b58eaceab681efe042b050c879d724c73b16f3b217196868)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usingColumnNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsMask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsMask]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsMask]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8dc0a0bc8e6309253e7d6fd841e1e3ec9e09987e11004363dbe8d10fb2bddab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__acbff6f3b5eda4e738b894f4cbf4603a40d858ea843e48fa257312aa67e17118)
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
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#function_name DataDatabricksCleanRoomAssets#function_name}.
        :param using_column_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#using_column_names DataDatabricksCleanRoomAssets#using_column_names}.
        '''
        value = DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsMask(
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
    def mask(
        self,
    ) -> DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsMaskOutputReference:
        return typing.cast(DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsMaskOutputReference, jsii.get(self, "mask"))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="maskInput")
    def mask_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsMask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsMask]], jsii.get(self, "maskInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__251d8d9605f30987a06385f7f71355d0a36d4343cc12cff86d6397513c654fc9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fccd62d60d702c8126cd21dfcd66b162e420007432f57b4901c97d7c9c09cc2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0bb747b14f01cec917f11887113aa34626cca21c67680501cca97952c6e8f398)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nullable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="partitionIndex")
    def partition_index(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "partitionIndex"))

    @partition_index.setter
    def partition_index(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df31aeb8bb484c8376acedd21bc5389e0e7ce2523cf72a5fde71b023e531b02e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "partitionIndex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="position")
    def position(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "position"))

    @position.setter
    def position(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a1c27d2b2a32660261cdfb10da1211631682a62ccdc63f8745b152ccccd69ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "position", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeIntervalType")
    def type_interval_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeIntervalType"))

    @type_interval_type.setter
    def type_interval_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__085306bf240de3ab5c30c88e914ea75c720ca0cecea0c124728d51896a3fa78b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeIntervalType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeJson")
    def type_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeJson"))

    @type_json.setter
    def type_json(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8b071ad8531bbc5f6bb68f2b5053d2c6e022eb330e457dd4dec27f91c432125)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeJson", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeName")
    def type_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeName"))

    @type_name.setter
    def type_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b151d49ebe867934ac2ca165e65a1316b49971c58b43653153e6bc56d7f77a7f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typePrecision")
    def type_precision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "typePrecision"))

    @type_precision.setter
    def type_precision(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9131cf3be8b7d238c273dfb9034b499c4060288100453484a4228e7149f516db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typePrecision", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeScale")
    def type_scale(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "typeScale"))

    @type_scale.setter
    def type_scale(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1492ae17e7c49081c2524a73ef35b1fd099373c4f71823c1899ff6123cc40d74)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeScale", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeText")
    def type_text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeText"))

    @type_text.setter
    def type_text(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a522909638e7c10e53a2bbdd9d41c78aeeb2707aaa4446934ef777635d635ff2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeText", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksCleanRoomAssetsAssetsForeignTableColumns]:
        return typing.cast(typing.Optional[DataDatabricksCleanRoomAssetsAssetsForeignTableColumns], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksCleanRoomAssetsAssetsForeignTableColumns],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__528c7744c642653aac775d563c13bccf3e451e0f529ad5569467af8cc350c7a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsForeignTableLocalDetails",
    jsii_struct_bases=[],
    name_mapping={"local_name": "localName"},
)
class DataDatabricksCleanRoomAssetsAssetsForeignTableLocalDetails:
    def __init__(self, *, local_name: builtins.str) -> None:
        '''
        :param local_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#local_name DataDatabricksCleanRoomAssets#local_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c9f69c97e298a3b872f31a6715c6fd47005196653b8ba32295f92698ce3613f)
            check_type(argname="argument local_name", value=local_name, expected_type=type_hints["local_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "local_name": local_name,
        }

    @builtins.property
    def local_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#local_name DataDatabricksCleanRoomAssets#local_name}.'''
        result = self._values.get("local_name")
        assert result is not None, "Required property 'local_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetsAssetsForeignTableLocalDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomAssetsAssetsForeignTableLocalDetailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsForeignTableLocalDetailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8c4f677bbfa325d0f9560d24735e2f63b9e47c7517c92cda6a69718cca80e376)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="localNameInput")
    def local_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "localNameInput"))

    @builtins.property
    @jsii.member(jsii_name="localName")
    def local_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "localName"))

    @local_name.setter
    def local_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__657e582fe794a7e3004afcc967eb8503bf00fa129ead2d5feed689158e5c1bc9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "localName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsForeignTableLocalDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsForeignTableLocalDetails]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsForeignTableLocalDetails]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e8e9c5b636cf14fcf7c762ad1ad3115c1b48061444140edb951478b411c2361)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksCleanRoomAssetsAssetsForeignTableOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsForeignTableOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ad0f57880b265b2f6044e9ff52ec039ce4aedb394a9f6980e11f48820d47906a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="columns")
    def columns(self) -> DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsList:
        return typing.cast(DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsList, jsii.get(self, "columns"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsForeignTable]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsForeignTable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsForeignTable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed55badc2064460d6905ab1692010a309c1be152a4016f7e015bb94238e61d55)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksCleanRoomAssetsAssetsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c590f7e5258b8869631f847af1262b2e9d2e6499dafde7c7f7605fa91c64e79d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksCleanRoomAssetsAssetsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f60c29df7415e3e826ec4336beae18f05f2d1fbb0d37330525cd3dbaed6030d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksCleanRoomAssetsAssetsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99648372affee022b34c9e5d149f28bfaea0680c7ff24f4e1836a16b0d567899)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fad6891f4172c9f6c545bad54cbd902935718415908d0b3c21082f0acab4db14)
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
            type_hints = typing.get_type_hints(_typecheckingstub__97da1c841be15ef9229639507177a165c714d71c8526cebbcd2529a51208d081)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetsAssets]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetsAssets]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetsAssets]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5bfdf5466ceaca7a7a01d57c5c82466937ca615b28f676f62ac5675ee559c845)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsNotebook",
    jsii_struct_bases=[],
    name_mapping={
        "notebook_content": "notebookContent",
        "runner_collaborator_aliases": "runnerCollaboratorAliases",
    },
)
class DataDatabricksCleanRoomAssetsAssetsNotebook:
    def __init__(
        self,
        *,
        notebook_content: builtins.str,
        runner_collaborator_aliases: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param notebook_content: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#notebook_content DataDatabricksCleanRoomAssets#notebook_content}.
        :param runner_collaborator_aliases: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#runner_collaborator_aliases DataDatabricksCleanRoomAssets#runner_collaborator_aliases}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e83b4da0d5082fdb0292c5cbf919939281feec026395f5cc9047b9553ff8c56)
            check_type(argname="argument notebook_content", value=notebook_content, expected_type=type_hints["notebook_content"])
            check_type(argname="argument runner_collaborator_aliases", value=runner_collaborator_aliases, expected_type=type_hints["runner_collaborator_aliases"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "notebook_content": notebook_content,
        }
        if runner_collaborator_aliases is not None:
            self._values["runner_collaborator_aliases"] = runner_collaborator_aliases

    @builtins.property
    def notebook_content(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#notebook_content DataDatabricksCleanRoomAssets#notebook_content}.'''
        result = self._values.get("notebook_content")
        assert result is not None, "Required property 'notebook_content' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def runner_collaborator_aliases(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#runner_collaborator_aliases DataDatabricksCleanRoomAssets#runner_collaborator_aliases}.'''
        result = self._values.get("runner_collaborator_aliases")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetsAssetsNotebook(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomAssetsAssetsNotebookOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsNotebookOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c4183429132d579442aaa0ebd845ef156faa45908837d23795d1116575c35758)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetRunnerCollaboratorAliases")
    def reset_runner_collaborator_aliases(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunnerCollaboratorAliases", []))

    @builtins.property
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property
    @jsii.member(jsii_name="reviews")
    def reviews(self) -> "DataDatabricksCleanRoomAssetsAssetsNotebookReviewsList":
        return typing.cast("DataDatabricksCleanRoomAssetsAssetsNotebookReviewsList", jsii.get(self, "reviews"))

    @builtins.property
    @jsii.member(jsii_name="reviewState")
    def review_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reviewState"))

    @builtins.property
    @jsii.member(jsii_name="notebookContentInput")
    def notebook_content_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "notebookContentInput"))

    @builtins.property
    @jsii.member(jsii_name="runnerCollaboratorAliasesInput")
    def runner_collaborator_aliases_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "runnerCollaboratorAliasesInput"))

    @builtins.property
    @jsii.member(jsii_name="notebookContent")
    def notebook_content(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notebookContent"))

    @notebook_content.setter
    def notebook_content(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3379d8925cede4615c2e2dc18f464253007b64933f9ef5b525bb1a26bab6b0e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notebookContent", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runnerCollaboratorAliases")
    def runner_collaborator_aliases(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "runnerCollaboratorAliases"))

    @runner_collaborator_aliases.setter
    def runner_collaborator_aliases(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a392f96645d577f3d3e3e5643c27390a7ce2646f0cfcb16eab3f2eed1bae8677)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runnerCollaboratorAliases", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsNotebook]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsNotebook]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsNotebook]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f19caa06f7e0075c9ec40a9c2d00a4bc496f548505ea0d0ce47341616780e01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsNotebookReviews",
    jsii_struct_bases=[],
    name_mapping={
        "comment": "comment",
        "created_at_millis": "createdAtMillis",
        "reviewer_collaborator_alias": "reviewerCollaboratorAlias",
        "review_state": "reviewState",
        "review_sub_reason": "reviewSubReason",
    },
)
class DataDatabricksCleanRoomAssetsAssetsNotebookReviews:
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        created_at_millis: typing.Optional[jsii.Number] = None,
        reviewer_collaborator_alias: typing.Optional[builtins.str] = None,
        review_state: typing.Optional[builtins.str] = None,
        review_sub_reason: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#comment DataDatabricksCleanRoomAssets#comment}.
        :param created_at_millis: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#created_at_millis DataDatabricksCleanRoomAssets#created_at_millis}.
        :param reviewer_collaborator_alias: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#reviewer_collaborator_alias DataDatabricksCleanRoomAssets#reviewer_collaborator_alias}.
        :param review_state: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#review_state DataDatabricksCleanRoomAssets#review_state}.
        :param review_sub_reason: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#review_sub_reason DataDatabricksCleanRoomAssets#review_sub_reason}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e84692452a029b2d4fe1b0cc7306ca432c340b3f681e7d01a3a782e902938c83)
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument created_at_millis", value=created_at_millis, expected_type=type_hints["created_at_millis"])
            check_type(argname="argument reviewer_collaborator_alias", value=reviewer_collaborator_alias, expected_type=type_hints["reviewer_collaborator_alias"])
            check_type(argname="argument review_state", value=review_state, expected_type=type_hints["review_state"])
            check_type(argname="argument review_sub_reason", value=review_sub_reason, expected_type=type_hints["review_sub_reason"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if comment is not None:
            self._values["comment"] = comment
        if created_at_millis is not None:
            self._values["created_at_millis"] = created_at_millis
        if reviewer_collaborator_alias is not None:
            self._values["reviewer_collaborator_alias"] = reviewer_collaborator_alias
        if review_state is not None:
            self._values["review_state"] = review_state
        if review_sub_reason is not None:
            self._values["review_sub_reason"] = review_sub_reason

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#comment DataDatabricksCleanRoomAssets#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def created_at_millis(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#created_at_millis DataDatabricksCleanRoomAssets#created_at_millis}.'''
        result = self._values.get("created_at_millis")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def reviewer_collaborator_alias(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#reviewer_collaborator_alias DataDatabricksCleanRoomAssets#reviewer_collaborator_alias}.'''
        result = self._values.get("reviewer_collaborator_alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def review_state(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#review_state DataDatabricksCleanRoomAssets#review_state}.'''
        result = self._values.get("review_state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def review_sub_reason(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#review_sub_reason DataDatabricksCleanRoomAssets#review_sub_reason}.'''
        result = self._values.get("review_sub_reason")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetsAssetsNotebookReviews(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomAssetsAssetsNotebookReviewsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsNotebookReviewsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3b22d488e3a61623666a679feb10bddc254d7359d8941aa768364a9ed655a52f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksCleanRoomAssetsAssetsNotebookReviewsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__585c83245e06226458f9984ec85d8a3a44136e6cf92b442fedfd19580f64735d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksCleanRoomAssetsAssetsNotebookReviewsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0969196e4f07b0c6a88addaf346a64e98bdd4f6d391b6ab0e77a71981c879447)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ae69db2d92b435598a056da0e2354cc9795b3848a799743082779c990896dc41)
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
            type_hints = typing.get_type_hints(_typecheckingstub__75326ffa455b620c150ed5f474939800958c9d2ab068137e08c7584b3ac0d413)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetsAssetsNotebookReviews]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetsAssetsNotebookReviews]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetsAssetsNotebookReviews]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__854c3cb7b342e5c0572a886a91b5f72832d2c21b41e0ca7107d8a3355f824462)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksCleanRoomAssetsAssetsNotebookReviewsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsNotebookReviewsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6f0687d2985ed1d003633b2cdf484c064854915124ccb0fa6571bc758080706b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="resetCreatedAtMillis")
    def reset_created_at_millis(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatedAtMillis", []))

    @jsii.member(jsii_name="resetReviewerCollaboratorAlias")
    def reset_reviewer_collaborator_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReviewerCollaboratorAlias", []))

    @jsii.member(jsii_name="resetReviewState")
    def reset_review_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReviewState", []))

    @jsii.member(jsii_name="resetReviewSubReason")
    def reset_review_sub_reason(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReviewSubReason", []))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="createdAtMillisInput")
    def created_at_millis_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "createdAtMillisInput"))

    @builtins.property
    @jsii.member(jsii_name="reviewerCollaboratorAliasInput")
    def reviewer_collaborator_alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "reviewerCollaboratorAliasInput"))

    @builtins.property
    @jsii.member(jsii_name="reviewStateInput")
    def review_state_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "reviewStateInput"))

    @builtins.property
    @jsii.member(jsii_name="reviewSubReasonInput")
    def review_sub_reason_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "reviewSubReasonInput"))

    @builtins.property
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45182bccacdbb8acc6fb4462553799744bb8a6f1d2ff2b21f9b6e1e5b17e2ea3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="createdAtMillis")
    def created_at_millis(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "createdAtMillis"))

    @created_at_millis.setter
    def created_at_millis(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c5b53c06432718019ecea97f4173144b7fd511bf8e94de7548c890c00f0782b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdAtMillis", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="reviewerCollaboratorAlias")
    def reviewer_collaborator_alias(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reviewerCollaboratorAlias"))

    @reviewer_collaborator_alias.setter
    def reviewer_collaborator_alias(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f02f08b2860c031e1e4f4f7c7f7f9f8afd05e83a6a6d0006b67f3ecc4cfa39b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reviewerCollaboratorAlias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="reviewState")
    def review_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reviewState"))

    @review_state.setter
    def review_state(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcd17a0458255c2b487a1f74731ffb6fee99c18bdeefaf6d110e42a82b11619a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reviewState", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="reviewSubReason")
    def review_sub_reason(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reviewSubReason"))

    @review_sub_reason.setter
    def review_sub_reason(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ddc1f327edecaef5f30af95424a513779adea59dd1e68a8bb5fa8a8fa48fa1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reviewSubReason", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksCleanRoomAssetsAssetsNotebookReviews]:
        return typing.cast(typing.Optional[DataDatabricksCleanRoomAssetsAssetsNotebookReviews], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksCleanRoomAssetsAssetsNotebookReviews],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bde1befaa7cbc6cc61a5ff87e9aef28ed9266db754b0b4a37800d1a2319fe358)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksCleanRoomAssetsAssetsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__26f9f4d66496cbefb86c0f5ccfe6ef96f93c4e8c3d8cd91e352ab3e707f7cb18)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putForeignTable")
    def put_foreign_table(self) -> None:
        value = DataDatabricksCleanRoomAssetsAssetsForeignTable()

        return typing.cast(None, jsii.invoke(self, "putForeignTable", [value]))

    @jsii.member(jsii_name="putForeignTableLocalDetails")
    def put_foreign_table_local_details(self, *, local_name: builtins.str) -> None:
        '''
        :param local_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#local_name DataDatabricksCleanRoomAssets#local_name}.
        '''
        value = DataDatabricksCleanRoomAssetsAssetsForeignTableLocalDetails(
            local_name=local_name
        )

        return typing.cast(None, jsii.invoke(self, "putForeignTableLocalDetails", [value]))

    @jsii.member(jsii_name="putNotebook")
    def put_notebook(
        self,
        *,
        notebook_content: builtins.str,
        runner_collaborator_aliases: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param notebook_content: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#notebook_content DataDatabricksCleanRoomAssets#notebook_content}.
        :param runner_collaborator_aliases: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#runner_collaborator_aliases DataDatabricksCleanRoomAssets#runner_collaborator_aliases}.
        '''
        value = DataDatabricksCleanRoomAssetsAssetsNotebook(
            notebook_content=notebook_content,
            runner_collaborator_aliases=runner_collaborator_aliases,
        )

        return typing.cast(None, jsii.invoke(self, "putNotebook", [value]))

    @jsii.member(jsii_name="putTable")
    def put_table(self) -> None:
        value = DataDatabricksCleanRoomAssetsAssetsTable()

        return typing.cast(None, jsii.invoke(self, "putTable", [value]))

    @jsii.member(jsii_name="putTableLocalDetails")
    def put_table_local_details(
        self,
        *,
        local_name: builtins.str,
        partitions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitions", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param local_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#local_name DataDatabricksCleanRoomAssets#local_name}.
        :param partitions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#partitions DataDatabricksCleanRoomAssets#partitions}.
        '''
        value = DataDatabricksCleanRoomAssetsAssetsTableLocalDetails(
            local_name=local_name, partitions=partitions
        )

        return typing.cast(None, jsii.invoke(self, "putTableLocalDetails", [value]))

    @jsii.member(jsii_name="putView")
    def put_view(self) -> None:
        value = DataDatabricksCleanRoomAssetsAssetsView()

        return typing.cast(None, jsii.invoke(self, "putView", [value]))

    @jsii.member(jsii_name="putViewLocalDetails")
    def put_view_local_details(self, *, local_name: builtins.str) -> None:
        '''
        :param local_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#local_name DataDatabricksCleanRoomAssets#local_name}.
        '''
        value = DataDatabricksCleanRoomAssetsAssetsViewLocalDetails(
            local_name=local_name
        )

        return typing.cast(None, jsii.invoke(self, "putViewLocalDetails", [value]))

    @jsii.member(jsii_name="putVolumeLocalDetails")
    def put_volume_local_details(self, *, local_name: builtins.str) -> None:
        '''
        :param local_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#local_name DataDatabricksCleanRoomAssets#local_name}.
        '''
        value = DataDatabricksCleanRoomAssetsAssetsVolumeLocalDetails(
            local_name=local_name
        )

        return typing.cast(None, jsii.invoke(self, "putVolumeLocalDetails", [value]))

    @jsii.member(jsii_name="resetCleanRoomName")
    def reset_clean_room_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCleanRoomName", []))

    @jsii.member(jsii_name="resetForeignTable")
    def reset_foreign_table(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForeignTable", []))

    @jsii.member(jsii_name="resetForeignTableLocalDetails")
    def reset_foreign_table_local_details(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForeignTableLocalDetails", []))

    @jsii.member(jsii_name="resetNotebook")
    def reset_notebook(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotebook", []))

    @jsii.member(jsii_name="resetTable")
    def reset_table(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTable", []))

    @jsii.member(jsii_name="resetTableLocalDetails")
    def reset_table_local_details(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTableLocalDetails", []))

    @jsii.member(jsii_name="resetView")
    def reset_view(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetView", []))

    @jsii.member(jsii_name="resetViewLocalDetails")
    def reset_view_local_details(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetViewLocalDetails", []))

    @jsii.member(jsii_name="resetVolumeLocalDetails")
    def reset_volume_local_details(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVolumeLocalDetails", []))

    @builtins.property
    @jsii.member(jsii_name="addedAt")
    def added_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "addedAt"))

    @builtins.property
    @jsii.member(jsii_name="foreignTable")
    def foreign_table(
        self,
    ) -> DataDatabricksCleanRoomAssetsAssetsForeignTableOutputReference:
        return typing.cast(DataDatabricksCleanRoomAssetsAssetsForeignTableOutputReference, jsii.get(self, "foreignTable"))

    @builtins.property
    @jsii.member(jsii_name="foreignTableLocalDetails")
    def foreign_table_local_details(
        self,
    ) -> DataDatabricksCleanRoomAssetsAssetsForeignTableLocalDetailsOutputReference:
        return typing.cast(DataDatabricksCleanRoomAssetsAssetsForeignTableLocalDetailsOutputReference, jsii.get(self, "foreignTableLocalDetails"))

    @builtins.property
    @jsii.member(jsii_name="notebook")
    def notebook(self) -> DataDatabricksCleanRoomAssetsAssetsNotebookOutputReference:
        return typing.cast(DataDatabricksCleanRoomAssetsAssetsNotebookOutputReference, jsii.get(self, "notebook"))

    @builtins.property
    @jsii.member(jsii_name="ownerCollaboratorAlias")
    def owner_collaborator_alias(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ownerCollaboratorAlias"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="table")
    def table(self) -> "DataDatabricksCleanRoomAssetsAssetsTableOutputReference":
        return typing.cast("DataDatabricksCleanRoomAssetsAssetsTableOutputReference", jsii.get(self, "table"))

    @builtins.property
    @jsii.member(jsii_name="tableLocalDetails")
    def table_local_details(
        self,
    ) -> "DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsOutputReference":
        return typing.cast("DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsOutputReference", jsii.get(self, "tableLocalDetails"))

    @builtins.property
    @jsii.member(jsii_name="view")
    def view(self) -> "DataDatabricksCleanRoomAssetsAssetsViewOutputReference":
        return typing.cast("DataDatabricksCleanRoomAssetsAssetsViewOutputReference", jsii.get(self, "view"))

    @builtins.property
    @jsii.member(jsii_name="viewLocalDetails")
    def view_local_details(
        self,
    ) -> "DataDatabricksCleanRoomAssetsAssetsViewLocalDetailsOutputReference":
        return typing.cast("DataDatabricksCleanRoomAssetsAssetsViewLocalDetailsOutputReference", jsii.get(self, "viewLocalDetails"))

    @builtins.property
    @jsii.member(jsii_name="volumeLocalDetails")
    def volume_local_details(
        self,
    ) -> "DataDatabricksCleanRoomAssetsAssetsVolumeLocalDetailsOutputReference":
        return typing.cast("DataDatabricksCleanRoomAssetsAssetsVolumeLocalDetailsOutputReference", jsii.get(self, "volumeLocalDetails"))

    @builtins.property
    @jsii.member(jsii_name="assetTypeInput")
    def asset_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "assetTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="cleanRoomNameInput")
    def clean_room_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cleanRoomNameInput"))

    @builtins.property
    @jsii.member(jsii_name="foreignTableInput")
    def foreign_table_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsForeignTable]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsForeignTable]], jsii.get(self, "foreignTableInput"))

    @builtins.property
    @jsii.member(jsii_name="foreignTableLocalDetailsInput")
    def foreign_table_local_details_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsForeignTableLocalDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsForeignTableLocalDetails]], jsii.get(self, "foreignTableLocalDetailsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="notebookInput")
    def notebook_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsNotebook]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsNotebook]], jsii.get(self, "notebookInput"))

    @builtins.property
    @jsii.member(jsii_name="tableInput")
    def table_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksCleanRoomAssetsAssetsTable"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksCleanRoomAssetsAssetsTable"]], jsii.get(self, "tableInput"))

    @builtins.property
    @jsii.member(jsii_name="tableLocalDetailsInput")
    def table_local_details_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksCleanRoomAssetsAssetsTableLocalDetails"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksCleanRoomAssetsAssetsTableLocalDetails"]], jsii.get(self, "tableLocalDetailsInput"))

    @builtins.property
    @jsii.member(jsii_name="viewInput")
    def view_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksCleanRoomAssetsAssetsView"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksCleanRoomAssetsAssetsView"]], jsii.get(self, "viewInput"))

    @builtins.property
    @jsii.member(jsii_name="viewLocalDetailsInput")
    def view_local_details_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksCleanRoomAssetsAssetsViewLocalDetails"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksCleanRoomAssetsAssetsViewLocalDetails"]], jsii.get(self, "viewLocalDetailsInput"))

    @builtins.property
    @jsii.member(jsii_name="volumeLocalDetailsInput")
    def volume_local_details_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksCleanRoomAssetsAssetsVolumeLocalDetails"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksCleanRoomAssetsAssetsVolumeLocalDetails"]], jsii.get(self, "volumeLocalDetailsInput"))

    @builtins.property
    @jsii.member(jsii_name="assetType")
    def asset_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "assetType"))

    @asset_type.setter
    def asset_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9cfdfb186c3896a178816e0554a0c5ad770673a44af3d499c1ace74e05cdd0c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "assetType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cleanRoomName")
    def clean_room_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cleanRoomName"))

    @clean_room_name.setter
    def clean_room_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f19658dbbf8538f1a1ffc06e6c7cdedb84f2144424b86254c3e197c7f7a0d31)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cleanRoomName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a62a26a4c5a4b54007060a62fc201afe0f913130c3efde46b58fb27e463fe5c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataDatabricksCleanRoomAssetsAssets]:
        return typing.cast(typing.Optional[DataDatabricksCleanRoomAssetsAssets], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksCleanRoomAssetsAssets],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c03dc1ada6e6f1e3ea010e4995a420391320d4c9501fad71b60f056e10f2abd5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsTable",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksCleanRoomAssetsAssetsTable:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetsAssetsTable(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsTableColumns",
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
class DataDatabricksCleanRoomAssetsAssetsTableColumns:
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        mask: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetsAssetsTableColumnsMask", typing.Dict[builtins.str, typing.Any]]] = None,
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
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#comment DataDatabricksCleanRoomAssets#comment}.
        :param mask: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#mask DataDatabricksCleanRoomAssets#mask}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#name DataDatabricksCleanRoomAssets#name}.
        :param nullable: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#nullable DataDatabricksCleanRoomAssets#nullable}.
        :param partition_index: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#partition_index DataDatabricksCleanRoomAssets#partition_index}.
        :param position: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#position DataDatabricksCleanRoomAssets#position}.
        :param type_interval_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_interval_type DataDatabricksCleanRoomAssets#type_interval_type}.
        :param type_json: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_json DataDatabricksCleanRoomAssets#type_json}.
        :param type_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_name DataDatabricksCleanRoomAssets#type_name}.
        :param type_precision: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_precision DataDatabricksCleanRoomAssets#type_precision}.
        :param type_scale: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_scale DataDatabricksCleanRoomAssets#type_scale}.
        :param type_text: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_text DataDatabricksCleanRoomAssets#type_text}.
        '''
        if isinstance(mask, dict):
            mask = DataDatabricksCleanRoomAssetsAssetsTableColumnsMask(**mask)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5762e3825c63bbd88b96705dd6434c0a978edc09ff49d8a7ec81072812864cd9)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#comment DataDatabricksCleanRoomAssets#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mask(
        self,
    ) -> typing.Optional["DataDatabricksCleanRoomAssetsAssetsTableColumnsMask"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#mask DataDatabricksCleanRoomAssets#mask}.'''
        result = self._values.get("mask")
        return typing.cast(typing.Optional["DataDatabricksCleanRoomAssetsAssetsTableColumnsMask"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#name DataDatabricksCleanRoomAssets#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nullable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#nullable DataDatabricksCleanRoomAssets#nullable}.'''
        result = self._values.get("nullable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def partition_index(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#partition_index DataDatabricksCleanRoomAssets#partition_index}.'''
        result = self._values.get("partition_index")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def position(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#position DataDatabricksCleanRoomAssets#position}.'''
        result = self._values.get("position")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_interval_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_interval_type DataDatabricksCleanRoomAssets#type_interval_type}.'''
        result = self._values.get("type_interval_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_json DataDatabricksCleanRoomAssets#type_json}.'''
        result = self._values.get("type_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_name DataDatabricksCleanRoomAssets#type_name}.'''
        result = self._values.get("type_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_precision(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_precision DataDatabricksCleanRoomAssets#type_precision}.'''
        result = self._values.get("type_precision")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_scale(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_scale DataDatabricksCleanRoomAssets#type_scale}.'''
        result = self._values.get("type_scale")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_text(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_text DataDatabricksCleanRoomAssets#type_text}.'''
        result = self._values.get("type_text")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetsAssetsTableColumns(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomAssetsAssetsTableColumnsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsTableColumnsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b706ebe6efd8720c398b58d4ad70bc8ed864555227e647b7ee131465d661ee67)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksCleanRoomAssetsAssetsTableColumnsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e065cdcf4682ebfecb947adc089c6bc203c8aac0226c03eb1113b492bd7543c6)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksCleanRoomAssetsAssetsTableColumnsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ce00250c679bcb819b945175a6874901bada18441100d1b4b3e531bcd295728)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1af7dea25cde2c637430bc763f91a92d2d021c75c252cd3415d1c747aefcd3e9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__77f2a4349f9212d357dad8afc26b2f7a939dbc81d6d327fc22c2d4da2947b7e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetsAssetsTableColumns]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetsAssetsTableColumns]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetsAssetsTableColumns]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9057b2168c43f572c72a80065bd468ecf73f7503db319acb378e7ea079fa9264)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsTableColumnsMask",
    jsii_struct_bases=[],
    name_mapping={
        "function_name": "functionName",
        "using_column_names": "usingColumnNames",
    },
)
class DataDatabricksCleanRoomAssetsAssetsTableColumnsMask:
    def __init__(
        self,
        *,
        function_name: typing.Optional[builtins.str] = None,
        using_column_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#function_name DataDatabricksCleanRoomAssets#function_name}.
        :param using_column_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#using_column_names DataDatabricksCleanRoomAssets#using_column_names}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a635c675bd239fb1acafd9222c426749db276524f5c2abc1b9dc74d8f13c1e6)
            check_type(argname="argument function_name", value=function_name, expected_type=type_hints["function_name"])
            check_type(argname="argument using_column_names", value=using_column_names, expected_type=type_hints["using_column_names"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if function_name is not None:
            self._values["function_name"] = function_name
        if using_column_names is not None:
            self._values["using_column_names"] = using_column_names

    @builtins.property
    def function_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#function_name DataDatabricksCleanRoomAssets#function_name}.'''
        result = self._values.get("function_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def using_column_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#using_column_names DataDatabricksCleanRoomAssets#using_column_names}.'''
        result = self._values.get("using_column_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetsAssetsTableColumnsMask(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomAssetsAssetsTableColumnsMaskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsTableColumnsMaskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__254542fa8f7d50d3e0ba205a0824ee0a98e9a4364b9285f539363b494bfd07df)
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
            type_hints = typing.get_type_hints(_typecheckingstub__60a864765245a11b707c83b2802748f5eb4c4a6c599eef636ed2029d96c474d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "functionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usingColumnNames")
    def using_column_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "usingColumnNames"))

    @using_column_names.setter
    def using_column_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__294410eb2041339778a796461210d4fe26ce0adcaf0484816c12ed88b2e1f9f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usingColumnNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsTableColumnsMask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsTableColumnsMask]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsTableColumnsMask]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6aba457a2016a74277dfa146ff749310ffa1a8003743c916caf1229d11bd35f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksCleanRoomAssetsAssetsTableColumnsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsTableColumnsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1b0062eb391d622aeb52e392db425f7be7aca757861cb32f781c6fa1453276c9)
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
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#function_name DataDatabricksCleanRoomAssets#function_name}.
        :param using_column_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#using_column_names DataDatabricksCleanRoomAssets#using_column_names}.
        '''
        value = DataDatabricksCleanRoomAssetsAssetsTableColumnsMask(
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
    def mask(
        self,
    ) -> DataDatabricksCleanRoomAssetsAssetsTableColumnsMaskOutputReference:
        return typing.cast(DataDatabricksCleanRoomAssetsAssetsTableColumnsMaskOutputReference, jsii.get(self, "mask"))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="maskInput")
    def mask_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsTableColumnsMask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsTableColumnsMask]], jsii.get(self, "maskInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__4e6e65834a3d7841fd13295ca7fa4f3a41e35af3ac48d482e2122b8393d49601)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efb36c81d614d62c488c41d9ec2df857c10f7082060a4bb562e7a31b59f976aa)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6dd8d4ad77176357d3ea026d00e5dc4275f42e91dd2aff4c985a22588c0ea29e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nullable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="partitionIndex")
    def partition_index(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "partitionIndex"))

    @partition_index.setter
    def partition_index(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54a383906cb63c53cb167ecef3998e27edd8eaa383d8a29283d5c51874d93c0f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "partitionIndex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="position")
    def position(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "position"))

    @position.setter
    def position(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcee01cccee34a5eb7c535b10aba8ba756163a47820d975bd1435f3c7a7d1491)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "position", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeIntervalType")
    def type_interval_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeIntervalType"))

    @type_interval_type.setter
    def type_interval_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e49a6376a722d6fa29a34040034149a4b6ea18f75cc159d6c09962c55bee9649)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeIntervalType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeJson")
    def type_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeJson"))

    @type_json.setter
    def type_json(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e56fec945f0794378012300f43e84478b143c88a509a551ff092f6be0fd5cff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeJson", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeName")
    def type_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeName"))

    @type_name.setter
    def type_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2c39d1eb5a966a3086e0650cdd9ff8b8f803cbb7acc95a33a0947047b9c9103)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typePrecision")
    def type_precision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "typePrecision"))

    @type_precision.setter
    def type_precision(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd364f365009f51a34437a52596439faf587aabd2b67a7c1f9b3f0b757744cbf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typePrecision", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeScale")
    def type_scale(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "typeScale"))

    @type_scale.setter
    def type_scale(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d66677c21ba9fd5de34699f71ba0b1d67b36c7bf9575b690fa79aad8c070391)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeScale", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeText")
    def type_text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeText"))

    @type_text.setter
    def type_text(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__648fb228b6777599dfaf307beb7d82aa902d046a1f2d27722874a005b7c1aea1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeText", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksCleanRoomAssetsAssetsTableColumns]:
        return typing.cast(typing.Optional[DataDatabricksCleanRoomAssetsAssetsTableColumns], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksCleanRoomAssetsAssetsTableColumns],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a10112d860300a3997485b3aecfaffbbfa0a1c61e90567d91133e4087a076e13)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsTableLocalDetails",
    jsii_struct_bases=[],
    name_mapping={"local_name": "localName", "partitions": "partitions"},
)
class DataDatabricksCleanRoomAssetsAssetsTableLocalDetails:
    def __init__(
        self,
        *,
        local_name: builtins.str,
        partitions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitions", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param local_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#local_name DataDatabricksCleanRoomAssets#local_name}.
        :param partitions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#partitions DataDatabricksCleanRoomAssets#partitions}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1043145ad9b91a44dbc53e073eac6bc4a4bd9e37ae2beaacb7ad1f2edf6b1473)
            check_type(argname="argument local_name", value=local_name, expected_type=type_hints["local_name"])
            check_type(argname="argument partitions", value=partitions, expected_type=type_hints["partitions"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "local_name": local_name,
        }
        if partitions is not None:
            self._values["partitions"] = partitions

    @builtins.property
    def local_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#local_name DataDatabricksCleanRoomAssets#local_name}.'''
        result = self._values.get("local_name")
        assert result is not None, "Required property 'local_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def partitions(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitions"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#partitions DataDatabricksCleanRoomAssets#partitions}.'''
        result = self._values.get("partitions")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitions"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetsAssetsTableLocalDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__29e638f8c80abfc38d5e4e7dbcb083aede902f65556788c4614d16c57c027490)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putPartitions")
    def put_partitions(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitions", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b156daefda2c43df44cefc870d9e4e6604fd89807c38275a82a08360d3e1ebc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putPartitions", [value]))

    @jsii.member(jsii_name="resetPartitions")
    def reset_partitions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPartitions", []))

    @builtins.property
    @jsii.member(jsii_name="partitions")
    def partitions(
        self,
    ) -> "DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsList":
        return typing.cast("DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsList", jsii.get(self, "partitions"))

    @builtins.property
    @jsii.member(jsii_name="localNameInput")
    def local_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "localNameInput"))

    @builtins.property
    @jsii.member(jsii_name="partitionsInput")
    def partitions_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitions"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitions"]]], jsii.get(self, "partitionsInput"))

    @builtins.property
    @jsii.member(jsii_name="localName")
    def local_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "localName"))

    @local_name.setter
    def local_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__409381f728e2de50c9a6b99c48a517f3e1a2c37ba5647be70be43db553ac506a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "localName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsTableLocalDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsTableLocalDetails]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsTableLocalDetails]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2efc9157b03cb9abb063dd7cd5522c7b1ebaeb0bf26c9669f516d1852f34b5e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitions",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitions:
    def __init__(
        self,
        *,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValue", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#value DataDatabricksCleanRoomAssets#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__448154e8a4c1c228d6eb4e1fe269dfbf5692c878712788ecc38612477479d041)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValue"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#value DataDatabricksCleanRoomAssets#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValue"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7a6f96ca47d6508a6ecc23778212b72fa44a183c6812f14f78501145825b63ba)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d0a2e772c54855a5561028cb6cf91e6c239e5f7df7ead827b30a8039849e374)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4be3161cc4f3e7006c81b1bb3d67b65ab01cee080d58cf9f7cfc1d57db8484ea)
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
            type_hints = typing.get_type_hints(_typecheckingstub__38df0a06f28032dc1e8ab1c0d920366c5aa7fe553d4a808766c4f85d92ecd6f7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__527a9c51fbb58b7d2e68b9a9bec24414aa9c69457b545af30ea80504521da088)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitions]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitions]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitions]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54231806553ce569a7cc254eb9923865e5dabb98959cb13beeaea19368e04ce5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4cdfb21285da34e37df3689af4f680311feee105c29255691b5f19cef5da1069)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putValue")
    def put_value(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValue", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26bbd2b8ee60e525401cab5ebc3253c9bd839a6481c6ba691e816515d85096e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putValue", [value]))

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(
        self,
    ) -> "DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValueList":
        return typing.cast("DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValueList", jsii.get(self, "value"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValue"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValue"]]], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitions]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitions]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitions]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d7e2dc13b38fa764b30203b075bbd1328f1f5cb6a8d09eba6f80baa4cee8b1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValue",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "op": "op",
        "recipient_property_key": "recipientPropertyKey",
        "value": "value",
    },
)
class DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValue:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        op: typing.Optional[builtins.str] = None,
        recipient_property_key: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#name DataDatabricksCleanRoomAssets#name}.
        :param op: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#op DataDatabricksCleanRoomAssets#op}.
        :param recipient_property_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#recipient_property_key DataDatabricksCleanRoomAssets#recipient_property_key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#value DataDatabricksCleanRoomAssets#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac5f1fed7cf9154fc273889238f03906c998b93a1abe90e78db3ba4327b38555)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument op", value=op, expected_type=type_hints["op"])
            check_type(argname="argument recipient_property_key", value=recipient_property_key, expected_type=type_hints["recipient_property_key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if op is not None:
            self._values["op"] = op
        if recipient_property_key is not None:
            self._values["recipient_property_key"] = recipient_property_key
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#name DataDatabricksCleanRoomAssets#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def op(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#op DataDatabricksCleanRoomAssets#op}.'''
        result = self._values.get("op")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def recipient_property_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#recipient_property_key DataDatabricksCleanRoomAssets#recipient_property_key}.'''
        result = self._values.get("recipient_property_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#value DataDatabricksCleanRoomAssets#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValueList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValueList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2bedd99da4001c2670fc0322f1764b82c239a0edeb9f83115604f45ccb478563)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValueOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__301060877858ce1b332339e2c88cb01360740db14d326c23b1da037c141f59b8)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValueOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8be7597d1f21109a53d21bff537f31f277ff75e91d4568e6411c05242554fdcb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8f18fa443a949e36af794561ea9eb4f3ea81cee36e4cfae609e44336774abb2a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__acfe3f06aa7a27a3a5764095a0cc100555a6bc65149ac81f39ca0eddeb76e0d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValue]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValue]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValue]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb618703c4d17cc7d41cab59c1b7914bca065f781e14a8783c7f4f82f9ad6e90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValueOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValueOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__472cde61241ac21ed1613bb10205edd343c1d0524d611a2994ba76ed1504318d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetOp")
    def reset_op(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOp", []))

    @jsii.member(jsii_name="resetRecipientPropertyKey")
    def reset_recipient_property_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRecipientPropertyKey", []))

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="opInput")
    def op_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "opInput"))

    @builtins.property
    @jsii.member(jsii_name="recipientPropertyKeyInput")
    def recipient_property_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "recipientPropertyKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08faaedd8068c2f2ddb23555c9c23d41a2fb6aa7962b5bc0a57fa194b89dc0a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="op")
    def op(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "op"))

    @op.setter
    def op(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc4f2ccded5322393a6934c85474a04400513662c1aff2b2c7198f2884d3008c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "op", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="recipientPropertyKey")
    def recipient_property_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "recipientPropertyKey"))

    @recipient_property_key.setter
    def recipient_property_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4889bc1e4ef46cf566e9653765113e4771e7bd99a3092fff27c98f88d7dd197c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "recipientPropertyKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2717e927467a59f4b200af17e06da0f9141019b63d7a418dbd6daf097278c024)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValue]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValue]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValue]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__573ed6db82d6ef6a926b3ffbe5d170f1ec843f6559ab03693a088c096c920dca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksCleanRoomAssetsAssetsTableOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsTableOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__00f728243d233e6de9cc29b18f1491e128137818ead44397c8297515a452c373)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="columns")
    def columns(self) -> DataDatabricksCleanRoomAssetsAssetsTableColumnsList:
        return typing.cast(DataDatabricksCleanRoomAssetsAssetsTableColumnsList, jsii.get(self, "columns"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsTable]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsTable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsTable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23d3d28dc4550506b952acd632cbe5e9821587f86b9922b6fd2d24ab3e736038)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsView",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksCleanRoomAssetsAssetsView:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetsAssetsView(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsViewColumns",
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
class DataDatabricksCleanRoomAssetsAssetsViewColumns:
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        mask: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetsAssetsViewColumnsMask", typing.Dict[builtins.str, typing.Any]]] = None,
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
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#comment DataDatabricksCleanRoomAssets#comment}.
        :param mask: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#mask DataDatabricksCleanRoomAssets#mask}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#name DataDatabricksCleanRoomAssets#name}.
        :param nullable: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#nullable DataDatabricksCleanRoomAssets#nullable}.
        :param partition_index: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#partition_index DataDatabricksCleanRoomAssets#partition_index}.
        :param position: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#position DataDatabricksCleanRoomAssets#position}.
        :param type_interval_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_interval_type DataDatabricksCleanRoomAssets#type_interval_type}.
        :param type_json: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_json DataDatabricksCleanRoomAssets#type_json}.
        :param type_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_name DataDatabricksCleanRoomAssets#type_name}.
        :param type_precision: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_precision DataDatabricksCleanRoomAssets#type_precision}.
        :param type_scale: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_scale DataDatabricksCleanRoomAssets#type_scale}.
        :param type_text: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_text DataDatabricksCleanRoomAssets#type_text}.
        '''
        if isinstance(mask, dict):
            mask = DataDatabricksCleanRoomAssetsAssetsViewColumnsMask(**mask)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__479d08fa75464b7108fa3355b363281d9ab9be99b1ea45c1e467ae4915bfd61c)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#comment DataDatabricksCleanRoomAssets#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mask(
        self,
    ) -> typing.Optional["DataDatabricksCleanRoomAssetsAssetsViewColumnsMask"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#mask DataDatabricksCleanRoomAssets#mask}.'''
        result = self._values.get("mask")
        return typing.cast(typing.Optional["DataDatabricksCleanRoomAssetsAssetsViewColumnsMask"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#name DataDatabricksCleanRoomAssets#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nullable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#nullable DataDatabricksCleanRoomAssets#nullable}.'''
        result = self._values.get("nullable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def partition_index(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#partition_index DataDatabricksCleanRoomAssets#partition_index}.'''
        result = self._values.get("partition_index")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def position(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#position DataDatabricksCleanRoomAssets#position}.'''
        result = self._values.get("position")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_interval_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_interval_type DataDatabricksCleanRoomAssets#type_interval_type}.'''
        result = self._values.get("type_interval_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_json DataDatabricksCleanRoomAssets#type_json}.'''
        result = self._values.get("type_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_name DataDatabricksCleanRoomAssets#type_name}.'''
        result = self._values.get("type_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_precision(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_precision DataDatabricksCleanRoomAssets#type_precision}.'''
        result = self._values.get("type_precision")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_scale(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_scale DataDatabricksCleanRoomAssets#type_scale}.'''
        result = self._values.get("type_scale")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_text(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#type_text DataDatabricksCleanRoomAssets#type_text}.'''
        result = self._values.get("type_text")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetsAssetsViewColumns(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomAssetsAssetsViewColumnsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsViewColumnsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__16cb9a29b40a6df9902ec80be9f8f3d987ec0e1e54ce611afe413ba277780f2e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksCleanRoomAssetsAssetsViewColumnsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a253de48ec83f9c37fccb31afd506fa5cc8e3a7df207856408b115021926c0b7)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksCleanRoomAssetsAssetsViewColumnsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab6c4a166ceb1db0a5a23929293a713b8e3724db51a9a7aa5bc2e6a992efc751)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d9625af70ae5f33873352d9911614e45d83e1bd467891e3f702000271adafe37)
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
            type_hints = typing.get_type_hints(_typecheckingstub__453343442d6df371ce897ffcb285c22f91a71d745255692643572e0f3de0322d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetsAssetsViewColumns]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetsAssetsViewColumns]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetsAssetsViewColumns]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f92265808ae02ae9af715156be3df506874a0e77fc53d1b338c6a0ac42764774)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsViewColumnsMask",
    jsii_struct_bases=[],
    name_mapping={
        "function_name": "functionName",
        "using_column_names": "usingColumnNames",
    },
)
class DataDatabricksCleanRoomAssetsAssetsViewColumnsMask:
    def __init__(
        self,
        *,
        function_name: typing.Optional[builtins.str] = None,
        using_column_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#function_name DataDatabricksCleanRoomAssets#function_name}.
        :param using_column_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#using_column_names DataDatabricksCleanRoomAssets#using_column_names}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7bf20e9443495d897c785b9d962fe7d4403d83d2576b99494b719c6819498e08)
            check_type(argname="argument function_name", value=function_name, expected_type=type_hints["function_name"])
            check_type(argname="argument using_column_names", value=using_column_names, expected_type=type_hints["using_column_names"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if function_name is not None:
            self._values["function_name"] = function_name
        if using_column_names is not None:
            self._values["using_column_names"] = using_column_names

    @builtins.property
    def function_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#function_name DataDatabricksCleanRoomAssets#function_name}.'''
        result = self._values.get("function_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def using_column_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#using_column_names DataDatabricksCleanRoomAssets#using_column_names}.'''
        result = self._values.get("using_column_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetsAssetsViewColumnsMask(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomAssetsAssetsViewColumnsMaskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsViewColumnsMaskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f232843ece1a87d49aeac5ef966a60b0c59313b68f16d5e1d076cdfa59496a80)
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
            type_hints = typing.get_type_hints(_typecheckingstub__99229a48f028114d55d73112e0d20c1e840d68313b2ef7036f36f7ae685a71de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "functionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usingColumnNames")
    def using_column_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "usingColumnNames"))

    @using_column_names.setter
    def using_column_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42ab3ceb03a0959dc9925d7061052e196190ec759cf5c5065ea04cdcfe07a216)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usingColumnNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsViewColumnsMask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsViewColumnsMask]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsViewColumnsMask]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d65899e271a404d3420cd5ca57a961caebcda5bbe41c99bf199193ce86f32bf6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksCleanRoomAssetsAssetsViewColumnsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsViewColumnsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5e41aa1280d1014d0b77b4f5af85a3740befd8f8e4a58f9df0e17785a4405802)
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
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#function_name DataDatabricksCleanRoomAssets#function_name}.
        :param using_column_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#using_column_names DataDatabricksCleanRoomAssets#using_column_names}.
        '''
        value = DataDatabricksCleanRoomAssetsAssetsViewColumnsMask(
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
    def mask(self) -> DataDatabricksCleanRoomAssetsAssetsViewColumnsMaskOutputReference:
        return typing.cast(DataDatabricksCleanRoomAssetsAssetsViewColumnsMaskOutputReference, jsii.get(self, "mask"))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="maskInput")
    def mask_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsViewColumnsMask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsViewColumnsMask]], jsii.get(self, "maskInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__c92cf5de89f0af4f5f6679b8d7f585b284202fc214e4681ed98b56ffab430d29)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4cf1ef5b8e6da12956b8e00f5d8e1e491aadc8ddafd06afe8e8b6928471aa82)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9b85b88a5be753acd5f3843e5d66c54a93421aa1bd425332a067b3e446652660)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nullable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="partitionIndex")
    def partition_index(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "partitionIndex"))

    @partition_index.setter
    def partition_index(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dac52c5c401bf6d61b7899284fcde9a73abe236ed6d62473b94397583fc97144)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "partitionIndex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="position")
    def position(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "position"))

    @position.setter
    def position(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af06deb5ceeea68e880e4ec33ccdbd1b5489cce93d51fa4ef3f3c0019af8a222)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "position", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeIntervalType")
    def type_interval_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeIntervalType"))

    @type_interval_type.setter
    def type_interval_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76fc45c2af1c81e4ed990832ea599a164ef827ff8f540b036cb8ae8da40e094c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeIntervalType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeJson")
    def type_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeJson"))

    @type_json.setter
    def type_json(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05380d43d77bc6e24a4f45dbfde9f1b8ef4bcbc96388998a66676af8f717391d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeJson", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeName")
    def type_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeName"))

    @type_name.setter
    def type_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6ba099d7a9f0310a8238ab934ec340f3946296e259eee6e7b7938f818476e67)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typePrecision")
    def type_precision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "typePrecision"))

    @type_precision.setter
    def type_precision(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7fcfb008b1a40b06b8d130a81471d157502e1ddf1f59ca3e7812def406521b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typePrecision", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeScale")
    def type_scale(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "typeScale"))

    @type_scale.setter
    def type_scale(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a2e112db29df9653e4f342155e665ba7efceb2c3f94da0f3e052343d76e6d32)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeScale", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeText")
    def type_text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeText"))

    @type_text.setter
    def type_text(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc0d964452eeb98d6981f1fcccc5e95e269f9bef2246831b2dc251a27f9f5042)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeText", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksCleanRoomAssetsAssetsViewColumns]:
        return typing.cast(typing.Optional[DataDatabricksCleanRoomAssetsAssetsViewColumns], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksCleanRoomAssetsAssetsViewColumns],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b153dcac07c05ada01a809725c574f97ca7bce9cfccee8c5c319cba884179109)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsViewLocalDetails",
    jsii_struct_bases=[],
    name_mapping={"local_name": "localName"},
)
class DataDatabricksCleanRoomAssetsAssetsViewLocalDetails:
    def __init__(self, *, local_name: builtins.str) -> None:
        '''
        :param local_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#local_name DataDatabricksCleanRoomAssets#local_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05af3b1b4845e0eee2e0087dabc32480d93d18908bea7c32dd9406e847b98fea)
            check_type(argname="argument local_name", value=local_name, expected_type=type_hints["local_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "local_name": local_name,
        }

    @builtins.property
    def local_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#local_name DataDatabricksCleanRoomAssets#local_name}.'''
        result = self._values.get("local_name")
        assert result is not None, "Required property 'local_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetsAssetsViewLocalDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomAssetsAssetsViewLocalDetailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsViewLocalDetailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3b24812626cf3daf42ebef2133afd571d94a308ebd396521c38105639315775c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="localNameInput")
    def local_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "localNameInput"))

    @builtins.property
    @jsii.member(jsii_name="localName")
    def local_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "localName"))

    @local_name.setter
    def local_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd56cd7fc53aaa2374b3a14ca26ff116b087b62400ecddf2f43b312a7119c170)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "localName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsViewLocalDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsViewLocalDetails]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsViewLocalDetails]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d79c8ff684a27f0cd2a41ddf4d301c97092f9e1b6dd7e24db8978b7802f437a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksCleanRoomAssetsAssetsViewOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsViewOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0847dc9b1b6f8eddd7213b0fda566fbb7258a698d929277e89b7f3764c5c1b22)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="columns")
    def columns(self) -> DataDatabricksCleanRoomAssetsAssetsViewColumnsList:
        return typing.cast(DataDatabricksCleanRoomAssetsAssetsViewColumnsList, jsii.get(self, "columns"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsView]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsView]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsView]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ca421378a8f04e3b7ad8c4e723e2aca0ef5792b264b4381c1e59e844a314bfd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsVolumeLocalDetails",
    jsii_struct_bases=[],
    name_mapping={"local_name": "localName"},
)
class DataDatabricksCleanRoomAssetsAssetsVolumeLocalDetails:
    def __init__(self, *, local_name: builtins.str) -> None:
        '''
        :param local_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#local_name DataDatabricksCleanRoomAssets#local_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aef66e5cb569321c965874a63535903ee1e7af27ad6bf2d17b88b96303c61796)
            check_type(argname="argument local_name", value=local_name, expected_type=type_hints["local_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "local_name": local_name,
        }

    @builtins.property
    def local_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#local_name DataDatabricksCleanRoomAssets#local_name}.'''
        result = self._values.get("local_name")
        assert result is not None, "Required property 'local_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetsAssetsVolumeLocalDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomAssetsAssetsVolumeLocalDetailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsAssetsVolumeLocalDetailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c50390b6c3cc2507ec680fa4622a493e8019d1d70fffe75eadd0b1e0d79766f5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="localNameInput")
    def local_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "localNameInput"))

    @builtins.property
    @jsii.member(jsii_name="localName")
    def local_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "localName"))

    @local_name.setter
    def local_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cd8d9026beda284631f310071e816e4a924e8146776e71f17cd44c8b0ed1836)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "localName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsVolumeLocalDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsVolumeLocalDetails]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsVolumeLocalDetails]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28aa1414b157193e8e99cb65e0be01691a56768ead0bbe29aca7cbaf774499b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssets.DataDatabricksCleanRoomAssetsConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "clean_room_name": "cleanRoomName",
        "workspace_id": "workspaceId",
    },
)
class DataDatabricksCleanRoomAssetsConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        clean_room_name: builtins.str,
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
        :param clean_room_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#clean_room_name DataDatabricksCleanRoomAssets#clean_room_name}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#workspace_id DataDatabricksCleanRoomAssets#workspace_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e595cb6d96dba79ea05636f0b94cecbf0fa393222784959345f82c3e633ec3ea)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument clean_room_name", value=clean_room_name, expected_type=type_hints["clean_room_name"])
            check_type(argname="argument workspace_id", value=workspace_id, expected_type=type_hints["workspace_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "clean_room_name": clean_room_name,
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
    def clean_room_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#clean_room_name DataDatabricksCleanRoomAssets#clean_room_name}.'''
        result = self._values.get("clean_room_name")
        assert result is not None, "Required property 'clean_room_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def workspace_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_assets#workspace_id DataDatabricksCleanRoomAssets#workspace_id}.'''
        result = self._values.get("workspace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataDatabricksCleanRoomAssets",
    "DataDatabricksCleanRoomAssetsAssets",
    "DataDatabricksCleanRoomAssetsAssetsForeignTable",
    "DataDatabricksCleanRoomAssetsAssetsForeignTableColumns",
    "DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsList",
    "DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsMask",
    "DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsMaskOutputReference",
    "DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsOutputReference",
    "DataDatabricksCleanRoomAssetsAssetsForeignTableLocalDetails",
    "DataDatabricksCleanRoomAssetsAssetsForeignTableLocalDetailsOutputReference",
    "DataDatabricksCleanRoomAssetsAssetsForeignTableOutputReference",
    "DataDatabricksCleanRoomAssetsAssetsList",
    "DataDatabricksCleanRoomAssetsAssetsNotebook",
    "DataDatabricksCleanRoomAssetsAssetsNotebookOutputReference",
    "DataDatabricksCleanRoomAssetsAssetsNotebookReviews",
    "DataDatabricksCleanRoomAssetsAssetsNotebookReviewsList",
    "DataDatabricksCleanRoomAssetsAssetsNotebookReviewsOutputReference",
    "DataDatabricksCleanRoomAssetsAssetsOutputReference",
    "DataDatabricksCleanRoomAssetsAssetsTable",
    "DataDatabricksCleanRoomAssetsAssetsTableColumns",
    "DataDatabricksCleanRoomAssetsAssetsTableColumnsList",
    "DataDatabricksCleanRoomAssetsAssetsTableColumnsMask",
    "DataDatabricksCleanRoomAssetsAssetsTableColumnsMaskOutputReference",
    "DataDatabricksCleanRoomAssetsAssetsTableColumnsOutputReference",
    "DataDatabricksCleanRoomAssetsAssetsTableLocalDetails",
    "DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsOutputReference",
    "DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitions",
    "DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsList",
    "DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsOutputReference",
    "DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValue",
    "DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValueList",
    "DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValueOutputReference",
    "DataDatabricksCleanRoomAssetsAssetsTableOutputReference",
    "DataDatabricksCleanRoomAssetsAssetsView",
    "DataDatabricksCleanRoomAssetsAssetsViewColumns",
    "DataDatabricksCleanRoomAssetsAssetsViewColumnsList",
    "DataDatabricksCleanRoomAssetsAssetsViewColumnsMask",
    "DataDatabricksCleanRoomAssetsAssetsViewColumnsMaskOutputReference",
    "DataDatabricksCleanRoomAssetsAssetsViewColumnsOutputReference",
    "DataDatabricksCleanRoomAssetsAssetsViewLocalDetails",
    "DataDatabricksCleanRoomAssetsAssetsViewLocalDetailsOutputReference",
    "DataDatabricksCleanRoomAssetsAssetsViewOutputReference",
    "DataDatabricksCleanRoomAssetsAssetsVolumeLocalDetails",
    "DataDatabricksCleanRoomAssetsAssetsVolumeLocalDetailsOutputReference",
    "DataDatabricksCleanRoomAssetsConfig",
]

publication.publish()

def _typecheckingstub__d956f34b241a5ed4c8a224d1131b86dfeda714f873a9b29ad425ea3829c670ca(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    clean_room_name: builtins.str,
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

def _typecheckingstub__96f4f56b1665d0a2e69be7287dd0322fecfc6e81cc10256f2e78d5d9d8e67528(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df83a8fa4d79fbbe6238ff85e129fcf7ba7b000130552e5b3ce94b733a6f528a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2845f8814e0b03a440fc7f86acc15a2c70392fea265021a964ee6219e931ee15(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a3691e69c31801ce0e43158fe50942cd062b432d7e42e331ef7ac56a9b85b3e(
    *,
    asset_type: builtins.str,
    name: builtins.str,
    clean_room_name: typing.Optional[builtins.str] = None,
    foreign_table: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetsAssetsForeignTable, typing.Dict[builtins.str, typing.Any]]] = None,
    foreign_table_local_details: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetsAssetsForeignTableLocalDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    notebook: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetsAssetsNotebook, typing.Dict[builtins.str, typing.Any]]] = None,
    table: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetsAssetsTable, typing.Dict[builtins.str, typing.Any]]] = None,
    table_local_details: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetsAssetsTableLocalDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    view: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetsAssetsView, typing.Dict[builtins.str, typing.Any]]] = None,
    view_local_details: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetsAssetsViewLocalDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    volume_local_details: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetsAssetsVolumeLocalDetails, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06ec042b7fc658e6c42efe2c7764c19ba50adf762ef92259001bdf12c3bc0f2f(
    *,
    comment: typing.Optional[builtins.str] = None,
    mask: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsMask, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__e1cc0dc53e29a26ed71407d1f6c3abb20713309db1bb5de993aa1ca8842bd702(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d96ecf7785f7ee8f81678dbfa17571e442a6d050744b8a18f00b61db818187fa(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44f6d5ebe020c12f66b9bf570c4110c4b81f70933300bca4785a7564977e06ee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c36e0bbe44df13a515a7b14944e0fe2ae43a2c2de6d436f6ae3f3f718d1f7a41(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30104ded72b7c2604ba095ea606c5571ec240a168eaae1369271cdac2605251b(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47ba5171675711fc95b55fff4bb6966446509f8aefac99ac620c9e3426b00c85(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetsAssetsForeignTableColumns]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2d71bce57794f76b780d0a9a0c2306a9f1e4630f42ddbacc7da096a8ffc23fb(
    *,
    function_name: typing.Optional[builtins.str] = None,
    using_column_names: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42de93a79e0a909e8ee48883665228d3bbe0183bb53c2a844b69aa20476e1c17(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d63e97312d30f176d896562b32af07962267d29f4147410b2da0670441f7873(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78a976e7bd11bd00b58eaceab681efe042b050c879d724c73b16f3b217196868(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8dc0a0bc8e6309253e7d6fd841e1e3ec9e09987e11004363dbe8d10fb2bddab(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsForeignTableColumnsMask]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acbff6f3b5eda4e738b894f4cbf4603a40d858ea843e48fa257312aa67e17118(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__251d8d9605f30987a06385f7f71355d0a36d4343cc12cff86d6397513c654fc9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fccd62d60d702c8126cd21dfcd66b162e420007432f57b4901c97d7c9c09cc2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bb747b14f01cec917f11887113aa34626cca21c67680501cca97952c6e8f398(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df31aeb8bb484c8376acedd21bc5389e0e7ce2523cf72a5fde71b023e531b02e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a1c27d2b2a32660261cdfb10da1211631682a62ccdc63f8745b152ccccd69ec(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__085306bf240de3ab5c30c88e914ea75c720ca0cecea0c124728d51896a3fa78b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8b071ad8531bbc5f6bb68f2b5053d2c6e022eb330e457dd4dec27f91c432125(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b151d49ebe867934ac2ca165e65a1316b49971c58b43653153e6bc56d7f77a7f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9131cf3be8b7d238c273dfb9034b499c4060288100453484a4228e7149f516db(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1492ae17e7c49081c2524a73ef35b1fd099373c4f71823c1899ff6123cc40d74(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a522909638e7c10e53a2bbdd9d41c78aeeb2707aaa4446934ef777635d635ff2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__528c7744c642653aac775d563c13bccf3e451e0f529ad5569467af8cc350c7a4(
    value: typing.Optional[DataDatabricksCleanRoomAssetsAssetsForeignTableColumns],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c9f69c97e298a3b872f31a6715c6fd47005196653b8ba32295f92698ce3613f(
    *,
    local_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c4f677bbfa325d0f9560d24735e2f63b9e47c7517c92cda6a69718cca80e376(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__657e582fe794a7e3004afcc967eb8503bf00fa129ead2d5feed689158e5c1bc9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e8e9c5b636cf14fcf7c762ad1ad3115c1b48061444140edb951478b411c2361(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsForeignTableLocalDetails]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad0f57880b265b2f6044e9ff52ec039ce4aedb394a9f6980e11f48820d47906a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed55badc2064460d6905ab1692010a309c1be152a4016f7e015bb94238e61d55(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsForeignTable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c590f7e5258b8869631f847af1262b2e9d2e6499dafde7c7f7605fa91c64e79d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f60c29df7415e3e826ec4336beae18f05f2d1fbb0d37330525cd3dbaed6030d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99648372affee022b34c9e5d149f28bfaea0680c7ff24f4e1836a16b0d567899(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fad6891f4172c9f6c545bad54cbd902935718415908d0b3c21082f0acab4db14(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97da1c841be15ef9229639507177a165c714d71c8526cebbcd2529a51208d081(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bfdf5466ceaca7a7a01d57c5c82466937ca615b28f676f62ac5675ee559c845(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetsAssets]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e83b4da0d5082fdb0292c5cbf919939281feec026395f5cc9047b9553ff8c56(
    *,
    notebook_content: builtins.str,
    runner_collaborator_aliases: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4183429132d579442aaa0ebd845ef156faa45908837d23795d1116575c35758(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3379d8925cede4615c2e2dc18f464253007b64933f9ef5b525bb1a26bab6b0e4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a392f96645d577f3d3e3e5643c27390a7ce2646f0cfcb16eab3f2eed1bae8677(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f19caa06f7e0075c9ec40a9c2d00a4bc496f548505ea0d0ce47341616780e01(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsNotebook]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e84692452a029b2d4fe1b0cc7306ca432c340b3f681e7d01a3a782e902938c83(
    *,
    comment: typing.Optional[builtins.str] = None,
    created_at_millis: typing.Optional[jsii.Number] = None,
    reviewer_collaborator_alias: typing.Optional[builtins.str] = None,
    review_state: typing.Optional[builtins.str] = None,
    review_sub_reason: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b22d488e3a61623666a679feb10bddc254d7359d8941aa768364a9ed655a52f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__585c83245e06226458f9984ec85d8a3a44136e6cf92b442fedfd19580f64735d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0969196e4f07b0c6a88addaf346a64e98bdd4f6d391b6ab0e77a71981c879447(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae69db2d92b435598a056da0e2354cc9795b3848a799743082779c990896dc41(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75326ffa455b620c150ed5f474939800958c9d2ab068137e08c7584b3ac0d413(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__854c3cb7b342e5c0572a886a91b5f72832d2c21b41e0ca7107d8a3355f824462(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetsAssetsNotebookReviews]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f0687d2985ed1d003633b2cdf484c064854915124ccb0fa6571bc758080706b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45182bccacdbb8acc6fb4462553799744bb8a6f1d2ff2b21f9b6e1e5b17e2ea3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c5b53c06432718019ecea97f4173144b7fd511bf8e94de7548c890c00f0782b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f02f08b2860c031e1e4f4f7c7f7f9f8afd05e83a6a6d0006b67f3ecc4cfa39b5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcd17a0458255c2b487a1f74731ffb6fee99c18bdeefaf6d110e42a82b11619a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ddc1f327edecaef5f30af95424a513779adea59dd1e68a8bb5fa8a8fa48fa1c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bde1befaa7cbc6cc61a5ff87e9aef28ed9266db754b0b4a37800d1a2319fe358(
    value: typing.Optional[DataDatabricksCleanRoomAssetsAssetsNotebookReviews],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26f9f4d66496cbefb86c0f5ccfe6ef96f93c4e8c3d8cd91e352ab3e707f7cb18(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9cfdfb186c3896a178816e0554a0c5ad770673a44af3d499c1ace74e05cdd0c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f19658dbbf8538f1a1ffc06e6c7cdedb84f2144424b86254c3e197c7f7a0d31(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a62a26a4c5a4b54007060a62fc201afe0f913130c3efde46b58fb27e463fe5c6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c03dc1ada6e6f1e3ea010e4995a420391320d4c9501fad71b60f056e10f2abd5(
    value: typing.Optional[DataDatabricksCleanRoomAssetsAssets],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5762e3825c63bbd88b96705dd6434c0a978edc09ff49d8a7ec81072812864cd9(
    *,
    comment: typing.Optional[builtins.str] = None,
    mask: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetsAssetsTableColumnsMask, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__b706ebe6efd8720c398b58d4ad70bc8ed864555227e647b7ee131465d661ee67(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e065cdcf4682ebfecb947adc089c6bc203c8aac0226c03eb1113b492bd7543c6(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ce00250c679bcb819b945175a6874901bada18441100d1b4b3e531bcd295728(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1af7dea25cde2c637430bc763f91a92d2d021c75c252cd3415d1c747aefcd3e9(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77f2a4349f9212d357dad8afc26b2f7a939dbc81d6d327fc22c2d4da2947b7e2(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9057b2168c43f572c72a80065bd468ecf73f7503db319acb378e7ea079fa9264(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetsAssetsTableColumns]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a635c675bd239fb1acafd9222c426749db276524f5c2abc1b9dc74d8f13c1e6(
    *,
    function_name: typing.Optional[builtins.str] = None,
    using_column_names: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__254542fa8f7d50d3e0ba205a0824ee0a98e9a4364b9285f539363b494bfd07df(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60a864765245a11b707c83b2802748f5eb4c4a6c599eef636ed2029d96c474d6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__294410eb2041339778a796461210d4fe26ce0adcaf0484816c12ed88b2e1f9f6(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6aba457a2016a74277dfa146ff749310ffa1a8003743c916caf1229d11bd35f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsTableColumnsMask]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b0062eb391d622aeb52e392db425f7be7aca757861cb32f781c6fa1453276c9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e6e65834a3d7841fd13295ca7fa4f3a41e35af3ac48d482e2122b8393d49601(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efb36c81d614d62c488c41d9ec2df857c10f7082060a4bb562e7a31b59f976aa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6dd8d4ad77176357d3ea026d00e5dc4275f42e91dd2aff4c985a22588c0ea29e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54a383906cb63c53cb167ecef3998e27edd8eaa383d8a29283d5c51874d93c0f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcee01cccee34a5eb7c535b10aba8ba756163a47820d975bd1435f3c7a7d1491(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e49a6376a722d6fa29a34040034149a4b6ea18f75cc159d6c09962c55bee9649(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e56fec945f0794378012300f43e84478b143c88a509a551ff092f6be0fd5cff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2c39d1eb5a966a3086e0650cdd9ff8b8f803cbb7acc95a33a0947047b9c9103(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd364f365009f51a34437a52596439faf587aabd2b67a7c1f9b3f0b757744cbf(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d66677c21ba9fd5de34699f71ba0b1d67b36c7bf9575b690fa79aad8c070391(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__648fb228b6777599dfaf307beb7d82aa902d046a1f2d27722874a005b7c1aea1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a10112d860300a3997485b3aecfaffbbfa0a1c61e90567d91133e4087a076e13(
    value: typing.Optional[DataDatabricksCleanRoomAssetsAssetsTableColumns],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1043145ad9b91a44dbc53e073eac6bc4a4bd9e37ae2beaacb7ad1f2edf6b1473(
    *,
    local_name: builtins.str,
    partitions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitions, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29e638f8c80abfc38d5e4e7dbcb083aede902f65556788c4614d16c57c027490(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b156daefda2c43df44cefc870d9e4e6604fd89807c38275a82a08360d3e1ebc(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitions, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__409381f728e2de50c9a6b99c48a517f3e1a2c37ba5647be70be43db553ac506a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2efc9157b03cb9abb063dd7cd5522c7b1ebaeb0bf26c9669f516d1852f34b5e7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsTableLocalDetails]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__448154e8a4c1c228d6eb4e1fe269dfbf5692c878712788ecc38612477479d041(
    *,
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValue, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a6f96ca47d6508a6ecc23778212b72fa44a183c6812f14f78501145825b63ba(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d0a2e772c54855a5561028cb6cf91e6c239e5f7df7ead827b30a8039849e374(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4be3161cc4f3e7006c81b1bb3d67b65ab01cee080d58cf9f7cfc1d57db8484ea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38df0a06f28032dc1e8ab1c0d920366c5aa7fe553d4a808766c4f85d92ecd6f7(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__527a9c51fbb58b7d2e68b9a9bec24414aa9c69457b545af30ea80504521da088(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54231806553ce569a7cc254eb9923865e5dabb98959cb13beeaea19368e04ce5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitions]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4cdfb21285da34e37df3689af4f680311feee105c29255691b5f19cef5da1069(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26bbd2b8ee60e525401cab5ebc3253c9bd839a6481c6ba691e816515d85096e5(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValue, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d7e2dc13b38fa764b30203b075bbd1328f1f5cb6a8d09eba6f80baa4cee8b1c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitions]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac5f1fed7cf9154fc273889238f03906c998b93a1abe90e78db3ba4327b38555(
    *,
    name: typing.Optional[builtins.str] = None,
    op: typing.Optional[builtins.str] = None,
    recipient_property_key: typing.Optional[builtins.str] = None,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bedd99da4001c2670fc0322f1764b82c239a0edeb9f83115604f45ccb478563(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__301060877858ce1b332339e2c88cb01360740db14d326c23b1da037c141f59b8(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8be7597d1f21109a53d21bff537f31f277ff75e91d4568e6411c05242554fdcb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f18fa443a949e36af794561ea9eb4f3ea81cee36e4cfae609e44336774abb2a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acfe3f06aa7a27a3a5764095a0cc100555a6bc65149ac81f39ca0eddeb76e0d3(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb618703c4d17cc7d41cab59c1b7914bca065f781e14a8783c7f4f82f9ad6e90(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValue]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__472cde61241ac21ed1613bb10205edd343c1d0524d611a2994ba76ed1504318d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08faaedd8068c2f2ddb23555c9c23d41a2fb6aa7962b5bc0a57fa194b89dc0a3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc4f2ccded5322393a6934c85474a04400513662c1aff2b2c7198f2884d3008c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4889bc1e4ef46cf566e9653765113e4771e7bd99a3092fff27c98f88d7dd197c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2717e927467a59f4b200af17e06da0f9141019b63d7a418dbd6daf097278c024(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__573ed6db82d6ef6a926b3ffbe5d170f1ec843f6559ab03693a088c096c920dca(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsTableLocalDetailsPartitionsValue]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00f728243d233e6de9cc29b18f1491e128137818ead44397c8297515a452c373(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23d3d28dc4550506b952acd632cbe5e9821587f86b9922b6fd2d24ab3e736038(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsTable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__479d08fa75464b7108fa3355b363281d9ab9be99b1ea45c1e467ae4915bfd61c(
    *,
    comment: typing.Optional[builtins.str] = None,
    mask: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetsAssetsViewColumnsMask, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__16cb9a29b40a6df9902ec80be9f8f3d987ec0e1e54ce611afe413ba277780f2e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a253de48ec83f9c37fccb31afd506fa5cc8e3a7df207856408b115021926c0b7(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab6c4a166ceb1db0a5a23929293a713b8e3724db51a9a7aa5bc2e6a992efc751(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9625af70ae5f33873352d9911614e45d83e1bd467891e3f702000271adafe37(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__453343442d6df371ce897ffcb285c22f91a71d745255692643572e0f3de0322d(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f92265808ae02ae9af715156be3df506874a0e77fc53d1b338c6a0ac42764774(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetsAssetsViewColumns]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bf20e9443495d897c785b9d962fe7d4403d83d2576b99494b719c6819498e08(
    *,
    function_name: typing.Optional[builtins.str] = None,
    using_column_names: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f232843ece1a87d49aeac5ef966a60b0c59313b68f16d5e1d076cdfa59496a80(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99229a48f028114d55d73112e0d20c1e840d68313b2ef7036f36f7ae685a71de(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42ab3ceb03a0959dc9925d7061052e196190ec759cf5c5065ea04cdcfe07a216(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d65899e271a404d3420cd5ca57a961caebcda5bbe41c99bf199193ce86f32bf6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsViewColumnsMask]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e41aa1280d1014d0b77b4f5af85a3740befd8f8e4a58f9df0e17785a4405802(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c92cf5de89f0af4f5f6679b8d7f585b284202fc214e4681ed98b56ffab430d29(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4cf1ef5b8e6da12956b8e00f5d8e1e491aadc8ddafd06afe8e8b6928471aa82(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b85b88a5be753acd5f3843e5d66c54a93421aa1bd425332a067b3e446652660(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dac52c5c401bf6d61b7899284fcde9a73abe236ed6d62473b94397583fc97144(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af06deb5ceeea68e880e4ec33ccdbd1b5489cce93d51fa4ef3f3c0019af8a222(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76fc45c2af1c81e4ed990832ea599a164ef827ff8f540b036cb8ae8da40e094c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05380d43d77bc6e24a4f45dbfde9f1b8ef4bcbc96388998a66676af8f717391d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6ba099d7a9f0310a8238ab934ec340f3946296e259eee6e7b7938f818476e67(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7fcfb008b1a40b06b8d130a81471d157502e1ddf1f59ca3e7812def406521b7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a2e112db29df9653e4f342155e665ba7efceb2c3f94da0f3e052343d76e6d32(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc0d964452eeb98d6981f1fcccc5e95e269f9bef2246831b2dc251a27f9f5042(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b153dcac07c05ada01a809725c574f97ca7bce9cfccee8c5c319cba884179109(
    value: typing.Optional[DataDatabricksCleanRoomAssetsAssetsViewColumns],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05af3b1b4845e0eee2e0087dabc32480d93d18908bea7c32dd9406e847b98fea(
    *,
    local_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b24812626cf3daf42ebef2133afd571d94a308ebd396521c38105639315775c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd56cd7fc53aaa2374b3a14ca26ff116b087b62400ecddf2f43b312a7119c170(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d79c8ff684a27f0cd2a41ddf4d301c97092f9e1b6dd7e24db8978b7802f437a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsViewLocalDetails]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0847dc9b1b6f8eddd7213b0fda566fbb7258a698d929277e89b7f3764c5c1b22(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ca421378a8f04e3b7ad8c4e723e2aca0ef5792b264b4381c1e59e844a314bfd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsView]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aef66e5cb569321c965874a63535903ee1e7af27ad6bf2d17b88b96303c61796(
    *,
    local_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c50390b6c3cc2507ec680fa4622a493e8019d1d70fffe75eadd0b1e0d79766f5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cd8d9026beda284631f310071e816e4a924e8146776e71f17cd44c8b0ed1836(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28aa1414b157193e8e99cb65e0be01691a56768ead0bbe29aca7cbaf774499b6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetsAssetsVolumeLocalDetails]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e595cb6d96dba79ea05636f0b94cecbf0fa393222784959345f82c3e633ec3ea(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    clean_room_name: builtins.str,
    workspace_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
