r'''
# `data_databricks_clean_room_asset_revisions_clean_room_asset`

Refer to the Terraform Registry for docs: [`data_databricks_clean_room_asset_revisions_clean_room_asset`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset).
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


class DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset databricks_clean_room_asset_revisions_clean_room_asset}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        asset_type: builtins.str,
        name: builtins.str,
        clean_room_name: typing.Optional[builtins.str] = None,
        foreign_table: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTable", typing.Dict[builtins.str, typing.Any]]] = None,
        foreign_table_local_details: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableLocalDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        notebook: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebook", typing.Dict[builtins.str, typing.Any]]] = None,
        table: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTable", typing.Dict[builtins.str, typing.Any]]] = None,
        table_local_details: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        view: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetView", typing.Dict[builtins.str, typing.Any]]] = None,
        view_local_details: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewLocalDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        volume_local_details: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetVolumeLocalDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        workspace_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset databricks_clean_room_asset_revisions_clean_room_asset} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param asset_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#asset_type DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#asset_type}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#name}.
        :param clean_room_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#clean_room_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#clean_room_name}.
        :param foreign_table: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#foreign_table DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#foreign_table}.
        :param foreign_table_local_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#foreign_table_local_details DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#foreign_table_local_details}.
        :param notebook: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#notebook DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#notebook}.
        :param table: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#table DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#table}.
        :param table_local_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#table_local_details DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#table_local_details}.
        :param view: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#view DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#view}.
        :param view_local_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#view_local_details DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#view_local_details}.
        :param volume_local_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#volume_local_details DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#volume_local_details}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#workspace_id DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#workspace_id}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33383ce8ce2357c43601b2a09e9bf402db35d195e3806183f6529fa71cfb960c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetConfig(
            asset_type=asset_type,
            name=name,
            clean_room_name=clean_room_name,
            foreign_table=foreign_table,
            foreign_table_local_details=foreign_table_local_details,
            notebook=notebook,
            table=table,
            table_local_details=table_local_details,
            view=view,
            view_local_details=view_local_details,
            volume_local_details=volume_local_details,
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
        '''Generates CDKTF code for importing a DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset to import.
        :param import_from_id: The id of the existing DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__878dac6b3b4edd19ce9a0ac502a3cf072c6e96361d468308d7533ae556e65480)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putForeignTable")
    def put_foreign_table(self) -> None:
        value = DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTable()

        return typing.cast(None, jsii.invoke(self, "putForeignTable", [value]))

    @jsii.member(jsii_name="putForeignTableLocalDetails")
    def put_foreign_table_local_details(self, *, local_name: builtins.str) -> None:
        '''
        :param local_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#local_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#local_name}.
        '''
        value = DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableLocalDetails(
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
        :param notebook_content: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#notebook_content DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#notebook_content}.
        :param runner_collaborator_aliases: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#runner_collaborator_aliases DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#runner_collaborator_aliases}.
        '''
        value = DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebook(
            notebook_content=notebook_content,
            runner_collaborator_aliases=runner_collaborator_aliases,
        )

        return typing.cast(None, jsii.invoke(self, "putNotebook", [value]))

    @jsii.member(jsii_name="putTable")
    def put_table(self) -> None:
        value = DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTable()

        return typing.cast(None, jsii.invoke(self, "putTable", [value]))

    @jsii.member(jsii_name="putTableLocalDetails")
    def put_table_local_details(
        self,
        *,
        local_name: builtins.str,
        partitions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitions", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param local_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#local_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#local_name}.
        :param partitions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#partitions DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#partitions}.
        '''
        value = DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetails(
            local_name=local_name, partitions=partitions
        )

        return typing.cast(None, jsii.invoke(self, "putTableLocalDetails", [value]))

    @jsii.member(jsii_name="putView")
    def put_view(self) -> None:
        value = DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetView()

        return typing.cast(None, jsii.invoke(self, "putView", [value]))

    @jsii.member(jsii_name="putViewLocalDetails")
    def put_view_local_details(self, *, local_name: builtins.str) -> None:
        '''
        :param local_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#local_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#local_name}.
        '''
        value = DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewLocalDetails(
            local_name=local_name
        )

        return typing.cast(None, jsii.invoke(self, "putViewLocalDetails", [value]))

    @jsii.member(jsii_name="putVolumeLocalDetails")
    def put_volume_local_details(self, *, local_name: builtins.str) -> None:
        '''
        :param local_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#local_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#local_name}.
        '''
        value = DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetVolumeLocalDetails(
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
    @jsii.member(jsii_name="addedAt")
    def added_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "addedAt"))

    @builtins.property
    @jsii.member(jsii_name="foreignTable")
    def foreign_table(
        self,
    ) -> "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableOutputReference":
        return typing.cast("DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableOutputReference", jsii.get(self, "foreignTable"))

    @builtins.property
    @jsii.member(jsii_name="foreignTableLocalDetails")
    def foreign_table_local_details(
        self,
    ) -> "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableLocalDetailsOutputReference":
        return typing.cast("DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableLocalDetailsOutputReference", jsii.get(self, "foreignTableLocalDetails"))

    @builtins.property
    @jsii.member(jsii_name="notebook")
    def notebook(
        self,
    ) -> "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebookOutputReference":
        return typing.cast("DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebookOutputReference", jsii.get(self, "notebook"))

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
    def table(
        self,
    ) -> "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableOutputReference":
        return typing.cast("DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableOutputReference", jsii.get(self, "table"))

    @builtins.property
    @jsii.member(jsii_name="tableLocalDetails")
    def table_local_details(
        self,
    ) -> "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsOutputReference":
        return typing.cast("DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsOutputReference", jsii.get(self, "tableLocalDetails"))

    @builtins.property
    @jsii.member(jsii_name="view")
    def view(
        self,
    ) -> "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewOutputReference":
        return typing.cast("DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewOutputReference", jsii.get(self, "view"))

    @builtins.property
    @jsii.member(jsii_name="viewLocalDetails")
    def view_local_details(
        self,
    ) -> "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewLocalDetailsOutputReference":
        return typing.cast("DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewLocalDetailsOutputReference", jsii.get(self, "viewLocalDetails"))

    @builtins.property
    @jsii.member(jsii_name="volumeLocalDetails")
    def volume_local_details(
        self,
    ) -> "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetVolumeLocalDetailsOutputReference":
        return typing.cast("DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetVolumeLocalDetailsOutputReference", jsii.get(self, "volumeLocalDetails"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTable"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTable"]], jsii.get(self, "foreignTableInput"))

    @builtins.property
    @jsii.member(jsii_name="foreignTableLocalDetailsInput")
    def foreign_table_local_details_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableLocalDetails"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableLocalDetails"]], jsii.get(self, "foreignTableLocalDetailsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="notebookInput")
    def notebook_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebook"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebook"]], jsii.get(self, "notebookInput"))

    @builtins.property
    @jsii.member(jsii_name="tableInput")
    def table_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTable"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTable"]], jsii.get(self, "tableInput"))

    @builtins.property
    @jsii.member(jsii_name="tableLocalDetailsInput")
    def table_local_details_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetails"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetails"]], jsii.get(self, "tableLocalDetailsInput"))

    @builtins.property
    @jsii.member(jsii_name="viewInput")
    def view_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetView"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetView"]], jsii.get(self, "viewInput"))

    @builtins.property
    @jsii.member(jsii_name="viewLocalDetailsInput")
    def view_local_details_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewLocalDetails"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewLocalDetails"]], jsii.get(self, "viewLocalDetailsInput"))

    @builtins.property
    @jsii.member(jsii_name="volumeLocalDetailsInput")
    def volume_local_details_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetVolumeLocalDetails"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetVolumeLocalDetails"]], jsii.get(self, "volumeLocalDetailsInput"))

    @builtins.property
    @jsii.member(jsii_name="workspaceIdInput")
    def workspace_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workspaceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="assetType")
    def asset_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "assetType"))

    @asset_type.setter
    def asset_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a6904e5d3e84379756cfe3db892427242affef4a018df6f113357d27e9190b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "assetType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cleanRoomName")
    def clean_room_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cleanRoomName"))

    @clean_room_name.setter
    def clean_room_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cc48ea309090f72f5ecb63901f9da11c407eb800df9c54e4d486e74de71c532)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cleanRoomName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fed64d7711f866993d4203c0ab41a29b4b1de6e953ea66ee7e7cc41460955d5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workspaceId")
    def workspace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceId"))

    @workspace_id.setter
    def workspace_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a2d088f1cc7b682a745dd22db1a399beabcb5bab0a6d249f45f084debcc3c51)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workspaceId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
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
        "workspace_id": "workspaceId",
    },
)
class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetConfig(
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
        asset_type: builtins.str,
        name: builtins.str,
        clean_room_name: typing.Optional[builtins.str] = None,
        foreign_table: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTable", typing.Dict[builtins.str, typing.Any]]] = None,
        foreign_table_local_details: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableLocalDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        notebook: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebook", typing.Dict[builtins.str, typing.Any]]] = None,
        table: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTable", typing.Dict[builtins.str, typing.Any]]] = None,
        table_local_details: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        view: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetView", typing.Dict[builtins.str, typing.Any]]] = None,
        view_local_details: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewLocalDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        volume_local_details: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetVolumeLocalDetails", typing.Dict[builtins.str, typing.Any]]] = None,
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
        :param asset_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#asset_type DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#asset_type}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#name}.
        :param clean_room_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#clean_room_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#clean_room_name}.
        :param foreign_table: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#foreign_table DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#foreign_table}.
        :param foreign_table_local_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#foreign_table_local_details DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#foreign_table_local_details}.
        :param notebook: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#notebook DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#notebook}.
        :param table: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#table DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#table}.
        :param table_local_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#table_local_details DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#table_local_details}.
        :param view: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#view DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#view}.
        :param view_local_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#view_local_details DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#view_local_details}.
        :param volume_local_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#volume_local_details DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#volume_local_details}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#workspace_id DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#workspace_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(foreign_table, dict):
            foreign_table = DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTable(**foreign_table)
        if isinstance(foreign_table_local_details, dict):
            foreign_table_local_details = DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableLocalDetails(**foreign_table_local_details)
        if isinstance(notebook, dict):
            notebook = DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebook(**notebook)
        if isinstance(table, dict):
            table = DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTable(**table)
        if isinstance(table_local_details, dict):
            table_local_details = DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetails(**table_local_details)
        if isinstance(view, dict):
            view = DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetView(**view)
        if isinstance(view_local_details, dict):
            view_local_details = DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewLocalDetails(**view_local_details)
        if isinstance(volume_local_details, dict):
            volume_local_details = DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetVolumeLocalDetails(**volume_local_details)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__828690ffdfd94607ab1e81b9d6fa5376e2ba57eabe1bb8db584a077bca8f46e8)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
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
            check_type(argname="argument workspace_id", value=workspace_id, expected_type=type_hints["workspace_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "asset_type": asset_type,
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
    def asset_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#asset_type DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#asset_type}.'''
        result = self._values.get("asset_type")
        assert result is not None, "Required property 'asset_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def clean_room_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#clean_room_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#clean_room_name}.'''
        result = self._values.get("clean_room_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def foreign_table(
        self,
    ) -> typing.Optional["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTable"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#foreign_table DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#foreign_table}.'''
        result = self._values.get("foreign_table")
        return typing.cast(typing.Optional["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTable"], result)

    @builtins.property
    def foreign_table_local_details(
        self,
    ) -> typing.Optional["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableLocalDetails"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#foreign_table_local_details DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#foreign_table_local_details}.'''
        result = self._values.get("foreign_table_local_details")
        return typing.cast(typing.Optional["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableLocalDetails"], result)

    @builtins.property
    def notebook(
        self,
    ) -> typing.Optional["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebook"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#notebook DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#notebook}.'''
        result = self._values.get("notebook")
        return typing.cast(typing.Optional["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebook"], result)

    @builtins.property
    def table(
        self,
    ) -> typing.Optional["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTable"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#table DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#table}.'''
        result = self._values.get("table")
        return typing.cast(typing.Optional["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTable"], result)

    @builtins.property
    def table_local_details(
        self,
    ) -> typing.Optional["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetails"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#table_local_details DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#table_local_details}.'''
        result = self._values.get("table_local_details")
        return typing.cast(typing.Optional["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetails"], result)

    @builtins.property
    def view(
        self,
    ) -> typing.Optional["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetView"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#view DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#view}.'''
        result = self._values.get("view")
        return typing.cast(typing.Optional["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetView"], result)

    @builtins.property
    def view_local_details(
        self,
    ) -> typing.Optional["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewLocalDetails"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#view_local_details DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#view_local_details}.'''
        result = self._values.get("view_local_details")
        return typing.cast(typing.Optional["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewLocalDetails"], result)

    @builtins.property
    def volume_local_details(
        self,
    ) -> typing.Optional["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetVolumeLocalDetails"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#volume_local_details DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#volume_local_details}.'''
        result = self._values.get("volume_local_details")
        return typing.cast(typing.Optional["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetVolumeLocalDetails"], result)

    @builtins.property
    def workspace_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#workspace_id DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#workspace_id}.'''
        result = self._values.get("workspace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTable",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTable:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTable(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumns",
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
class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumns:
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        mask: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsMask", typing.Dict[builtins.str, typing.Any]]] = None,
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
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#comment DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#comment}.
        :param mask: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#mask DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#mask}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#name}.
        :param nullable: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#nullable DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#nullable}.
        :param partition_index: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#partition_index DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#partition_index}.
        :param position: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#position DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#position}.
        :param type_interval_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_interval_type DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_interval_type}.
        :param type_json: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_json DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_json}.
        :param type_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_name}.
        :param type_precision: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_precision DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_precision}.
        :param type_scale: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_scale DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_scale}.
        :param type_text: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_text DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_text}.
        '''
        if isinstance(mask, dict):
            mask = DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsMask(**mask)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__561a9d842bbba3538d6a892fd70ef63ffe745c977602f4d8f97339630913ce31)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#comment DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mask(
        self,
    ) -> typing.Optional["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsMask"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#mask DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#mask}.'''
        result = self._values.get("mask")
        return typing.cast(typing.Optional["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsMask"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nullable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#nullable DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#nullable}.'''
        result = self._values.get("nullable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def partition_index(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#partition_index DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#partition_index}.'''
        result = self._values.get("partition_index")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def position(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#position DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#position}.'''
        result = self._values.get("position")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_interval_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_interval_type DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_interval_type}.'''
        result = self._values.get("type_interval_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_json DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_json}.'''
        result = self._values.get("type_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_name}.'''
        result = self._values.get("type_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_precision(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_precision DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_precision}.'''
        result = self._values.get("type_precision")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_scale(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_scale DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_scale}.'''
        result = self._values.get("type_scale")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_text(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_text DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_text}.'''
        result = self._values.get("type_text")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumns(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0ec615e2295c5d42748d1288731b6ccce5b4fbb31d50c615de4d8e7270552395)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9eb3326faec736e362ed49cf9634b82982c2556e68ec73672b72d5f275f5df9)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcede0e24a8e0aa10af5fcebdd64e6b7f4ad61c6136444f98f922f782c7d26b7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__787d225b6ff4cb80a530fbc9c7946702f02dce8cb0f4ece6b2ad918912b57736)
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
            type_hints = typing.get_type_hints(_typecheckingstub__99c6d9cb08e1590025277bdc9356e7058afc58d50a282251d95ed22b2901c800)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumns]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumns]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumns]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f106f4682fdfc2d2ccc9d2d1cf6b6e5a8e75cb643609807c1bd266946ae4e99b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsMask",
    jsii_struct_bases=[],
    name_mapping={
        "function_name": "functionName",
        "using_column_names": "usingColumnNames",
    },
)
class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsMask:
    def __init__(
        self,
        *,
        function_name: typing.Optional[builtins.str] = None,
        using_column_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#function_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#function_name}.
        :param using_column_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#using_column_names DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#using_column_names}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da94b9f25719ad4f6d46dacdab1b8521f8218392ccca8124e666230b5dc288d4)
            check_type(argname="argument function_name", value=function_name, expected_type=type_hints["function_name"])
            check_type(argname="argument using_column_names", value=using_column_names, expected_type=type_hints["using_column_names"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if function_name is not None:
            self._values["function_name"] = function_name
        if using_column_names is not None:
            self._values["using_column_names"] = using_column_names

    @builtins.property
    def function_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#function_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#function_name}.'''
        result = self._values.get("function_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def using_column_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#using_column_names DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#using_column_names}.'''
        result = self._values.get("using_column_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsMask(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsMaskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsMaskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b7f6054ae182f0b0d71fc67a6520dfd38f3339f40d91de3f7fcbc9ed688887c2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__715377dc16aee0054fe6b425f60c28b570267d04093aa91588f7593f38b99026)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "functionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usingColumnNames")
    def using_column_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "usingColumnNames"))

    @using_column_names.setter
    def using_column_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ce2aa94760820996646ddfd4c0bc7849abd984332d9f53dad2157efd61b97eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usingColumnNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsMask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsMask]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsMask]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34615945aaa632f5d8e82c57bb8f80cea3855ba4e2251e820c2cb7387b2ab7ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d281617648abe067c6c4a0de74d65795e4127ba07309759a2573bbbe8895997a)
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
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#function_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#function_name}.
        :param using_column_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#using_column_names DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#using_column_names}.
        '''
        value = DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsMask(
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
    ) -> DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsMaskOutputReference:
        return typing.cast(DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsMaskOutputReference, jsii.get(self, "mask"))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="maskInput")
    def mask_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsMask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsMask]], jsii.get(self, "maskInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__52833c97f37fb4a356a9ec0d35f4542c49f12f8a26cf2772ac07e1a4657d0764)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ab3d9577df51338d5f7e2213e4c6841206dc4813e8fab6dd07eea3951295722)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5a65a718ea057f5e6e64d47c2fa8d036bfebaccd7909c7adad9fc1bfafb63b1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nullable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="partitionIndex")
    def partition_index(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "partitionIndex"))

    @partition_index.setter
    def partition_index(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be31d9fd78d7a866834354874c0c2e50be690dffa4e9e7ff5db851b5c7ab2dd6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "partitionIndex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="position")
    def position(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "position"))

    @position.setter
    def position(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bef6f103781d9f37e0d8e625ae26908ea5e91206aedb4053fd07edead7c24a4b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "position", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeIntervalType")
    def type_interval_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeIntervalType"))

    @type_interval_type.setter
    def type_interval_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb3106f50d6890cc6261ec47bf19bb7c84db18e17f18cfbfcaf94470d49a3200)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeIntervalType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeJson")
    def type_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeJson"))

    @type_json.setter
    def type_json(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1cc73d6ed99cab08f4cba29f16a89622ecc47e50471138aadc89e1f6bc6e1864)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeJson", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeName")
    def type_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeName"))

    @type_name.setter
    def type_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e2035f50c7c34ee98439aa0c5842017a78e0333d114d929195aae1a3f10cf00)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typePrecision")
    def type_precision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "typePrecision"))

    @type_precision.setter
    def type_precision(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c1bd860362baefb4bd600b7ffa542b240094719830dae7a1c6b92baa55aec66)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typePrecision", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeScale")
    def type_scale(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "typeScale"))

    @type_scale.setter
    def type_scale(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9353b6866134250d0769bb914cca2de6fd07d7c7bd02ef520d34a37b19097db2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeScale", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeText")
    def type_text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeText"))

    @type_text.setter
    def type_text(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3eeb0adeac0b00a26b37e2badba0a8c9e28373b74c2146a093ad7ff2de631975)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeText", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumns]:
        return typing.cast(typing.Optional[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumns], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumns],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e00bd34e04b168936ace9ccf1e38c3933067c775dd01219d46b491065993c582)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableLocalDetails",
    jsii_struct_bases=[],
    name_mapping={"local_name": "localName"},
)
class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableLocalDetails:
    def __init__(self, *, local_name: builtins.str) -> None:
        '''
        :param local_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#local_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#local_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__461162c3ff843fa14cad4ad8b1495d581bfa439fecbfc779894450e25354d372)
            check_type(argname="argument local_name", value=local_name, expected_type=type_hints["local_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "local_name": local_name,
        }

    @builtins.property
    def local_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#local_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#local_name}.'''
        result = self._values.get("local_name")
        assert result is not None, "Required property 'local_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableLocalDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableLocalDetailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableLocalDetailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6f1292f9fa54deb6f0d113446ce8c17cea5803fb248f2b236a649ac404966e14)
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
            type_hints = typing.get_type_hints(_typecheckingstub__939a698c93af7e34665d772f9ebf98e7cd2dc64dde8cf4f98ed28d93f541ebcc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "localName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableLocalDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableLocalDetails]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableLocalDetails]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72032196d598cb031b16ffed390d2692f3a8016471377ecef972ea7a3598d22d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b42580951312753e221efeba0bb207a6e5e1028086a0898da97418c4dbf5910d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="columns")
    def columns(
        self,
    ) -> DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsList:
        return typing.cast(DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsList, jsii.get(self, "columns"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTable]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8bb95279b76004c4b05adc0fe4383caa47090f7e2f2a37637b83b36751e8a77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebook",
    jsii_struct_bases=[],
    name_mapping={
        "notebook_content": "notebookContent",
        "runner_collaborator_aliases": "runnerCollaboratorAliases",
    },
)
class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebook:
    def __init__(
        self,
        *,
        notebook_content: builtins.str,
        runner_collaborator_aliases: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param notebook_content: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#notebook_content DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#notebook_content}.
        :param runner_collaborator_aliases: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#runner_collaborator_aliases DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#runner_collaborator_aliases}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f7295fa74ac99f0a2948cc44a5b0fe3a5ea258d3c84a2f03cf1f581fd9c440b)
            check_type(argname="argument notebook_content", value=notebook_content, expected_type=type_hints["notebook_content"])
            check_type(argname="argument runner_collaborator_aliases", value=runner_collaborator_aliases, expected_type=type_hints["runner_collaborator_aliases"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "notebook_content": notebook_content,
        }
        if runner_collaborator_aliases is not None:
            self._values["runner_collaborator_aliases"] = runner_collaborator_aliases

    @builtins.property
    def notebook_content(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#notebook_content DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#notebook_content}.'''
        result = self._values.get("notebook_content")
        assert result is not None, "Required property 'notebook_content' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def runner_collaborator_aliases(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#runner_collaborator_aliases DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#runner_collaborator_aliases}.'''
        result = self._values.get("runner_collaborator_aliases")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebook(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebookOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebookOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c8ab45a6618c7bc0a406500370f5dc0a7c5eb4c9940f3170c9275992db17327d)
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
    def reviews(
        self,
    ) -> "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebookReviewsList":
        return typing.cast("DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebookReviewsList", jsii.get(self, "reviews"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__0f2fc7b37b35b1b4a271da0915a202bc01ff26e172ab4785d1879f494366cf1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notebookContent", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runnerCollaboratorAliases")
    def runner_collaborator_aliases(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "runnerCollaboratorAliases"))

    @runner_collaborator_aliases.setter
    def runner_collaborator_aliases(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__acbe3ff7db9902c612620ddbf127e765b505c2f0fd2c131ba47789ed66c284e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runnerCollaboratorAliases", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebook]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebook]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebook]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69397be7300e067c4cc8e19bda1a374f1b8f6a84dd4c14f9f5762c0e306c9d6c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebookReviews",
    jsii_struct_bases=[],
    name_mapping={
        "comment": "comment",
        "created_at_millis": "createdAtMillis",
        "reviewer_collaborator_alias": "reviewerCollaboratorAlias",
        "review_state": "reviewState",
        "review_sub_reason": "reviewSubReason",
    },
)
class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebookReviews:
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
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#comment DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#comment}.
        :param created_at_millis: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#created_at_millis DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#created_at_millis}.
        :param reviewer_collaborator_alias: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#reviewer_collaborator_alias DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#reviewer_collaborator_alias}.
        :param review_state: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#review_state DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#review_state}.
        :param review_sub_reason: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#review_sub_reason DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#review_sub_reason}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eeba5a509d28d33bd54fd65d49c0adfcdf4f5a7207ffca384301190d345088c3)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#comment DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def created_at_millis(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#created_at_millis DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#created_at_millis}.'''
        result = self._values.get("created_at_millis")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def reviewer_collaborator_alias(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#reviewer_collaborator_alias DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#reviewer_collaborator_alias}.'''
        result = self._values.get("reviewer_collaborator_alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def review_state(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#review_state DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#review_state}.'''
        result = self._values.get("review_state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def review_sub_reason(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#review_sub_reason DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#review_sub_reason}.'''
        result = self._values.get("review_sub_reason")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebookReviews(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebookReviewsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebookReviewsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b227f6957ff04bb69015bf81a0ae97ae199caeee1ae6ef70241cc4c7100806b3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebookReviewsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1af47575061811f2f847dc3bb64aa4fbfb61dbccbf8b570a17750467463a71ef)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebookReviewsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c90fae9b59f43ba6df8a87cd2a2bb6a5f6304b5305a5c6d76b7fba20698fada)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b87443dde4c408a91f4e698847948ee0ee6264e0b42cdb30254805862b5dbc75)
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
            type_hints = typing.get_type_hints(_typecheckingstub__190cfdc4fe2ee5098e32dbb57823264f275ce4e437cfaf6728bbc60f77ad859d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebookReviews]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebookReviews]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebookReviews]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85e0b073f640cc0ed01c62b042c326903a52594b85d6bf025d754588daf76c14)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebookReviewsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebookReviewsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__076afd4c35db3ef541ed740b79084eae67661c8462e627ec9892fc76b3274c29)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cbf094ed8f6f4d9ad367399c23aef03ad5242ff462e96396e87a7d7be8c21550)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="createdAtMillis")
    def created_at_millis(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "createdAtMillis"))

    @created_at_millis.setter
    def created_at_millis(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9069b09f52e29051bdf1607b384ca648ca2052a7729eae0fb5aaa697a3e0c288)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdAtMillis", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="reviewerCollaboratorAlias")
    def reviewer_collaborator_alias(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reviewerCollaboratorAlias"))

    @reviewer_collaborator_alias.setter
    def reviewer_collaborator_alias(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c733973b354349a74ae14104ed13208f29b15e5a50a63c65d031ba5cb55bcaaa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reviewerCollaboratorAlias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="reviewState")
    def review_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reviewState"))

    @review_state.setter
    def review_state(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfefee15c05120a3cd4ce9e4ccc271bb06c09ab56b03c3cd2e224b483cbe3bae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reviewState", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="reviewSubReason")
    def review_sub_reason(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reviewSubReason"))

    @review_sub_reason.setter
    def review_sub_reason(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f98de49993aaa645a2c9cb44d6410ab640181a3a446aac53d9855d7162f909e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reviewSubReason", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebookReviews]:
        return typing.cast(typing.Optional[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebookReviews], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebookReviews],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6f72eeaa791ae1321adcdfb576fc7b8d8fb09a03b582e02e61ee23638ececa3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTable",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTable:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTable(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumns",
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
class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumns:
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        mask: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsMask", typing.Dict[builtins.str, typing.Any]]] = None,
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
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#comment DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#comment}.
        :param mask: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#mask DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#mask}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#name}.
        :param nullable: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#nullable DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#nullable}.
        :param partition_index: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#partition_index DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#partition_index}.
        :param position: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#position DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#position}.
        :param type_interval_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_interval_type DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_interval_type}.
        :param type_json: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_json DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_json}.
        :param type_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_name}.
        :param type_precision: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_precision DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_precision}.
        :param type_scale: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_scale DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_scale}.
        :param type_text: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_text DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_text}.
        '''
        if isinstance(mask, dict):
            mask = DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsMask(**mask)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a7122d633010101bc927f26e31fabf409412daf610642871fb5be16617b92c8)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#comment DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mask(
        self,
    ) -> typing.Optional["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsMask"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#mask DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#mask}.'''
        result = self._values.get("mask")
        return typing.cast(typing.Optional["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsMask"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nullable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#nullable DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#nullable}.'''
        result = self._values.get("nullable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def partition_index(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#partition_index DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#partition_index}.'''
        result = self._values.get("partition_index")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def position(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#position DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#position}.'''
        result = self._values.get("position")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_interval_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_interval_type DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_interval_type}.'''
        result = self._values.get("type_interval_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_json DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_json}.'''
        result = self._values.get("type_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_name}.'''
        result = self._values.get("type_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_precision(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_precision DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_precision}.'''
        result = self._values.get("type_precision")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_scale(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_scale DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_scale}.'''
        result = self._values.get("type_scale")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_text(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_text DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_text}.'''
        result = self._values.get("type_text")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumns(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__def51e95b19106b7563705aba53312abc7f4896d167019e5409b1029daf280d5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a409c6ab30ce57009f79ccb1b10fd2eab9fa4614fe8c047d61e4b2afde199398)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1dcaad84dd073d1fe3413d3a55cf9513fbb2d79b2a4928a11f0e2949284199d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6f00c00d508807a01892357c04e72a25d658a550d259dfd3e478a525a346624a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4994cd6453371f8736e1626c70624d15fb7d025616962e189b0e982a4193b822)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumns]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumns]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumns]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15ddcbdb932a906aa09230ec3b8442245c029a397d05eb6256e8b161f69eacbf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsMask",
    jsii_struct_bases=[],
    name_mapping={
        "function_name": "functionName",
        "using_column_names": "usingColumnNames",
    },
)
class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsMask:
    def __init__(
        self,
        *,
        function_name: typing.Optional[builtins.str] = None,
        using_column_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#function_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#function_name}.
        :param using_column_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#using_column_names DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#using_column_names}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6627cb79bf2d0f9837c4c9fe03020556e57628036113bf5752e7982dffd98c4a)
            check_type(argname="argument function_name", value=function_name, expected_type=type_hints["function_name"])
            check_type(argname="argument using_column_names", value=using_column_names, expected_type=type_hints["using_column_names"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if function_name is not None:
            self._values["function_name"] = function_name
        if using_column_names is not None:
            self._values["using_column_names"] = using_column_names

    @builtins.property
    def function_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#function_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#function_name}.'''
        result = self._values.get("function_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def using_column_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#using_column_names DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#using_column_names}.'''
        result = self._values.get("using_column_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsMask(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsMaskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsMaskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2812217022d49e6f13baab8db0c27b42863467c30d4cd4a5de65e8293bcadf59)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9cff77519f7bf8f66660c307f88688bf08b25929a6831d80ef38c4204826a202)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "functionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usingColumnNames")
    def using_column_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "usingColumnNames"))

    @using_column_names.setter
    def using_column_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81ad6c4693db0e9e43f3988cf55ad3611994538fbe6a0a7bd2e0247d278f610b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usingColumnNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsMask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsMask]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsMask]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a660b540eb8f3dc6cb814786bcefbefaaaaeeeadad0e917741c6ce7cc882920)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__35ca920b8915cdcd3bc54188850c053ad4aeb86c8bb0b11a0e8be2d2ab765930)
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
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#function_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#function_name}.
        :param using_column_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#using_column_names DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#using_column_names}.
        '''
        value = DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsMask(
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
    ) -> DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsMaskOutputReference:
        return typing.cast(DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsMaskOutputReference, jsii.get(self, "mask"))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="maskInput")
    def mask_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsMask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsMask]], jsii.get(self, "maskInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__879d52073ff7a4ef433a055e2fd78e0dceb4c1fe5e96b5dbd1d85f3328759a57)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8df312fc732fa74eada3c531f4156d646abf607a561c0cbe36c1557ad463f0c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8b7acae5d70ea85e3fc3f63d556bdf9cdc23159245d5d7740dc9c06108aeccd1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nullable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="partitionIndex")
    def partition_index(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "partitionIndex"))

    @partition_index.setter
    def partition_index(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6ef7cb88d1560533959abbd441a61cc646c94826da9efcb4d0c44d5bd357954)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "partitionIndex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="position")
    def position(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "position"))

    @position.setter
    def position(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dccfdbb365b76dca2cbb8810494948fb331f9539569ad0a6406b3f5baadf9173)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "position", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeIntervalType")
    def type_interval_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeIntervalType"))

    @type_interval_type.setter
    def type_interval_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__627d29336e6ccd2f9010de3a8548a7a410c61ae44ac496aba5cb0b343f3cddb2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeIntervalType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeJson")
    def type_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeJson"))

    @type_json.setter
    def type_json(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24f3808068237f96b99a9d3d92bc8cbbb0af24f74404a917f57c0a29a2f6e4dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeJson", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeName")
    def type_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeName"))

    @type_name.setter
    def type_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6415697c334efab9cae160fb8d75e0f663b0c0dc1588bc8bade785623ea92a7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typePrecision")
    def type_precision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "typePrecision"))

    @type_precision.setter
    def type_precision(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f13e6eaef8d0b25961814ebb7fc02bf7bb708233e3583794f6fcfa5513f7d8f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typePrecision", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeScale")
    def type_scale(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "typeScale"))

    @type_scale.setter
    def type_scale(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__775532ed9522e04ae9fb6e0020a91c1210c3051ef80e31dd40659ea39a2e5d7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeScale", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeText")
    def type_text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeText"))

    @type_text.setter
    def type_text(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7daf080abd37add0c54453b24d396f80f6642fda74f96a39f95e29a95b9b347)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeText", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumns]:
        return typing.cast(typing.Optional[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumns], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumns],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__264cb4dbf912cd126e8dd0a74e516a5966786157b810191ebb3104c371da459d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetails",
    jsii_struct_bases=[],
    name_mapping={"local_name": "localName", "partitions": "partitions"},
)
class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetails:
    def __init__(
        self,
        *,
        local_name: builtins.str,
        partitions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitions", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param local_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#local_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#local_name}.
        :param partitions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#partitions DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#partitions}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8165ce10bdeb89950cbfe3eb468ff377eff57d8b77150974e83d481c6ad3d59b)
            check_type(argname="argument local_name", value=local_name, expected_type=type_hints["local_name"])
            check_type(argname="argument partitions", value=partitions, expected_type=type_hints["partitions"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "local_name": local_name,
        }
        if partitions is not None:
            self._values["partitions"] = partitions

    @builtins.property
    def local_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#local_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#local_name}.'''
        result = self._values.get("local_name")
        assert result is not None, "Required property 'local_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def partitions(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitions"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#partitions DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#partitions}.'''
        result = self._values.get("partitions")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitions"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__67b61d1f1e7730cb1d20d5251b61356aab6f1b0e27a471550fb20c773aa8d519)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putPartitions")
    def put_partitions(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitions", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68f8bda31c763697a8c10a8e2aab3e90b43efc08b3bcfe8e715ab1a43ff5b99c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putPartitions", [value]))

    @jsii.member(jsii_name="resetPartitions")
    def reset_partitions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPartitions", []))

    @builtins.property
    @jsii.member(jsii_name="partitions")
    def partitions(
        self,
    ) -> "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsList":
        return typing.cast("DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsList", jsii.get(self, "partitions"))

    @builtins.property
    @jsii.member(jsii_name="localNameInput")
    def local_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "localNameInput"))

    @builtins.property
    @jsii.member(jsii_name="partitionsInput")
    def partitions_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitions"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitions"]]], jsii.get(self, "partitionsInput"))

    @builtins.property
    @jsii.member(jsii_name="localName")
    def local_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "localName"))

    @local_name.setter
    def local_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73eee334eaf2f61781ede6f763535512f09b164e763388c03850ea2ddfeff445)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "localName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetails]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetails]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3950b8b3d9a0810968663f2be60728e8aad5ff876e0821d5986076bb84e690d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitions",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitions:
    def __init__(
        self,
        *,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValue", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#value DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80c76367f99277fad304228f49ee658c96f03ccd039d6bd22ac113e52a6296f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValue"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#value DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValue"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2b2397eb2deda8a9040601fb6b441c3242b6fe8174a041ad04be7cda08c723be)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1a38e56ff3c14acf7f732c0117ad89e8a8fbc7b0605168f394415e6d3b88c0c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9beea055b32b51b304ca712755aca04bfc7614dfce12c99a3e58247fab43347e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5770c9b1b5b2a9acac872367495046d0abe71557146c18ff7298a8e05cb1630d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cb4cd8305fd19cec17c7d611caea66de3c03ea47f244fe6b5897b3fa2e890e69)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitions]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitions]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitions]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81459b02761b4a07876cfd5fed9398d7bd28de8ccab071a15b4135d2bb7b97b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1c873d90e4865f430979a4923f36dcd329bbed8b2e1b7cc1bd13d12ece695250)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putValue")
    def put_value(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValue", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35ba56d89da7cd0fdbb4142adedfb774bc058107f51803d15f9fb81fa2cd506b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putValue", [value]))

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(
        self,
    ) -> "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValueList":
        return typing.cast("DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValueList", jsii.get(self, "value"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValue"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValue"]]], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitions]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitions]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitions]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68474c1a9e1dcbc7ed42b495266e50211b520b312c8c8c4d20e4ade8a7a5cda7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValue",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "op": "op",
        "recipient_property_key": "recipientPropertyKey",
        "value": "value",
    },
)
class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValue:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        op: typing.Optional[builtins.str] = None,
        recipient_property_key: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#name}.
        :param op: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#op DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#op}.
        :param recipient_property_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#recipient_property_key DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#recipient_property_key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#value DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa26dff04f879d430583dac5e9f3e14c36217318b61e9fd49b7864f9c66d6a70)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def op(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#op DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#op}.'''
        result = self._values.get("op")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def recipient_property_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#recipient_property_key DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#recipient_property_key}.'''
        result = self._values.get("recipient_property_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#value DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValueList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValueList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c7c6e08845a07a77f2ac5733bb37c93bd2f4ff479a37cd255ef94bf16b5406bc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValueOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e91e43c0483f9bd1a7f765fc8052105fab9161e63a3ed5923570ed871d499df)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValueOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ca616d0e3738970034ea2a695f007506f63eb35d6615f4995a0ca7ad847d33f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a700d39aaed13f3a27e0bf28bdbf19fbcb1dac6d8506c15cf4244c51852f0529)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6a2e61d3425f6bf389b6bb6e49611319af25dabe78f5f54745057400e413810e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValue]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValue]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValue]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32876df31a16b7554f12a206a4011587232469a370652cf0ecefa0b5cb2e9591)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValueOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValueOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0bb1fe55b74c01c82098c9fa63f85acb892ac8ffff124f00f69b529b1fd3581e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d531b8a2416ffcf232cb12caf3c7c809e952a83b04ee5ce707ecb566ae8f4ea9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="op")
    def op(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "op"))

    @op.setter
    def op(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab0ab9d4ec6b586d7948a8904899430b663c3248e4dc539af7d946144da20a8b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "op", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="recipientPropertyKey")
    def recipient_property_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "recipientPropertyKey"))

    @recipient_property_key.setter
    def recipient_property_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e85dd5b4e5fff93a2c54deff36d2788dd2cf2d420cf2f71775cbe6445ff9f364)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "recipientPropertyKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6cce7a02ebd128563a9ad63783dda5cb8a6c29ab046b28fdd6b0009aef421f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValue]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValue]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValue]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de7ec1c266a6d208f0add8ee1a254c7366b0f996756b43c13d2416f9cb483537)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2b7fe21fb84ee41e818ecb1fb3aa81cff71b9e163fc93120aaf454a94d7f1591)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="columns")
    def columns(
        self,
    ) -> DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsList:
        return typing.cast(DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsList, jsii.get(self, "columns"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTable]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c2aa70e302ef4dad726aa5faf20bc85adaf22fb182e34f127a4075df2b74dbe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetView",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetView:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetView(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumns",
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
class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumns:
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        mask: typing.Optional[typing.Union["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsMask", typing.Dict[builtins.str, typing.Any]]] = None,
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
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#comment DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#comment}.
        :param mask: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#mask DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#mask}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#name}.
        :param nullable: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#nullable DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#nullable}.
        :param partition_index: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#partition_index DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#partition_index}.
        :param position: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#position DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#position}.
        :param type_interval_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_interval_type DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_interval_type}.
        :param type_json: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_json DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_json}.
        :param type_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_name}.
        :param type_precision: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_precision DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_precision}.
        :param type_scale: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_scale DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_scale}.
        :param type_text: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_text DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_text}.
        '''
        if isinstance(mask, dict):
            mask = DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsMask(**mask)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48bfb04833da9d00f61802efbd5c866e91c529230e90488addadaed0c62752f1)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#comment DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mask(
        self,
    ) -> typing.Optional["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsMask"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#mask DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#mask}.'''
        result = self._values.get("mask")
        return typing.cast(typing.Optional["DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsMask"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nullable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#nullable DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#nullable}.'''
        result = self._values.get("nullable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def partition_index(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#partition_index DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#partition_index}.'''
        result = self._values.get("partition_index")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def position(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#position DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#position}.'''
        result = self._values.get("position")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_interval_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_interval_type DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_interval_type}.'''
        result = self._values.get("type_interval_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_json DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_json}.'''
        result = self._values.get("type_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_name}.'''
        result = self._values.get("type_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_precision(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_precision DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_precision}.'''
        result = self._values.get("type_precision")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_scale(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_scale DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_scale}.'''
        result = self._values.get("type_scale")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_text(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#type_text DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#type_text}.'''
        result = self._values.get("type_text")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumns(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3ebaa544f73dcacc68641d25349a6e0f97c8b5e1dcdbcf30df47daad568a2cf3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__081d2d1c0b4598246c4d2a6ec9924b5bab35dc12f35ded36e704997516187b84)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1cc9e03dee1bd8a90e9be312d51178a4215fb9d8452a13cc34f192c75385cf1a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__027cd3ac2f26963fec8e2be229ff87c615c29b2926ac180380bf48560c26a129)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6434a6b487fee3b5946df15ef54efd34814354b008793f1663c5079efce2701e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumns]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumns]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumns]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7430f759117914c676b2e48e91a5623092526d92a883b8fea2ea7eea524be9b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsMask",
    jsii_struct_bases=[],
    name_mapping={
        "function_name": "functionName",
        "using_column_names": "usingColumnNames",
    },
)
class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsMask:
    def __init__(
        self,
        *,
        function_name: typing.Optional[builtins.str] = None,
        using_column_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#function_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#function_name}.
        :param using_column_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#using_column_names DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#using_column_names}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da653e64e268847965dda6511bd8d24639ee8c71bf9c4a8ae25a8ce05661bb92)
            check_type(argname="argument function_name", value=function_name, expected_type=type_hints["function_name"])
            check_type(argname="argument using_column_names", value=using_column_names, expected_type=type_hints["using_column_names"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if function_name is not None:
            self._values["function_name"] = function_name
        if using_column_names is not None:
            self._values["using_column_names"] = using_column_names

    @builtins.property
    def function_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#function_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#function_name}.'''
        result = self._values.get("function_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def using_column_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#using_column_names DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#using_column_names}.'''
        result = self._values.get("using_column_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsMask(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsMaskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsMaskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__33ec4dd2830b16f0975ede31004dd7e7fa0f401bb139626da9046d0a8dcd708a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d5086ebc0b3ba8e722732d7cb2e33c85a2c973abb17c2fd7dacdff6880486275)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "functionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usingColumnNames")
    def using_column_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "usingColumnNames"))

    @using_column_names.setter
    def using_column_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91d3dd72db6c08512649539a7d6c515319923f6f11c218a5131c540964a6f56b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usingColumnNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsMask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsMask]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsMask]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2279bf6968ebb6db768903e5552de067d19546475d69b4141f91ca7d5aee329f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1388f7a55f9a3b29c3f7f9f97a5c9d855208fd8ab66c314f56f0435afa2f1a2b)
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
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#function_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#function_name}.
        :param using_column_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#using_column_names DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#using_column_names}.
        '''
        value = DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsMask(
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
    ) -> DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsMaskOutputReference:
        return typing.cast(DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsMaskOutputReference, jsii.get(self, "mask"))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="maskInput")
    def mask_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsMask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsMask]], jsii.get(self, "maskInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__8cc5bdc1012af198a68a2253ef69233b2744abac77e771b4af6591175bc1abb2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2cfe966ac2a95c7b98e226c1824b1c85e7c6a2c87d0b981511d78da922ab6c1d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c862ce022f6af7967fd1f8f5580781fa96f49f0fe21adbe83719cf8cb267b4e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nullable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="partitionIndex")
    def partition_index(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "partitionIndex"))

    @partition_index.setter
    def partition_index(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__418971cb2c5ecfd2424b282cb49cd61f8a145aa7a398ad0c849cabe900ffbc50)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "partitionIndex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="position")
    def position(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "position"))

    @position.setter
    def position(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d7b8aacf6dd094ce009d8262f0f2765f9f1cf0ba6008b957814454a145b031a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "position", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeIntervalType")
    def type_interval_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeIntervalType"))

    @type_interval_type.setter
    def type_interval_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__532af16a8f5d27ca3f080f65325a405c59fd184ce96d66f2ca8884a452ec3aa1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeIntervalType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeJson")
    def type_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeJson"))

    @type_json.setter
    def type_json(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5bd1d01ea0348ed2cddb2e31143871efc20c579867642939c2fb56dfef23c3c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeJson", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeName")
    def type_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeName"))

    @type_name.setter
    def type_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad8d05dba5e2e6f4cf161241d9f0f5cb788ac0e0d36485fdd3953b5363d37928)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typePrecision")
    def type_precision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "typePrecision"))

    @type_precision.setter
    def type_precision(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82896513852ac215021d380912ce76580de081822ecccbb8993d1c2f6d6b35bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typePrecision", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeScale")
    def type_scale(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "typeScale"))

    @type_scale.setter
    def type_scale(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79225a6917e36f484c455e994c766dcca2cf602480742a0267fbd473809ef158)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeScale", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeText")
    def type_text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeText"))

    @type_text.setter
    def type_text(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__689a1580e28f4f00c6159a583bde8305e4da9aeda01669cbe5cd5e6bd7c6b341)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeText", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumns]:
        return typing.cast(typing.Optional[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumns], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumns],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea1490777eed9f87452369d089cfbb53cf9100a285e43440508306199dc7b03f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewLocalDetails",
    jsii_struct_bases=[],
    name_mapping={"local_name": "localName"},
)
class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewLocalDetails:
    def __init__(self, *, local_name: builtins.str) -> None:
        '''
        :param local_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#local_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#local_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca0d5f09d85e04a00dab3e55294891562c5d33bd4468bbafca429574670cefe0)
            check_type(argname="argument local_name", value=local_name, expected_type=type_hints["local_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "local_name": local_name,
        }

    @builtins.property
    def local_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#local_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#local_name}.'''
        result = self._values.get("local_name")
        assert result is not None, "Required property 'local_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewLocalDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewLocalDetailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewLocalDetailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bcceaa40e321836668a3fe3e9e8d557f6e73cbfe0b5c8e6515c8b891e7dad60b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5ce2d49798149ad80837448a62db8344579c4acc4f444f2f7bd68b7cb7176932)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "localName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewLocalDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewLocalDetails]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewLocalDetails]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__543c595ac04b9e40e4fe01fe809f2b2817fae2b160e9e9ae9f192368bd3be757)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5ed50710aacb5635795e2ec011f221563fd82ce29813213fd80cac4d22d34c38)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="columns")
    def columns(
        self,
    ) -> DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsList:
        return typing.cast(DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsList, jsii.get(self, "columns"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetView]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetView]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetView]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcde590b0ace018e7ba584cca92da0b0b7a450f1b0fa1a028356383f69ffc116)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetVolumeLocalDetails",
    jsii_struct_bases=[],
    name_mapping={"local_name": "localName"},
)
class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetVolumeLocalDetails:
    def __init__(self, *, local_name: builtins.str) -> None:
        '''
        :param local_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#local_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#local_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef223ec5e5b63e58a86ff249362f0da704c4a9dc99ae344ecdf9c89e8e0210b6)
            check_type(argname="argument local_name", value=local_name, expected_type=type_hints["local_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "local_name": local_name,
        }

    @builtins.property
    def local_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_room_asset_revisions_clean_room_asset#local_name DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset#local_name}.'''
        result = self._values.get("local_name")
        assert result is not None, "Required property 'local_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetVolumeLocalDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetVolumeLocalDetailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomAssetRevisionsCleanRoomAsset.DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetVolumeLocalDetailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c013f9f7e3480a68ba47b92801acaeec517a561fbce41521fe3936450e31141b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9caacebecb9a65a32464ae716ec7a35915c27b2c97eca569079ae3cb40f28e16)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "localName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetVolumeLocalDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetVolumeLocalDetails]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetVolumeLocalDetails]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68c06866601a7d92f55a50fe382de14716fdd0637db5baf234ceddb285f3917f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAsset",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetConfig",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTable",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumns",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsList",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsMask",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsMaskOutputReference",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsOutputReference",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableLocalDetails",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableLocalDetailsOutputReference",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableOutputReference",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebook",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebookOutputReference",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebookReviews",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebookReviewsList",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebookReviewsOutputReference",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTable",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumns",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsList",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsMask",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsMaskOutputReference",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsOutputReference",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetails",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsOutputReference",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitions",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsList",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsOutputReference",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValue",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValueList",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValueOutputReference",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableOutputReference",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetView",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumns",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsList",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsMask",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsMaskOutputReference",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsOutputReference",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewLocalDetails",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewLocalDetailsOutputReference",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewOutputReference",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetVolumeLocalDetails",
    "DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetVolumeLocalDetailsOutputReference",
]

