r'''
# `databricks_clean_room_asset`

Refer to the Terraform Registry for docs: [`databricks_clean_room_asset`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset).
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


class CleanRoomAsset(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAsset",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset databricks_clean_room_asset}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        asset_type: builtins.str,
        name: builtins.str,
        clean_room_name: typing.Optional[builtins.str] = None,
        foreign_table: typing.Optional[typing.Union["CleanRoomAssetForeignTable", typing.Dict[builtins.str, typing.Any]]] = None,
        foreign_table_local_details: typing.Optional[typing.Union["CleanRoomAssetForeignTableLocalDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        notebook: typing.Optional[typing.Union["CleanRoomAssetNotebook", typing.Dict[builtins.str, typing.Any]]] = None,
        table: typing.Optional[typing.Union["CleanRoomAssetTable", typing.Dict[builtins.str, typing.Any]]] = None,
        table_local_details: typing.Optional[typing.Union["CleanRoomAssetTableLocalDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        view: typing.Optional[typing.Union["CleanRoomAssetView", typing.Dict[builtins.str, typing.Any]]] = None,
        view_local_details: typing.Optional[typing.Union["CleanRoomAssetViewLocalDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        volume_local_details: typing.Optional[typing.Union["CleanRoomAssetVolumeLocalDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        workspace_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset databricks_clean_room_asset} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param asset_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#asset_type CleanRoomAsset#asset_type}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#name CleanRoomAsset#name}.
        :param clean_room_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#clean_room_name CleanRoomAsset#clean_room_name}.
        :param foreign_table: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#foreign_table CleanRoomAsset#foreign_table}.
        :param foreign_table_local_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#foreign_table_local_details CleanRoomAsset#foreign_table_local_details}.
        :param notebook: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#notebook CleanRoomAsset#notebook}.
        :param table: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#table CleanRoomAsset#table}.
        :param table_local_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#table_local_details CleanRoomAsset#table_local_details}.
        :param view: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#view CleanRoomAsset#view}.
        :param view_local_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#view_local_details CleanRoomAsset#view_local_details}.
        :param volume_local_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#volume_local_details CleanRoomAsset#volume_local_details}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#workspace_id CleanRoomAsset#workspace_id}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a60dd203af0ac0b160476606b8a637056f66664a21ad2f2a5cd5ed4f386a02bc)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = CleanRoomAssetConfig(
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
        '''Generates CDKTF code for importing a CleanRoomAsset resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the CleanRoomAsset to import.
        :param import_from_id: The id of the existing CleanRoomAsset that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the CleanRoomAsset to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__904173d453faada27d070165187249960ffc95a04c46ecdae501d5a07eec9aed)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putForeignTable")
    def put_foreign_table(self) -> None:
        value = CleanRoomAssetForeignTable()

        return typing.cast(None, jsii.invoke(self, "putForeignTable", [value]))

    @jsii.member(jsii_name="putForeignTableLocalDetails")
    def put_foreign_table_local_details(self, *, local_name: builtins.str) -> None:
        '''
        :param local_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#local_name CleanRoomAsset#local_name}.
        '''
        value = CleanRoomAssetForeignTableLocalDetails(local_name=local_name)

        return typing.cast(None, jsii.invoke(self, "putForeignTableLocalDetails", [value]))

    @jsii.member(jsii_name="putNotebook")
    def put_notebook(
        self,
        *,
        notebook_content: builtins.str,
        runner_collaborator_aliases: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param notebook_content: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#notebook_content CleanRoomAsset#notebook_content}.
        :param runner_collaborator_aliases: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#runner_collaborator_aliases CleanRoomAsset#runner_collaborator_aliases}.
        '''
        value = CleanRoomAssetNotebook(
            notebook_content=notebook_content,
            runner_collaborator_aliases=runner_collaborator_aliases,
        )

        return typing.cast(None, jsii.invoke(self, "putNotebook", [value]))

    @jsii.member(jsii_name="putTable")
    def put_table(self) -> None:
        value = CleanRoomAssetTable()

        return typing.cast(None, jsii.invoke(self, "putTable", [value]))

    @jsii.member(jsii_name="putTableLocalDetails")
    def put_table_local_details(
        self,
        *,
        local_name: builtins.str,
        partitions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CleanRoomAssetTableLocalDetailsPartitions", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param local_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#local_name CleanRoomAsset#local_name}.
        :param partitions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#partitions CleanRoomAsset#partitions}.
        '''
        value = CleanRoomAssetTableLocalDetails(
            local_name=local_name, partitions=partitions
        )

        return typing.cast(None, jsii.invoke(self, "putTableLocalDetails", [value]))

    @jsii.member(jsii_name="putView")
    def put_view(self) -> None:
        value = CleanRoomAssetView()

        return typing.cast(None, jsii.invoke(self, "putView", [value]))

    @jsii.member(jsii_name="putViewLocalDetails")
    def put_view_local_details(self, *, local_name: builtins.str) -> None:
        '''
        :param local_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#local_name CleanRoomAsset#local_name}.
        '''
        value = CleanRoomAssetViewLocalDetails(local_name=local_name)

        return typing.cast(None, jsii.invoke(self, "putViewLocalDetails", [value]))

    @jsii.member(jsii_name="putVolumeLocalDetails")
    def put_volume_local_details(self, *, local_name: builtins.str) -> None:
        '''
        :param local_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#local_name CleanRoomAsset#local_name}.
        '''
        value = CleanRoomAssetVolumeLocalDetails(local_name=local_name)

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
    def foreign_table(self) -> "CleanRoomAssetForeignTableOutputReference":
        return typing.cast("CleanRoomAssetForeignTableOutputReference", jsii.get(self, "foreignTable"))

    @builtins.property
    @jsii.member(jsii_name="foreignTableLocalDetails")
    def foreign_table_local_details(
        self,
    ) -> "CleanRoomAssetForeignTableLocalDetailsOutputReference":
        return typing.cast("CleanRoomAssetForeignTableLocalDetailsOutputReference", jsii.get(self, "foreignTableLocalDetails"))

    @builtins.property
    @jsii.member(jsii_name="notebook")
    def notebook(self) -> "CleanRoomAssetNotebookOutputReference":
        return typing.cast("CleanRoomAssetNotebookOutputReference", jsii.get(self, "notebook"))

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
    def table(self) -> "CleanRoomAssetTableOutputReference":
        return typing.cast("CleanRoomAssetTableOutputReference", jsii.get(self, "table"))

    @builtins.property
    @jsii.member(jsii_name="tableLocalDetails")
    def table_local_details(self) -> "CleanRoomAssetTableLocalDetailsOutputReference":
        return typing.cast("CleanRoomAssetTableLocalDetailsOutputReference", jsii.get(self, "tableLocalDetails"))

    @builtins.property
    @jsii.member(jsii_name="view")
    def view(self) -> "CleanRoomAssetViewOutputReference":
        return typing.cast("CleanRoomAssetViewOutputReference", jsii.get(self, "view"))

    @builtins.property
    @jsii.member(jsii_name="viewLocalDetails")
    def view_local_details(self) -> "CleanRoomAssetViewLocalDetailsOutputReference":
        return typing.cast("CleanRoomAssetViewLocalDetailsOutputReference", jsii.get(self, "viewLocalDetails"))

    @builtins.property
    @jsii.member(jsii_name="volumeLocalDetails")
    def volume_local_details(self) -> "CleanRoomAssetVolumeLocalDetailsOutputReference":
        return typing.cast("CleanRoomAssetVolumeLocalDetailsOutputReference", jsii.get(self, "volumeLocalDetails"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "CleanRoomAssetForeignTable"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "CleanRoomAssetForeignTable"]], jsii.get(self, "foreignTableInput"))

    @builtins.property
    @jsii.member(jsii_name="foreignTableLocalDetailsInput")
    def foreign_table_local_details_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "CleanRoomAssetForeignTableLocalDetails"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "CleanRoomAssetForeignTableLocalDetails"]], jsii.get(self, "foreignTableLocalDetailsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="notebookInput")
    def notebook_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "CleanRoomAssetNotebook"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "CleanRoomAssetNotebook"]], jsii.get(self, "notebookInput"))

    @builtins.property
    @jsii.member(jsii_name="tableInput")
    def table_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "CleanRoomAssetTable"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "CleanRoomAssetTable"]], jsii.get(self, "tableInput"))

    @builtins.property
    @jsii.member(jsii_name="tableLocalDetailsInput")
    def table_local_details_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "CleanRoomAssetTableLocalDetails"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "CleanRoomAssetTableLocalDetails"]], jsii.get(self, "tableLocalDetailsInput"))

    @builtins.property
    @jsii.member(jsii_name="viewInput")
    def view_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "CleanRoomAssetView"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "CleanRoomAssetView"]], jsii.get(self, "viewInput"))

    @builtins.property
    @jsii.member(jsii_name="viewLocalDetailsInput")
    def view_local_details_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "CleanRoomAssetViewLocalDetails"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "CleanRoomAssetViewLocalDetails"]], jsii.get(self, "viewLocalDetailsInput"))

    @builtins.property
    @jsii.member(jsii_name="volumeLocalDetailsInput")
    def volume_local_details_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "CleanRoomAssetVolumeLocalDetails"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "CleanRoomAssetVolumeLocalDetails"]], jsii.get(self, "volumeLocalDetailsInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__60f3096211cc66005d5cad866406b956fa7c3d652ad7066c03085734028f250c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "assetType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cleanRoomName")
    def clean_room_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cleanRoomName"))

    @clean_room_name.setter
    def clean_room_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58d7277f4544f9bc875f92f5b26a1c90c3b0e5930db2f33a1baaf2dbf5776688)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cleanRoomName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8183c0aa2375affc34230a24453351acaa9ac696e177e113083f6c4bc0dd4c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workspaceId")
    def workspace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceId"))

    @workspace_id.setter
    def workspace_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2dc73f17b04f4290cd965cd282d36ca03139fe9a65900a4a33811c3947cfddbc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workspaceId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetConfig",
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
class CleanRoomAssetConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        foreign_table: typing.Optional[typing.Union["CleanRoomAssetForeignTable", typing.Dict[builtins.str, typing.Any]]] = None,
        foreign_table_local_details: typing.Optional[typing.Union["CleanRoomAssetForeignTableLocalDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        notebook: typing.Optional[typing.Union["CleanRoomAssetNotebook", typing.Dict[builtins.str, typing.Any]]] = None,
        table: typing.Optional[typing.Union["CleanRoomAssetTable", typing.Dict[builtins.str, typing.Any]]] = None,
        table_local_details: typing.Optional[typing.Union["CleanRoomAssetTableLocalDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        view: typing.Optional[typing.Union["CleanRoomAssetView", typing.Dict[builtins.str, typing.Any]]] = None,
        view_local_details: typing.Optional[typing.Union["CleanRoomAssetViewLocalDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        volume_local_details: typing.Optional[typing.Union["CleanRoomAssetVolumeLocalDetails", typing.Dict[builtins.str, typing.Any]]] = None,
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
        :param asset_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#asset_type CleanRoomAsset#asset_type}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#name CleanRoomAsset#name}.
        :param clean_room_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#clean_room_name CleanRoomAsset#clean_room_name}.
        :param foreign_table: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#foreign_table CleanRoomAsset#foreign_table}.
        :param foreign_table_local_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#foreign_table_local_details CleanRoomAsset#foreign_table_local_details}.
        :param notebook: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#notebook CleanRoomAsset#notebook}.
        :param table: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#table CleanRoomAsset#table}.
        :param table_local_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#table_local_details CleanRoomAsset#table_local_details}.
        :param view: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#view CleanRoomAsset#view}.
        :param view_local_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#view_local_details CleanRoomAsset#view_local_details}.
        :param volume_local_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#volume_local_details CleanRoomAsset#volume_local_details}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#workspace_id CleanRoomAsset#workspace_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(foreign_table, dict):
            foreign_table = CleanRoomAssetForeignTable(**foreign_table)
        if isinstance(foreign_table_local_details, dict):
            foreign_table_local_details = CleanRoomAssetForeignTableLocalDetails(**foreign_table_local_details)
        if isinstance(notebook, dict):
            notebook = CleanRoomAssetNotebook(**notebook)
        if isinstance(table, dict):
            table = CleanRoomAssetTable(**table)
        if isinstance(table_local_details, dict):
            table_local_details = CleanRoomAssetTableLocalDetails(**table_local_details)
        if isinstance(view, dict):
            view = CleanRoomAssetView(**view)
        if isinstance(view_local_details, dict):
            view_local_details = CleanRoomAssetViewLocalDetails(**view_local_details)
        if isinstance(volume_local_details, dict):
            volume_local_details = CleanRoomAssetVolumeLocalDetails(**volume_local_details)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2851bb51a227e4dcdff9f524922fa0d78a4bab49b68d0340374abd08e2d17e39)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#asset_type CleanRoomAsset#asset_type}.'''
        result = self._values.get("asset_type")
        assert result is not None, "Required property 'asset_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#name CleanRoomAsset#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def clean_room_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#clean_room_name CleanRoomAsset#clean_room_name}.'''
        result = self._values.get("clean_room_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def foreign_table(self) -> typing.Optional["CleanRoomAssetForeignTable"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#foreign_table CleanRoomAsset#foreign_table}.'''
        result = self._values.get("foreign_table")
        return typing.cast(typing.Optional["CleanRoomAssetForeignTable"], result)

    @builtins.property
    def foreign_table_local_details(
        self,
    ) -> typing.Optional["CleanRoomAssetForeignTableLocalDetails"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#foreign_table_local_details CleanRoomAsset#foreign_table_local_details}.'''
        result = self._values.get("foreign_table_local_details")
        return typing.cast(typing.Optional["CleanRoomAssetForeignTableLocalDetails"], result)

    @builtins.property
    def notebook(self) -> typing.Optional["CleanRoomAssetNotebook"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#notebook CleanRoomAsset#notebook}.'''
        result = self._values.get("notebook")
        return typing.cast(typing.Optional["CleanRoomAssetNotebook"], result)

    @builtins.property
    def table(self) -> typing.Optional["CleanRoomAssetTable"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#table CleanRoomAsset#table}.'''
        result = self._values.get("table")
        return typing.cast(typing.Optional["CleanRoomAssetTable"], result)

    @builtins.property
    def table_local_details(self) -> typing.Optional["CleanRoomAssetTableLocalDetails"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#table_local_details CleanRoomAsset#table_local_details}.'''
        result = self._values.get("table_local_details")
        return typing.cast(typing.Optional["CleanRoomAssetTableLocalDetails"], result)

    @builtins.property
    def view(self) -> typing.Optional["CleanRoomAssetView"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#view CleanRoomAsset#view}.'''
        result = self._values.get("view")
        return typing.cast(typing.Optional["CleanRoomAssetView"], result)

    @builtins.property
    def view_local_details(self) -> typing.Optional["CleanRoomAssetViewLocalDetails"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#view_local_details CleanRoomAsset#view_local_details}.'''
        result = self._values.get("view_local_details")
        return typing.cast(typing.Optional["CleanRoomAssetViewLocalDetails"], result)

    @builtins.property
    def volume_local_details(
        self,
    ) -> typing.Optional["CleanRoomAssetVolumeLocalDetails"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#volume_local_details CleanRoomAsset#volume_local_details}.'''
        result = self._values.get("volume_local_details")
        return typing.cast(typing.Optional["CleanRoomAssetVolumeLocalDetails"], result)

    @builtins.property
    def workspace_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#workspace_id CleanRoomAsset#workspace_id}.'''
        result = self._values.get("workspace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CleanRoomAssetConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetForeignTable",
    jsii_struct_bases=[],
    name_mapping={},
)
class CleanRoomAssetForeignTable:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CleanRoomAssetForeignTable(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetForeignTableColumns",
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
class CleanRoomAssetForeignTableColumns:
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        mask: typing.Optional[typing.Union["CleanRoomAssetForeignTableColumnsMask", typing.Dict[builtins.str, typing.Any]]] = None,
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
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#comment CleanRoomAsset#comment}.
        :param mask: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#mask CleanRoomAsset#mask}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#name CleanRoomAsset#name}.
        :param nullable: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#nullable CleanRoomAsset#nullable}.
        :param partition_index: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#partition_index CleanRoomAsset#partition_index}.
        :param position: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#position CleanRoomAsset#position}.
        :param type_interval_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_interval_type CleanRoomAsset#type_interval_type}.
        :param type_json: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_json CleanRoomAsset#type_json}.
        :param type_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_name CleanRoomAsset#type_name}.
        :param type_precision: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_precision CleanRoomAsset#type_precision}.
        :param type_scale: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_scale CleanRoomAsset#type_scale}.
        :param type_text: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_text CleanRoomAsset#type_text}.
        '''
        if isinstance(mask, dict):
            mask = CleanRoomAssetForeignTableColumnsMask(**mask)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed6249de755526863406e69bf2fddedcfd16357430ef42eed6385eeed567649b)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#comment CleanRoomAsset#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mask(self) -> typing.Optional["CleanRoomAssetForeignTableColumnsMask"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#mask CleanRoomAsset#mask}.'''
        result = self._values.get("mask")
        return typing.cast(typing.Optional["CleanRoomAssetForeignTableColumnsMask"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#name CleanRoomAsset#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nullable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#nullable CleanRoomAsset#nullable}.'''
        result = self._values.get("nullable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def partition_index(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#partition_index CleanRoomAsset#partition_index}.'''
        result = self._values.get("partition_index")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def position(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#position CleanRoomAsset#position}.'''
        result = self._values.get("position")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_interval_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_interval_type CleanRoomAsset#type_interval_type}.'''
        result = self._values.get("type_interval_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_json CleanRoomAsset#type_json}.'''
        result = self._values.get("type_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_name CleanRoomAsset#type_name}.'''
        result = self._values.get("type_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_precision(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_precision CleanRoomAsset#type_precision}.'''
        result = self._values.get("type_precision")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_scale(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_scale CleanRoomAsset#type_scale}.'''
        result = self._values.get("type_scale")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_text(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_text CleanRoomAsset#type_text}.'''
        result = self._values.get("type_text")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CleanRoomAssetForeignTableColumns(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CleanRoomAssetForeignTableColumnsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetForeignTableColumnsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__051c261004838651c23bafdfbb399fdb5832535a560f256a9a821a6a1d9734b2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "CleanRoomAssetForeignTableColumnsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8754c7104586cd98587cc995f55f87519dcc26a5bd2ea0fe9f9aaa88dc73aebe)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CleanRoomAssetForeignTableColumnsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d2bac3381db4598a945165e3b75e03feef890ea69043d1f879f17dc2e885ff4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3af4f4b31304b738a23be45367c24719e60f033df9bdd2e1d425bf9743e1a6cd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7897dc44560a5933b80bf5322701a0f99c436c69968f9210fce58259d9134468)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomAssetForeignTableColumns]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomAssetForeignTableColumns]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomAssetForeignTableColumns]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46c5accb5506659bf24fdb0bab9f88440c3e489ce8ca796b5abf1dd17a45d4e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetForeignTableColumnsMask",
    jsii_struct_bases=[],
    name_mapping={
        "function_name": "functionName",
        "using_column_names": "usingColumnNames",
    },
)
class CleanRoomAssetForeignTableColumnsMask:
    def __init__(
        self,
        *,
        function_name: typing.Optional[builtins.str] = None,
        using_column_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#function_name CleanRoomAsset#function_name}.
        :param using_column_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#using_column_names CleanRoomAsset#using_column_names}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35931af06f315413a0f351425b3632040b109ba6d71fc37d6b8ca1c551659852)
            check_type(argname="argument function_name", value=function_name, expected_type=type_hints["function_name"])
            check_type(argname="argument using_column_names", value=using_column_names, expected_type=type_hints["using_column_names"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if function_name is not None:
            self._values["function_name"] = function_name
        if using_column_names is not None:
            self._values["using_column_names"] = using_column_names

    @builtins.property
    def function_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#function_name CleanRoomAsset#function_name}.'''
        result = self._values.get("function_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def using_column_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#using_column_names CleanRoomAsset#using_column_names}.'''
        result = self._values.get("using_column_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CleanRoomAssetForeignTableColumnsMask(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CleanRoomAssetForeignTableColumnsMaskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetForeignTableColumnsMaskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c72f55d9a3831575f288b4e16b25aafc2cacff30006a567de919a8d5ced919b7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f8173fa900fddb905c6ea8c6951cb328eddb18e57451d00e8cc6165b50578759)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "functionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usingColumnNames")
    def using_column_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "usingColumnNames"))

    @using_column_names.setter
    def using_column_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1846a3ca9784127c4e50578368cc2a810b791c2405a337557533599c7a5d12bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usingColumnNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetForeignTableColumnsMask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetForeignTableColumnsMask]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetForeignTableColumnsMask]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57c03eff7afc7eb4fab8bb49f688a23f584307da75ed0c72977af1666e3ed6dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CleanRoomAssetForeignTableColumnsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetForeignTableColumnsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7d1a6e826d4956dd1d54606b307062012df737f9ea2d452d155ed58cf2364ee4)
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
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#function_name CleanRoomAsset#function_name}.
        :param using_column_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#using_column_names CleanRoomAsset#using_column_names}.
        '''
        value = CleanRoomAssetForeignTableColumnsMask(
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
    def mask(self) -> CleanRoomAssetForeignTableColumnsMaskOutputReference:
        return typing.cast(CleanRoomAssetForeignTableColumnsMaskOutputReference, jsii.get(self, "mask"))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="maskInput")
    def mask_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetForeignTableColumnsMask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetForeignTableColumnsMask]], jsii.get(self, "maskInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__5d1d88718e7e459fbc26ccf21e8c0846b57f0887953823aa3e66eefd60bb1704)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b2f95cffc9ff8faf8140c43dd3cdcfb6b58971200e5355c28c6cd4f3304136f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e63afe5192871846cb78be5ede53fd6ffa30124f106dbf3d52b84b731a530313)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nullable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="partitionIndex")
    def partition_index(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "partitionIndex"))

    @partition_index.setter
    def partition_index(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8609894cd185fca41d5ff1a5fa4f744b148b865a920f81cea232580731918860)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "partitionIndex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="position")
    def position(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "position"))

    @position.setter
    def position(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffee91ee1a51ffdcab1b92019f01c143878152deac6ac1f2982612cc9c9c42d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "position", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeIntervalType")
    def type_interval_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeIntervalType"))

    @type_interval_type.setter
    def type_interval_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c36e5c379f5e13082a7d41da6b1fd2e9d7a77dfd351995ca3ab6fa2f214c27a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeIntervalType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeJson")
    def type_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeJson"))

    @type_json.setter
    def type_json(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f37155d19da543b5e7889ce9f8694188d4f714ef240c2e1723e4a1baa3535910)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeJson", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeName")
    def type_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeName"))

    @type_name.setter
    def type_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__259e380f08bf3802f21c184bcc25d867c96231d8d0cf17ee0af504216dce690a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typePrecision")
    def type_precision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "typePrecision"))

    @type_precision.setter
    def type_precision(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e1f32da7bd9c085da368e2366c148cfed90b2342e7bfb7f123fa1bffd60ffb8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typePrecision", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeScale")
    def type_scale(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "typeScale"))

    @type_scale.setter
    def type_scale(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5f6bbebc7f743573421bb528ff55cd1213dead46203fd3c664f8c38d1aa687c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeScale", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeText")
    def type_text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeText"))

    @type_text.setter
    def type_text(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79f6bb8af996bb1d3e1494674a4b40d8f6eec1f77ec25e90a235fa20172032a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeText", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CleanRoomAssetForeignTableColumns]:
        return typing.cast(typing.Optional[CleanRoomAssetForeignTableColumns], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CleanRoomAssetForeignTableColumns],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cfccc97da60de91ee238c3232f8029816707aad8e9d306809b32654c84dcfd1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetForeignTableLocalDetails",
    jsii_struct_bases=[],
    name_mapping={"local_name": "localName"},
)
class CleanRoomAssetForeignTableLocalDetails:
    def __init__(self, *, local_name: builtins.str) -> None:
        '''
        :param local_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#local_name CleanRoomAsset#local_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fed4eee928d0d939442aa00c785338137976b2f4999973de8280d67abc2cd10a)
            check_type(argname="argument local_name", value=local_name, expected_type=type_hints["local_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "local_name": local_name,
        }

    @builtins.property
    def local_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#local_name CleanRoomAsset#local_name}.'''
        result = self._values.get("local_name")
        assert result is not None, "Required property 'local_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CleanRoomAssetForeignTableLocalDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CleanRoomAssetForeignTableLocalDetailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetForeignTableLocalDetailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b77986b8e25cb65efbe626a551c8ef09c31c7e1cb9e7e498b5b3cb4ead08ad6d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a1bbc43887bcc7bbd26b945d7a9f0e40d108c6ccbde4feb94b83c30f04aa2c62)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "localName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetForeignTableLocalDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetForeignTableLocalDetails]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetForeignTableLocalDetails]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2054334057ac2d5de285951ff9399a78808843dd2aab0b64d8667c84cfab36f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CleanRoomAssetForeignTableOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetForeignTableOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__548d8be54724a594642aa9c0a27e6b4b0cde1ffbabd0a44d5cbbae51b34bf1fb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="columns")
    def columns(self) -> CleanRoomAssetForeignTableColumnsList:
        return typing.cast(CleanRoomAssetForeignTableColumnsList, jsii.get(self, "columns"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetForeignTable]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetForeignTable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetForeignTable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06c81631f675671e2f05a61ad59c15710d984e7571be665a9c731b568e1ef035)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetNotebook",
    jsii_struct_bases=[],
    name_mapping={
        "notebook_content": "notebookContent",
        "runner_collaborator_aliases": "runnerCollaboratorAliases",
    },
)
class CleanRoomAssetNotebook:
    def __init__(
        self,
        *,
        notebook_content: builtins.str,
        runner_collaborator_aliases: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param notebook_content: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#notebook_content CleanRoomAsset#notebook_content}.
        :param runner_collaborator_aliases: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#runner_collaborator_aliases CleanRoomAsset#runner_collaborator_aliases}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c1a0702eda0aa2ffc2bdc17d57cd65e8511a6773568311654ffcf2c22546689)
            check_type(argname="argument notebook_content", value=notebook_content, expected_type=type_hints["notebook_content"])
            check_type(argname="argument runner_collaborator_aliases", value=runner_collaborator_aliases, expected_type=type_hints["runner_collaborator_aliases"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "notebook_content": notebook_content,
        }
        if runner_collaborator_aliases is not None:
            self._values["runner_collaborator_aliases"] = runner_collaborator_aliases

    @builtins.property
    def notebook_content(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#notebook_content CleanRoomAsset#notebook_content}.'''
        result = self._values.get("notebook_content")
        assert result is not None, "Required property 'notebook_content' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def runner_collaborator_aliases(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#runner_collaborator_aliases CleanRoomAsset#runner_collaborator_aliases}.'''
        result = self._values.get("runner_collaborator_aliases")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CleanRoomAssetNotebook(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CleanRoomAssetNotebookOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetNotebookOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__efeaf395667bcb81bdd66eb60be161ff74c58ec12fcfd39029efc9fb0adab6f1)
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
    def reviews(self) -> "CleanRoomAssetNotebookReviewsList":
        return typing.cast("CleanRoomAssetNotebookReviewsList", jsii.get(self, "reviews"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__ee032ca4a368db29047093419004727b0c2c1a60aba79e2c9cac88d024dbd9f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notebookContent", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runnerCollaboratorAliases")
    def runner_collaborator_aliases(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "runnerCollaboratorAliases"))

    @runner_collaborator_aliases.setter
    def runner_collaborator_aliases(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__231b610c679ccbe0efeff30c058425ea0168166a150497fbebd757e57079483e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runnerCollaboratorAliases", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetNotebook]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetNotebook]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetNotebook]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1922a0b9eed75e3dac7a595bca4514893fe9b52995dbf7c712b19130ba49bd0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetNotebookReviews",
    jsii_struct_bases=[],
    name_mapping={
        "comment": "comment",
        "created_at_millis": "createdAtMillis",
        "reviewer_collaborator_alias": "reviewerCollaboratorAlias",
        "review_state": "reviewState",
        "review_sub_reason": "reviewSubReason",
    },
)
class CleanRoomAssetNotebookReviews:
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
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#comment CleanRoomAsset#comment}.
        :param created_at_millis: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#created_at_millis CleanRoomAsset#created_at_millis}.
        :param reviewer_collaborator_alias: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#reviewer_collaborator_alias CleanRoomAsset#reviewer_collaborator_alias}.
        :param review_state: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#review_state CleanRoomAsset#review_state}.
        :param review_sub_reason: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#review_sub_reason CleanRoomAsset#review_sub_reason}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76dc6c113c282e2742c0cbf6569353a73ef0338bded0c45ba7dab3d4a3257284)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#comment CleanRoomAsset#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def created_at_millis(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#created_at_millis CleanRoomAsset#created_at_millis}.'''
        result = self._values.get("created_at_millis")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def reviewer_collaborator_alias(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#reviewer_collaborator_alias CleanRoomAsset#reviewer_collaborator_alias}.'''
        result = self._values.get("reviewer_collaborator_alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def review_state(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#review_state CleanRoomAsset#review_state}.'''
        result = self._values.get("review_state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def review_sub_reason(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#review_sub_reason CleanRoomAsset#review_sub_reason}.'''
        result = self._values.get("review_sub_reason")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CleanRoomAssetNotebookReviews(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CleanRoomAssetNotebookReviewsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetNotebookReviewsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__df589fc19619f3873adf79f3e9285c31e416eeb08f4ef512b22dda40ced8ce21)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "CleanRoomAssetNotebookReviewsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c72687f315fa2f096ba5256feb529bdfa8270c4ca0bec875dbd030ad54adfa0)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CleanRoomAssetNotebookReviewsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5d6e695585b637bdade16608035a176a86f0eea8e02e0bc5d7f83c721fd0e20)
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
            type_hints = typing.get_type_hints(_typecheckingstub__db14770f14d505a9ab920f6cb956eb3fd21714205c90a50983cd2f2699bbfe2c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5549a1d0bb078a72459ee9656ea0c4a24ff2cf21e0298e999227e5a41eb9d978)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomAssetNotebookReviews]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomAssetNotebookReviews]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomAssetNotebookReviews]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7df44d82b18f45154191dc01414a67f0df7dda0777e7aaef1b6ce894969c4a1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CleanRoomAssetNotebookReviewsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetNotebookReviewsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__352e25dc381fef339f0aa33ec989aa5488a6e179eb17c733077956379723d2a8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__198ed7eba43585fc18ee814eff56941def60cece35b9f24731b67d553a134a2b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="createdAtMillis")
    def created_at_millis(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "createdAtMillis"))

    @created_at_millis.setter
    def created_at_millis(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d80d80d9b720cb17dbbfa9671f4019de23c4d0f080092143aa026108a105127)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdAtMillis", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="reviewerCollaboratorAlias")
    def reviewer_collaborator_alias(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reviewerCollaboratorAlias"))

    @reviewer_collaborator_alias.setter
    def reviewer_collaborator_alias(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02e2d5e1a9d3a894967f7b21f2f59cdf9687a31a9749ccaa9cd380a6ac168356)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reviewerCollaboratorAlias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="reviewState")
    def review_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reviewState"))

    @review_state.setter
    def review_state(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6bdd58fcc3fdd5fe76b297352677f289744c6faa49239f673d92f384e0e5502)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reviewState", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="reviewSubReason")
    def review_sub_reason(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reviewSubReason"))

    @review_sub_reason.setter
    def review_sub_reason(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a7b0bf1a453c937537bc106875e96dbfcba7b75e4da37c36bc068706b3c161f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reviewSubReason", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CleanRoomAssetNotebookReviews]:
        return typing.cast(typing.Optional[CleanRoomAssetNotebookReviews], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CleanRoomAssetNotebookReviews],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5a020a4625c80229c9bad2c5676f2341577c1e563566a0b7522167745846c7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetTable",
    jsii_struct_bases=[],
    name_mapping={},
)
class CleanRoomAssetTable:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CleanRoomAssetTable(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetTableColumns",
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
class CleanRoomAssetTableColumns:
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        mask: typing.Optional[typing.Union["CleanRoomAssetTableColumnsMask", typing.Dict[builtins.str, typing.Any]]] = None,
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
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#comment CleanRoomAsset#comment}.
        :param mask: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#mask CleanRoomAsset#mask}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#name CleanRoomAsset#name}.
        :param nullable: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#nullable CleanRoomAsset#nullable}.
        :param partition_index: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#partition_index CleanRoomAsset#partition_index}.
        :param position: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#position CleanRoomAsset#position}.
        :param type_interval_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_interval_type CleanRoomAsset#type_interval_type}.
        :param type_json: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_json CleanRoomAsset#type_json}.
        :param type_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_name CleanRoomAsset#type_name}.
        :param type_precision: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_precision CleanRoomAsset#type_precision}.
        :param type_scale: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_scale CleanRoomAsset#type_scale}.
        :param type_text: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_text CleanRoomAsset#type_text}.
        '''
        if isinstance(mask, dict):
            mask = CleanRoomAssetTableColumnsMask(**mask)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__330b39ccafa36ba273af82f7fce7721135a0aee7757bcccd6e1190f887ceac1b)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#comment CleanRoomAsset#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mask(self) -> typing.Optional["CleanRoomAssetTableColumnsMask"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#mask CleanRoomAsset#mask}.'''
        result = self._values.get("mask")
        return typing.cast(typing.Optional["CleanRoomAssetTableColumnsMask"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#name CleanRoomAsset#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nullable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#nullable CleanRoomAsset#nullable}.'''
        result = self._values.get("nullable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def partition_index(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#partition_index CleanRoomAsset#partition_index}.'''
        result = self._values.get("partition_index")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def position(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#position CleanRoomAsset#position}.'''
        result = self._values.get("position")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_interval_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_interval_type CleanRoomAsset#type_interval_type}.'''
        result = self._values.get("type_interval_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_json CleanRoomAsset#type_json}.'''
        result = self._values.get("type_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_name CleanRoomAsset#type_name}.'''
        result = self._values.get("type_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_precision(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_precision CleanRoomAsset#type_precision}.'''
        result = self._values.get("type_precision")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_scale(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_scale CleanRoomAsset#type_scale}.'''
        result = self._values.get("type_scale")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_text(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_text CleanRoomAsset#type_text}.'''
        result = self._values.get("type_text")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CleanRoomAssetTableColumns(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CleanRoomAssetTableColumnsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetTableColumnsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7ed1bf7c9186bd4e172058814a0bbbd79ab5c62ed456d6f51590c4e22194d081)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "CleanRoomAssetTableColumnsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a8777303d754cdcbb8de81a02cd9b1288ffd3580233a8f2919582e5a2710ef9)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CleanRoomAssetTableColumnsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8f7a615305076966c24a4911d945f90dc317e8155cdd2900e4280fdb422746b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6f2f5d436f9a8866fce0bf50f7fff2cff793b216177dcc8368ad56390f36670d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__039d8fd8b447e1ccd06c58f13f8e630a9cd662e44e7199895d34cdb86bb3991e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomAssetTableColumns]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomAssetTableColumns]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomAssetTableColumns]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b827e40fade76c0b742e8eebd7fd0dc088b584fdc44272f5fe750998cc4e130)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetTableColumnsMask",
    jsii_struct_bases=[],
    name_mapping={
        "function_name": "functionName",
        "using_column_names": "usingColumnNames",
    },
)
class CleanRoomAssetTableColumnsMask:
    def __init__(
        self,
        *,
        function_name: typing.Optional[builtins.str] = None,
        using_column_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#function_name CleanRoomAsset#function_name}.
        :param using_column_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#using_column_names CleanRoomAsset#using_column_names}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3315efe05f43b9bd5080322be8ed55bc79b606a644b617497d6fdd9cfc763577)
            check_type(argname="argument function_name", value=function_name, expected_type=type_hints["function_name"])
            check_type(argname="argument using_column_names", value=using_column_names, expected_type=type_hints["using_column_names"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if function_name is not None:
            self._values["function_name"] = function_name
        if using_column_names is not None:
            self._values["using_column_names"] = using_column_names

    @builtins.property
    def function_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#function_name CleanRoomAsset#function_name}.'''
        result = self._values.get("function_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def using_column_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#using_column_names CleanRoomAsset#using_column_names}.'''
        result = self._values.get("using_column_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CleanRoomAssetTableColumnsMask(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CleanRoomAssetTableColumnsMaskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetTableColumnsMaskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__49453691ce974e5d1162db50ba4b8bd7806e524630f1f9d2e0fdddabad2401a6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d3b08fd640dd367ac9f4d0595d826b04bd8adb9b3c09937453518a9746bef324)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "functionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usingColumnNames")
    def using_column_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "usingColumnNames"))

    @using_column_names.setter
    def using_column_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61d66edaec750792f3b7d09686ac43b6dd891ecc63c7d5d1a81ffc81d0894cc8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usingColumnNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetTableColumnsMask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetTableColumnsMask]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetTableColumnsMask]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2fb267ce8c89d97d72eb4dd791679f81043a0a983bb76ed180299c5c4da5e13)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CleanRoomAssetTableColumnsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetTableColumnsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7d1b0697f9a9ac3a356f80c0351477738910df1d233beca9ea4cf182c90afba9)
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
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#function_name CleanRoomAsset#function_name}.
        :param using_column_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#using_column_names CleanRoomAsset#using_column_names}.
        '''
        value = CleanRoomAssetTableColumnsMask(
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
    def mask(self) -> CleanRoomAssetTableColumnsMaskOutputReference:
        return typing.cast(CleanRoomAssetTableColumnsMaskOutputReference, jsii.get(self, "mask"))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="maskInput")
    def mask_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetTableColumnsMask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetTableColumnsMask]], jsii.get(self, "maskInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__f8b2ab9e48ced85375ff7ca4238cee2d063167e41a0ec20566f49126573332ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54b6760c1505508c081d4488136c4e158dcdc5864fe9063f6e4dd9f3a701c745)
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
            type_hints = typing.get_type_hints(_typecheckingstub__461d0cb4e22b31f7c4c55513f7215d8bcba5cd7d2c8f64fcf5f1ae385d9fe5e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nullable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="partitionIndex")
    def partition_index(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "partitionIndex"))

    @partition_index.setter
    def partition_index(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a35f209c5dd84a915838665c22da049d33e7db50ff5347415991cfcaf8752e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "partitionIndex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="position")
    def position(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "position"))

    @position.setter
    def position(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05f31f071630a608b5b7e2f1eefdb222528004559064c66ab8e8c73f7fd935e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "position", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeIntervalType")
    def type_interval_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeIntervalType"))

    @type_interval_type.setter
    def type_interval_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__016259e6282dcf75a27e67257714c9a35a950b71017554d56162d715d176fc1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeIntervalType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeJson")
    def type_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeJson"))

    @type_json.setter
    def type_json(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e228eb334e233fa284ed4cb921767e991c9b1d8d1f874053ec5282d908720b30)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeJson", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeName")
    def type_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeName"))

    @type_name.setter
    def type_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87def45ed2eb0841ef8d01be4a296f5ffc38a4888a8e086f99700e734e2d1da7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typePrecision")
    def type_precision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "typePrecision"))

    @type_precision.setter
    def type_precision(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc3745c5b6b561f2ed5ff40acfe173162602af714b137472987ad2588ac4b953)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typePrecision", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeScale")
    def type_scale(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "typeScale"))

    @type_scale.setter
    def type_scale(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f970dc6e5cea7229000e941a4060a4f32677dab4298428f69acac19e1301af60)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeScale", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeText")
    def type_text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeText"))

    @type_text.setter
    def type_text(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c522ad4005f10014cf029d835c958a6d486d23bd4db428c28e50168dbbfe98b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeText", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CleanRoomAssetTableColumns]:
        return typing.cast(typing.Optional[CleanRoomAssetTableColumns], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CleanRoomAssetTableColumns],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c676b7ccd024da2ede8f3a2afa39f1f38fdbc9c4675e1968e3cf50e7c40d75d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetTableLocalDetails",
    jsii_struct_bases=[],
    name_mapping={"local_name": "localName", "partitions": "partitions"},
)
class CleanRoomAssetTableLocalDetails:
    def __init__(
        self,
        *,
        local_name: builtins.str,
        partitions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CleanRoomAssetTableLocalDetailsPartitions", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param local_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#local_name CleanRoomAsset#local_name}.
        :param partitions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#partitions CleanRoomAsset#partitions}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4739882ea5c921acc89f5fa1ed73ab9a303c28240beb3fac5c8a4223744d524b)
            check_type(argname="argument local_name", value=local_name, expected_type=type_hints["local_name"])
            check_type(argname="argument partitions", value=partitions, expected_type=type_hints["partitions"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "local_name": local_name,
        }
        if partitions is not None:
            self._values["partitions"] = partitions

    @builtins.property
    def local_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#local_name CleanRoomAsset#local_name}.'''
        result = self._values.get("local_name")
        assert result is not None, "Required property 'local_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def partitions(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CleanRoomAssetTableLocalDetailsPartitions"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#partitions CleanRoomAsset#partitions}.'''
        result = self._values.get("partitions")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CleanRoomAssetTableLocalDetailsPartitions"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CleanRoomAssetTableLocalDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CleanRoomAssetTableLocalDetailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetTableLocalDetailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a00347ef51cecd12f864ed6b49a958c54aeb7d5426175d41fdacd715be17bc68)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putPartitions")
    def put_partitions(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CleanRoomAssetTableLocalDetailsPartitions", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e53e39e89d3c9b2c029c5fd14a1668d2e24f73717e14fdae332f6b24cfb8ade)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putPartitions", [value]))

    @jsii.member(jsii_name="resetPartitions")
    def reset_partitions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPartitions", []))

    @builtins.property
    @jsii.member(jsii_name="partitions")
    def partitions(self) -> "CleanRoomAssetTableLocalDetailsPartitionsList":
        return typing.cast("CleanRoomAssetTableLocalDetailsPartitionsList", jsii.get(self, "partitions"))

    @builtins.property
    @jsii.member(jsii_name="localNameInput")
    def local_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "localNameInput"))

    @builtins.property
    @jsii.member(jsii_name="partitionsInput")
    def partitions_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CleanRoomAssetTableLocalDetailsPartitions"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CleanRoomAssetTableLocalDetailsPartitions"]]], jsii.get(self, "partitionsInput"))

    @builtins.property
    @jsii.member(jsii_name="localName")
    def local_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "localName"))

    @local_name.setter
    def local_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b462f8bacb796f8efb86a5ee44ca41c72af9d1699e053e1d0d436223a6dc945a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "localName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetTableLocalDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetTableLocalDetails]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetTableLocalDetails]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d04371b6a6fe5f84f57560e35429dc95737153bb09713d15e3c4b181ee572f52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetTableLocalDetailsPartitions",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class CleanRoomAssetTableLocalDetailsPartitions:
    def __init__(
        self,
        *,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CleanRoomAssetTableLocalDetailsPartitionsValue", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#value CleanRoomAsset#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe4586424526874249b6393075b1bd4ff32102e78fe70e232f13717d1ece3c35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CleanRoomAssetTableLocalDetailsPartitionsValue"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#value CleanRoomAsset#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CleanRoomAssetTableLocalDetailsPartitionsValue"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CleanRoomAssetTableLocalDetailsPartitions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CleanRoomAssetTableLocalDetailsPartitionsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetTableLocalDetailsPartitionsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e66bb5227c8c1674a4e48a7dec48d4a3853b12d34065850a1b2e263b517a27f9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "CleanRoomAssetTableLocalDetailsPartitionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28702293b245217fbb6a35b2e58c5d702f2729a496d2e5b21121b93e37229945)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CleanRoomAssetTableLocalDetailsPartitionsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3a715afa76a98acc215bf3264fae94a90495a647eec6a36c4d067b0d81a59c7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fef7d4c6f0ba83b8544fec43fa901db892958d425d63b02fc2dd966ade1aba5b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__83c3d49d5ac145a5a5978553e7ff4ae2c17c7b98f83af7835f9e1e0fd2264d1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomAssetTableLocalDetailsPartitions]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomAssetTableLocalDetailsPartitions]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomAssetTableLocalDetailsPartitions]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f061627bc63005e7eec5ccb075dde6f48ecbf438195192600a9467d0476bdde)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CleanRoomAssetTableLocalDetailsPartitionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetTableLocalDetailsPartitionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__84c9cb305d32cb808b5ab664461e032c9ff385b0f8b49f7c11eb44ca17b58321)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putValue")
    def put_value(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CleanRoomAssetTableLocalDetailsPartitionsValue", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__667727871f18b4a098dc9d1dea45904fa023ffcbd4cb77f18ec4a9444831d1e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putValue", [value]))

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> "CleanRoomAssetTableLocalDetailsPartitionsValueList":
        return typing.cast("CleanRoomAssetTableLocalDetailsPartitionsValueList", jsii.get(self, "value"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CleanRoomAssetTableLocalDetailsPartitionsValue"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CleanRoomAssetTableLocalDetailsPartitionsValue"]]], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetTableLocalDetailsPartitions]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetTableLocalDetailsPartitions]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetTableLocalDetailsPartitions]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52b813a53a2e2f0b570a665d15e2f3291dd53babbb5e447d23d3bf4db61d5a5c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetTableLocalDetailsPartitionsValue",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "op": "op",
        "recipient_property_key": "recipientPropertyKey",
        "value": "value",
    },
)
class CleanRoomAssetTableLocalDetailsPartitionsValue:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        op: typing.Optional[builtins.str] = None,
        recipient_property_key: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#name CleanRoomAsset#name}.
        :param op: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#op CleanRoomAsset#op}.
        :param recipient_property_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#recipient_property_key CleanRoomAsset#recipient_property_key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#value CleanRoomAsset#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac68bd01a977692d8da1f87974397d241ea7585aaa871b526d1501996309a614)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#name CleanRoomAsset#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def op(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#op CleanRoomAsset#op}.'''
        result = self._values.get("op")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def recipient_property_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#recipient_property_key CleanRoomAsset#recipient_property_key}.'''
        result = self._values.get("recipient_property_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#value CleanRoomAsset#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CleanRoomAssetTableLocalDetailsPartitionsValue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CleanRoomAssetTableLocalDetailsPartitionsValueList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetTableLocalDetailsPartitionsValueList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ec40d452005088fb09144f8a2ed106ad1cdcee5549c32c7746552f345794aed8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "CleanRoomAssetTableLocalDetailsPartitionsValueOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86ded69c8aff8f9d295430641a1a66c4b56a46d16bbdb5132dc07553d1f29ff3)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CleanRoomAssetTableLocalDetailsPartitionsValueOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f73f016e25a4addc910272beb769f0906a04e2a2067441b0c6c9dfbb8e15f6e1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__51b639395a20347f835fca36881ac632e1b34dc0968a2c7610d34cc543bbf220)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9f1cb0a0bb9badeb26c32c460ad364213870d9e9f2d3ed7d5baf1f1b63159466)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomAssetTableLocalDetailsPartitionsValue]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomAssetTableLocalDetailsPartitionsValue]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomAssetTableLocalDetailsPartitionsValue]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5add6dbeece996b02ff7ed8f4f024e02fb04978b0c5a01f173aeb61c2902a66e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CleanRoomAssetTableLocalDetailsPartitionsValueOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetTableLocalDetailsPartitionsValueOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b1508e5ec934b14d4fc30c1933795865e7d9d48653eff6cfeca7ccdfb44f9e48)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cfbc7439d22cc3eabb44c8dd188253b8e63b5eab6d44ba063ff6e3974e9ddb20)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="op")
    def op(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "op"))

    @op.setter
    def op(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99aa2483f40902264142faf81d51513fff47c83ad0815d657ce5ead4d5104929)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "op", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="recipientPropertyKey")
    def recipient_property_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "recipientPropertyKey"))

    @recipient_property_key.setter
    def recipient_property_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__abf81c090026928669194a0af9c9951d8ef492e40addd3e5d082c4d643ba6f4d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "recipientPropertyKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fadfbe0a654608d50d51749d4679501ca4b5ed417731d567bf6b0f2c59214c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetTableLocalDetailsPartitionsValue]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetTableLocalDetailsPartitionsValue]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetTableLocalDetailsPartitionsValue]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6590ef57e26928d4f76074e053f71479de1baa05f8faa4fe9d56a3458344806)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CleanRoomAssetTableOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetTableOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__52f6c147007e842416e53e2b86af4da9f050462b722cf44166b115d2069d28da)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="columns")
    def columns(self) -> CleanRoomAssetTableColumnsList:
        return typing.cast(CleanRoomAssetTableColumnsList, jsii.get(self, "columns"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetTable]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetTable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetTable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81b11b165bf40d47c04a91cb5385dae80ec06dcd5f5184cb6e8627cb4fd59068)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetView",
    jsii_struct_bases=[],
    name_mapping={},
)
class CleanRoomAssetView:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CleanRoomAssetView(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetViewColumns",
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
class CleanRoomAssetViewColumns:
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        mask: typing.Optional[typing.Union["CleanRoomAssetViewColumnsMask", typing.Dict[builtins.str, typing.Any]]] = None,
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
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#comment CleanRoomAsset#comment}.
        :param mask: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#mask CleanRoomAsset#mask}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#name CleanRoomAsset#name}.
        :param nullable: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#nullable CleanRoomAsset#nullable}.
        :param partition_index: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#partition_index CleanRoomAsset#partition_index}.
        :param position: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#position CleanRoomAsset#position}.
        :param type_interval_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_interval_type CleanRoomAsset#type_interval_type}.
        :param type_json: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_json CleanRoomAsset#type_json}.
        :param type_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_name CleanRoomAsset#type_name}.
        :param type_precision: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_precision CleanRoomAsset#type_precision}.
        :param type_scale: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_scale CleanRoomAsset#type_scale}.
        :param type_text: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_text CleanRoomAsset#type_text}.
        '''
        if isinstance(mask, dict):
            mask = CleanRoomAssetViewColumnsMask(**mask)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d16925fbb01d8a995647387395c00b9c2df27678c07e1e939607ae7d1e38539)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#comment CleanRoomAsset#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mask(self) -> typing.Optional["CleanRoomAssetViewColumnsMask"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#mask CleanRoomAsset#mask}.'''
        result = self._values.get("mask")
        return typing.cast(typing.Optional["CleanRoomAssetViewColumnsMask"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#name CleanRoomAsset#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nullable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#nullable CleanRoomAsset#nullable}.'''
        result = self._values.get("nullable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def partition_index(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#partition_index CleanRoomAsset#partition_index}.'''
        result = self._values.get("partition_index")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def position(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#position CleanRoomAsset#position}.'''
        result = self._values.get("position")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_interval_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_interval_type CleanRoomAsset#type_interval_type}.'''
        result = self._values.get("type_interval_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_json CleanRoomAsset#type_json}.'''
        result = self._values.get("type_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_name CleanRoomAsset#type_name}.'''
        result = self._values.get("type_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_precision(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_precision CleanRoomAsset#type_precision}.'''
        result = self._values.get("type_precision")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_scale(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_scale CleanRoomAsset#type_scale}.'''
        result = self._values.get("type_scale")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type_text(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#type_text CleanRoomAsset#type_text}.'''
        result = self._values.get("type_text")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CleanRoomAssetViewColumns(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CleanRoomAssetViewColumnsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetViewColumnsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__63e532ee44287ba478bdd5e29da577bdeb3ceffaf34ec8a3236e8cb7dae36905)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "CleanRoomAssetViewColumnsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec8ba41b72b085a0a18d18fd120f3e123e38fd9022d818b7d82e697f9052982a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CleanRoomAssetViewColumnsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__356f030415058a84236897d32f9db58da9eb4a73438e48687e255fe3dcaddab1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__453d9c07b6f05e6d4dbf415475ea72f39b3a36003ef75532b9cfa1858f2f8cd5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__579a89d5217988a46c29f908ccab645043d272145df3131a7c1f50508896ab20)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomAssetViewColumns]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomAssetViewColumns]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomAssetViewColumns]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__696d07f168530eb04bbf79c3cf59c1913fad60e382d36c6ccd65f2fc4856f713)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetViewColumnsMask",
    jsii_struct_bases=[],
    name_mapping={
        "function_name": "functionName",
        "using_column_names": "usingColumnNames",
    },
)
class CleanRoomAssetViewColumnsMask:
    def __init__(
        self,
        *,
        function_name: typing.Optional[builtins.str] = None,
        using_column_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#function_name CleanRoomAsset#function_name}.
        :param using_column_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#using_column_names CleanRoomAsset#using_column_names}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b06202038eee6dbeba0f5d47a292ae2152e54defd151b6b31d05cd9927ee3853)
            check_type(argname="argument function_name", value=function_name, expected_type=type_hints["function_name"])
            check_type(argname="argument using_column_names", value=using_column_names, expected_type=type_hints["using_column_names"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if function_name is not None:
            self._values["function_name"] = function_name
        if using_column_names is not None:
            self._values["using_column_names"] = using_column_names

    @builtins.property
    def function_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#function_name CleanRoomAsset#function_name}.'''
        result = self._values.get("function_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def using_column_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#using_column_names CleanRoomAsset#using_column_names}.'''
        result = self._values.get("using_column_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CleanRoomAssetViewColumnsMask(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CleanRoomAssetViewColumnsMaskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetViewColumnsMaskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c216ac0ec510c9433b2cd3f9da321f1f8f9da2e01b86d096c91b5ba4d3a35ac0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__95ab3e754db52dc3e1ae759c31aa9330d9cce6f2ff940fa4cae0c54f03df8715)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "functionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usingColumnNames")
    def using_column_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "usingColumnNames"))

    @using_column_names.setter
    def using_column_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a1899674320a0bd35b5eced681b16808cd0919f02ddfbf1b992205cab867aa6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usingColumnNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetViewColumnsMask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetViewColumnsMask]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetViewColumnsMask]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__320ea75a1abadca5baa2dd5b1b3655f804a4f66a019829aa7122c43f109d932d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CleanRoomAssetViewColumnsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetViewColumnsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b57e735cf84d48aa2722ccb28ec7a07d139f4abbfcc925638d1110ad50ffaec1)
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
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#function_name CleanRoomAsset#function_name}.
        :param using_column_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#using_column_names CleanRoomAsset#using_column_names}.
        '''
        value = CleanRoomAssetViewColumnsMask(
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
    def mask(self) -> CleanRoomAssetViewColumnsMaskOutputReference:
        return typing.cast(CleanRoomAssetViewColumnsMaskOutputReference, jsii.get(self, "mask"))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="maskInput")
    def mask_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetViewColumnsMask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetViewColumnsMask]], jsii.get(self, "maskInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__41a26465ef8ebaf2c5cb08d767fb1db9bdf11c73be6fca93619f6ae0f43dc1fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d55021979e8e669bf6534495cab0269f2260e8e71661b2abc5ef8a3b939b7f6e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__519d7809a8687f0c4419435931008a9217f51cc590eda9f89bf494221ddeea31)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nullable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="partitionIndex")
    def partition_index(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "partitionIndex"))

    @partition_index.setter
    def partition_index(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3b7cc3b03dd64a303f2408f414b851cc2774af5ce20f208e96e9e538c116712)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "partitionIndex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="position")
    def position(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "position"))

    @position.setter
    def position(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86cef1844c293cd8ac5389a3c832da2f5f4e22f3782f08b9f8d0e8f5707fff89)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "position", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeIntervalType")
    def type_interval_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeIntervalType"))

    @type_interval_type.setter
    def type_interval_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0a98d1beacd44615cfa0cfcea747ad93553d812ea03d9a3fd9ae6216e94fea7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeIntervalType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeJson")
    def type_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeJson"))

    @type_json.setter
    def type_json(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__001ce2097943c965e197f14907feb5055fb81230cfb671d6c4006a29ad01d988)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeJson", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeName")
    def type_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeName"))

    @type_name.setter
    def type_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da826697ed229e185d7b3e35b612ef02bea7e424a4df70d5022f378cac70d20c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typePrecision")
    def type_precision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "typePrecision"))

    @type_precision.setter
    def type_precision(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3fc4576304b1330bbdd68b96738289c26ed4c67a7c4c4929f68f2fe746ca2bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typePrecision", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeScale")
    def type_scale(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "typeScale"))

    @type_scale.setter
    def type_scale(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__853a58c2dbf4eb97d8ebae8850967c71860cfcc7915f533ec7107dd019a35499)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeScale", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeText")
    def type_text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeText"))

    @type_text.setter
    def type_text(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af9dc952ae98dd0aa68ec67edc5ec36acd38ef3696731cad20f870f90d0d0f7f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeText", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CleanRoomAssetViewColumns]:
        return typing.cast(typing.Optional[CleanRoomAssetViewColumns], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[CleanRoomAssetViewColumns]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48c074dbf640776727fdc41b6e7355d23e4778a3b215db2e0c96d44df3e93cbc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetViewLocalDetails",
    jsii_struct_bases=[],
    name_mapping={"local_name": "localName"},
)
class CleanRoomAssetViewLocalDetails:
    def __init__(self, *, local_name: builtins.str) -> None:
        '''
        :param local_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#local_name CleanRoomAsset#local_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e2112e7f9a7b1e6bdf34d479b95cdf9e2cc7ba8b2e448f1f00c5bcd511a982a)
            check_type(argname="argument local_name", value=local_name, expected_type=type_hints["local_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "local_name": local_name,
        }

    @builtins.property
    def local_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#local_name CleanRoomAsset#local_name}.'''
        result = self._values.get("local_name")
        assert result is not None, "Required property 'local_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CleanRoomAssetViewLocalDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CleanRoomAssetViewLocalDetailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetViewLocalDetailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__874ced66a77395144cea324224e941d89ac20ab73ba0343c8eb6253717686ad3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2665edd86c7cfd42e515fa4d7b7fa9f8dd2b74ecaaf964c95d06f1666c11a5f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "localName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetViewLocalDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetViewLocalDetails]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetViewLocalDetails]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6b0b366248c6c889e209115cc710f72df7bb917516cf7ac0e22bc2a5748cc13)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CleanRoomAssetViewOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetViewOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ccac5fd3fae473caa0803c1002e3bfd5812bc1e59adae1332bd9f2e50e355b7d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="columns")
    def columns(self) -> CleanRoomAssetViewColumnsList:
        return typing.cast(CleanRoomAssetViewColumnsList, jsii.get(self, "columns"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetView]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetView]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetView]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2be84331fbac858531de97555a88cadf75e7addaa7004a69770ff5df0bf39a97)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetVolumeLocalDetails",
    jsii_struct_bases=[],
    name_mapping={"local_name": "localName"},
)
class CleanRoomAssetVolumeLocalDetails:
    def __init__(self, *, local_name: builtins.str) -> None:
        '''
        :param local_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#local_name CleanRoomAsset#local_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8886ab3ec8632f59db14f22f8a91da5a1af38c5b7bf71ee693522c728bbc5e21)
            check_type(argname="argument local_name", value=local_name, expected_type=type_hints["local_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "local_name": local_name,
        }

    @builtins.property
    def local_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_room_asset#local_name CleanRoomAsset#local_name}.'''
        result = self._values.get("local_name")
        assert result is not None, "Required property 'local_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CleanRoomAssetVolumeLocalDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CleanRoomAssetVolumeLocalDetailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomAsset.CleanRoomAssetVolumeLocalDetailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3895c88f02508e89aafa3c447bc56c83a286f54b558a471e6922895eda40469b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2685fc303152c181af93c31eb6f374eacced39feb5ff55508bf96169be060ca8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "localName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetVolumeLocalDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetVolumeLocalDetails]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetVolumeLocalDetails]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e11b30eebd428ce55fc272c77254f1588b435e404a791c007e4ff70f8b32750)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "CleanRoomAsset",
    "CleanRoomAssetConfig",
    "CleanRoomAssetForeignTable",
    "CleanRoomAssetForeignTableColumns",
    "CleanRoomAssetForeignTableColumnsList",
    "CleanRoomAssetForeignTableColumnsMask",
    "CleanRoomAssetForeignTableColumnsMaskOutputReference",
    "CleanRoomAssetForeignTableColumnsOutputReference",
    "CleanRoomAssetForeignTableLocalDetails",
    "CleanRoomAssetForeignTableLocalDetailsOutputReference",
    "CleanRoomAssetForeignTableOutputReference",
    "CleanRoomAssetNotebook",
    "CleanRoomAssetNotebookOutputReference",
    "CleanRoomAssetNotebookReviews",
    "CleanRoomAssetNotebookReviewsList",
    "CleanRoomAssetNotebookReviewsOutputReference",
    "CleanRoomAssetTable",
    "CleanRoomAssetTableColumns",
    "CleanRoomAssetTableColumnsList",
    "CleanRoomAssetTableColumnsMask",
    "CleanRoomAssetTableColumnsMaskOutputReference",
    "CleanRoomAssetTableColumnsOutputReference",
    "CleanRoomAssetTableLocalDetails",
    "CleanRoomAssetTableLocalDetailsOutputReference",
    "CleanRoomAssetTableLocalDetailsPartitions",
    "CleanRoomAssetTableLocalDetailsPartitionsList",
    "CleanRoomAssetTableLocalDetailsPartitionsOutputReference",
    "CleanRoomAssetTableLocalDetailsPartitionsValue",
    "CleanRoomAssetTableLocalDetailsPartitionsValueList",
    "CleanRoomAssetTableLocalDetailsPartitionsValueOutputReference",
    "CleanRoomAssetTableOutputReference",
    "CleanRoomAssetView",
    "CleanRoomAssetViewColumns",
    "CleanRoomAssetViewColumnsList",
    "CleanRoomAssetViewColumnsMask",
    "CleanRoomAssetViewColumnsMaskOutputReference",
    "CleanRoomAssetViewColumnsOutputReference",
    "CleanRoomAssetViewLocalDetails",
    "CleanRoomAssetViewLocalDetailsOutputReference",
    "CleanRoomAssetViewOutputReference",
    "CleanRoomAssetVolumeLocalDetails",
    "CleanRoomAssetVolumeLocalDetailsOutputReference",
]