publication.publish()

def _typecheckingstub__33383ce8ce2357c43601b2a09e9bf402db35d195e3806183f6529fa71cfb960c(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    asset_type: builtins.str,
    name: builtins.str,
    clean_room_name: typing.Optional[builtins.str] = None,
    foreign_table: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTable, typing.Dict[builtins.str, typing.Any]]] = None,
    foreign_table_local_details: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableLocalDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    notebook: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebook, typing.Dict[builtins.str, typing.Any]]] = None,
    table: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTable, typing.Dict[builtins.str, typing.Any]]] = None,
    table_local_details: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    view: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetView, typing.Dict[builtins.str, typing.Any]]] = None,
    view_local_details: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewLocalDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    volume_local_details: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetVolumeLocalDetails, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__878dac6b3b4edd19ce9a0ac502a3cf072c6e96361d468308d7533ae556e65480(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a6904e5d3e84379756cfe3db892427242affef4a018df6f113357d27e9190b7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cc48ea309090f72f5ecb63901f9da11c407eb800df9c54e4d486e74de71c532(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fed64d7711f866993d4203c0ab41a29b4b1de6e953ea66ee7e7cc41460955d5f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a2d088f1cc7b682a745dd22db1a399beabcb5bab0a6d249f45f084debcc3c51(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__828690ffdfd94607ab1e81b9d6fa5376e2ba57eabe1bb8db584a077bca8f46e8(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    asset_type: builtins.str,
    name: builtins.str,
    clean_room_name: typing.Optional[builtins.str] = None,
    foreign_table: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTable, typing.Dict[builtins.str, typing.Any]]] = None,
    foreign_table_local_details: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableLocalDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    notebook: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebook, typing.Dict[builtins.str, typing.Any]]] = None,
    table: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTable, typing.Dict[builtins.str, typing.Any]]] = None,
    table_local_details: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    view: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetView, typing.Dict[builtins.str, typing.Any]]] = None,
    view_local_details: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewLocalDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    volume_local_details: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetVolumeLocalDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    workspace_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__561a9d842bbba3538d6a892fd70ef63ffe745c977602f4d8f97339630913ce31(
    *,
    comment: typing.Optional[builtins.str] = None,
    mask: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsMask, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__0ec615e2295c5d42748d1288731b6ccce5b4fbb31d50c615de4d8e7270552395(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9eb3326faec736e362ed49cf9634b82982c2556e68ec73672b72d5f275f5df9(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcede0e24a8e0aa10af5fcebdd64e6b7f4ad61c6136444f98f922f782c7d26b7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__787d225b6ff4cb80a530fbc9c7946702f02dce8cb0f4ece6b2ad918912b57736(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99c6d9cb08e1590025277bdc9356e7058afc58d50a282251d95ed22b2901c800(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f106f4682fdfc2d2ccc9d2d1cf6b6e5a8e75cb643609807c1bd266946ae4e99b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumns]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da94b9f25719ad4f6d46dacdab1b8521f8218392ccca8124e666230b5dc288d4(
    *,
    function_name: typing.Optional[builtins.str] = None,
    using_column_names: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7f6054ae182f0b0d71fc67a6520dfd38f3339f40d91de3f7fcbc9ed688887c2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__715377dc16aee0054fe6b425f60c28b570267d04093aa91588f7593f38b99026(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ce2aa94760820996646ddfd4c0bc7849abd984332d9f53dad2157efd61b97eb(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34615945aaa632f5d8e82c57bb8f80cea3855ba4e2251e820c2cb7387b2ab7ef(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumnsMask]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d281617648abe067c6c4a0de74d65795e4127ba07309759a2573bbbe8895997a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52833c97f37fb4a356a9ec0d35f4542c49f12f8a26cf2772ac07e1a4657d0764(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ab3d9577df51338d5f7e2213e4c6841206dc4813e8fab6dd07eea3951295722(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a65a718ea057f5e6e64d47c2fa8d036bfebaccd7909c7adad9fc1bfafb63b1f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be31d9fd78d7a866834354874c0c2e50be690dffa4e9e7ff5db851b5c7ab2dd6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bef6f103781d9f37e0d8e625ae26908ea5e91206aedb4053fd07edead7c24a4b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb3106f50d6890cc6261ec47bf19bb7c84db18e17f18cfbfcaf94470d49a3200(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cc73d6ed99cab08f4cba29f16a89622ecc47e50471138aadc89e1f6bc6e1864(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e2035f50c7c34ee98439aa0c5842017a78e0333d114d929195aae1a3f10cf00(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c1bd860362baefb4bd600b7ffa542b240094719830dae7a1c6b92baa55aec66(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9353b6866134250d0769bb914cca2de6fd07d7c7bd02ef520d34a37b19097db2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3eeb0adeac0b00a26b37e2badba0a8c9e28373b74c2146a093ad7ff2de631975(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e00bd34e04b168936ace9ccf1e38c3933067c775dd01219d46b491065993c582(
    value: typing.Optional[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableColumns],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__461162c3ff843fa14cad4ad8b1495d581bfa439fecbfc779894450e25354d372(
    *,
    local_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f1292f9fa54deb6f0d113446ce8c17cea5803fb248f2b236a649ac404966e14(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__939a698c93af7e34665d772f9ebf98e7cd2dc64dde8cf4f98ed28d93f541ebcc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72032196d598cb031b16ffed390d2692f3a8016471377ecef972ea7a3598d22d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTableLocalDetails]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b42580951312753e221efeba0bb207a6e5e1028086a0898da97418c4dbf5910d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8bb95279b76004c4b05adc0fe4383caa47090f7e2f2a37637b83b36751e8a77(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetForeignTable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f7295fa74ac99f0a2948cc44a5b0fe3a5ea258d3c84a2f03cf1f581fd9c440b(
    *,
    notebook_content: builtins.str,
    runner_collaborator_aliases: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8ab45a6618c7bc0a406500370f5dc0a7c5eb4c9940f3170c9275992db17327d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f2fc7b37b35b1b4a271da0915a202bc01ff26e172ab4785d1879f494366cf1f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acbe3ff7db9902c612620ddbf127e765b505c2f0fd2c131ba47789ed66c284e2(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69397be7300e067c4cc8e19bda1a374f1b8f6a84dd4c14f9f5762c0e306c9d6c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebook]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eeba5a509d28d33bd54fd65d49c0adfcdf4f5a7207ffca384301190d345088c3(
    *,
    comment: typing.Optional[builtins.str] = None,
    created_at_millis: typing.Optional[jsii.Number] = None,
    reviewer_collaborator_alias: typing.Optional[builtins.str] = None,
    review_state: typing.Optional[builtins.str] = None,
    review_sub_reason: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b227f6957ff04bb69015bf81a0ae97ae199caeee1ae6ef70241cc4c7100806b3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1af47575061811f2f847dc3bb64aa4fbfb61dbccbf8b570a17750467463a71ef(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c90fae9b59f43ba6df8a87cd2a2bb6a5f6304b5305a5c6d76b7fba20698fada(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b87443dde4c408a91f4e698847948ee0ee6264e0b42cdb30254805862b5dbc75(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__190cfdc4fe2ee5098e32dbb57823264f275ce4e437cfaf6728bbc60f77ad859d(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85e0b073f640cc0ed01c62b042c326903a52594b85d6bf025d754588daf76c14(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebookReviews]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__076afd4c35db3ef541ed740b79084eae67661c8462e627ec9892fc76b3274c29(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbf094ed8f6f4d9ad367399c23aef03ad5242ff462e96396e87a7d7be8c21550(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9069b09f52e29051bdf1607b384ca648ca2052a7729eae0fb5aaa697a3e0c288(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c733973b354349a74ae14104ed13208f29b15e5a50a63c65d031ba5cb55bcaaa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfefee15c05120a3cd4ce9e4ccc271bb06c09ab56b03c3cd2e224b483cbe3bae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f98de49993aaa645a2c9cb44d6410ab640181a3a446aac53d9855d7162f909e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6f72eeaa791ae1321adcdfb576fc7b8d8fb09a03b582e02e61ee23638ececa3(
    value: typing.Optional[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetNotebookReviews],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a7122d633010101bc927f26e31fabf409412daf610642871fb5be16617b92c8(
    *,
    comment: typing.Optional[builtins.str] = None,
    mask: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsMask, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__def51e95b19106b7563705aba53312abc7f4896d167019e5409b1029daf280d5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a409c6ab30ce57009f79ccb1b10fd2eab9fa4614fe8c047d61e4b2afde199398(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1dcaad84dd073d1fe3413d3a55cf9513fbb2d79b2a4928a11f0e2949284199d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f00c00d508807a01892357c04e72a25d658a550d259dfd3e478a525a346624a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4994cd6453371f8736e1626c70624d15fb7d025616962e189b0e982a4193b822(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15ddcbdb932a906aa09230ec3b8442245c029a397d05eb6256e8b161f69eacbf(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumns]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6627cb79bf2d0f9837c4c9fe03020556e57628036113bf5752e7982dffd98c4a(
    *,
    function_name: typing.Optional[builtins.str] = None,
    using_column_names: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2812217022d49e6f13baab8db0c27b42863467c30d4cd4a5de65e8293bcadf59(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cff77519f7bf8f66660c307f88688bf08b25929a6831d80ef38c4204826a202(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81ad6c4693db0e9e43f3988cf55ad3611994538fbe6a0a7bd2e0247d278f610b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a660b540eb8f3dc6cb814786bcefbefaaaaeeeadad0e917741c6ce7cc882920(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumnsMask]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35ca920b8915cdcd3bc54188850c053ad4aeb86c8bb0b11a0e8be2d2ab765930(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__879d52073ff7a4ef433a055e2fd78e0dceb4c1fe5e96b5dbd1d85f3328759a57(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8df312fc732fa74eada3c531f4156d646abf607a561c0cbe36c1557ad463f0c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b7acae5d70ea85e3fc3f63d556bdf9cdc23159245d5d7740dc9c06108aeccd1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6ef7cb88d1560533959abbd441a61cc646c94826da9efcb4d0c44d5bd357954(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dccfdbb365b76dca2cbb8810494948fb331f9539569ad0a6406b3f5baadf9173(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__627d29336e6ccd2f9010de3a8548a7a410c61ae44ac496aba5cb0b343f3cddb2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24f3808068237f96b99a9d3d92bc8cbbb0af24f74404a917f57c0a29a2f6e4dc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6415697c334efab9cae160fb8d75e0f663b0c0dc1588bc8bade785623ea92a7c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f13e6eaef8d0b25961814ebb7fc02bf7bb708233e3583794f6fcfa5513f7d8f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__775532ed9522e04ae9fb6e0020a91c1210c3051ef80e31dd40659ea39a2e5d7c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7daf080abd37add0c54453b24d396f80f6642fda74f96a39f95e29a95b9b347(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__264cb4dbf912cd126e8dd0a74e516a5966786157b810191ebb3104c371da459d(
    value: typing.Optional[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableColumns],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8165ce10bdeb89950cbfe3eb468ff377eff57d8b77150974e83d481c6ad3d59b(
    *,
    local_name: builtins.str,
    partitions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitions, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67b61d1f1e7730cb1d20d5251b61356aab6f1b0e27a471550fb20c773aa8d519(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68f8bda31c763697a8c10a8e2aab3e90b43efc08b3bcfe8e715ab1a43ff5b99c(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitions, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73eee334eaf2f61781ede6f763535512f09b164e763388c03850ea2ddfeff445(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3950b8b3d9a0810968663f2be60728e8aad5ff876e0821d5986076bb84e690d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetails]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80c76367f99277fad304228f49ee658c96f03ccd039d6bd22ac113e52a6296f9(
    *,
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValue, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b2397eb2deda8a9040601fb6b441c3242b6fe8174a041ad04be7cda08c723be(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1a38e56ff3c14acf7f732c0117ad89e8a8fbc7b0605168f394415e6d3b88c0c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9beea055b32b51b304ca712755aca04bfc7614dfce12c99a3e58247fab43347e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5770c9b1b5b2a9acac872367495046d0abe71557146c18ff7298a8e05cb1630d(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb4cd8305fd19cec17c7d611caea66de3c03ea47f244fe6b5897b3fa2e890e69(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81459b02761b4a07876cfd5fed9398d7bd28de8ccab071a15b4135d2bb7b97b8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitions]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c873d90e4865f430979a4923f36dcd329bbed8b2e1b7cc1bd13d12ece695250(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35ba56d89da7cd0fdbb4142adedfb774bc058107f51803d15f9fb81fa2cd506b(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValue, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68474c1a9e1dcbc7ed42b495266e50211b520b312c8c8c4d20e4ade8a7a5cda7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitions]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa26dff04f879d430583dac5e9f3e14c36217318b61e9fd49b7864f9c66d6a70(
    *,
    name: typing.Optional[builtins.str] = None,
    op: typing.Optional[builtins.str] = None,
    recipient_property_key: typing.Optional[builtins.str] = None,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7c6e08845a07a77f2ac5733bb37c93bd2f4ff479a37cd255ef94bf16b5406bc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e91e43c0483f9bd1a7f765fc8052105fab9161e63a3ed5923570ed871d499df(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ca616d0e3738970034ea2a695f007506f63eb35d6615f4995a0ca7ad847d33f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a700d39aaed13f3a27e0bf28bdbf19fbcb1dac6d8506c15cf4244c51852f0529(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a2e61d3425f6bf389b6bb6e49611319af25dabe78f5f54745057400e413810e(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32876df31a16b7554f12a206a4011587232469a370652cf0ecefa0b5cb2e9591(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValue]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bb1fe55b74c01c82098c9fa63f85acb892ac8ffff124f00f69b529b1fd3581e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d531b8a2416ffcf232cb12caf3c7c809e952a83b04ee5ce707ecb566ae8f4ea9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab0ab9d4ec6b586d7948a8904899430b663c3248e4dc539af7d946144da20a8b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e85dd5b4e5fff93a2c54deff36d2788dd2cf2d420cf2f71775cbe6445ff9f364(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6cce7a02ebd128563a9ad63783dda5cb8a6c29ab046b28fdd6b0009aef421f3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de7ec1c266a6d208f0add8ee1a254c7366b0f996756b43c13d2416f9cb483537(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTableLocalDetailsPartitionsValue]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b7fe21fb84ee41e818ecb1fb3aa81cff71b9e163fc93120aaf454a94d7f1591(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c2aa70e302ef4dad726aa5faf20bc85adaf22fb182e34f127a4075df2b74dbe(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetTable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48bfb04833da9d00f61802efbd5c866e91c529230e90488addadaed0c62752f1(
    *,
    comment: typing.Optional[builtins.str] = None,
    mask: typing.Optional[typing.Union[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsMask, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__3ebaa544f73dcacc68641d25349a6e0f97c8b5e1dcdbcf30df47daad568a2cf3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__081d2d1c0b4598246c4d2a6ec9924b5bab35dc12f35ded36e704997516187b84(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cc9e03dee1bd8a90e9be312d51178a4215fb9d8452a13cc34f192c75385cf1a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__027cd3ac2f26963fec8e2be229ff87c615c29b2926ac180380bf48560c26a129(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6434a6b487fee3b5946df15ef54efd34814354b008793f1663c5079efce2701e(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7430f759117914c676b2e48e91a5623092526d92a883b8fea2ea7eea524be9b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumns]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da653e64e268847965dda6511bd8d24639ee8c71bf9c4a8ae25a8ce05661bb92(
    *,
    function_name: typing.Optional[builtins.str] = None,
    using_column_names: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33ec4dd2830b16f0975ede31004dd7e7fa0f401bb139626da9046d0a8dcd708a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5086ebc0b3ba8e722732d7cb2e33c85a2c973abb17c2fd7dacdff6880486275(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91d3dd72db6c08512649539a7d6c515319923f6f11c218a5131c540964a6f56b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2279bf6968ebb6db768903e5552de067d19546475d69b4141f91ca7d5aee329f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumnsMask]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1388f7a55f9a3b29c3f7f9f97a5c9d855208fd8ab66c314f56f0435afa2f1a2b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cc5bdc1012af198a68a2253ef69233b2744abac77e771b4af6591175bc1abb2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cfe966ac2a95c7b98e226c1824b1c85e7c6a2c87d0b981511d78da922ab6c1d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c862ce022f6af7967fd1f8f5580781fa96f49f0fe21adbe83719cf8cb267b4e1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__418971cb2c5ecfd2424b282cb49cd61f8a145aa7a398ad0c849cabe900ffbc50(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d7b8aacf6dd094ce009d8262f0f2765f9f1cf0ba6008b957814454a145b031a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__532af16a8f5d27ca3f080f65325a405c59fd184ce96d66f2ca8884a452ec3aa1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bd1d01ea0348ed2cddb2e31143871efc20c579867642939c2fb56dfef23c3c4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad8d05dba5e2e6f4cf161241d9f0f5cb788ac0e0d36485fdd3953b5363d37928(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82896513852ac215021d380912ce76580de081822ecccbb8993d1c2f6d6b35bb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79225a6917e36f484c455e994c766dcca2cf602480742a0267fbd473809ef158(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__689a1580e28f4f00c6159a583bde8305e4da9aeda01669cbe5cd5e6bd7c6b341(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea1490777eed9f87452369d089cfbb53cf9100a285e43440508306199dc7b03f(
    value: typing.Optional[DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewColumns],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca0d5f09d85e04a00dab3e55294891562c5d33bd4468bbafca429574670cefe0(
    *,
    local_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcceaa40e321836668a3fe3e9e8d557f6e73cbfe0b5c8e6515c8b891e7dad60b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ce2d49798149ad80837448a62db8344579c4acc4f444f2f7bd68b7cb7176932(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__543c595ac04b9e40e4fe01fe809f2b2817fae2b160e9e9ae9f192368bd3be757(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetViewLocalDetails]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ed50710aacb5635795e2ec011f221563fd82ce29813213fd80cac4d22d34c38(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcde590b0ace018e7ba584cca92da0b0b7a450f1b0fa1a028356383f69ffc116(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetView]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef223ec5e5b63e58a86ff249362f0da704c4a9dc99ae344ecdf9c89e8e0210b6(
    *,
    local_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c013f9f7e3480a68ba47b92801acaeec517a561fbce41521fe3936450e31141b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9caacebecb9a65a32464ae716ec7a35915c27b2c97eca569079ae3cb40f28e16(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68c06866601a7d92f55a50fe382de14716fdd0637db5baf234ceddb285f3917f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomAssetRevisionsCleanRoomAssetVolumeLocalDetails]],
) -> None:
    """Type checking stubs"""
    pass