publication.publish()

def _typecheckingstub__a60dd203af0ac0b160476606b8a637056f66664a21ad2f2a5cd5ed4f386a02bc(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    asset_type: builtins.str,
    name: builtins.str,
    clean_room_name: typing.Optional[builtins.str] = None,
    foreign_table: typing.Optional[typing.Union[CleanRoomAssetForeignTable, typing.Dict[builtins.str, typing.Any]]] = None,
    foreign_table_local_details: typing.Optional[typing.Union[CleanRoomAssetForeignTableLocalDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    notebook: typing.Optional[typing.Union[CleanRoomAssetNotebook, typing.Dict[builtins.str, typing.Any]]] = None,
    table: typing.Optional[typing.Union[CleanRoomAssetTable, typing.Dict[builtins.str, typing.Any]]] = None,
    table_local_details: typing.Optional[typing.Union[CleanRoomAssetTableLocalDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    view: typing.Optional[typing.Union[CleanRoomAssetView, typing.Dict[builtins.str, typing.Any]]] = None,
    view_local_details: typing.Optional[typing.Union[CleanRoomAssetViewLocalDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    volume_local_details: typing.Optional[typing.Union[CleanRoomAssetVolumeLocalDetails, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__904173d453faada27d070165187249960ffc95a04c46ecdae501d5a07eec9aed(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60f3096211cc66005d5cad866406b956fa7c3d652ad7066c03085734028f250c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58d7277f4544f9bc875f92f5b26a1c90c3b0e5930db2f33a1baaf2dbf5776688(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8183c0aa2375affc34230a24453351acaa9ac696e177e113083f6c4bc0dd4c1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2dc73f17b04f4290cd965cd282d36ca03139fe9a65900a4a33811c3947cfddbc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2851bb51a227e4dcdff9f524922fa0d78a4bab49b68d0340374abd08e2d17e39(
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
    foreign_table: typing.Optional[typing.Union[CleanRoomAssetForeignTable, typing.Dict[builtins.str, typing.Any]]] = None,
    foreign_table_local_details: typing.Optional[typing.Union[CleanRoomAssetForeignTableLocalDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    notebook: typing.Optional[typing.Union[CleanRoomAssetNotebook, typing.Dict[builtins.str, typing.Any]]] = None,
    table: typing.Optional[typing.Union[CleanRoomAssetTable, typing.Dict[builtins.str, typing.Any]]] = None,
    table_local_details: typing.Optional[typing.Union[CleanRoomAssetTableLocalDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    view: typing.Optional[typing.Union[CleanRoomAssetView, typing.Dict[builtins.str, typing.Any]]] = None,
    view_local_details: typing.Optional[typing.Union[CleanRoomAssetViewLocalDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    volume_local_details: typing.Optional[typing.Union[CleanRoomAssetVolumeLocalDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    workspace_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed6249de755526863406e69bf2fddedcfd16357430ef42eed6385eeed567649b(
    *,
    comment: typing.Optional[builtins.str] = None,
    mask: typing.Optional[typing.Union[CleanRoomAssetForeignTableColumnsMask, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__051c261004838651c23bafdfbb399fdb5832535a560f256a9a821a6a1d9734b2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8754c7104586cd98587cc995f55f87519dcc26a5bd2ea0fe9f9aaa88dc73aebe(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d2bac3381db4598a945165e3b75e03feef890ea69043d1f879f17dc2e885ff4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3af4f4b31304b738a23be45367c24719e60f033df9bdd2e1d425bf9743e1a6cd(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7897dc44560a5933b80bf5322701a0f99c436c69968f9210fce58259d9134468(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46c5accb5506659bf24fdb0bab9f88440c3e489ce8ca796b5abf1dd17a45d4e7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomAssetForeignTableColumns]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35931af06f315413a0f351425b3632040b109ba6d71fc37d6b8ca1c551659852(
    *,
    function_name: typing.Optional[builtins.str] = None,
    using_column_names: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c72f55d9a3831575f288b4e16b25aafc2cacff30006a567de919a8d5ced919b7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8173fa900fddb905c6ea8c6951cb328eddb18e57451d00e8cc6165b50578759(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1846a3ca9784127c4e50578368cc2a810b791c2405a337557533599c7a5d12bd(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57c03eff7afc7eb4fab8bb49f688a23f584307da75ed0c72977af1666e3ed6dc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetForeignTableColumnsMask]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d1a6e826d4956dd1d54606b307062012df737f9ea2d452d155ed58cf2364ee4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d1d88718e7e459fbc26ccf21e8c0846b57f0887953823aa3e66eefd60bb1704(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b2f95cffc9ff8faf8140c43dd3cdcfb6b58971200e5355c28c6cd4f3304136f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e63afe5192871846cb78be5ede53fd6ffa30124f106dbf3d52b84b731a530313(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8609894cd185fca41d5ff1a5fa4f744b148b865a920f81cea232580731918860(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffee91ee1a51ffdcab1b92019f01c143878152deac6ac1f2982612cc9c9c42d8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c36e5c379f5e13082a7d41da6b1fd2e9d7a77dfd351995ca3ab6fa2f214c27a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f37155d19da543b5e7889ce9f8694188d4f714ef240c2e1723e4a1baa3535910(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__259e380f08bf3802f21c184bcc25d867c96231d8d0cf17ee0af504216dce690a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e1f32da7bd9c085da368e2366c148cfed90b2342e7bfb7f123fa1bffd60ffb8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5f6bbebc7f743573421bb528ff55cd1213dead46203fd3c664f8c38d1aa687c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79f6bb8af996bb1d3e1494674a4b40d8f6eec1f77ec25e90a235fa20172032a3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cfccc97da60de91ee238c3232f8029816707aad8e9d306809b32654c84dcfd1(
    value: typing.Optional[CleanRoomAssetForeignTableColumns],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fed4eee928d0d939442aa00c785338137976b2f4999973de8280d67abc2cd10a(
    *,
    local_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b77986b8e25cb65efbe626a551c8ef09c31c7e1cb9e7e498b5b3cb4ead08ad6d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1bbc43887bcc7bbd26b945d7a9f0e40d108c6ccbde4feb94b83c30f04aa2c62(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2054334057ac2d5de285951ff9399a78808843dd2aab0b64d8667c84cfab36f5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetForeignTableLocalDetails]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__548d8be54724a594642aa9c0a27e6b4b0cde1ffbabd0a44d5cbbae51b34bf1fb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06c81631f675671e2f05a61ad59c15710d984e7571be665a9c731b568e1ef035(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetForeignTable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c1a0702eda0aa2ffc2bdc17d57cd65e8511a6773568311654ffcf2c22546689(
    *,
    notebook_content: builtins.str,
    runner_collaborator_aliases: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efeaf395667bcb81bdd66eb60be161ff74c58ec12fcfd39029efc9fb0adab6f1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee032ca4a368db29047093419004727b0c2c1a60aba79e2c9cac88d024dbd9f9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__231b610c679ccbe0efeff30c058425ea0168166a150497fbebd757e57079483e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1922a0b9eed75e3dac7a595bca4514893fe9b52995dbf7c712b19130ba49bd0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetNotebook]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76dc6c113c282e2742c0cbf6569353a73ef0338bded0c45ba7dab3d4a3257284(
    *,
    comment: typing.Optional[builtins.str] = None,
    created_at_millis: typing.Optional[jsii.Number] = None,
    reviewer_collaborator_alias: typing.Optional[builtins.str] = None,
    review_state: typing.Optional[builtins.str] = None,
    review_sub_reason: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df589fc19619f3873adf79f3e9285c31e416eeb08f4ef512b22dda40ced8ce21(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c72687f315fa2f096ba5256feb529bdfa8270c4ca0bec875dbd030ad54adfa0(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5d6e695585b637bdade16608035a176a86f0eea8e02e0bc5d7f83c721fd0e20(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db14770f14d505a9ab920f6cb956eb3fd21714205c90a50983cd2f2699bbfe2c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5549a1d0bb078a72459ee9656ea0c4a24ff2cf21e0298e999227e5a41eb9d978(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7df44d82b18f45154191dc01414a67f0df7dda0777e7aaef1b6ce894969c4a1c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomAssetNotebookReviews]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__352e25dc381fef339f0aa33ec989aa5488a6e179eb17c733077956379723d2a8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__198ed7eba43585fc18ee814eff56941def60cece35b9f24731b67d553a134a2b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d80d80d9b720cb17dbbfa9671f4019de23c4d0f080092143aa026108a105127(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02e2d5e1a9d3a894967f7b21f2f59cdf9687a31a9749ccaa9cd380a6ac168356(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6bdd58fcc3fdd5fe76b297352677f289744c6faa49239f673d92f384e0e5502(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a7b0bf1a453c937537bc106875e96dbfcba7b75e4da37c36bc068706b3c161f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5a020a4625c80229c9bad2c5676f2341577c1e563566a0b7522167745846c7a(
    value: typing.Optional[CleanRoomAssetNotebookReviews],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__330b39ccafa36ba273af82f7fce7721135a0aee7757bcccd6e1190f887ceac1b(
    *,
    comment: typing.Optional[builtins.str] = None,
    mask: typing.Optional[typing.Union[CleanRoomAssetTableColumnsMask, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__7ed1bf7c9186bd4e172058814a0bbbd79ab5c62ed456d6f51590c4e22194d081(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a8777303d754cdcbb8de81a02cd9b1288ffd3580233a8f2919582e5a2710ef9(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8f7a615305076966c24a4911d945f90dc317e8155cdd2900e4280fdb422746b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f2f5d436f9a8866fce0bf50f7fff2cff793b216177dcc8368ad56390f36670d(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__039d8fd8b447e1ccd06c58f13f8e630a9cd662e44e7199895d34cdb86bb3991e(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b827e40fade76c0b742e8eebd7fd0dc088b584fdc44272f5fe750998cc4e130(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomAssetTableColumns]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3315efe05f43b9bd5080322be8ed55bc79b606a644b617497d6fdd9cfc763577(
    *,
    function_name: typing.Optional[builtins.str] = None,
    using_column_names: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49453691ce974e5d1162db50ba4b8bd7806e524630f1f9d2e0fdddabad2401a6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3b08fd640dd367ac9f4d0595d826b04bd8adb9b3c09937453518a9746bef324(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61d66edaec750792f3b7d09686ac43b6dd891ecc63c7d5d1a81ffc81d0894cc8(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2fb267ce8c89d97d72eb4dd791679f81043a0a983bb76ed180299c5c4da5e13(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetTableColumnsMask]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d1b0697f9a9ac3a356f80c0351477738910df1d233beca9ea4cf182c90afba9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8b2ab9e48ced85375ff7ca4238cee2d063167e41a0ec20566f49126573332ce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54b6760c1505508c081d4488136c4e158dcdc5864fe9063f6e4dd9f3a701c745(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__461d0cb4e22b31f7c4c55513f7215d8bcba5cd7d2c8f64fcf5f1ae385d9fe5e4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a35f209c5dd84a915838665c22da049d33e7db50ff5347415991cfcaf8752e2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05f31f071630a608b5b7e2f1eefdb222528004559064c66ab8e8c73f7fd935e7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__016259e6282dcf75a27e67257714c9a35a950b71017554d56162d715d176fc1c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e228eb334e233fa284ed4cb921767e991c9b1d8d1f874053ec5282d908720b30(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87def45ed2eb0841ef8d01be4a296f5ffc38a4888a8e086f99700e734e2d1da7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc3745c5b6b561f2ed5ff40acfe173162602af714b137472987ad2588ac4b953(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f970dc6e5cea7229000e941a4060a4f32677dab4298428f69acac19e1301af60(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c522ad4005f10014cf029d835c958a6d486d23bd4db428c28e50168dbbfe98b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c676b7ccd024da2ede8f3a2afa39f1f38fdbc9c4675e1968e3cf50e7c40d75d7(
    value: typing.Optional[CleanRoomAssetTableColumns],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4739882ea5c921acc89f5fa1ed73ab9a303c28240beb3fac5c8a4223744d524b(
    *,
    local_name: builtins.str,
    partitions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CleanRoomAssetTableLocalDetailsPartitions, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a00347ef51cecd12f864ed6b49a958c54aeb7d5426175d41fdacd715be17bc68(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e53e39e89d3c9b2c029c5fd14a1668d2e24f73717e14fdae332f6b24cfb8ade(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CleanRoomAssetTableLocalDetailsPartitions, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b462f8bacb796f8efb86a5ee44ca41c72af9d1699e053e1d0d436223a6dc945a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d04371b6a6fe5f84f57560e35429dc95737153bb09713d15e3c4b181ee572f52(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetTableLocalDetails]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe4586424526874249b6393075b1bd4ff32102e78fe70e232f13717d1ece3c35(
    *,
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CleanRoomAssetTableLocalDetailsPartitionsValue, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e66bb5227c8c1674a4e48a7dec48d4a3853b12d34065850a1b2e263b517a27f9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28702293b245217fbb6a35b2e58c5d702f2729a496d2e5b21121b93e37229945(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3a715afa76a98acc215bf3264fae94a90495a647eec6a36c4d067b0d81a59c7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fef7d4c6f0ba83b8544fec43fa901db892958d425d63b02fc2dd966ade1aba5b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83c3d49d5ac145a5a5978553e7ff4ae2c17c7b98f83af7835f9e1e0fd2264d1d(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f061627bc63005e7eec5ccb075dde6f48ecbf438195192600a9467d0476bdde(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomAssetTableLocalDetailsPartitions]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84c9cb305d32cb808b5ab664461e032c9ff385b0f8b49f7c11eb44ca17b58321(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__667727871f18b4a098dc9d1dea45904fa023ffcbd4cb77f18ec4a9444831d1e8(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CleanRoomAssetTableLocalDetailsPartitionsValue, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52b813a53a2e2f0b570a665d15e2f3291dd53babbb5e447d23d3bf4db61d5a5c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetTableLocalDetailsPartitions]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac68bd01a977692d8da1f87974397d241ea7585aaa871b526d1501996309a614(
    *,
    name: typing.Optional[builtins.str] = None,
    op: typing.Optional[builtins.str] = None,
    recipient_property_key: typing.Optional[builtins.str] = None,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec40d452005088fb09144f8a2ed106ad1cdcee5549c32c7746552f345794aed8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86ded69c8aff8f9d295430641a1a66c4b56a46d16bbdb5132dc07553d1f29ff3(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f73f016e25a4addc910272beb769f0906a04e2a2067441b0c6c9dfbb8e15f6e1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51b639395a20347f835fca36881ac632e1b34dc0968a2c7610d34cc543bbf220(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f1cb0a0bb9badeb26c32c460ad364213870d9e9f2d3ed7d5baf1f1b63159466(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5add6dbeece996b02ff7ed8f4f024e02fb04978b0c5a01f173aeb61c2902a66e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomAssetTableLocalDetailsPartitionsValue]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1508e5ec934b14d4fc30c1933795865e7d9d48653eff6cfeca7ccdfb44f9e48(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfbc7439d22cc3eabb44c8dd188253b8e63b5eab6d44ba063ff6e3974e9ddb20(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99aa2483f40902264142faf81d51513fff47c83ad0815d657ce5ead4d5104929(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abf81c090026928669194a0af9c9951d8ef492e40addd3e5d082c4d643ba6f4d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fadfbe0a654608d50d51749d4679501ca4b5ed417731d567bf6b0f2c59214c6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6590ef57e26928d4f76074e053f71479de1baa05f8faa4fe9d56a3458344806(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetTableLocalDetailsPartitionsValue]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52f6c147007e842416e53e2b86af4da9f050462b722cf44166b115d2069d28da(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81b11b165bf40d47c04a91cb5385dae80ec06dcd5f5184cb6e8627cb4fd59068(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetTable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d16925fbb01d8a995647387395c00b9c2df27678c07e1e939607ae7d1e38539(
    *,
    comment: typing.Optional[builtins.str] = None,
    mask: typing.Optional[typing.Union[CleanRoomAssetViewColumnsMask, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__63e532ee44287ba478bdd5e29da577bdeb3ceffaf34ec8a3236e8cb7dae36905(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec8ba41b72b085a0a18d18fd120f3e123e38fd9022d818b7d82e697f9052982a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__356f030415058a84236897d32f9db58da9eb4a73438e48687e255fe3dcaddab1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__453d9c07b6f05e6d4dbf415475ea72f39b3a36003ef75532b9cfa1858f2f8cd5(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__579a89d5217988a46c29f908ccab645043d272145df3131a7c1f50508896ab20(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__696d07f168530eb04bbf79c3cf59c1913fad60e382d36c6ccd65f2fc4856f713(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomAssetViewColumns]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b06202038eee6dbeba0f5d47a292ae2152e54defd151b6b31d05cd9927ee3853(
    *,
    function_name: typing.Optional[builtins.str] = None,
    using_column_names: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c216ac0ec510c9433b2cd3f9da321f1f8f9da2e01b86d096c91b5ba4d3a35ac0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95ab3e754db52dc3e1ae759c31aa9330d9cce6f2ff940fa4cae0c54f03df8715(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a1899674320a0bd35b5eced681b16808cd0919f02ddfbf1b992205cab867aa6(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__320ea75a1abadca5baa2dd5b1b3655f804a4f66a019829aa7122c43f109d932d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetViewColumnsMask]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b57e735cf84d48aa2722ccb28ec7a07d139f4abbfcc925638d1110ad50ffaec1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41a26465ef8ebaf2c5cb08d767fb1db9bdf11c73be6fca93619f6ae0f43dc1fa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d55021979e8e669bf6534495cab0269f2260e8e71661b2abc5ef8a3b939b7f6e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__519d7809a8687f0c4419435931008a9217f51cc590eda9f89bf494221ddeea31(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3b7cc3b03dd64a303f2408f414b851cc2774af5ce20f208e96e9e538c116712(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86cef1844c293cd8ac5389a3c832da2f5f4e22f3782f08b9f8d0e8f5707fff89(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0a98d1beacd44615cfa0cfcea747ad93553d812ea03d9a3fd9ae6216e94fea7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__001ce2097943c965e197f14907feb5055fb81230cfb671d6c4006a29ad01d988(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da826697ed229e185d7b3e35b612ef02bea7e424a4df70d5022f378cac70d20c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3fc4576304b1330bbdd68b96738289c26ed4c67a7c4c4929f68f2fe746ca2bf(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__853a58c2dbf4eb97d8ebae8850967c71860cfcc7915f533ec7107dd019a35499(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af9dc952ae98dd0aa68ec67edc5ec36acd38ef3696731cad20f870f90d0d0f7f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48c074dbf640776727fdc41b6e7355d23e4778a3b215db2e0c96d44df3e93cbc(
    value: typing.Optional[CleanRoomAssetViewColumns],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e2112e7f9a7b1e6bdf34d479b95cdf9e2cc7ba8b2e448f1f00c5bcd511a982a(
    *,
    local_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__874ced66a77395144cea324224e941d89ac20ab73ba0343c8eb6253717686ad3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2665edd86c7cfd42e515fa4d7b7fa9f8dd2b74ecaaf964c95d06f1666c11a5f9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6b0b366248c6c889e209115cc710f72df7bb917516cf7ac0e22bc2a5748cc13(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetViewLocalDetails]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccac5fd3fae473caa0803c1002e3bfd5812bc1e59adae1332bd9f2e50e355b7d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2be84331fbac858531de97555a88cadf75e7addaa7004a69770ff5df0bf39a97(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetView]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8886ab3ec8632f59db14f22f8a91da5a1af38c5b7bf71ee693522c728bbc5e21(
    *,
    local_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3895c88f02508e89aafa3c447bc56c83a286f54b558a471e6922895eda40469b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2685fc303152c181af93c31eb6f374eacced39feb5ff55508bf96169be060ca8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e11b30eebd428ce55fc272c77254f1588b435e404a791c007e4ff70f8b32750(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomAssetVolumeLocalDetails]],
) -> None:
    """Type checking stubs"""
    pass
